# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from app.db.models.config import Config

def get_all(db:Session, filter:str = None, type:str='client'):
    if filter:
        res = db.query(Config).filter(Config.type == type).all()
    else:
        res = db.query(Config).filter(Config.type == type, Config.filter == filter).all()
        
    return res
