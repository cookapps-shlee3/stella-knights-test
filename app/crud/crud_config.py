# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from app.db.models.config import Config


def get(db:Session, key:str, type:str='server'):
    res = db.query(Config).filter(Config.key == key, Config.type == type).first()
    return res.value if res else None


def get_by_filter(db:Session, key:str, filter:str = None, type:str='server'):
    if filter:
        res =  db.query(Config).filter(Config.key == key, Config.filter == filter, Config.type == type).first()
    else:
        res =  db.query(Config).filter(Config.key == key, Config.type == type).first()
    return res.value if res else None


def get_all(db:Session, filter:str = None, type:str='client'):
    if filter:
        res = db.query(Config).filter(Config.type == type).all()
    else:
        res = db.query(Config).filter(Config.type == type, Config.filter == filter).all()
        
    return res
