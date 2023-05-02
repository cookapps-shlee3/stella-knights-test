# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.db.connection import get_db
from app.params.ReqParam import PostListReqParam, PostRewardReqParam, PostRewardsReqParam
from app.apis import postbox_apis
from app.auth.auth_bearer import JWTBearer
from app.params.ResParam import ResponseCode, get_response


postbox_router = APIRouter(prefix='/postbox')


@postbox_router.post("/list")
async def list(req:PostListReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await postbox_apis.postbox_list(req, db)

    

@postbox_router.post("/reward")
async def reward(req:PostRewardReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):

    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
        
    if not req.post_id:
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, msg='Invalid Post ID', uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await postbox_apis.postbox_reward(req, db)




@postbox_router.post("/rewards")
async def rewards(req:PostRewardsReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.post_ids:
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, msg='Invalid Post ID', uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d

    return await postbox_apis.postbox_rewards(req, db)
