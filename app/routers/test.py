import json
import time
from fastapi import APIRouter, Depends, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional
from app.db.connection import get_db
from app.params.ReqParam import BaseReqParam, BattleSaveReqParam
from app.apis import test
from app.auth.auth_bearer import JWTBearer
from app.params.ResParam import get_response, ResponseCode
from app.config.settings import Constant
from app.db.models.user import UserDataBattle
from fastapi_cache.decorator import cache
from loguru import logger
from pymongo import MongoClient
from app.config.settings import settings
from app.db.models.user import UserDataMongo


# @cache(namespace='no', expire=100)
# async def get_quest_list(db:Session):
#     return user_quest_list(db)

# def user_quest_list(db:Session):
#     quest_list = crud_quest.get_all(db)
#     if quest_list:
#         quest_map_temp = {}
#         for quest in quest_list:
#             logger.info(str(quest.quest_id))
#             quest_map_temp[str(quest.quest_id)] = {'type':quest.reward_type, 'count':quest.reward_count}

#         return json.dumps(quest_map_temp)
#     return ''

test_router = APIRouter()

@test_router.get("/test")
async def test_list(db:Session=Depends(get_db)):
    with MongoClient(settings.MONGO_URL) as client:
        msg_collection = client['afk-dungeon']['user_save']
        msg_list = msg_collection.find({"_id":11111})
        print(msg_list[0])
        for msg in msg_list:
            print(msg)
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=str(int(time.time())))


@test_router.get("/test_insert")
async def test_list(db:Session=Depends(get_db)):
    user_data = UserDataMongo()
    user_data.id = 11113
    user_data.category = "test"
    user_data.data = {"test_value":1}
    with MongoClient(settings.MONGO_URL) as client:
        msg_collection = client['afk-dungeon']['user_save']
        result = msg_collection.insert_one(jsonable_encoder(user_data))
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=str(int(time.time())))

@test_router.post("/testtt")
async def test_list(data:BaseReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
#async def test_listttt(req:BattleSaveReqParam,  data:BaseReqParam, db:Session = Depends(get_db), service: Service = Depends(Provide[Container.service])):
    with MongoClient(settings.MONGO_URL) as client:
        msg_collection = client['afk-dungeon']['user_save']
        msg_collection.find({'_id':data.uid})
    
    return get_response(code=ResponseCode.RES_SUCCESS)
