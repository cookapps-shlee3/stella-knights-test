# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.params.ReqParam import BaseReqParam
from app.params.CurrencyReqParam import *
from app.apis import currency_apis
from app.auth.auth_bearer import JWTBearer
from app.config.settings import Constant
from app.params.ResParam import ResponseCode, get_response


currency_router = APIRouter(prefix='/currency')



@currency_router.post("/update")
async def currnecy_update(req:CurrencyUpdateReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await currency_apis.currency_update(req, db)




@currency_router.post("/get")
async def currnecy_get(req:CurrencyUpdateReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await currency_apis.currency_get(req, db)




@currency_router.post("/use")
async def currnecy_use(req:CurrencyUpdateReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await currency_apis.currency_use(req, db)

