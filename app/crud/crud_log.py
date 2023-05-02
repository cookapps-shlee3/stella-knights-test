# -*- coding: utf-8 -*-
import time
import json
from datetime import datetime

from sqlalchemy import insert
from sqlalchemy.orm import Session
from app.params.ReqParam import BattleData
from app.db.models.log import LogBattle
from app.db.models.log import LogLogin
from app.db.models.log import LogHash
from app.db.models.log import LogUserAttr
from app.db.models.log import LogUserAttrHistory
from app.db.models.user import UserBannedDevice
from app.db.models.user import UserMembers
from app.db.models.hash_manager import HashManager
from app.config.settings import Constant
from app.crud.crud_user_data import get


def set_battle_log(db:Session, uid:int, log:BattleData, version:int):
    if not uid or not log : return
    
    mode = log.mode
    rank = log.oRank
    trophy = log.mTrophy
    crown = log.crown
    o_nickname = log.oNick
    m_deck = log.oDeck
    o_deck = log.oDeck
    version = version if version else ''
    status = log.status
    is_ai = 1 if log.isAI == True else 0
    is_friendly = 1 if log.isFriendly == True else 0
    win = 1 if log.win == True else 0
    
    data = LogBattle()
    data.log_date = int(datetime.now().strftime('%Y%m%d'))
    data.uid = uid
    data.version = version
    data.status = status
    data.mode = mode
    data.rank = rank
    data.trophy = trophy
    data.crown = crown
    data.o_nickname = o_nickname
    data.m_deck = m_deck
    data.o_deck = o_deck
    data.is_ai = is_ai
    data.is_friendly = is_friendly
    data.win = win
    data.created = datetime.now()
    
    
    db.add(data)
    db.commit()
    db.refresh(data)
    
def set_access_log(db:Session, path, uid:int, platform:str, device_id:str, auth_id:str, auth_platform:str, app_version:str, status:int = 0, hash:str=''):
    if not auth_id : auth_id =''
    if not auth_platform : auth_platform = ''
    if not app_version : app_version = ''
    
    if auth_platform == Constant.AUTH_PLATFORM_GUEST:
        auth_id = ''
        
    data = LogLogin()
    data.log_date = int(datetime.now().strftime('%Y%m%d'))
    
    data.uid = uid
    data.path = path
    data.platform = platform
    data.device_id = device_id
    data.auth_id = auth_id
    data.auth_platform = auth_platform
    data.version = app_version
    data.status = status
    data.hash_key = hash
    data.created = datetime.now()
    
    db.add(data)
    db.commit()
    db.refresh(data)


def set_hash_log(db:Session, device_id:str, app_version:int, hash_key:str):
    if not app_version or not hash_key: return
    
    result = db.query(LogHash).filter(LogHash.device_id == device_id, LogHash.hash_key == hash_key, LogHash.version == app_version).one_or_none()
    
    if not result:
        data = LogHash()
        data.version = app_version
        data.hash_key = hash_key
        data.device_id = device_id
        data.created = datetime.now()
        
        db.add(data)
        db.commit()
    #    db.refresh(data)
    
def is_hack(db:Session, device_id:str, app_version, hash_key:str):
    if not app_version or not hash_key or not device_id:return False
    
    banned_user_info = db.query(UserBannedDevice).filter(UserBannedDevice.device_id == device_id).first()
    if banned_user_info:
        return True
    
    result = db.query(HashManager).filter(HashManager.version == app_version).all()
    white_list = []
    for item in result:
        white_list.append(item.hask_key)
        
    if not white_list: return False
    
    if hash_key in white_list:
        return False
    
    data = UserBannedDevice()
    data.device_id = device_id
    data.tag = app_version+':'+hash_key
    data.created = datetime.now()
    
    db.add(data)
    db.commit()
    # db.refresh(data)
    
    return True


def get_user_data_log(db:Session, uid:int):
    return db.query(LogUserAttr).filter(LogUserAttr.uid == uid).first()



def set_user_data_log(db:Session, uid:int, prev_user_data:LogUserAttr, new_user_data, user_member_info:UserMembers):
    level = 0 if 'level' not in new_user_data or not new_user_data['level'] else new_user_data['level']
    coin = 0 if 'coin' not in new_user_data or not new_user_data['coin'] else new_user_data['coin']
    jewel = 0 if 'jewel' not in new_user_data or not new_user_data['jewel'] else new_user_data['jewel']
    stone = 0 if 'stone' not in new_user_data or not new_user_data['stone'] else new_user_data['stone']
    acc_get_jewel = 0 if 'accGetJewel' not in new_user_data or not new_user_data['accGetJewel'] else new_user_data['accGetJewel']
    acc_use_jewel = 0 if 'accUseJewel' not in new_user_data or not new_user_data['accUseJewel'] else new_user_data['accUseJewel']
    
    if not prev_user_data:
        data = LogUserAttr()
        data.uid = uid
        data.level = level
        data.coin = coin
        data.jewel = jewel
        data.stone = stone
        data.acc_get_jewel = acc_get_jewel
        data.acc_use_jewel = acc_use_jewel
        db.add(data)
        db.commit()
        db.refresh(data)
    else:
        p_level = prev_user_data.level
        p_coin = prev_user_data.coin
        p_jewel = prev_user_data.jewel
        p_stone = prev_user_data.stone
        p_acc_get_jewel = prev_user_data.acc_get_jewel
        p_acc_use_jewel = prev_user_data.acc_use_jewel
        
        is_insert_history = False
        update_params = {}
        if p_level != level:
            update_params['level'] = level
            is_insert_history = True
        
        if p_coin != coin:
            update_params['coin'] = coin
            is_insert_history = True
        
        if p_jewel != jewel:
            update_params['jewel'] = jewel
            is_insert_history = True
            
        if p_stone != stone:
            update_params['stone'] = stone
            is_insert_history = True
            
        if p_acc_get_jewel != acc_get_jewel: update_params['acc_get_jewel'] = acc_get_jewel
        if p_acc_use_jewel != acc_use_jewel: update_params['acc_use_jewel'] = acc_use_jewel
        
        if not update_params:
            db.query(LogUserAttr).filter(LogUserAttr.uid == uid).update(update_params)
            db.commit()
            
            if jewel < 50000 and (jewel - p_jewel) < 30000 and (stone - p_stone) < 100000 :
                is_insert_history = False
                
            
            ## 가입 6시간 이내 주얼 누적 5만 이상
            timegap = (int(time.time()) - int(user_member_info.created.timestamp()))
            if ( timegap < (3600 * 6) and int(acc_get_jewel) >= 50000) or (timegap < (3600 * 48) and int(acc_use_jewel) >= 100000) or (timegap < (3600 * 6) and int(stone) >= 100000):
                is_insert_history = True
                
            ## 데이터 조작 의심
            if (jewel < -5000) or (coin < -1000000) or (stone < -1000) :
                is_insert_history = True
            
            ## 결재자 체크
            if is_insert_history:
                result = get(db, uid, 'purchases')
                if not result:
                    if not result.data:
                        purchase_data = json.loads(result.data)
                        if not purchase_data:
                            is_insert_history = False

            white_list = []
            if is_insert_history and (uid in white_list):
                if db.query(LogUserAttrHistory).filter(LogUserAttrHistory.uid == uid).count() == 0:
                    data = LogUserAttrHistory()
                    data.log_date = int(datetime.now('%Y%m%d'))
                    data.log_hour = int(datetime.now('%H'))
                    data.uid = uid
                    data.level = level
                    data.coin = coin
                    data.jewel = jewel
                    data.stone = stone
                    data.at_level = p_level
                    data.at_coin = p_coin
                    data.at_jewel = p_jewel
                    data.at_stone = p_stone
                    data.acc_get_jewel = acc_get_jewel
                    data.created = datetime.now()
                    db.add(data)
                    db.commit()
