# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.auth.auth_bearer import JWTBearer
from app.params.ResParam import ResponseCode, get_response
from app.guild.api import guild_apis
from app.params.ReqParam import *
from app.guild.params.ReqParam import *



guild_router = APIRouter(prefix='/guild')

@guild_router.post("/guildList")
async def list(req:BaseReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.code:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)

    return guild_apis.guild_list(req, db)



@guild_router.post("/guildInfo")
async def info(req:GuildInfo, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.code:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)

    return guild_apis.guild_info(req, db)



@guild_router.post("/createGuild")
async def create(req:GuildCreate, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.code:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)

    return guild_apis.guild_create(req, db)



@guild_router.post("/modifyGuild")
async def list(req:GuildModify, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.code:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)

    return guild_apis.guild_modify(req, db)



@guild_router.post("/searchGuild")
async def search(req:GuildSearch, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.code:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)

    return guild_apis.guild_search(req, db)



@guild_router.post("/joinGuild")
async def list(req:GuildJoin, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.code:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)

    return guild_apis.guild_join(req, db)



@guild_router.post("/leaveGuild")
async def leave(req:GuildLeave, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.code:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)

    return guild_apis.guild_leave(req, db)



@guild_router.post("/banGuildUser")
async def ban(req:GuildBan, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.code:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)

    return guild_apis.guild_user_ban(req, db)



@guild_router.post("/acceptJoinUser")
async def acceptJoin(req:GuildAcceptJoin, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.code:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)

    return guild_apis.guild_accept_join_user(req, db)



@guild_router.post("/rejectJoinUser")
async def reject_join(req:GuildRejectJoin, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.code:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)

    return guild_apis.guild_reject_join_user(req, db)



@guild_router.post("/setUserCoLeader")
async def set_coleader(req:GuildSetCoLeader, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.code:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)

    return guild_apis.guild_set_user_coleader(req, db)



@guild_router.post("/setUserNormal")
async def set_normal(req:GuildSetNormal, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.code:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)

    return guild_apis.guild_set_user_normal(req, db)



@guild_router.post("/verifyMessage")
async def verify_message(req:GuildVerifyMessage, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.code:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)

    return guild_apis.guild_verigy_message(req, db)



@guild_router.post("/receiveHelp")
async def receive_help(req:GuildReceiveHelp, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.uid or not req.code:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)

    return guild_apis.guild_receive_help(req, db)



