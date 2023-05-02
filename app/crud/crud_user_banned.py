# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from app.db.models.user import UserBanned


def get(db:Session, uid:int):
    return db.query(UserBanned).filter(UserBanned.uid == uid).first()

def remove(db:Session, uid:int):
    return db.query(UserBanned).filter(UserBanned.uid == uid).delete()
    
    