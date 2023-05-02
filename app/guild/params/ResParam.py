from enum import Enum
from pydantic import BaseModel
from typing import Optional

class BaseResParam(BaseModel):
    code:int=200
    msg:Optional[str]=''
    data:Optional[dict]=None


class ResponseCode(Enum):
    SUCCESS= 200,
    BAD_REQUEST= 400,
    UNAUTHORIZED= 401,
    NOT_FOUND= 404,  
    INTERNAL_SERVER_ERROR= 500,
    CUSTOM_SERVER_ERROR = 1000,
    INVALID_APP_ID= 9000,
    NOT_EXIST_USER= 9001,
    NOT_EXIST_GUILD= 9002,
    NOT_GUILD_MEMBER= 9003,
    UNAUTHORIZED_GUILD_ACTION= 9004,
    MAX_GUILD_USER_COUNT= 9005,
    MAX_FREE_LIFE_COUNT= 9006,
    REQUEST_LIFE_COOL_TIME= 9007,
    NOT_EXIST_MESSAGE= 9008,
    MAX_RECEIVE_COUNT= 9009,
    ALREADY_SEND_HELP= 9010,
    NOT_EXIST_MESSAGE_TYPE= 9011,
    ALREADY_REQUEST_MESSAGE= 9012,
    BAN_GUILD_USER= 9013,
    ALREADY_JOINED_GUILD_USER= 9014,
    MAX_GUILD_COLEADER_COUNT= 9015,
    
    
    def hasValue(self, code):
        for rspCode in ResponseCode:
            if code == rspCode:
                return True
        
        return False
    
# 길드 유형 (개방형, 폐쇄형)
class GuildType(Enum):
    OPEN = 1,
    CLOSE = 2,
    
    def hasValue(self, code):
        for rspCode in GuildType:
            if code == rspCode:
                return True
        
        return False


# 가입 상태 (0:없음, 1:신청, 2:승인, 3:거절, 4:강퇴)
class JoinStatus(Enum):
    NONE= 0,
    REQUEST= 1,
    ACCEPT= 2,
    REJECT= 3,
    BAN= 4,
    
    def hasValue(self, code):
        for rspCode in JoinStatus:
            if code == rspCode:
                return True
        
        return False
    
class MessageType(Enum):
    NOTICE= 50,
    REQUEST_JOIN= 51,
    JOIN= 52,
    LEAVE= 53,
    BAN= 54,
    REJECT= 55,
    REQUEST_LIFE= 100,    # 요청 - 라이프 요청
    HELP_LIFE= 101,       # 도움 - 라이프 도움 보내기
    CUSTOM_ACTION= 102,   # 각 게임에서 자체적으로 사용할 메시지 타입 (extraParam 파라미터로 자유롭게 사용)

    
    def hasValue(self, code):
        for rspCode in MessageType:
            if code == rspCode:
                return True
        
        return False


def get_response(code:ResponseCode, msg:str='', data=None):
    res = BaseResParam()
    res.code = code.value[0]
    if not msg:
        res.msg = code.name
    else:
        res.msg = msg
    
    if data:
        res.data = data
        
    return res