# -*- coding: utf-8 -*-
import os
from sqlalchemy.orm import Session
from app.params.ResParam import get_response, ResponseCode
from app.params.CurrencyReqParam import *
from app.util.util import get
from app.crud.cache import crud_user_currency
from app.classes.CurrencyManager import CurrencyManager



## Set Timezone
os.environ['TZ'] = 'UTC'


def __update_currency(db:Session, uid:int, type:str, amount:int):
    crud_user_currency.set_user_currency(db, uid, type, amount)
    # 추가로 로그를 남길수 있는 방법을 생각해 보자.

#########################################################################################################################################################


async def currency_update(req:CurrencyUpdateReqParam, db:Session):
    if req.data:
        for item in req.data:
            type = get(item, 'type', None)
            value = get(item, 'value', None)
            if type in CurrencyManager.get_currency_type() and (value != None):
                __update_currency(db, req.uid, type, value)

    
    data = crud_user_currency.get_user_currency_data(db, req.uid)
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)


#########################################################################################################################################################


async def currency_get(req:CurrencyUpdateReqParam, db:Session):
    currencyManager = CurrencyManager()
    if req.data:
        for item in req.data:
            type = get(item, 'type', None)
            value = get(item, 'value', None)
            if type in CurrencyManager.get_currency_type() and (value != None):
                currencyManager.__get_currency(db, req.uid, type, value)

    data = crud_user_currency.get_user_currency_data(db, req.uid)
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)


#########################################################################################################################################################


async def currency_use(req:CurrencyUpdateReqParam, db:Session):
    
    currencyManager = CurrencyManager()
    use_list = []
    if req.data:
        for item in req.data:
            type = get(item, 'type', None)
            value = get(item, 'value', None)
            if type in CurrencyManager.get_currency_type() and (value != None):
                use_list.append({'type':type, 'value':value})
        
        if use_list:
            result = currencyManager.use_currencys(db, req.uid, use_list)
            if result == None:
                return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, uid=req.uid)
   
    data = crud_user_currency.get_user_currency_data(db, req.uid)
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)


#########################################################################################################################################################


