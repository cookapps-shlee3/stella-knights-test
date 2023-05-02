import json
from app.redis.redisCache import RedisCache
from app.config.settings import Constant

async def get_user_member_info(service:RedisCache, uid:int):
    if not uid:
        return True
    
    key = Constant.PROJECT_NAME + '_member' + ':' + str(uid)
    str_json = service.get_value(key)
    if str_json:
        member_info = json.loads(str_json)
        if member_info:
            return member_info
    
    return None


async def set_user_member_info(service:RedisCache, uid:int, user_member:dict):
    if not uid:
        return
    
    key = Constant.PROJECT_NAME + '_member' + ':' + str(uid)
    
    if user_member:
        str_json = json.dumps(user_member, ensure_ascii = False)
        service.set_value(key, str_json)
