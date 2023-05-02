# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.params.ReqParam import BaseReqParam
from app.params.CurrencyReqParam import *
from app.apis import shop_apis
from app.auth.auth_bearer import JWTBearer
from app.config.settings import Constant
from app.params.ResParam import ResponseCode, get_response


shop_router = APIRouter(prefix='/shop')




# 상점 갱신
@shop_router.post("/homeshop/refresh")
async def homeshop_refresh(req:CurrencyHomeShopRefreshReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await shop_apis.shop_refresh_homeshop(req, db)



# 상점 물품 구매
@shop_router.post("/homeshop/buy")
async def homeshop_buy(req:CurrencyHomeShopBuyReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await shop_apis.shop_buy_homeshop(req, db)




# 상점 갱신
@shop_router.post("/pvpshop/refresh")
async def pvpshop_refresh(req:CurrencyPvpShopRefreshReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await shop_apis.shop_refresh_pvpshop(req, db)



# 상점 물품 구매
@shop_router.post("/pvpshop/buy")
async def pvpshop_buy(req:CurrencyPvpShopBuyReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await shop_apis.shop_buy_pvpshop(req, db)




@shop_router.post("/expedition/buy")
async def game_expedition_buy(req:ExpiditionShopBuyReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await shop_apis.shop_buy_expedition(req, db)



@shop_router.post("/expedition/refresh")
async def game_expedition_refresh(req:ExpiditionShopRefreshReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await shop_apis.shop_refresh_expedition(req, db)
