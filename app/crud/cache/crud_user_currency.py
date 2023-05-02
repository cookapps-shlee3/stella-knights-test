# -*- coding: utf-8 -*-
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.db.models.cache.currency import *
from app.config.settings import settings


def get_user_currency_all(db:Session, uid:int):
    user_currency = globals()[f"UserCurrency_{uid % 10}"]
    user_data_list = db.query(user_currency).filter(user_currency.uid == uid).all()
    
    return user_data_list


def get_user_currency(db:Session, uid:int, type:str):
    user_currency = globals()[f"UserCurrency_{uid % 10}"]
    user_data = db.query(user_currency).filter(user_currency.uid == uid, user_currency.type == type).one_or_none()
    
    return user_data

def get(db:Session, uid:int, type:str):
    return get_user_currency(db, uid, type)

def gets(db:Session, uid:int, types:list):
    user_currency = globals()[f"UserCurrency_{uid % 10}"]
    return db.query(user_currency).filter(user_currency.type.in_(types)).all()


def update_user_currency(db:Session, uid:int, type:str, total_amount:int, amount:int=0, is_get:bool=False, updated:datetime=None):
    user_currency = globals()[f"UserCurrency_{uid % 10}"]
    if is_get:
        user_data = db.query(user_currency).filter(user_currency.uid == uid, user_currency.type == type).update({'amount':total_amount, 'daily_get':user_currency.daily_get+amount, 'total_get':user_currency.total_get+amount})
    else:
        user_data = db.query(user_currency).filter(user_currency.uid == uid, user_currency.type == type).update({'amount':total_amount, 'daily_use':user_currency.daily_use+amount, 'total_use':user_currency.total_use+amount})
    
    db.commit()
    
    return user_data  



def update_get_user_currency(db:Session, uid:int, type:str, amount:int=0):
    user_currency = globals()[f"UserCurrency_{uid % 10}"]
    user_data = db.query(user_currency).filter(user_currency.uid == uid, user_currency.type == type).update({'amount':user_currency.amount + amount, 'daily_get':user_currency.daily_get+amount, 'total_get':user_currency.total_get+amount})

    db.commit()
    
    return user_data




def update_use_user_currency(db:Session, uid:int, type:str, amount:int=0):
    user_currency = globals()[f"UserCurrency_{uid % 10}"]
    now = datetime.now()
    user_data = db.query(user_currency).filter(user_currency.uid == uid, user_currency.type == type).update({'amount':user_currency.amount-amount, 'daily_use':user_currency.daily_use+amount, 'total_use':user_currency.total_use+amount, 'updated':now})
        
    db.commit()
    
    return user_data



def reset_user_daily_currency(db:Session, uid:int):
    user_currency = globals()[f"UserCurrency_{uid % 10}"]
    user_data = db.query(user_currency).filter(user_currency.uid == uid).update({'daily_get':0, 'daily_use':0,})
    db.commit()
    
    return user_data




def get_user_currency_orm(uid:int):
    user_currency = globals()[f"UserCurrency_{uid % 10}"]
    insert_data = user_currency()
        
    return insert_data

def save(db:Session, uid:int, type:str, amount:int):
    insert_data = get_user_currency(db, uid, type)
    
    if insert_data:
        update_user_currency(db, uid, type, amount)
        insert_data.amount = amount
    else:
        insert_data = get_user_currency_orm(uid)
        insert_data.uid = uid
        insert_data.type = type
        insert_data.amount = amount
        insert_data.updated = datetime.now()
        db.add(insert_data)

    db.commit()
    return insert_data
    
    
def insert(db:Session, uid:int, type:str, amount:int):
    insert_data = get_user_currency_orm(uid)
    insert_data.uid = uid
    insert_data.type = type
    insert_data.amount = amount
    insert_data.updated = datetime.now()
    insert_data.created = datetime.now()
    db.add(insert_data)

    db.commit()
    return insert_data
       

def get_user_currency_data(db:Session, uid:int):
    user_currencys = get_user_currency_all(db, uid)
    result = []
    for user_currency in user_currencys:
        result.append(user_currency.getdict())
    data = {'currency':result}
    return data


def set_user_currency(db:Session, uid:int, type:str, amount:int=0):
    user_currency = globals()[f"UserCurrency_{uid % 10}"]
    user_data = db.query(user_currency).filter(user_currency.uid == uid, user_currency.type == type).update({'amount':amount})
        
    db.commit()
    
    return user_data