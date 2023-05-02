import json
from loguru import logger
from app.config.settings import Constant
from app.redis import redisCache

async def is_not_white_uid(service:redisCache, platform:str, device_id:str):
    if not device_id:
        return True
    
    key = Constant.PROJECT_NAME + '_white_' + platform
    str_json = await service.get_value(key)
    if not str_json:
        return True
    else:
        arr_device_ids = json.loads(str_json)
        if device_id in arr_device_ids:
            logger.warning(device_id)
            return False
    
    return True
