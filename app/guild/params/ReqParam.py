from pydantic import BaseModel
from typing import Optional

class BaseReqParam(BaseModel):
    p:str = 'unknown'
    d:str = ''
    h:Optional[str] = ''
    v:int = 0
    version:int = 0
    uid:Optional[int] = 0
    platform:Optional[str]=''
    device_id:Optional[str]=''


class GuildInfo(BaseReqParam):
    guild_id:int = 0
    

class GuildCreate(BaseReqParam):
    logo:int = 0
    name:str = 'guild_name'
    comment:str = "guild description"
    type:int = 0
    minimum_level:int = 50
    default_score:Optional[int] = 0



class GuildModify(BaseReqParam):
    guild_id:int = 0
    logo:int = 0
    comment:str = "guild description"
    type:int = 0
    minimum_level:int = 50



class GuildSearch(BaseReqParam):
    search_name:str = ''

    
    
    
class GuildJoin(BaseReqParam):
    guild_id:int = 0
    gid:Optional[int] = 0



class GuildLeave(BaseReqParam):
    guild_id:int = 0
    user_guild_score:Optional[int]=0



class GuildBan(BaseReqParam):
    guild_id:int = 0
    user_guild_score:Optional[int]=0



class GuildAcceptJoin(BaseReqParam):
    guild_id:int = 0
    target_uid:int = 0
    gid:Optional[int] = 0



class GuildRejectJoin(BaseReqParam):
    guild_id:int = 0
    target_uid:int = 0



class GuildSetCoLeader(BaseReqParam):
    guild_id:int = 0
    target_uid:int = 0



class GuildSetNormal(BaseReqParam):
    guild_id:int = 0
    target_uid:int = 0



class GuildVerifyMessage(BaseReqParam):
    app_id:int = 0
    channel_id:int = 0
    name:str = ''
    message_type:int = 0
    extra_param:dict = {'target_uid':0}
    request_timestamp:int = 12345



class GuildReceiveHelp(BaseReqParam):
    request_timestamp:int = 12345
    
