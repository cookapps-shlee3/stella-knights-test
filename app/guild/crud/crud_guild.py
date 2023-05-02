# -*- coding: utf-8 -*-
from telnetlib import LOGOUT
import time
import random
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.guild import GuildHelp, GuildInfo, GuildJoinStatus, GuildMember, GuildMessage, UserMembers
from ..config.config import config
from ..params.ResParam import JoinStatus

def get(db:Session, uid:int):
    return db.query(UserMembers).filter(UserMembers.uid == uid).first()


def get_user_join_status(db:Session, uid:int):
    guild_join_status = db.query(GuildJoinStatus).filter(GuildJoinStatus.uid == uid).first()
    return guild_join_status


def get_guild_list(db:Session):
    query = db.query(GuildInfo).filter(GuildInfo.user_count < config.DEFAULT_MAX_GUILD_USER_COUNT)
    row_count = int(query.count())
    random_list = query.offset(int(row_count*random.random())).limit(config.SHOW_GUILD_LIST_COUNT).all()
    
    random_result = []
    if random_list and len(random_list) > 0:
        for item in random_list:
            random_result.append(GuildInfo(item))
    
    return random_result


def get_guild_member_list(db:Session, guild_id:int):
    sql = "SELECT um.uid, um.nickname, um.gid, gm.assist_count, gm.user_level "
    sql += " FROM guild_member AS gm JOIN user_member AS um ON gm.uid = um.uid WHERE gm.guild_id = {} ORDER BY um.gid DESC"
    sql = sql.format(guild_id)
    query = db.execute(sql)
    result = query.fetchall()
        
    return result


def count_coleader(db:Session, guild_id:int):
    result = db.query(GuildMember).filter(GuildMember.guild_id == guild_id, GuildMember.user_level == config.GUILD_COLEADER_LEVEL).count()
    return result


def set_guild_user_level(db:Session, guild_id:int, uid:int, user_level:int):
    result = db.query(GuildMember).filter(GuildMember.guild_id == guild_id, GuildMember.uid == uid).update({GuildMember.user_level : user_level})
    db.commit()
    return result


## 이걸 어찌 할까나?
def get_guild_member(db:Session, guild_id:int, uid:int):
    result = db.query(GuildMember).filter(GuildMember.guild_id == guild_id, GuildMember.uid == uid).first()
    return result


def get_member(db:Session, uid:int):
    result = db.query(GuildMember).filter(GuildMember.uid == uid).first()
    return result


def count_any_guild_member(db:Session, uid:int):
    result = db.query(GuildMember).filter(GuildMember.uid == uid).count()
    return result


def create_guild(db:Session, uid:int, name:str, logo:int, type:int, minimum_level:int, comment:str, guild_score:int):
    data = GuildInfo()
    data.name = name
    data.logo = logo
    data.type = type
    data.minimum_level = minimum_level
    data.guild_score = guild_score
    data.comment = comment
    db.add(data)
    db.commit()
    db.refresh(data)
    
    member = GuildMember()
    member.guild_id = data.guild_id
    member.uid = uid
    member.user_level = config.GUILD_LEADER_LEVEL
    
    db.add(member)
    db.commit()
    return data.guild_id



def get_guild_info(db:Session, guild_id:int):
    result = db.query(GuildInfo).filter(GuildInfo.guild_id == guild_id).first()
    return result


def set_modify_guild(db:Session, guild_id:int, logo:int, type:int, minimum_level:int, comment:str):
    result = db.query(GuildInfo).filter(GuildInfo.guild_id == guild_id).update({GuildInfo.logo : logo, GuildInfo.type :type, GuildInfo.minimum_level : minimum_level, GuildInfo.comment:comment})
    db.commit()
    return result


def get_search_guild(db:Session, search_name:str):
    search = "%{}%".format(search_name)
    return db.query(GuildInfo).filter(GuildInfo.name.like(search)).all()


def count_guild_user(db:Session, guild_id:int):
    result = db.query(GuildMember).filter(GuildMember.guild_id == guild_id).count()
    return result


def set_join_guild(db:Session, guild_id:int, uid:int, gid:int):
    # 길드 정도에 대해서 업데이트 처리를 한 후
    result = db.query(GuildInfo).filter(GuildInfo.guild_id == guild_id).update({GuildInfo.user_count : GuildInfo.user_count+1, GuildInfo.guild_score :GuildInfo.guild_score+gid})
    db.commit()
    
    # 길드 멤버 정보에 사용자 정보를 추가하도록 한다. 데이터가 있는 경우에는 길드 아이디를 변경해야 합니다.
    sql = "INSERT INTO `guild_member` (`guild_id`, `uid`) VALUES ({}, {}) ON DUPLICATE KEY UPDATE guild_id = VALUES(`guild_id`)"
    sql = sql.format(guild_id, uid)
    db.connection()
    db.execute(sql)
    db.commit()
    return result


def get_request_join_guild(db:Session, guild_id:int, uid:int):
    result = db.query(GuildJoinStatus).filter(GuildJoinStatus.guild_id == guild_id, GuildJoinStatus.uid == uid).first()
    return result


def set_request_join_guild(db:Session, guild_id:int, uid:int):
    
    data = GuildJoinStatus()
    data.guild_id = guild_id
    data.uid = uid
    data.status = JoinStatus.REQUEST
    db.add(data)
    db.commit()    


def set_join_status(db:Session, guild_id:int, uid:int, status:int):
    data = GuildJoinStatus()
    data.uid = uid
    data.guild_id = guild_id
    data.status = status
    db.add(data)
    db.commit()



def set_leave_guild(db:Session, guild_id:int, uid:int, gid:int):
    result = db.query(GuildMember).filter(GuildMember.guild_id == guild_id, GuildMember.uid == uid).update({GuildMember.guild_id : 0})
    
    count_user = count_guild_user(db, guild_id)
    
    if count_user == 0:
        db.query(GuildInfo).filter(GuildInfo.guild_id == guild_id).delete()
        db.commit()
    else:
        result = db.query(GuildInfo).filter(GuildInfo.guild_id == guild_id).update({GuildInfo.user_count : GuildInfo.user_count - 1, GuildInfo.guild_score :GuildInfo.guild_score - gid})
        db.commit()


def add_guild_message(db:Session, guild_id:int, uid:int, nickname:str, message_type:int, request_timestamp:int, request_count:int):
    data = GuildMessage()
    data.guild_id = guild_id
    data.uid = uid
    data.nickname = nickname
    data.request_timestamp = request_timestamp
    data.request_count = request_count
    data.created_timestamp = int(time.time())
    db.add(data)
    db.commit()


def delete_guild_message(db:Session, guild_id:int, uid:int, message_type:int):
    db.query(GuildMessage).filter(GuildMessage.guild_id == guild_id, GuildMessage.uid == uid, GuildMessage.message_type == message_type).delete()
    db.commit()


def delete_guild_help(db:Session, guild_id:int, uid:int, message_type:int):
    db.query(GuildHelp).filter(GuildHelp.guild_id == guild_id, GuildMember.uid == uid, GuildHelp.message_type == message_type).delete()
    db.commit()
    
    db.query(GuildMember).filter(GuildMember.uid == uid).update({GuildMember.assist_count : GuildMember.assist_count + 1})
    db.commit()


def send_guild_help(db:Session, guild_id:int, uid:int, target_message_type:int, message_type:int, sender_uid:int):
    
    db.query(GuildMessage).filter(GuildMessage.guild_id == guild_id, GuildMessage.uid == uid, GuildMessage.message_type == message_type).update({GuildMessage.receive_count : GuildMessage.receive_count + 1})
    db.commit()
    
    
    data = GuildHelp()
    data.guild_id = guild_id
    data.uid = uid
    data.message_type = message_type
    data.sender_uid = sender_uid
    db.add(data)
    db.commit()
    
    db.query(GuildMember).filter(GuildMember.uid == uid).update({GuildMember.assist_count : GuildMember.assist_count + 1})
    db.commit()
    



def get_guild_message(db:Session, guild_id:int, uid:int, message_type:int):
    result = db.query(GuildMessage).filter(GuildMessage.guild_id == guild_id, GuildMessage.uid == uid, GuildMessage.message_type == message_type).first()
    return result


def count_guild_help(db:Session, guild_id:int, uid:int, message_type:int, sender_uid:int):
    result = db.query(GuildHelp).filter(GuildHelp.guild_id == guild_id, GuildHelp.uid == uid, GuildHelp.message_type == message_type, GuildHelp.sender_uid == sender_uid).count()
    return result

