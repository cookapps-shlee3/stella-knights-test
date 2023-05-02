# -*- coding: utf-8 -*-
import json
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.db.models.user import UserMembers, UserPayment, UserDataBattle, UserReview
from app.redis.redisCache import redis
from app.config.settings import Constant

async def get(db:Session, uid:int, is_first:bool=False) -> UserMembers:
    key = Constant.PROJECT_NAME + '_member'
    if not is_first:
        str_json = await redis.get_hash(key, uid)
        if str_json:
            member_info = json.loads(str_json)
            if member_info:
                user_member = UserMembers()
                user_member.setClassFromDict(member_info)
                return user_member
        else:
            user_member = db.query(UserMembers).filter(UserMembers.uid == uid).first()
    else:
        user_member = db.query(UserMembers).filter(UserMembers.uid == uid).first()
    
    if user_member:
        str_json = jsonable_encoder(user_member)
        await redis.set_hash(key, uid, json.dumps(str_json, ensure_ascii = False))
        
    return user_member

def create(db:Session, device_id, social_id:str='', type=0,  server=0):
    if type == 0:
        db_user = UserMembers()
        db_user.server = 0
        db_user.login_device_id = device_id
        db_user.social_id = social_id
        db_user.created = datetime.now()
        db_user.updated = datetime.now()

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        db_user.nickname = 'guest_' + str(db_user.uid)
        db.query(UserMembers).filter(UserMembers.uid == db_user.uid).update({UserMembers.nickname : db_user.nickname})
        # db.add(db_user)
        db.commit()
        db.refresh(db_user)
    else:
        db_user = UserMembers()
        db_user.login_device_id = device_id
        db_user.is_nickname = 1
        db_user.social_id = social_id
        db_user.created = datetime.now()
        db_user.updated = datetime.now()
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    return db_user

def create_new_server(db:Session, device_id:str, social_id:str='', server:int=0):
    db_user = UserMembers()
    db_user.server = server
    db_user.login_device_id = device_id
    db_user.social_id = social_id
    db_user.created = datetime.now()
    db_user.updated = datetime.now()
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    db_user.nickname = 'guest_' + str(db_user.uid)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user.uid


async def update_server(db:Session, uid:int, server:int):
    key = Constant.PROJECT_NAME + '_member'
    str_json = await redis.get_hash(key, uid)
    if str_json:
        member_info = json.loads(str_json)
        if member_info:
            user_member = UserMembers()
            user_member.setClassFromDict(member_info)
            user_member.server = server
            str_json = jsonable_encoder(user_member)
            await redis.set_hash(key, uid, json.dumps(str_json, ensure_ascii = False))
        
    res = db.query(UserMembers).filter(UserMembers.uid == uid).update({'server': server})
    db.commit()
    return res


async def update_social_id(db:Session, uid:int, social_id:str):
    key = Constant.PROJECT_NAME + '_member'
    str_json = await redis.get_hash(key, uid)
    if str_json:
        member_info = json.loads(str_json)
        if member_info:
            user_member = UserMembers()
            user_member.setClassFromDict(member_info)
            user_member.social_id = social_id
            str_json = jsonable_encoder(user_member)
            await redis.set_hash(key, uid, json.dumps(str_json, ensure_ascii = False))
        
    res = db.query(UserMembers).filter(UserMembers.uid == uid).update({'social_id': social_id})
    db.commit()
    return res


async def update_term_agree_lst(db:Session, uids:list):
    for uid in uids:
        key = Constant.PROJECT_NAME + '_member'
        str_json = await redis.get_hash(key, uid)
        if str_json:
            member_info = json.loads(str_json)
            if member_info:
                user_member = UserMembers()
                user_member.setClassFromDict(member_info)
                user_member.is_terms_agree = 1
                str_json = jsonable_encoder(user_member)
                await redis.set_hash(key, uid, json.dumps(str_json, ensure_ascii = False))
    
    db.query(UserMembers).filter(UserMembers.uid.in_(uids)).update({'is_terms_agree':1})
    db.commit()


async def update_refresh(db:Session, uid:int):
    key = Constant.PROJECT_NAME + '_member'
    str_json = await redis.get_hash(key, uid)
    if str_json:
        member_info = json.loads(str_json)
        if member_info:
            user_member = UserMembers()
            user_member.setClassFromDict(member_info)
            user_member.updated = datetime.now()
            str_json = jsonable_encoder(user_member)
            await redis.set_hash(key, uid, json.dumps(str_json, ensure_ascii = False))
            
    db.query(UserMembers).filter(UserMembers.uid == uid).update({'updated': datetime.now()})
    db.commit()

    
async def update_level(db:Session, uid:int, level:int):
    key = Constant.PROJECT_NAME + '_member'
    str_json = await redis.get_hash(key, uid)
    if str_json:
        member_info = json.loads(str_json)
        if member_info:
            user_member = UserMembers()
            user_member.setClassFromDict(member_info)
            user_member.level = level
            user_member.updated = datetime.now()
            str_json = jsonable_encoder(user_member)
            await redis.set_hash(key, uid, json.dumps(str_json, ensure_ascii = False))
            
    db.query(UserMembers).filter(UserMembers.uid == uid).update({'level' : level, 'updated' : datetime.now()})
    db.commit()


async def update_login_device_id(db:Session, uid:int, device_id:str):
    key = Constant.PROJECT_NAME + '_member'
    str_json = await redis.get_hash(key, uid)
    if str_json:
        member_info = json.loads(str_json)
        if member_info:
            user_member = UserMembers()
            user_member.setClassFromDict(member_info)
            user_member.login_device_id = device_id
            str_json = jsonable_encoder(user_member)
            await redis.set_hash(key, uid, json.dumps(str_json, ensure_ascii = False))
            
    db.query(UserMembers).filter(UserMembers.uid == uid).update({'login_device_id' : device_id})
    db.commit()
    
    
def has_nickname(db:Session, nickname:str):
    res = db.query(UserMembers).filter(UserMembers.nickname == nickname).count()
    return True if res > 0 else False


async def update_nickname(db:Session, uid:int, nickname:str):
    key = Constant.PROJECT_NAME + '_member'
    str_json = await redis.get_hash(key, uid)
    if str_json:
        member_info = json.loads(str_json)
        if member_info:
            user_member = UserMembers()
            user_member.setClassFromDict(member_info)
            user_member.nickname = nickname
            str_json = jsonable_encoder(user_member)
            await redis.set_hash(key, uid, json.dumps(str_json, ensure_ascii = False))
    db.query(UserMembers).filter(UserMembers.uid == uid).update({'nickname' : nickname, 'is_nickname' : 1})
    db.commit()
    
    

# def has_accountId(db:Session, uid:int):
#     res = db.query(UserAccount).filter(UserAccount.uid == uid).count()
#     return True if res > 0 else False


# def update_accountID(db:Session, uid:int, nickname:str):
#     db.query(UserAccount).filter(UserAccount.uid == uid).update({UserAccount.auth_id : nickname})
    

def check_purchase(db:Session, uid:int):
    res = db.query(UserPayment).filter(UserPayment.uid == uid).count()
    return True if res > 0 else False


def get_profile_data(db:Session, uid:int):
    battle_data = db.query(UserDataBattle).filter(UserDataBattle.uid == uid).first()
    if battle_data:
        battle_data = json.loads(battle_data.data)
        profile_info = {
            'uid' : battle_data['uid'],
            'nickname' : battle_data['nick'],
            'data' : battle_data
        }
        
    else:
        profile_info = None
        
    return profile_info
    
    
def get_review(db:Session, uid:int):
    res = db.query(UserReview).filter(UserReview.uid == uid).one_or_none()
    return res

    
def insert_rewiew(db:Session, uid:int, language:str, purchased:int, legend_count:int, art:float, fun:float, balance:float, ip:str):
    db_user = UserReview()
    db_user.uid = uid
    db_user.language = language
    db_user.purchased = purchased
    db_user.legend_count = legend_count
    db_user.art_star = art
    db_user.fun_star = fun
    db_user.balance_star = balance
    db_user.ip = ip
    db_user.created = datetime.now()
    
    db.add(db_user)
    db.commit()
