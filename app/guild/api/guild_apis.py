# -*- coding: utf-8 -*-
from fastapi import Request
from sqlalchemy.orm import Session
from ..params.ResParam import get_response, ResponseCode, JoinStatus, GuildType, MessageType
from ..params.ReqParam import *
from ..crud import crud_guild
from ..config.config import config


def guild_list(req:BaseReqParam, db:Session):
    
    user_join_status = crud_guild.get_user_join_status(db, req.uid)
    guild_list = crud_guild.get_guild_list(db)
    
    for key in guild_list:
        key.join_status = user_join_status.status if user_join_status and (key.guild_id == user_join_status.guild_id) else JoinStatus.NONE
    
    return get_response(code=ResponseCode.SUCCESS, data=guild_list, uid=req.uid)


def guild_info(req:GuildInfo, db:Session):
    
    guild_members = crud_guild.get_guild_member_list(db, req.guild_id)
    
    return get_response(code=ResponseCode.SUCCESS, data=guild_members, uid=req.uid)


def guild_create(req:GuildCreate, db:Session):
 
    guild_member = crud_guild.get_member(db, req.uid)
    
    if guild_member and guild_member.guild_id > 0:
        return get_response(code=ResponseCode.UNAUTHORIZED_GUILD_ACTION, uid=req.uid)
    
    if crud_guild.count_any_guild_member(db, req.uid) > 0:
        return get_response(code=ResponseCode.ALREADY_JOINED_GUILD_USER, uid=req.uid)
    
    guild_info = crud_guild.create_guild(db, req.uid, req.name, req.logo, req.type, req.minimum_level, req.comment, req.default_score)
    
    return get_response(code=ResponseCode.SUCCESS, data=guild_info, uid=req.uid)



def guild_modify(req:GuildModify, db:Session):
    
    guild_leader_info = crud_guild.get_guild_member(db, req.guild_id, req.uid)
    
    if not guild_leader_info:
        return get_response(code=ResponseCode.NOT_GUILD_MEMBER, uid=req.uid)
    
    
    if guild_leader_info.user_level < config.GUILD_COLEADER_LEVEL:
        return get_response(code=ResponseCode.UNAUTHORIZED_GUILD_ACTION, uid=req.uid)
    
    crud_guild.set_modify_guild(db, req.guild_id, req.logo, req.type, req.minimum_level, req.comment)
    
    data = crud_guild.get_guild_info(db, req.guild_id)
    
    return get_response(code=ResponseCode.SUCCESS, data=data, uid=req.uid)



def guild_search(req:GuildSearch, db:Session):
    
    user_join_status = crud_guild.get_user_join_status(db, req.uid)
    
    guild_list = crud_guild.get_search_guild(db, req.search_name)
    
    for key in guild_list:
        key.join_status = user_join_status.status if user_join_status and (key.guild_id == user_join_status.guild_id) else JoinStatus.NONE
    
    return get_response(code=ResponseCode.SUCCESS, data=guild_list, uid=req.uid)




def guild_join(req:GuildJoin, db:Session):
    
    user_member = crud_guild.get(db, req.uid)
    
    guild_info = crud_guild.get_guild_info(db, req.guild_id)
    if not guild_info:
        return get_response(code=ResponseCode.NOT_EXIST_GUILD, uid=req.uid)
    
    count_guild_user = crud_guild.count_guild_user(db, req.guild_id)
    
    if count_guild_user >= config.DEFAULT_MAX_GUILD_USER_COUNT:
        return get_response(code=ResponseCode.MAX_GUILD_USER_COUNT, uid=req.uid)
    else:
        guild_member = crud_guild.get_member(db, req.uid)
        
        if guild_member:
            return get_response(code=ResponseCode.NOT_EXIST_USER, uid=req.uid)
        
        if guild_member.guild_id > 0:
            return get_response(code=ResponseCode.ALREADY_JOINED_GUILD_USER, uid=req.uid)
        
        guild_member_status = crud_guild.get_request_join_guild(db, req.guild_id, req.uid)
        
        if guild_member_status and (guild_member_status.status == JoinStatus.BAN):
            return get_response(code=ResponseCode.BAN_GUILD_USER, uid=req.uid)
        
        
        # 길드 타입에 따른 분기(개방형:1, 폐쇠형:2)
        if guild_info.type == GuildType.OPEN:
            crud_guild.set_join_guild(db, req.guild_id, req.uid, req.gid)
            
            data = {
                "chat_data":{
                    "app_id":config.APP_ID,
                    "channel_id":req.guild_id,
                    "uid":req.uid,
                    "name":user_member.nickname,
                    "message":'',
                    "message_type":MessageType.JOIN,
                    "extra_param": { 
                        "memberID":user_member.uid,
                        "memberName":user_member.nickname
                    }
                }
            }
        elif guild_info.type == GuildType.CLOSE:
            crud_guild.set_request_join_guild(db, req.guild_id, req.uid)
            
            data = {
                "chat_data":{
                    "app_id":config.APP_ID,
                    "channel_id":req.guild_id,
                    "uid":req.uid,
                    "name":user_member.nickname,
                    "message":'',
                    "message_type":MessageType.REQUEST_JOIN,
                    "extra_param": { 
                        "memberID":user_member.uid,
                        "memberName":user_member.nickname
                    }
                }
            }
            
            pass
        else:
            pass
    
    return get_response(code=ResponseCode.SUCCESS, uid=req.uid)




def guild_leave(req:GuildLeave, db:Session):
    
    guild_info = crud_guild.get_guild_info(db, req.guild_id)
    
    if not guild_info:
        return get_response(code=ResponseCode.NOT_EXIST_GUILD, uid=req.uid)
    
    
    guild_member = crud_guild.get_guild_member(db, req.guild_id, req.uid)
    
    if not guild_member:
        return get_response(code=ResponseCode.NOT_GUILD_MEMBER, uid=req.uid)
    
    if req.user_guild_score > 0:
        req.user_guild_score = guild_info.guild_score if (req.user_guild_score > guild_info.guild_score) else req.user_guild_score
        
    crud_guild.set_leave_guild(db, req.guild_id, req.uid, req.user_guild_score)
    
    user_member = crud_guild.get(db, req.uid)
    
    data = {
        "chat_data":{
            "app_id":config.APP_ID,
            "channel_id":req.guild_id,
            "uid":req.uid,
            "name":user_member.nickname,
            "message":'',
            "message_type":MessageType.LEAVE,
            "extra_param": { 
                "memberID":user_member.uid,
                "memberName":user_member.nickname
            }
        }
    }
    
    return get_response(code=ResponseCode.SUCCESS, data=data, uid=req.uid)




def guild_user_ban(req:GuildBan, db:Session):
    
    guild_info = crud_guild.get_guild_info(db, req.guild_id)
    
    if not guild_info:
        return get_response(code=ResponseCode.NOT_EXIST_GUILD, uid=req.uid)
    
    guild_member = crud_guild.get_guild_member(db, req.guild_id, req.uid)
    
    if not guild_member:
        return get_response(code=ResponseCode.NOT_GUILD_MEMBER, uid=req.uid)
    
    if req.user_guild_score > 0:
        req.user_guild_score = guild_info.guild_score if (req.user_guild_score > guild_info.guild_score) else req.user_guild_score
        
    crud_guild.set_leave_guild(db, req.guild_id, req.uid, req.user_guild_score)
    
    crud_guild.set_join_status(db, req.guild_id, req.uid, JoinStatus.BAN)
    
    
    user_member = crud_guild.get(db, req.uid)
    
    data = {
        "chat_data":{
            "app_id":config.APP_ID,
            "channel_id":req.guild_id,
            "uid":req.uid,
            "name":user_member.nickname,
            "message":'',
            "message_type":MessageType.BAN,
            "extra_param": { 
                "memberID":user_member.uid,
                "memberName":user_member.nickname
            }
        }
    }
    
    return get_response(code=ResponseCode.SUCCESS, data=data, uid=req.uid)




def guild_accept_join_user(req:GuildAcceptJoin, db:Session):
    
    guild_info = crud_guild.get_guild_info(db, req.guild_id)
    
    if not guild_info:
        return get_response(code=ResponseCode.NOT_EXIST_GUILD, uid=req.uid)
    
    guild_leader_info = crud_guild.get_guild_member(db, req.guild_id, req.uid)
    
    if not guild_leader_info:
        return get_response(code=ResponseCode.NOT_GUILD_MEMBER, uid=req.uid)
    
    if guild_leader_info.user_level < config.GUILD_COLEADER_LEVEL:
        return get_response(code=ResponseCode.UNAUTHORIZED_GUILD_ACTION, uid=req.uid)
    
    target_user_member = crud_guild.get(db, req.target_uid)
    if not target_user_member:
        return get_response(code=ResponseCode.NOT_EXIST_USER, uid=req.uid)
    
    if crud_guild.count_any_guild_member(db, req.uid) > 0:
        return get_response(code=ResponseCode.ALREADY_JOINED_GUILD_USER, uid=req.uid)
    
    crud_guild.set_join_guild(db, req.guild_id, req.target_uid, req.gid)
    
    crud_guild.set_join_status(db, req.guild_id, req.target_uid, JoinStatus.ACCEPT)
    
    data = {
        "chat_data":{
            "app_id":config.APP_ID,
            "channel_id":req.guild_id,
            "uid":target_user_member.uid,
            "name":target_user_member.nickname,
            "message":'',
            "message_type":MessageType.JOIN,
            "extra_param": { 
                "memberID":target_user_member.uid,
                "memberName":target_user_member.nickname
            }
        }
    }
    
    return get_response(code=ResponseCode.SUCCESS, data=data, uid=req.uid)




def guild_reject_join_user(req:GuildRejectJoin, db:Session):
    
    guild_info = crud_guild.get_guild_info(db, req.guild_id)
    
    if not guild_info:
        return get_response(code=ResponseCode.NOT_EXIST_GUILD, uid=req.uid)
    
    guild_leader_info = crud_guild.get_guild_member(db, req.guild_id, req.uid)
    guild_leader_member = crud_guild.get(db, req.uid)
    
    if not guild_leader_info:
        return get_response(code=ResponseCode.NOT_GUILD_MEMBER, uid=req.uid)
    
    if guild_leader_info.user_level < config.GUILD_COLEADER_LEVEL:
        return get_response(code=ResponseCode.UNAUTHORIZED_GUILD_ACTION, uid=req.uid)
    
    if not guild_leader_member:
        return get_response(code=ResponseCode.NOT_EXIST_USER, uid=req.uid)
    
    user_member = crud_guild.get(db, req.target_uid)
    if not user_member:
        return get_response(code=ResponseCode.NOT_EXIST_USER, uid=req.uid)
    
    # target_uid가 대상이 되어야 하지 않나? 왜 uid를 사용했지?
    if crud_guild.count_any_guild_member(req.target_uid) > 0:
        return get_response(code=ResponseCode.UNAUTHORIZED_GUILD_ACTION, uid=req.uid)
    
    crud_guild.set_join_status(db, req.guild_id, req.target_uid, JoinStatus.REJECT)
    
    data = {
        "chat_data":{
            "app_id":config.APP_ID,
            "channel_id":req.guild_id,
            "uid":guild_leader_member.uid,
            "name":guild_leader_member.nickname,
            "message":'',
            "message_type":MessageType.REJECT,
            "extra_param": { 
                "memberID":user_member.uid,
                "memberName":user_member.nickname
            }
        }
    }
    
    return get_response(code=ResponseCode.SUCCESS, data=data, uid=req.uid)





def guild_set_user_coleader(req:GuildSetCoLeader, db:Session):
    
    guild_info = crud_guild.get_guild_info(db, req.guild_id)
    
    if not guild_info:
        return get_response(code=ResponseCode.NOT_EXIST_GUILD, uid=req.uid)
    
    guild_leader_info = crud_guild.get_guild_member(db, req.guild_id, req.uid)
    
    if not guild_leader_info:
        return get_response(code=ResponseCode.NOT_GUILD_MEMBER, uid=req.uid)
    
    
    if guild_leader_info.user_level < config.GUILD_LEADER_LEVEL:
        return get_response(code=ResponseCode.UNAUTHORIZED_GUILD_ACTION, uid=req.uid)
    
    guild_member_info = crud_guild.get_guild_member(db, req.guild_id, req.target_uid)
    
    if not guild_member_info:
        return get_response(code=ResponseCode.NOT_GUILD_MEMBER, uid=req.uid)
    
    
    count_leader = crud_guild.count_coleader(db, req.guild_id)
    
    if count_leader >= config.MAX_COLEADER_COUNT:
        return get_response(code=ResponseCode.MAX_GUILD_COLEADER_COUNT, uid=req.uid)
    
    crud_guild.set_guild_user_level(db, req.guild_id, req.target_uid, config.GUILD_COLEADER_LEVEL)
    
    return get_response(code=ResponseCode.SUCCESS, uid=req.uid)
    


def guild_set_user_normal(req:GuildSetNormal, db:Session):
    
    guild_info = crud_guild.get_guild_info(db, req.guild_id)
    
    if not guild_info:
        return get_response(code=ResponseCode.NOT_EXIST_GUILD, uid=req.uid)
    
    guild_leader_info = crud_guild.get_guild_member(db, req.guild_id, req.uid)
    
    if not guild_leader_info:
        return get_response(code=ResponseCode.NOT_GUILD_MEMBER, uid=req.uid)
   
    if guild_leader_info.user_level < config.GUILD_LEADER_LEVEL:
        return get_response(code=ResponseCode.UNAUTHORIZED_GUILD_ACTION, uid=req.uid)
    
    guild_member_info = crud_guild.get_guild_member(db, req.guild_id, req.target_uid)
    
    if not guild_member_info:
        return get_response(code=ResponseCode.NOT_GUILD_MEMBER, uid=req.uid)
    
    if guild_member_info.user_level <= config.GUILD_NORMAL_LEVEL:
        return get_response(code=ResponseCode.BAD_REQUEST, uid=req.uid)
    
    crud_guild.set_guild_user_level(db, req.guild_id, req.target_uid, config.GUILD_NORMAL_LEVEL)
    
    return get_response(code=ResponseCode.SUCCESS, uid=req.uid)





def guild_verigy_message(req:GuildVerifyMessage, db:Session):
    
    
    if int(req.app_id) != config.APP_ID:
        return get_response(code=ResponseCode.INVALID_APP_ID, uid=req.uid)
    
    guild_id = int(req.channel_id)
    
    guild_member = crud_guild.get_guild_member(db, guild_id, req.uid)
    
    if not guild_member:
        return get_response(code=ResponseCode.NOT_GUILD_MEMBER, uid=req.uid)
    
    guild_message = None
    isRenew = 0
    prevMessage = {}
    
    if req.message_type == MessageType.REQUEST_LIFE:
        
        pass
    elif req.message_type == MessageType.HELP_LIFE:
        pass
    else:
        pass
    
    return get_response(code=ResponseCode.SUCCESS, uid=req.uid)





def guild_receive_help(req:GuildReceiveHelp, db:Session):
    
    return get_response(code=ResponseCode.SUCCESS, uid=req.uid)
