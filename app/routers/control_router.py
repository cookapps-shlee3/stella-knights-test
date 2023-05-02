# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.params.ReqParam import BaseReqParam
from app.params.CurrencyReqParam import *
from app.apis import control_apis
from app.auth.auth_bearer import JWTBearer
from app.config.settings import Constant
from app.params.ResParam import ResponseCode, get_response


control_router = APIRouter(prefix='/control')




# 사용자 레벨업
@control_router.post("/user/level")
async def level_user(req:CurrencyUserLevelReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await control_apis.control_user_level(req, db)




# 캐릭터 레벨업
@control_router.post("/character/level")
async def level_character(req:CurrencyCharacterLevelReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await control_apis.control_character_level(req, db)



# 캐릭터 레벨업
@control_router.post("/character/enhance")
async def level_character(req:CurrencyCharacterEnhanceReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await control_apis.control_character_enhance(req, db)




# 무기 레벨업
@control_router.post("/weapon/level")
async def level_weapon(req:CurrencyWeaponLevelReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await control_apis.control_weapon_level(req, db)




# 무기 판매
@control_router.post("/weapon/sell")
async def sell_weapon(req:CurrencyWeaponSellReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await control_apis.control_weapon_sell(req, db)




# 무기 다량 판매
@control_router.post("/weapon/list/sell")
async def sell_weapon_list(req:CurrencyWeaponListSellReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await control_apis.control_weapon_list_sell(req, db)

