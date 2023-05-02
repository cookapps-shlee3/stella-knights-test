# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models.user import UserPlatforms, UserPlatformsBackup


def get(db:Session, auth_id:str, auth_platform:str):
    return db.query(UserPlatforms).filter(UserPlatforms.auth_platform == auth_platform, UserPlatforms.auth_id == auth_id).first()


def get_by_uid(db:Session, uid:int):
    return db.query(UserPlatforms).filter(UserPlatforms.uid == uid).first()


def get_by_uids(db:Session, uids:list[int]):
    return db.query(UserPlatforms).filter(UserPlatforms.uid.in_(uids)).all()


def create(db:Session, auth_id:str, auth_platform:str, uid:int):
    data = UserPlatforms()
    data.auth_id = auth_id
    data.auth_platform = auth_platform
    data.uid = uid
    data.created = datetime.now()
    
    db.add(data)
    db.commit()
    

def insert_all(db:Session, platform_infos:list[UserPlatforms]):
    if platform_infos:
        for platform in platform_infos:
            backup = UserPlatformsBackup()
            backup.auth_platform = platform.auth_platform
            backup.auth_id = platform.auth_id
            backup.uid = platform.uid
            backup.created = datetime.now()
            
            db.add(backup)
            db.commit()    


def remove_uids(db:Session, uids:list[int]):
    db.query(UserPlatforms).filter(UserPlatforms.uid.in_(uids)).delete()
    db.commit()

    
## TODO : KIMKJ Account 항목은 추후 구현 함수 선언만 해 놓음.
def get_account(db:Session, auth_id:str):
    pass

def get_by_uid_account(db:Session, uid:int):
    pass

def create_account(db:Session, auth_id:str, auth_pw:str, uid:int):
    pass