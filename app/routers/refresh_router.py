# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.params.ReqParam import BaseReqParam
from app.params.CurrencyReqParam import *
from app.apis import refresh_apis
from app.auth.auth_bearer import JWTBearer
from app.config.settings import Constant
from app.params.ResParam import ResponseCode, get_response


refresh_router = APIRouter(prefix='/refresh')



# Bread Refresh
@refresh_router.post("/energy")
async def refresh_energy(req:CurrencyEnergyRefreshReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await refresh_apis.refresh_energy(req, db)


# PVP Ticket Refresh
@refresh_router.post("/pticket")
async def currency_refresh_pticket(req:CurrencyPVPTicketRefreshReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await refresh_apis.refresh_pticket(req, db)



@refresh_router.post("/daily/buy")
async def refresh_buy_daily(req:CurrencyFreeReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await refresh_apis.refresh_daily_buy(req, db)


@refresh_router.post("/weekly/buy")
async def refresh_buy_weekly(req:CurrencyFreeReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await refresh_apis.refresh_weekly_buy(req, db)


@refresh_router.post("/monthly/buy")
async def refresh_buy_daily(req:CurrencyFreeReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await refresh_apis.refresh_monthly_buy(req, db)



@refresh_router.post("/special/buy")
async def refresh_buy_special(req:CurrencyFreeReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await refresh_apis.refresh_special_buy(req, db)




@refresh_router.post("/daily/reset")
async def currency_daily_reset(req:BaseReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await refresh_apis.refresh_reset_daily(req, db)



@refresh_router.post("/session")
async def refresh_session(req:CurrencyEnergyRefreshReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await refresh_apis.refresh_energy(req, db)