# -*- coding: utf-8 -*-
import json
import time
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session
from app.db.models.user import *
from app.db.models.dummy_data_battle import DummyDataBattle
from app.db.models.user import UserDataBattle, UserBanned
from app.db.models.log import LogBanned, LogUserData
from pymongo import MongoClient
from pymongo import ReturnDocument
from app.config.settings import settings
from sqlalchemy.dialects.mysql import insert

def get_user_key(uid:int, category:str) -> str:
    return str(uid)+'_'+category


def get_user_data_all(db:Session, uid:int):
    user_data = globals()[f"UserData_{uid % 10}"]
    user_data_list = db.query(user_data).filter(user_data.uid == uid).all()
        
    return user_data_list

def get_all(db:Session, uid:int):
    user_data_list = get_user_data_all(db, uid)
    
    ret = {}
    for data in user_data_list:
        if data.data:
            ret[data.category] = json.loads(data.data)
    
    return ret

def get_all_by_mongo(uid:int):
    with MongoClient(settings.MONGO_URL) as client:
        msg_collection = client[settings.MONGO_DATABASE][settings.MONGO_COLLECTION]
        mgs_list = msg_collection.find({'uid':uid})
    
        ret = {}
        for data in mgs_list:
            ret[data['category']] = data['data']

        return ret

def get_by_mongo(db:Session, uid:int, category:str):
    with MongoClient(settings.MONGO_URL) as client:
        msg_collection = client[settings.MONGO_DATABASE][settings.MONGO_COLLECTION]
        key = get_user_key(uid, category)
        mgs_list = msg_collection.find_one({'_id':key})
    
        ret = {}
        for data in mgs_list:
            ret[data['category']] = data['data']

        return ret



def save_by_mongo(uid:int, category:str, data:dict):
    with MongoClient(settings.MONGO_URL) as client:
        msg_collection = client[settings.MONGO_DATABASE][settings.MONGO_COLLECTION]
        key = get_user_key(uid, category)
        
        # result = msg_collection.find_one_and_replace( filter={'_id':key}, replacement={'uid':uid, 'category':category, 'data':data}, upsert=True)
        result = msg_collection.find_one_and_update( filter={'_id':key}, update={'$set' : {'uid':uid, 'category':category, 'data':data}}, upsert=True, return_document=ReturnDocument.AFTER)
    
        return result


def get_user_data(db:Session, uid:int, category:str):
    user_data = globals()[f"UserData_{uid % 10}"]
    user_data = db.query(user_data).filter(user_data.uid == uid, user_data.category == category).first()
        
    return user_data

def get(db:Session, uid:int, category:str):
    return get_user_data(db, uid, category)


def update_user_data(db:Session, uid:int, category:str, data:str):
    user_data = globals()[f"UserData_{uid % 10}"]
    user_data = db.query(user_data).filter(user_data.uid == uid, user_data.category == category).update({'data':data, 'ts':int(time.time()), 'updated':datetime.now()})
        
    return user_data

def get_user_data_orm(uid:int):
    user_data = globals()[f"UserData_{uid % 10}"]
    insert_data = user_data()
        
    return insert_data

def save(db:Session, uid:int, category:str, data:str):

    # insert_stmt = insert(f"user_data_{uid % 10}").values(uid=uid, category=category, data=data)
    # on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(data=insert_stmt.inserted.data,status='U')
    
    # print(on_duplicate_key_stmt)
    insert_data = get_user_data_orm(uid)
    insert_data.uid = uid
    insert_data.category = category
    insert_data.data = data
    
    try:
        # 해당 코드는 데이터에만 가능함.
        result = update_user_data(db, uid, category, data)
        if not result:
            db.rollback()
            insert_data.ts = int(time.time())
            insert_data.updated = datetime.now()
            db.add(insert_data)
            db.commit()
        else:
            db.commit()        
    except:
        db.rollback()
        logger.warning(f'{category} of {str(uid)} is exception happen')
    
    
    # result = get_user_data(db, uid, category)
    
    # if result:
    #     update_user_data(db, uid, category, data)
    # else:
    #     insert_data = get_user_data_orm(uid)
    #     insert_data.uid = uid
    #     insert_data.category = category
    #     insert_data.data = data
    #     db.add(insert_data)

    # db.commit()
        
    
    # sql = "INSERT INTO `user_data_{}` (`uid`, `category`, `data`) VALUES ({}, '{}', '{}') ON DUPLICATE KEY UPDATE data = VALUES(`data`)"
    # sql = sql.format((uid%10), uid, category, data)
    # db.connection()
    # db.execute(sql)
    # db.commit()


def get_battle_data(db:Session, uid:int):
    if uid < 101:
        return db.query(DummyDataBattle).filter(DummyDataBattle.uid == uid).one_or_none()
    else:
        return db.query(UserDataBattle).filter(UserDataBattle.uid == uid).one_or_none()
    

def get_battle_dummy_data(db:Session, uid:int):
    return db.query(DummyDataBattle).filter(DummyDataBattle.uid == uid).first()
    
    
def get_battle_dummy_datas(db:Session, uids:list):
    return db.query(DummyDataBattle).filter(DummyDataBattle.uid.in_(uids)).all()


def get_battle_dummy_data_all(db:Session):
    return db.query(DummyDataBattle).all()


def get_battle_datas(db:Session, uids:list):
    return db.query(UserDataBattle).filter(UserDataBattle.uid.in_(uids)).all()


def save_battle_data(db:Session, uid:int, point:int, data:str):
    result = db.query(UserDataBattle).filter(UserDataBattle.uid == uid).first()
    
    if result:
        db.query(UserDataBattle).filter(UserDataBattle.uid == uid).update({'battle_point':point, 'data':data})
    else:
        insert_data = UserDataBattle()
        insert_data.uid = uid
        insert_data.battle_point = point
        insert_data.data = data
        db.add(insert_data)
    db.commit()


def save_logs(db:Session, uid:int, after_length, before_length, category:str, data:str):
    result = db.query(LogUserData).filter(LogUserData.uid == uid, LogUserData.category == category).one_or_none()
    
    if result:
        db.query(LogUserData).filter(LogUserData.uid == uid, LogUserData.category == category).update({'after_length':after_length, 'before_length':before_length, 'data':data})
    else:
        insert_data = LogUserData()
        insert_data.uid = uid
        insert_data.category = category
        insert_data.data = data
        insert_data.before_length = before_length
        insert_data.after_length = after_length
        db.add(insert_data)
    db.commit()
    
    # sql = "INSERT INTO `log_user_data` (`uid`, `category`, `data`, `after_length`, `before_length`) VALUES ({}, '{}', '{}', {}, {}) ON DUPLICATE KEY UPDATE data = VALUES(`data`), after_length = VALUES(`after_length`), before_length = VALUES(`before_length`)"
    # sql = sql.format(uid, category, data, after_length, before_length)
    # sql = sql.replace("\\", "\\\\")
    # db.execute(sql)
    # db.commit()
    

def verify_user_data_save(db:Session, data:dict, category:str):
    status = 0
    if category == 'hero':
        if ((('atkLv' in data) and  int(data['atkLv']) >= 999999) or 
        (('hpLv' in data) and  int(data['hpLv']) >= 999999) or 
        (('healLv' in data) and  int(data['healLv']) >= 999999) or 
        (('criLv' in data) and  int(data['criLv']) >= 999999) or 
        (('defLv' in data) and  int(data['defLv']) >= 999999) or 
        (('atkLv2' in data) and  int(data['atkLv2']) >= 999999) or 
        (('hpLv2' in data) and  int(data['hpLv2']) >= 999999) or 
        (('healLv2' in data) and  int(data['healLv2']) >= 999999) or 
        (('criLv2' in data) and  int(data['criLv2']) >= 999999) or 
        (('defLv2' in data) and  int(data['defLv2']) >= 999999)) :
            status = 1
    elif category == 'user':
        check = int(data['bestStage']) * (int(data['rebirth']) + 1)
        if(int(data['coin']) < 0 or int(data['jewel']) < 0 or int(data['stone']) < 0 or (int(data['accStage']) - check > 10000)):
            status = 1
    
    return status


def check_banned_user(db:Session, uid:int):
    count = db.query(UserBanned).filter(UserBanned.uid == uid).count()
    
    return True if count > 0 else False


def banned_logs(db:Session, uid:int, tag:str, desc:str, data:str):
    data = LogBanned()
    data.uid = uid
    data.tag = tag
    data.desc = desc
    data.data = data
    
    db.add(data)
    db.commit()
    db.refresh(data)
    
