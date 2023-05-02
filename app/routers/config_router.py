# -*- coding: utf-8 -*-
from typing import Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.params.ReqParam import CouponReqParam, BaseReqParam, ConfigReqParam
from app.auth.auth_bearer import JWTBearer
from app.params.ResParam import ResponseCode, get_response
from app.apis import users_apis, config_apis



config_router = APIRouter()

@config_router.post("/coupon")
async def coupon(req:CouponReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.code:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)

    return await users_apis.users_coupon(req, db)




@config_router.post("/time")
async def current_time():
    return config_apis.currnet_time()




@config_router.post("/version")
async def version_check(req:BaseReqParam, request:Request, db:Session = Depends(get_db)):
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    req.version = req.version if req.version else req.v

    return await config_apis.version(req, db, request)




@config_router.post("/config")
async def config(req:ConfigReqParam, db:Session = Depends(get_db)):
    
    return config_apis.config(req, db)


