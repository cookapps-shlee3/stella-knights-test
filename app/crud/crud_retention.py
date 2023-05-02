# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models.retention import RetentionUV, RetentionTag


def set_uv(db:Session, uid:int, device:str, device_id:str, social_id:str, ip:str):
    date_key = int(datetime.now().strftime('%Y%m%d'))
    data = RetentionUV()
    data.uid = uid
    data.social_id = social_id
    data.ip = ip
    data.hour = datetime.now().hour
    data.platform = device
    data.device_id = device_id
    data.rdate_key = date_key
    data.rdate = datetime.now()
    
    exists = db.query(RetentionUV).filter(RetentionUV.uid == uid, RetentionUV.rdate_key == date_key).first()
    if not exists:
        db.add(data)
        db.commit()
        return True
    
    return True


def set_tag(db:Session, alias:str, tag:str, uid:int):
    data = RetentionTag()
    data.alias = alias
    data.retention_tag = tag
    data.uid = uid
    data.rdate_key = int(datetime.now().strftime('%Y%m%d'))
    data.rdate = datetime.now()
    data.hour = datetime.now().hour
    
    exists = db.query(RetentionTag).filter(RetentionTag.uid == uid, RetentionTag.retention_tag == tag, RetentionTag.alias == alias).first()
    
    if not exists:
        db.add(data)
        db.commit()
        db.refresh(data)
        return True
    
    return True