# -*- coding: utf-8 -*-
from loguru import logger
from fastapi import Request
from sqlalchemy.orm import Session
from app.params.ReqParam import AuthReqParam
from app.params.ReqParam import ServerReqParam
from app.crud import crud_user_members, crud_user_devices, crud_user_platforms, crud_user_banned, crud_user_server, crud_retention, crud_log
from app.config.settings import Constant, settings
from app.params.ResParam import get_response, ResponseCode
from app.auth import auth_handler
from app.rabbit_mq import rabbit_api



async def auth_index(req:AuthReqParam, db:Session):
    is_new = False
    uid = req.uid
    nickname = ''
    user_data = None
    
    user_device_info = crud_user_devices.get(db, req.device_id)
    
    if Constant.AUTH_PLATFORM_FACEBOOK == req.auth_platform or Constant.AUTH_PLATFORM_APPLE == req.auth_platform or Constant.AUTH_PLATFORM_GAMECENTER == req.auth_platform or Constant.AUTH_PLATFORM_GOOGLE == req.auth_platform:
        if not req.auth_id:
            return get_response(code=ResponseCode.RES_AUTH_ID_IS_NULL, uid=req.uid)
        
        user_platform_info = crud_user_platforms.get(db, req.auth_id, req.auth_platform)
        
        if user_platform_info:
            uid = user_platform_info.uid
            if user_device_info:
                if user_device_info.uid != uid:
                    crud_user_devices.update_uid(db, req.device_id, uid)
            else:
                crud_user_devices.create(db, uid, req.device_id, req.platform)
        else:
            if user_device_info:
                mappint_uid = user_device_info.uid
                tmp_user_platform_info = crud_user_platforms.get_by_uid(db, mappint_uid)
                
                if tmp_user_platform_info and (req.auth_id != tmp_user_platform_info.auth_id) and (req.auth_platform == tmp_user_platform_info.auth_platform):
                    user_data = crud_user_members.create(db, req.device_id)
                    uid = user_data.uid
                    nickname = user_data.nickname
                    crud_user_devices.update_uid(db, req.device_id, uid)
                    is_new = True
                else:
                    uid = user_device_info.uid
            else:
                user_data= crud_user_members.create(db, req.device_id)
                uid = user_data.uid
                nickname = user_data.nickname
                crud_user_devices.create(db, uid, req.device_id, req.platform)
                is_new = True
                
            crud_user_platforms.create(db, req.auth_id, req.auth_platform, uid)
    elif Constant.AUTH_PLATFORM_GUEST == req.auth_platform:
        if not user_device_info:
            user_data = crud_user_members.create(db, req.device_id)
            uid = user_data.uid
            nickname = user_data.nickname
            crud_user_devices.create(db, uid, req.device_id, req.platform)
            is_new = True
        else:
            uid = user_device_info.uid    
                
    elif Constant.AUTH_PLATFORM_PG == req.auth_platform:
        auth_pw = req.auth_pw
        if not req.auth_id or not req.auth_pw:
            return
        ## TODO : KIMKJ  user_account 사용 여부에 따라서 추가 구현 가능성 고려
        pass
    
    
    user_member_info = await crud_user_members.get(db, uid, is_first=True)
    
    if not user_member_info.social_id:
        await crud_user_members.update_social_id(db, uid, req.auth_id)
    
    is_banned = False
    banned_user = crud_user_banned.get(db, uid)
    
    if banned_user:
        is_banned = True
    
    crud_log.set_access_log(db, 'login', uid, req.platform, req.device_id, req.auth_id, req.auth_platform, req.version, is_banned)
        
    response = {
        'uid' : uid,
        'isNew' : is_new,
        'isNickname' : user_member_info.is_nickname if user_member_info else 0,
        'isBanned' : is_banned
    }
    
    if is_new:
        crud_user_server.create(db, uid, uid, 0, 1)
        if user_data:
            await rabbit_api.send_new_user(uid, nickname, req.device_id, req.auth_id, req.platform, settings.LOCATION)
        
    server_infos = crud_user_server.get_all(db, uid)
    uid_info = []
    if server_infos and len(server_infos) > 0 :
        for server_info in server_infos:
            if server_info.server == 0:
                uid_info.append({
                    'server':server_info.server,
                    'uid':server_info.server_uid,
                    'is_base':1,
                    'profile_info':None
                })
                pass
            else:
                uid_info.append({
                    'server':server_info.server,
                    'uid':server_info.server_uid,
                    'is_base':server_info.is_base,
                    'profile_info':crud_user_members.get_profile_data(db, server_info.server_uid)
                })
        response ['uid_info'] = uid_info
        
    else:
        crud_user_server.create(db, uid, uid, user_member_info.server, 1)
        uid_info.append({
            'server':user_member_info.server,
            'uid':uid,
            'is_base':1,
            'profile_info':crud_user_members.get_profile_data(db, uid)
        })
        response ['uid_info'] = uid_info

    return get_response(code=ResponseCode.RES_SUCCESS, data=response, uid=req.uid)


async def auth_check(req:AuthReqParam, db:Session):
    user_member_info = await crud_user_members.get(db, req.uid)
    
    if user_member_info.login_device_id:
        if user_member_info.login_device_id != req.device_id:
            return
    
    is_banned = False
    banned_user = crud_user_banned.get(req.uid)
    
    if banned_user:
        is_banned = True
        
    response = {
        'isBanned' : is_banned
    }
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=response, uid=req.uid)


async def auth_server(req:ServerReqParam, db:Session, request:Request):
    user_member_info = await crud_user_members.get(db, req.uid)
    
    
    # origin_ip, forward_ip = None
    
    # x = 'x-forwarded-for'.encode('utf-8')
    # for header in request.headers.raw:
    #     if header[0] == x:
    #         origin_ip, forward_ip = header[1].decode('utf-8').split(', ')
    
    is_new = False
    is_new_server = False
    base_uid = 0
    
    if user_member_info.server == 0:
        ## 신규 유저
        ## 서버 선택이 안된 신규 유저 해당 서버로 정보 갱신.
        crud_user_server.update_server(db, req.uid, req.server, 1)
        await crud_user_members.update_server(db, req.uid, req.server)
        await rabbit_api.select_user_server(req.uid, req.server)
        base_uid = req.uid
        is_new = 1
        
    
    server_info = crud_user_server.get_server_uid(db, req.uid, req.server)
    base_uid = crud_user_server.base_uid(db, req.uid).uid
    base_member_info = await crud_user_members.get(db, base_uid)
    
    if server_info:
        base_uid = server_info.uid
        uid = server_info.server_uid
    else:
        uid = crud_user_members.create_new_server(db, req.d, req.server, base_member_info.social_id)
        crud_user_server.create(db, base_uid, uid, req.server)
        await rabbit_api.select_user_server(uid, req.server)
        user_member_info = await crud_user_members.get(db, uid)
        is_new_server = False
        
    if user_member_info.login_device_id != req.d:
        await crud_user_members.update_login_device_id(db, uid, req.d)
        
    if not user_member_info.social_id:
        await crud_user_members.update_social_id(db, uid, base_member_info.social_id)
        
    response = {
        'uid' : uid,
        'server' : req.server,
        'isNew' : is_new,
        'isNewServer' : is_new_server,
        'isNickname' : user_member_info.is_nickname
    }
    
    response['token'] = auth_handler.get({'uid' : uid})
    
    try:
        crud_retention.set_uv(db, base_uid, req.p, req.d, user_member_info.social_id, request.headers.get('origin_ip') if request.headers.get('origin_ip') else request.client.host)
    except Exception as e:
        logger.warning(e)
    
    
    if is_new:
        crud_retention.set_tag(db, "mobile_"+req.p, 'nru', base_uid)
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=response, uid=req.uid)



