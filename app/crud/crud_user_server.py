# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models.user import UserServer, UserServerBackup



## 이 함수는 redis쪽으로 이관하도록 추후 수정 함.
def is_not_white_uid(db:Session, platform:str, device_id:str):
    pass


def get(db:Session, uid:int, server:int):
    return db.query(UserServer).filter(UserServer.uid == uid, UserServer.server == server).first()


def get_all(db:Session, uid:int):
    return db.query(UserServer).filter(UserServer.uid == uid).all()


def get_server_uid(db:Session, uid:int, server:int):
    return db.query(UserServer).filter(UserServer.server_uid == uid, UserServer.server == server).first()


def base_uid(db:Session, uid:int):
    return db.query(UserServer).filter(UserServer.server_uid == uid).first()


def create(db:Session, uid:int, new_uid:int, region:int, is_base:int=0):
    data = UserServer()
    data.uid = uid
    data.is_base = is_base
    data.server_uid = new_uid
    data.server = region
    data.created = datetime.now()
    
    db.add(data)
    db.commit()
    db.refresh(data)


def update_server(db:Session, uid:int, server:int, is_base:int=0):
    res = db.query(UserServer).filter(UserServer.server_uid == uid).update({'server':server, 'is_base':is_base})
    db.commit()
    return res


def insert_all(db:Session, server_infos:list[UserServer]):
    if server_infos:
        for server_info in server_infos:
            backup = UserServerBackup()
            backup.uid = server_info.uid
            backup.is_base = server_info.is_base
            backup.server = server_info.server
            backup.server_uid = server_info.server_uid
            backup.created = datetime.now()
            
            db.add(backup)
            db.commit()
        
        
def remove_uids(db:Session, uids:list[int]):
    db.query(UserServer).filter(UserServer.uid.in_(uids)).delete()
    db.commit()