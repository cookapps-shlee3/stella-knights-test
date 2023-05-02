# -*- coding: utf-8 -*-
import time
from app.cache import CacheController
from fastapi import Request
from sqlalchemy.orm import Session
from app.params.ResParam import get_response, ResponseCode
from app.params.ReqParam import BaseReqParam, ConfigReqParam
from app.config.settings import Constant
from app.crud import crud_config, crud_user_devices, crud_user_banned, crud_log
from app.helper import server_helper, rankings_helper
from app.config.settings import Constant, settings
from app.redis.redisCache import redis
from app.util.util import get




def config(req:ConfigReqParam, db:Session):
    config_list = crud_config.get_all(db, filter)
    response = {
        'config' : config_list
    }
    return get_response(code=ResponseCode.RES_SUCCESS, data=response, uid=req.uid)


def currnet_time():
    now = int(time.time())
    response = {
        'serverTime' : now
    }
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=response)



async def version(req:BaseReqParam, db:Session, request:Request):
    
    status = Constant.CLIENT_STATUS_SKIP
    is_banned_expired = 0
    is_banned_msg = ''
    app_version = 99999999 if (not req.version) or (req.version == 0) else req.version
    
    version_value = await CacheController.get_mobile_version_info(db)
    version_info = version_value[req.platform]
       
    update_version = 0
    
    if app_version < get(version_info, 'min_version', 0):
        update_version = version_info['min_version']
        status = Constant.CLIENT_STATUS_FORCE_UPDATE
    elif app_version < get(version_info, 'max_version', 0):
        update_version = version_info['max_version']
        status = Constant.CLIENT_STATUS_SELECT_UPDATE
    
    
    total_app_verion = await CacheController.get_server_check_config_version(db)
    current_app_verion = total_app_verion[req.platform]
    if app_version <= int(current_app_verion):
        if await server_helper.is_not_white_uid(redis, req.platform, req.device_id):
            status = Constant.CLIENT_STATUS_SERVER_CHECK
    
    
    ## blacklist check
    if req.device_id:
        device_info = crud_user_devices.get(db, req.device_id)
        
        if device_info:
            banned_user = crud_user_banned.get(db, device_info.uid)
            
            if banned_user:
                if (not banned_user.expired) or (banned_user.expired == ''):
                    status = Constant.CLIENT_STATUS_ACCESS_DENIED
                    ## 기존 영구 벤
                    is_banned_expired = 0
                    is_banned_msg = 'abuse detection' if (not banned_user.msg) or banned_user.msg == '' else banned_user.msg
                else:
                    is_banned_expired = int(time.mktime(banned_user.expired.timetuple())) - int(time.time())
                    if is_banned_expired <= 0:
                        rankings_helper.banned_expired(db, redis, device_info.uid)
                        is_banned_expired = 0
                    else:
                        status = Constant.CLIENT_STATUS_ACCESS_DENIED
                        is_banned_msg = 'abuse detection' if (not banned_user.msg) or banned_user.msg == '' else banned_user.msg
    
    
        ## IP Banned
        ban_ips = ['82.79.152.154', '82.79.152.99', '82.79.152.119']
        user_ip = str(request.client.host)
        if (user_ip in ban_ips) or (user_ip.find('82.79.152') == 0):
            status = Constant.CLIENT_STATUS_ACCESS_DENIED
            
        hash_key = req.h
        hash_key = '' if not hash_key else hash_key
        if (req.platform == 'android') or (req.platform == 'onestore') and (hash_key):
            crud_log.set_hash_log(db, req.device_id, app_version , hash_key)
            is_hack = crud_log.is_hack(db, req.device_id, app_version, hash_key)
            
            if is_hack:
                status = Constant.CLIENT_STATUS_INVALID_HASH
    
    
    total_public_spec_version = await CacheController.get_publish_spec_version(db)
    spec_version = total_public_spec_version[req.platform]
    language_version = await CacheController.get_lang_version(db)
    language_system_version = await CacheController.get_lang_system_version(db)
    language_scenario_version = await CacheController.get_lang_scenario_version(db)
    total_limit_app_version = await CacheController.get_app_limit_spec_version(db)
    current_limit_app_version = total_limit_app_version[req.platform]
    total_limit_lang_version = await CacheController.get_app_limit_lang_version(db)
    current_limit_lang_version = total_limit_lang_version[req.platform]
    # total_limit_system_lang_version = await CacheController.get_app_limit_system_lang_version(db)
    # current_limit_system_lang_version = total_limit_system_lang_version[req.platform]
    # total_limit_scenario_lang_version = await CacheController.get_app_limit_scenario_lang_version(db)
    # current_limit_scenario_lang_version = total_limit_scenario_lang_version[req.platform]
    # total_spec_detail_version = await CacheController.get_app_spec_detail_version(db)
    
    
    if current_limit_app_version:
        limit_app_version =  current_limit_app_version['app_version']
        limit_spec_version = current_limit_app_version['spec_version']
        limit_lang_version = current_limit_lang_version['spec_version']
        # limit_system_lang_version = current_limit_system_lang_version['spec_version']
        # limit_scenario_lang_version = current_limit_scenario_lang_version['spec_version']
        
        if (limit_app_version > 0) and (limit_spec_version > 0):
            if req.version <= limit_app_version:
                spec_version = limit_spec_version
    
        if (limit_app_version > 0) and (limit_lang_version > 0):
            if req.version <= limit_app_version:
                language_version = limit_lang_version
                
        # if (limit_app_version > 0) and (limit_system_lang_version > 0):
        #     if req.version <= limit_app_version:
        #         language_system_version = limit_system_lang_version

                
        # if (limit_app_version > 0) and (limit_scenario_lang_version > 0):
        #     if req.version <= limit_app_version:
        #         language_scenario_version = limit_scenario_lang_version

    url = None
    lang = None
    cdn = None
    spec_ver = int(spec_version)
    lang_ver = int(language_version)
    
    if settings.USE_PRE_DEST:
        if req.v >= settings.PRE_DEST_VERSION:
            url = settings.PRE_DEST
            lang = settings.PRE_LANG_DEST
            cdn = settings.PRE_SPEC_DEST
            spec_ver = settings.PRE_SPEC_VER
            lang_ver = settings.PRE_LANG_VER
    
    response = {
        'status' : status,
        'app_version' : int(update_version),
        'spec_version' : spec_ver,
        'language_version' : lang_ver,
        # 'language_system_version' : int(language_system_version),
        # 'language_scenario_version' : int(language_scenario_version),
        # 'sped_detail_version' : total_spec_detail_version[req.platform],
        'isBannedMsg' : is_banned_msg,
        'isBannedExpired' : is_banned_expired,
        'url':url,
        'lang':lang,
        'cdn':cdn
    }
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=response, uid=req.uid)
        
        
    



