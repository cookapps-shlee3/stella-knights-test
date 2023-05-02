# -*- coding: utf-8 -*-
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.db.models.cache.currency_log import *
from app.config.settings import settings

def get_user_currency_orm(uid:int):
    user_currency = globals()[f"UserCurrencyLog_{uid % 10}"]
    insert_data = user_currency()
        
    return insert_data

def insert(db:Session, uid:int, type:str, amount:int, daily_get:int, daily_use:int, total_get:int, total_use:int):
    insert_data = get_user_currency_orm(uid)
    insert_data.uid = uid
    insert_data.type = type
    insert_data.amount = amount
    insert_data.daily_get = daily_get
    insert_data.daily_use = daily_use
    insert_data.total_get = total_get
    insert_data.total_use = total_use
    insert_data.date_key = datetime.now().strftime('%Y%m%d')
    insert_data.created = datetime.now()
    db.add(insert_data)

    db.commit()
    return insert_data
  