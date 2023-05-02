# -*- coding: utf-8 -*-
import time
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.params.ResParam import ResponseCode
from app.db.models.user_postbox import *
from app.db.models.special_postbox import SpecialPostbox
from dateutil.relativedelta import relativedelta
from app.util.util import get


def check_special_post(db:Session, uid:int, server:int):
    now = int(time.time())
    server_list = [0, server]
    special_posts = db.query(SpecialPostbox).filter(SpecialPostbox.server.in_(server_list), SpecialPostbox.expire_time>now, SpecialPostbox.start_time<=now).all()
    
    if special_posts:
        for post in special_posts:
            special_post_id = post.special_post_id
            is_rewarded_count = __get_is_rewarded_count(db, uid, special_post_id)
            if not is_rewarded_count:
                data = __get_user_postbox_orm(uid)
                data.uid = uid
                data.sender_uid = 0
                data.title_code = post.title_code
                data.desc_code = post.desc_code
                data.tab = 1
                data.product_id = None
                data.rewards = post.rewards
                data.start_time = post.start_time
                data.expire_time = post.expire_time
                data.created = datetime.now()
                data.special_reward_id = special_post_id
                
                db.add(data)
                db.commit()
                db.refresh(data)
                
def __get_is_rewarded_count(db:Session, uid:int, special_post_id:int):
    user_postbox = globals()[f"UserPostbox_{uid % 10}"]
    is_rewarded_count = db.query(user_postbox).filter(user_postbox.uid == uid,  user_postbox.special_reward_id == special_post_id).count()
    
    return is_rewarded_count

def is_exist_non_reward_post(db:Session, uid:int):
    now = int(time.time())
    user_postbox = globals()[f"UserPostbox_{uid % 10}"]
    non_rewarded_posts = db.query(user_postbox).filter(user_postbox.uid == uid, user_postbox.is_rewarded == 0, user_postbox.expire_time > now, user_postbox.start_time <= now).count()
    
    return True if non_rewarded_posts > 0 else False

def _get_admin_nickname(country:str):
    nickname = 'Operator'
    if country == 'KR':
        nickname = '운영자'
    elif country == 'TW':
        nickname = '遊戲操作負責人'
    elif country == 'CN':
        nickname = '游戏操作负责人'
    elif country == 'JP':
        nickname = '運営者'
        
    return nickname

def get_list(db:Session, uid:int, country:str='EN'):
    now = int(time.time())
    mod = uid%10
    sql = "SELECT t1.post_id, t1.sender_uid, t4.nickname as sender_nickname, t1.product_id, t1.product_key, t1.rewards, "
    sql += "t2.desc as `title`, t3.desc as `desc`, t1.start_time, t1.expire_time "
    sql += "FROM user_postbox_{} t1 LEFT JOIN user_members t4 ON t1.sender_uid = t4.uid "
    sql += "LEFT JOIN spec_postbox t2 ON t1.title_code = t2.code AND t2.category = 'TITLE' AND t2.country = '{}' "
    sql += "LEFT JOIN spec_postbox t3 ON t1.desc_code = t3.code AND t3.category = 'DESC' AND t3.country = '{}' "
    sql += "WHERE t1.uid = {} AND t1.is_rewarded = 0 AND t1.expire_time > {} AND t1.start_time <= {} ORDER BY t1.post_id DESC LIMIT 0, 30 "
    sql = sql.format(mod,country, country, uid, now, now)
    a = db.execute(sql)
    result = a.fetchall()
    
    admin_nickname = _get_admin_nickname(country=country)
    
    value = []
    if result:
        for post in result:
            temp = dict(post)
            if not temp['sender_uid']:
                temp['sender_nickname'] = admin_nickname
            
            # 보상이 있는 경우에는 json 형태로 변환해서 넣어주도록 코드 추가함.
            if get(temp, 'rewards'):
                temp['rewards'] = json.loads(temp['rewards'])
                
            
            value.append(temp)
    
    return value

def get_reward(db:Session, uid:int, post_id:int):
    user_postbox = globals()[f"UserPostbox_{uid % 10}"]
    post = db.query(user_postbox).filter(user_postbox.post_id == post_id, user_postbox.uid == uid).first()
    
    return post

def update_reward(db:Session, uid:int, post_id:int):
    user_postbox = globals()[f"UserPostbox_{uid % 10}"]
    res = db.query(user_postbox).filter(user_postbox.post_id == post_id).update({user_postbox.is_rewarded : 1})
    
    if not res:
        return ResponseCode.RES_INTERNAL_SERVER_ERROR
    
    db.commit()
    
    return ResponseCode.RES_SUCCESS

def reward(db:Session, uid:int, post_id:int):
    user_postbox = globals()[f"UserPostbox_{uid % 10}"]
    post = db.query(user_postbox).filter(user_postbox.post_id == post_id, user_postbox.uid == uid).first()
    
    if not post:
        return ResponseCode.RES_INVALID_POST_ID
    
    if post.is_rewarded == 1:
        return ResponseCode.RES_ALREADY_REWARDED
    
    now = int(time.time())
    if post.expire_time < now:
        return ResponseCode.RES_EXPIRED_POST_ID
    
    
    res = db.query(user_postbox).filter(user_postbox.post_id == post_id).update({user_postbox.is_rewarded : 1})
    
    if not res:
        return ResponseCode.RES_INTERNAL_SERVER_ERROR
    
    db.commit()
    
    return ResponseCode.RES_SUCCESS

def rewards(db:Session, uid:int, post_ids:list):
    user_postbox = globals()[f"UserPostbox_{uid % 10}"]
    
    res = db.query(user_postbox).filter(user_postbox.uid == uid, user_postbox.post_id.in_(post_ids)).update({user_postbox.is_rewarded : 1})
    
    if not res:
        return ResponseCode.RES_INTERNAL_SERVER_ERROR
    
    db.commit()
    
    return ResponseCode.RES_SUCCESS

def get_rewards(db:Session, uid:int, post_ids:list):
    user_postbox = globals()[f"UserPostbox_{uid % 10}"]
    posts = db.query(user_postbox).filter(user_postbox.uid == uid, user_postbox.post_id.in_(post_ids), user_postbox.is_rewarded != 1).all()
    
    return posts

def send_mail(db:Session, uid:int, rewards:list):
    now = datetime.now()
    data = __get_user_postbox_orm(uid)
    data.uid = uid
    data.sender_uid = 0
    data.title_code = 110017
    data.desc_code = 120025
    data.tab = 0
    data.product_id = None
    data.rewards = json.dumps(rewards)
    data.start_time = int(time.time())
    data.expire_time = int(time.time())+(60*60*24*365)
    data.created = datetime.now()
    
    db.add(data)
    db.commit()
    
def send_payment_mail(db:Session, uid:int, rewards:list, product_id:str):
    now = datetime.now()
    data = __get_user_postbox_orm(uid)
    data.uid = uid
    data.sender_uid = 0
    data.title_code = 110017
    data.desc_code = 120025
    data.tab = 0
    data.product_id = product_id
    data.rewards = json.dumps(rewards)
    data.start_time = int(time.time())
    data.expire_time = int(time.time())+(60*60*24*365)
    data.created = datetime.now()
    
    db.add(data)
    db.commit()

def __get_user_postbox_orm(uid:int):
    user_postbox = globals()[f"UserPostbox_{uid % 10}"]
    insert_data = user_postbox()
        
    return insert_data