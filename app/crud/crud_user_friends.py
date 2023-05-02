# -*- coding: utf-8 -*-
import time
import random
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models.user import UserMembers,UserFriends, UserFriendsInvite, UserFriendsRemove, UserSendGift, UserPostbox, FriendInfoBase
from app.config.settings import Constant
from app.params.ResParam import ResponseCode


def find_nickname(db:Session, nickname:str, server:int):
    search = "%{}%".format(nickname)
    return db.query(UserMembers).filter(UserMembers.nickname.like(search)).all()
    


def friends_list(db:Session, uid:int):
    sql = "SELECT t3.uid, t3.level, t3.server, t3.nickname, UNIX_TIMESTAMP(t3.updated) as updated, ifnull(t2.send_count, 0) as send_count "
    sql += ", ifnull(t2.date_key, 0) as date_key, t1.point, t1.gift_send FROM "
    sql += "user_friends t1 left join user_send_gift t2 on t1.friend_uid = t2.uid "
    sql += "left join user_members t3 on t1.friend_uid = t3.uid "
    sql += "WHERE t1.uid = {}"
    sql = sql.format(uid)
    query = db.execute(sql)
    result = query.fetchall()
    
    value = []
    if result:
        for friend in result:
            temp = dict(friend)
            if not temp['uid']:
                continue
            value.append(temp)
    
    return value


def friend_reverse_list(db:Session, uid:int):
    return db.query(UserFriends).filter(UserFriends.friend_uid == uid).all()


def friends_list_invite(db:Session, uid:int):
    sql = "SELECT t2.uid, t2.level, t2.server, t2.nickname, UNIX_TIMESTAMP(t2.updated) as updated FROM user_friends_invite t1 LEFT JOIN user_members t2 "
    sql += "ON t1.friend_uid = t2.uid WHERE t1.uid = {}"
    sql = sql.format(uid)
    query = db.execute(sql)
    result = query.fetchall()
    value = []
    
    if result:
        for friend in result:
            value.append(dict(friend))
    
    return value


def friend_list_my_invite(db:Session, uid:int):
    sql = "SELECT t2.uid, t2.level, t2.server, t2.nickname, UNIX_TIMESTAMP(t2.updated) as updated FROM user_friends_invite t1 LEFT JOIN user_members t2 "
    sql += "ON t1.uid = t2.uid WHERE t1.friend_uid = {}"
    sql = sql.format(uid)
    query = db.execute(sql)
    result = query.fetchall()
    value = []
    
    if result:
        for friend in result:
            value.append(dict(friend))
    
    return value


def random_list(db:Session, uid:int, my_level:int, server:int):
    uid_list = [uid]
    friends_list = db.query(UserFriends).filter(UserFriends.uid == uid).all()
    
    if friends_list and len(friends_list) > 0 :
        for friend in friends_list:
            uid_list.append(friend.friend_uid)

    row_level = 1 if ((my_level - 10) < 0) else my_level - 10
    high_level = 200 if ((my_level + 10) > 200) else my_level + 10
    
    # random_list = db.query(UserMembers).filter(UserMembers.uid.in_(uid_list), UserMembers.server == server, UserMembers.level >= row_level, UserMembers.level <= high_level).order_by(func.rand()).limit(20)
    query = db.query(UserMembers).filter(UserMembers.uid.notin_(uid_list), UserMembers.server == server, UserMembers.level >= row_level, UserMembers.level <= high_level)
    row_count = int(query.count())
    random_list = query.offset(int(row_count*random.random())).limit(20).all()
    
    random_result = []
    if random_list and len(random_list) > 0:
        for item in random_list:
            random_result.append(FriendInfoBase(item))
    
    return random_result


def remove_friend(db:Session, uid:int, target_uid:int):
    now_date_key = int(datetime.now().strftime('%Y%m%d'))
    my = UserFriendsRemove()
    target = UserFriendsRemove()
    my.uid = target.friend_uid = uid
    my.friend_uid = target.uid = target_uid
    my.date_key = target.date_key = now_date_key
    my.created = target.created = datetime.now()
    
    db.add_all([my, target])
    db.commit()
    
    db.query(UserFriends).filter(UserFriends.uid == uid, UserFriends.friend_uid == target_uid).delete()
    db.query(UserFriends).filter(UserFriends.uid == target_uid, UserFriends.friend_uid == uid).delete()
    return ResponseCode.RES_SUCCESS


def request_invite(db:Session, uid:int, target_uid:int):
    now_date_key = int(datetime.now().strftime('%Y%m%d'))
    remove_info = db.query(UserFriendsRemove).filter(UserFriendsRemove.uid == uid, UserFriendsRemove.friend_uid == target_uid).first()
    if remove_info and (remove_info.date_key >= now_date_key):
        return ResponseCode.RES_INVALID_REMAINING_TIME
    
    if db.query(UserFriendsInvite).filter(UserFriendsInvite.uid == target_uid).count() >= Constant.FRIENDS_MAX_COUNT :
        return ResponseCode.RES_INVITE_FRIENDS_EXCEED
    if db.query(UserFriendsInvite).filter(UserFriendsInvite.uid == target_uid, UserFriendsInvite.friend_uid == uid).first():
        return ResponseCode.RES_ALREADY_INVITE_FRIEND
    if db.query(UserFriendsInvite).filter(UserFriendsInvite.uid == uid, UserFriendsInvite.friend_uid == target_uid).first():
        return ResponseCode.RES_ALREADY_INVITE_LIST
    
    if db.query(UserFriends).filter(UserFriends.uid == target_uid).count() >= Constant.FRIENDS_MAX_COUNT:
        return ResponseCode.RES_TARGET_FRIENDS_EXCEED
    if db.query(UserFriends).filter(UserFriends.uid == uid).count() >= Constant.FRIENDS_MAX_COUNT:
        return ResponseCode.RES_MY_FRIENDS_EXCEED
    
    db.add(UserFriendsInvite(target_uid, uid))
    db.commit()
    return ResponseCode.RES_SUCCESS


def cancel_invite(db:Session, uid:int, target_uid:int):
    db.query(UserFriendsInvite).filter(UserFriendsInvite.uid == target_uid, UserFriendsInvite.friend_uid == uid).delete()
    db.commit()
    return ResponseCode.RES_SUCCESS


def accept_invite(db:Session, uid:int, target_uid:int):
    now_date_key = int(datetime.now().strftime('%Y%m%d'))
    remove_info = db.query(UserFriendsRemove).filter(UserFriendsRemove.uid == uid, UserFriendsRemove.friend_uid == target_uid).first()
    
    if remove_info and (remove_info.date_key >= now_date_key):
        return ResponseCode.RES_INVALID_REMAINING_TIME
    
    if db.query(UserFriends).filter(UserFriends.uid == uid).count() >= Constant.FRIENDS_MAX_COUNT:
        return ResponseCode.RES_MY_FRIENDS_EXCEED
    
    if db.query(UserFriends).filter(UserFriends.uid == target_uid).count() >= Constant.FRIENDS_MAX_COUNT:
        return ResponseCode.RES_TARGET_FRIENDS_EXCEED
    
    my = UserFriends(uid, target_uid)
    target = UserFriends(target_uid, uid)
    
    db.add_all([my, target])
    db.commit()
    
    db.query(UserFriendsInvite).filter(UserFriendsInvite.uid == uid, UserFriendsInvite.friend_uid == target_uid).delete()
    db.query(UserFriendsInvite).filter(UserFriendsInvite.uid == target_uid, UserFriendsInvite.friend_uid == uid).delete()
    db.query(UserFriendsRemove).filter(UserFriendsRemove.uid == uid, UserFriendsInvite.friend_uid == target_uid).delete()
    db.query(UserFriendsRemove).filter(UserFriendsRemove.uid == target_uid, UserFriendsInvite.friend_uid == uid).delete()
    
    return ResponseCode.RES_SUCCESS


def refuse_invite(db:Session, uid:int, target_uid:int):
    db.query(UserFriendsInvite).filter(UserFriendsInvite.uid == uid, UserFriendsInvite.friend_uid == target_uid).delete()
    return ResponseCode.RES_SUCCESS


def refresh_gift(db:Session, uid:int):
    now_date_key = int(datetime.now().strftime('%Y%m%d'))
    db.query(UserFriends).filter(UserFriends.uid == uid, UserFriends.date_key < now_date_key).update({UserFriends.gift_send: 1})
    db.commit()
    send_gift = db.query(UserSendGift).filter(UserSendGift.uid == uid).first()
    
    if not send_gift:
        data = UserSendGift()
        data.uid = uid
        data.send_count = 0
        data.date_key = now_date_key
        data.created = datetime.now()
        
        db.add(data)
        db.commit()
        db.refresh(data)
        return data
    else:
        if send_gift.date_key < now_date_key:
            db.query(UserSendGift).filter(UserSendGift.uid == uid).update({UserSendGift.date_key : now_date_key, UserSendGift.send_count : 0})
            send_gift.date_key = now_date_key
            send_gift.send_count = 0
            db.commit()
            return send_gift
        else:
            return send_gift
    

def get_send_gift_count(db:Session, target_uid:int):
    now_date_key = int(datetime.now().strftime('%Y%m%d'))
    send_gift = db.query(UserSendGift).filter(UserSendGift.uid == target_uid).first()
    
    if not send_gift:
        data = UserSendGift()
        data.uid = target_uid
        data.send_count = 0
        data.date_key = now_date_key
        data.created = datetime.now()
        
        db.add(data)
        db.commit()
    else:
        if send_gift.date_key < now_date_key:
            db.query(UserSendGift).filter(UserSendGift.uid == target_uid).update({UserSendGift.date_key : now_date_key, UserSendGift.send_count : 0})
            db.commit()
        else:
            return send_gift.send_count
    return 0



def send_gift(db:Session, uid:int, target_uid:int, friend_send_count:int):
    friend_info = db.query(UserFriends).filter(UserFriends.uid == uid, UserFriends.friend_uid == target_uid).first()
    if not friend_info:
        return ResponseCode.RES_INVALID_FRIEND
    
    if friend_info.gift_send < 1:
        return ResponseCode.RES_INVALID_GIFT_SEND
    
    db.query(UserFriends).filter(UserFriends.uid == uid, UserFriends.friend_uid == target_uid).update({UserFriends.gift_send : 0, UserFriends.date_key : int(datetime.now().strftime('%Y%m%d'))})
    db.query(UserSendGift).filter(UserSendGift.uid == target_uid).update({UserSendGift.send_count : (friend_send_count+1)})
    db.commit()
    
    post_type = ''
    post_count = 0
    post_id = 0
    rand = random.randint(0, 10000)
    if rand <= 3000:
        post_type = 'COIN'
        post_count = random.randint(1000000, 3000000)
    elif rand > 3000 and rand <= 5000:
        post_type = 'JEWEL'
        post_count = random.randint(300, 500)
    elif rand > 5000 and rand <= 7000:
        post_type = 'PICK'
        post_count = 10
    elif rand > 7000 and rand <= 9000:
        post_type = 'MIMIC_KEY'
        post_count = 1
    elif rand > 9000 and rand <= 10000:
        post_type = 'SOUL_STONE'
        post_count = 10

    now_ts = int(time.time())
    post_data = UserPostbox()
    post_data.uid = target_uid
    post_data.sender_uid = uid
    post_data.title_code = 110016
    post_data.desc_code = 120028
    post_data.tab = 0
    post_data.reward_type = post_type
    post_data.reward_id = post_id
    post_data.reward_count = post_count
    post_data.start_time = now_ts
    post_data.expire_time = now_ts + (86400 * 7)
    post_data.created = datetime.now()
    
    db.add(post_data)
    db.commit()
    
    return ResponseCode.RES_SUCCESS



def send_gifts(db:Session, uid:int):
    now_date_key = int(datetime.now().strftime('%Y%m%d'))
    sql = "SELECT t3.uid, t3.nickname, t2.send_count, t2.date_key, t1.point, t1.gift_send FROM "
    sql+= "user_friends t1 left join user_send_gift t2 on t1.friend_uid = t2.uid "
    sql+= "left join user_members t3 on t1.friend_uid = t3.uid "
    sql+= "WHERE t1.uid = {} AND t1.gift_send > 0"
    sql = sql.format(uid)
    query = db.execute(sql)
    result = query.fetchall()
    
    friend_gift_infos = []
    if result:
        for post in result:
            friend_gift_infos.append(dict(post))
    
    friend_uids = []
    friend_nosend_uids = []
    
    for gift_info in friend_gift_infos:
        if ('send_count' not in gift_info) or ('date_key' not in gift_info):
            data = UserSendGift()
            data.uid = uid
            data.send_count = 1
            data.date_key = now_date_key
            data.created = datetime.now()
            
            db.add(data)
            friend_uids.append(gift_info['uid'])
        else:
            if int(gift_info['date_key']) < now_date_key:
                db.query(UserSendGift).filter(UserSendGift.uid == int(gift_info['uid'])).update({UserSendGift.date_key : now_date_key, UserSendGift.send_count : 1})
                friend_uids.append(int(gift_info['uid']))
                db.commit()
            else:
                if gift_info['send_count'] < Constant.FRIENDS_MAX_GIFT_COUNT:
                    db.query(UserSendGift).filter(UserSendGift.uid == int(gift_info['uid'])).update({UserSendGift.send_count : (int(gift_info['send_count']) +1)})
                    friend_uids.append(int(gift_info['uid']))
                    db.commit()
                else:
                    friend_nosend_uids.append(int(gift_info['uid']))
        
    if len(friend_uids) == 0:
        return ResponseCode.RES_SUCCESS
    
    if len(friend_nosend_uids) > 0:
        db.query(UserFriends).filter(UserFriends.uid == uid, UserFriends.friend_uid.in_(friend_nosend_uids)).update({UserFriends.gift_send : 0, UserFriends.date_key : int(datetime.now().strftime('%Y%m%d'))})
        
    db.query(UserFriends).filter(UserFriends.uid == uid, UserFriends.friend_uid.in_(friend_uids)).update({UserFriends.gift_send : 0, UserFriends.date_key : int(datetime.now().strftime('%Y%m%d'))})
    db.commit()
    post_datas = []
    for friend_uid in friend_uids:
        post_type = ''
        post_count = 0
        post_id = 0
        rand = random.randint(0, 10000)
        if rand <= 3000:
            post_type = 'COIN'
            post_count = random.randint(1000000, 3000000)
        elif rand > 3000 and rand <= 5000:
            post_type = 'JEWEL'
            post_count = random.randint(300, 500)
        elif rand > 5000 and rand <= 7000:
            post_type = 'PICK'
            post_count = 10
        elif rand > 7000 and rand <= 9000:
            post_type = 'MIMIC_KEY'
            post_count = 1
        elif rand > 9000 and rand <= 10000:
            post_type = 'SOUL_STONE'
            post_count = 10

        now_ts = int(time.time())
        post_data = UserPostbox()
        post_data.uid = friend_uid
        post_data.sender_uid = uid
        post_data.title_code = 110016
        post_data.desc_code = 120028
        post_data.tab = 0
        post_data.reward_type = post_type
        post_data.reward_id = post_id
        post_data.reward_count = post_count
        post_data.start_time = now_ts
        post_data.expire_time = now_ts + (86400 * 7)
        post_data.created = datetime.now()
        
        post_datas.append(post_data)
        
    db.add_all(post_datas)
    db.commit()
    return ResponseCode.RES_SUCCESS
        
        
            