# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models.cache.cache_data import *

def get_pvp_round_info(db:Session):
    now = datetime.now()
    res = db.query(PvpRoundInfo).filter(PvpRoundInfo.end_date >= now).all()
    return res

def get_cache_data(db:Session, platform:str):
    res = db.query(CacheData).filter(CacheData.platform == platform).all()
    return res

def get_cache_data_keys(db:Session, platform:str):
    sql = "SELECT sheet_key FROM platform_cache_data where platform = '{}'"
    sql = sql.format(platform)
    a = db.execute(sql)
    result = a.fetchall()
    return result


def get_cache_data_all(db:Session, platform:str):
    sql = "SELECT * FROM platform_cache_data where platform = '{}'"
    sql = sql.format(platform)
    a = db.execute(sql)
    result = a.fetchall()
    return result