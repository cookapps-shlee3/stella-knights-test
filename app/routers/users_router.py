# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.db.connection import get_db
from app.params.ReqParam import BaseReqParam, DataSaveReqParam, NicknameSaveReqParam, BattleSaveReqParam, BattleInfosReqParam, ReviewReqParam
from app.apis import users_apis
from app.auth.auth_bearer import JWTBearer
from app.config.settings import Constant
from app.params.ResParam import ResponseCode, get_response


users_router = APIRouter(prefix='/users')


@users_router.post("/lobby")
async def login(req:BaseReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):

    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await users_apis.users_lobby(req, db)

    

@users_router.post("/data/save")
async def data_save(req:DataSaveReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    if not req.device_id:
        req.device_id = 'unknown'

    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or req.data_list == None:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    return await users_apis.users_data_save(req, db)




@users_router.post("/nickname/save")
async def nickname_save(req:NicknameSaveReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    req.nickname = req.nickname.replace("'", "\\'")
        
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.nickname:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)

    return await users_apis.users_nickname_save(req, db)



@users_router.post("/battle/save")
async def battle_save(req:BattleSaveReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid and not req.data:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    return await users_apis.users_battle_save(req, db)





@users_router.post("/battle/info")
async def battle_info(req:BaseReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    return users_apis.users_battle_info(req, db)




@users_router.post("/battle/infos")
async def battle_infos(req:BattleInfosReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uids:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    

    return users_apis.users_battle_infos(req, db)




@users_router.post("/refresh")
async def refresh(req:BaseReqParam, request:Request, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d

    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)

    return await users_apis.user_refresh(req, db, request)




@users_router.post("/delete")
async def delete_user(req:BaseReqParam, request:Request, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d

    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)

    return await users_apis.user_delete(req, db, request)



@users_router.post("/review")
async def user_review(req:ReviewReqParam,  request:Request, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)

    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d

    return await users_apis.user_review(req, db, request)



