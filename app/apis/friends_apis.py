# -*- coding: utf-8 -*-
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.params.ResParam import get_response, ResponseCode
from app.config.settings import Constant
from app.params.ReqParam import BaseReqParam, FriendReqParam, FriendNickReqParam
from app.crud import crud_user_friends, crud_user_members


def friends_info(req:BaseReqParam, db:Session):
    my_gift_count = crud_user_friends.refresh_gift(db, req.uid)
    friends_list = crud_user_friends.friends_list(db, req.uid)
    request_list = crud_user_friends.friends_list_invite(db, req.uid)
    request_my_list = crud_user_friends.friend_list_my_invite(db, req.uid)
    reverse_friend_list = crud_user_friends.friend_reverse_list(db, req.uid)
    
    now_date_key = int(datetime.now().strftime('%Y%m%d'))
    
    if friends_list:
        for reverse in reverse_friend_list:
            value = [friend for friend in friends_list if friend['uid'] == reverse.uid]
            if value:
                if (reverse.gift_send > 1) and (reverse.date_key == now_date_key):
                    value[0]['sended'] = True
                else:
                    value[0]['sended'] = False
    
    response = {
        'friends' : friends_list if len(friends_list) > 0 else None,
        'friends_request' : request_list if len(request_list) > 0 else None,
        'my_request' : request_my_list if len(request_my_list) > 0 else None,
        'send_count' : my_gift_count.send_count if my_gift_count else 0,
        'date_key' : my_gift_count.date_key if my_gift_count else 0
    }
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=response, uid=req.uid)



async def friends_recommand(req:BaseReqParam, db:Session):
    user_member_info = await crud_user_members.get(db, req.uid)
    
    if not user_member_info:
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, msg='Invalid User ID', uid=req.uid)
    
    random_list = crud_user_friends.random_list(db, req.uid, user_member_info.level, user_member_info.server)
    response = {
        'recommend_friends' : random_list if len(random_list) > 0 else None
    }
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=response, uid=req.uid)


def friends_request_invite(req:FriendReqParam, db:Session):
    result = crud_user_friends.request_invite(db, req.uid, req.target_uid)    
    
    if result != ResponseCode.RES_SUCCESS:
        return get_response(code=result, uid=req.uid)
    
    response = {
        'target_uid' : req.target_uid
    }
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=response, uid=req.uid)



def friends_cancel_invite(req:FriendReqParam, db:Session):
    result_code = crud_user_friends.cancel_invite(db, req.uid, req.target_uid)
    request_list = crud_user_friends.friend_list_my_invite(db, req.uid)
    
    response = {
        "target_uid":req.target_uid, 
        "my_request" : request_list if request_list and len(request_list) > 0 else None
    }
    
    return get_response(code=result_code, data=response, uid=req.uid)


def friends_accept_invite(req:FriendReqParam, db:Session):
    result_code = crud_user_friends.accept_invite(db, req.uid, req.target_uid)
    
    if result_code != ResponseCode.RES_SUCCESS:
        return get_response(code=result_code, uid=req.uid)
    
    request_list = crud_user_friends.friends_list_invite(db, req.uid)
    response = {
        "target_uid" : req.target_uid,
        "friends_request" : request_list if request_list and len(request_list) > 0 else None
    }
    
    return get_response(code=result_code, data=response, uid=req.uid)


def friends_refuse_invite(req:FriendReqParam, db:Session):
    result_code = crud_user_friends.refuse_invite(db, req.uid, req.target_uid)
    if result_code != ResponseCode.RES_SUCCESS:
        return get_response(code=result_code, uid=req.uid)
    
    request_list = crud_user_friends.friends_list_invite(db, req.uid)
    response = {
        "target_uid" : req.target_uid,
        "friends_request" : request_list if request_list and len(request_list) > 0 else None
    }
    
    return get_response(code=result_code, data=response, uid=req.uid)


def friends_remove(req:FriendReqParam, db:Session):
    result_code = crud_user_friends.remove_friend(db, req.uid, req.target_uid)
    if result_code != ResponseCode.RES_SUCCESS:
        return get_response(code=result_code, uid=req.uid)
    
    crud_user_friends.refresh_gift(db, req.uid)
    friends_list = crud_user_friends.friends_list(db, req.uid)
    
    response = {
        "target_uid" : req.target_uid,
        "friends" : friends_list if friends_list and len(friends_list) > 0 else None
    }
    
    return get_response(code=result_code, data=response, uid=req.uid)


async def friends_nickname_find(req:FriendNickReqParam, db:Session):
    user_member_info =  await crud_user_members.get(db, req.uid)
    if user_member_info and (user_member_info.nickname == req.nickname):
        return get_response(code=ResponseCode.RES_INVALID_MY_INFO, uid=req.uid)
    
    result = crud_user_friends.find_nickname(db, req.nickname, user_member_info.server)
    response = {
        "find_list" : result if result and len(result) > 0 else None
    }
    return get_response(code=ResponseCode.RES_SUCCESS, data=response, uid=req.uid)
    


def friends_send_gift(req:FriendReqParam, db:Session):
    friend_send_count = crud_user_friends.get_send_gift_count(db, req.target_uid)
    
    if friend_send_count >= Constant.FRIENDS_MAX_GIFT_COUNT:
        return get_response(code=ResponseCode.RES_SEND_GIFT_COUNT_FULL, uid=req.uid)
    
    result_code = crud_user_friends.send_gift(db, req.uid, req.target_uid, friend_send_count)
    if result_code != ResponseCode.RES_SUCCESS:
        return get_response(code=result_code, uid=req.uid)
    
    friends_list = crud_user_friends.friends_list(db, req.uid)
    response = {
        "target_uid" : req.target_uid,
        "friends" : friends_list if friends_list and len(friends_list) > 0 else None
    }
    return get_response(code=ResponseCode.RES_SUCCESS, data=response, uid=req.uid)


def friends_send_gifts(req:FriendReqParam, db:Session):
    result_code = crud_user_friends.send_gifts(db, req.uid)
    
    if result_code != ResponseCode.RES_SUCCESS:
        return get_response(code=result_code, uid=req.uid)
    
    friends_list = crud_user_friends.friends_list(db, req.uid)
    reverse_friend_list = crud_user_friends.friend_reverse_list(db, req.uid)
    
    now_date_key = int(datetime.now().strftime('%Y%m%d'))
    
    if friends_list:
        for reverse in reverse_friend_list:
            value = [ friend for friend in friends_list if friend['uid'] == reverse.uid]
            if value:
                if (reverse.gift_send > 1) and (reverse.date_key == now_date_key):
                    value['sended'] = True
                else:
                    value['sended'] = False
                    
    response = {
        "friends" : friends_list if friends_list and len(friends_list) > 0 else None
    }
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=response, uid=req.uid)

