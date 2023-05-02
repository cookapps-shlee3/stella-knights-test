# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.db.connection import get_db
from app.params.ReqParam import BaseReqParam, FriendReqParam, FriendNickReqParam
from app.apis import friends_apis
from app.auth.auth_bearer import JWTBearer
from app.params.ResParam import ResponseCode, get_response


friends_router = APIRouter(prefix='/friends')


@friends_router.post("/list")
async def list(req:BaseReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    return friends_apis.friends_info(req, db)

    

@friends_router.post("/invite")
async def invite(req:FriendReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.target_uid:
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, uid=req.uid)
    
    if req.uid == req.target_uid:
        return get_response(code=ResponseCode.RES_INVALID_MY_INFO, uid=req.uid)
    
    return friends_apis.friends_request_invite(req, db)




@friends_router.post("/cancel")
async def cancel(req:FriendReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
            
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.target_uid:
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, uid=req.uid)

    return friends_apis.friends_cancel_invite(req, db)



@friends_router.post("/accept")
async def accept(req:FriendReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.target_uid:
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, uid=req.uid)
    
    return friends_apis.friends_accept_invite(req, db)





@friends_router.post("/refuse")
async def battle_info(req:FriendReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.target_uid:
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, uid=req.uid)

    return friends_apis.friends_refuse_invite(req, db)




@friends_router.post("/remove")
async def remove(req:FriendReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.target_uid:
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, uid=req.uid)
    
    return friends_apis.friends_remove(req, db)




@friends_router.post("/recommend")
async def recommand(req:BaseReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)

    return await friends_apis.friends_recommand(req, db)



@friends_router.post("/find")
async def find(req:FriendNickReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.nickname:
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, uid=req.uid)

    req.nickname = req.nickname.replace("'", "\\'")

    return await friends_apis.friends_nickname_find(req, db)



@friends_router.post("/gift")
async def gift(req:FriendReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.target_uid:
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, uid=req.uid)

    return friends_apis.friends_send_gift(req,db)



@friends_router.post("/gifts")
async def gifts(req:FriendReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid:
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, uid=req.uid)

    return friends_apis.friends_send_gifts(req, db)
