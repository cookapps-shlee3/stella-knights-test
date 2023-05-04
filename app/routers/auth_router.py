# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.db.connection import get_db
from app.params.ReqParam import AuthReqParam, BaseReqParam
from app.params.ReqParam import ServerReqParam
from app.apis import auth_apis
from app.auth.auth_bearer import JWTBearer
from app.config.settings import Constant


auth_router = APIRouter(prefix='/auth')

@auth_router.post("/login/v2")
async def login(req:AuthReqParam, db:Session = Depends(get_db)):
    """
    1. Description
    - 로그인
    
    2. Request Parameter
    ```
    {
        "p": "android",
        "d": "111333333",
        "h": "",
        "v": 1003,
        "version": 0,
        "uid": 0,
        "pl111111atform": "",
        "device_id": "",
        "auth_id": "",
        "auth_pw": "",
        "auth_platm": "facebook"
    }
    ```
    """
    if not req.auth_id and not req.auth_platform:
        req.auth_platform = Constant.AUTH_PLATFORM_GUEST
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    if not req.device_id:
        req.device_id = 'unknown'
    
    if not req.platform or not req.device_id:
        return
    
    return await auth_apis.auth_index(req, db)

    

@auth_router.post("/check")
async def check(req:AuthReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return 
    
    req.device_id = req.device_id if req.device_id else req.d
    
    return await auth_apis.auth_check(req, db)


@auth_router.post("/server")
async def server(request:Request, req:ServerReqParam, db:Session = Depends(get_db), ):
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d

    return await auth_apis.auth_server(req, db, request)
