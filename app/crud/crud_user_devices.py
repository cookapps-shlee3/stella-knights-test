# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models.user import UserDevices, UserDevicesBackup


def get(db:Session, device_id:str):
    return db.query(UserDevices).filter(UserDevices.device_id == device_id).first()
    

def create(db:Session, uid:int, device_id:str, platform:str):
    data = UserDevices()
    data.uid = uid
    data.device_id = device_id
    data.platform = platform
    data.updated = datetime.now()
    data.created = datetime.now()
    
    db.add(data)
    db.commit()
    db.refresh(data)
    
    return data.id


def update_uid(db:Session, device_id:str, uid:int):
    db.query(UserDevices).filter(UserDevices.device_id == device_id).update({UserDevices.uid : uid})
    db.commit()
    
    
    
def get_by_uids(db:Session, uids:list[int]):
    return db.query(UserDevices).filter(UserDevices.uid.in_(uids)).all()



def insert_all(db:Session, device_infos:list[UserDevices]):
    if device_infos:
        for device in device_infos:
            backup = UserDevicesBackup()
            backup.id = device.id
            backup.device_id = device.device_id
            backup.platform = device.platform
            backup.updated = device.updated
            backup.created = datetime.now()
            
            db.add(backup)
            db.commit()    
            
def remove_uids(db:Session, uids:list[int]):
    db.query(UserDevices).filter(UserDevices.uid.in_(uids)).delete()
    db.commit()
