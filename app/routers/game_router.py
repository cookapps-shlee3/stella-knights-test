# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.params.ReqParam import BaseReqParam
from app.params.CurrencyReqParam import *
from app.apis import game_apis
from app.apis import gacha_new
from app.auth.auth_bearer import JWTBearer
from app.config.settings import Constant
from app.params.ResParam import ResponseCode, get_response
from app.classes.UserDataManager import UserDataManager
from app.util.util import get


game_router = APIRouter(prefix='/game')



# 스테이지 클리어
@game_router.post("/stage/clear")
async def game_clear_stage(req:CurrencyClearReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await game_apis.game_stage_clear(req, db)


# 스테이지 클리어 by 소탕권
@game_router.post("/stage/sweep")
async def game_clear_stage(req:CurrencySweepReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await game_apis.game_stage_sweep(req, db)


# 챕터 클리어
@game_router.post("/chapter/clear")
async def game_clear_chapter(req:CurrencyClearReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await game_apis.game_chapter_clear(req, db)



# 퀘스트 클리어
@game_router.post("/quest/clear")
async def game_clear_quest(req:CurrencyClearReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await game_apis.game_quest_clear(req, db)



# 가이드미션 클리어
@game_router.post("/guide_mission/clear")
async def game_clear_guide_mission(req:CurrencyClearReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await game_apis.game_guide_mission_clear(req, db)




@game_router.post("/quest/list/clear")
async def game_clear_quest_list(req:CurrencyClearListReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await game_apis.game_quest_clear_list(req, db)




@game_router.post("/gacha/first")
async def run_gacha(req:GachaReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    if (req.platform == 'android'):
        return await game_apis.run_gacha(req, db)
    
    return await game_apis.run_gacha_temp(req, db)


# hojun
@game_router.post("/gacha")
async def run_gacha(req:GachaReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    userdataManager = UserDataManager()
    user_category = 'User'
    user_datas = userdataManager.get(db, req.uid, user_category)
    
    if req.id == 2 or req.id == 4:
        pick_count = get(user_datas, 'KPickCount', None)
        if pick_count == None:
            user_datas['KPickCount'] = 0
        if (user_datas['KPickCount'] < 10) and (user_datas['KPickCount'] + 10) >= 10:
            return await game_apis.run_gacha(req, db)
    
    return await gacha_new.gacha(req, db)



@game_router.post("/gacha/reward")
async def run_gacha(req:GachaRewardReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await game_apis.get_gacha_reward(req, db)



@game_router.post("/exchange")
async def item_exchange(req:ExchangeItemReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await game_apis.exchange_item(req, db)





# 게임 시작시에 호출하도록 추가한 api
@game_router.post("/start")
async def game_start(req:CurrencyStartReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await game_apis.game_start(req, db)




# 게임 종료시에 호출하도록 추가한 api
@game_router.post("/dungeon/end")
async def game_dungeon_end(req:CurrencyEndReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await game_apis.game_dungeon_end(req, db)



#########################################################################################################################################################
# Expidition
#########################################################################################################################################################



@game_router.post("/expedition/start")
async def game_expedition_start(req:BaseReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await game_apis.game_expedition_start(req, db)



@game_router.post("/expedition/end")
async def game_expedition_end(req:ExpiditionEndReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await game_apis.game_expedition_end(req, db)



@game_router.post("/expedition/card/gacha")
async def game_expedition_gacha_card(req:CardGachaReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await game_apis.game_expedition_gacha(req, db)



@game_router.post("/expedition/card/giveup")
async def game_expedition_gacha_giveup(req:CardGachaGiveupReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await game_apis.game_expedition_card_giveup(req, db)



@game_router.post("/expedition/card/select")
async def game_expedition_gacha_select(req:CardGachaSelectReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if auth:
        if not req.uid  and (req.uid != auth['uid']):
            return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await game_apis.game_expedition_card_select(req, db)

