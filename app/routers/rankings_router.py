# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.db.connection import get_db
from app.params.ReqParam import *
from app.auth.auth_bearer import JWTBearer
from app.params.ResParam import get_response, ResponseCode
from app.apis import rankings_apis


rankings_router = APIRouter(prefix='/rankings')


@rankings_router.post('/weekly')
async def weekly(req:WeeklyReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.key:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    req.score =  -1 if not req.score and (req.score != 0) else req.score
    
    req.week = None if not req.week else int(req.week)
    
    return await rankings_apis.rankings_weekly(req, db)



@rankings_router.post("/weekly/number")
async def weekly_info(req:WeeklyReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    return await rankings_apis.rankings_current_week()



@rankings_router.post("/weekly/info")
async def weekly(req:WeeklyInfoReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.key:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d

    req.week = None if not req.week else int(req.week)
    
    return await rankings_apis.rankings_weekly_info(req, db)


@rankings_router.post("/weekly/search")
async def weekly_search(req:WeeklyReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED)
    
    return await rankings_apis.rankings_weekly_search(req, db)



@rankings_router.post("/weekly/section_info")
async def weekly_section_info(req:WeeklySectionReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED)
    
    if req.multiple == None:
        req.multiple = False
    
    if req.multiple:
        if req.section == None:
            req.section = 0
    
    return rankings_apis.rankings_weekly_section_info(req, db)





####################################################################################################################################################################################

@rankings_router.post('/custom/weekly')
async def weekly(req:CustomWeeklyReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.key:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    if req.day == None:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    if req.day > 6:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    req.score =  -1 if not req.score and (req.score != 0) else req.score
    
    req.week = None if not req.week else int(req.week)
    
    return await rankings_apis.rankings_custom_weekly(req, db)


@rankings_router.post("/custom/weekly/number")
async def current_custom_week(req:CustomWeekReqParam):
    
    if req.day == None:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    if req.day > 6:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    return await rankings_apis.rankings_current_custom_week(req)



@rankings_router.post("/custom/weekly/search")
async def weekly_custom_search(req:CustomWeeklyReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.key:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    if req.day == None:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    if req.day > 6:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    return await rankings_apis.rankings_custom_weekly_search(req, db)


####################################################################################################################################################################################

@rankings_router.post('/half')
async def half(req:HalfReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.key:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    req.score =  -1 if not req.score and (req.score != 0) else req.score
    
    req.half = None if not req.half else int(req.half)
    
    return await rankings_apis.rankings_half(req, db)



@rankings_router.post("/half/number")
async def half_info(req:BaseReqParam, db:Session = Depends(get_db)):
    return await rankings_apis.rankings_current_half(db)



@rankings_router.post("/half/info")
async def half_info(req:HalfInfoReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    if not req.key:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d

    req.week = None if not req.week else int(req.week)
    
    return await rankings_apis.rankings_half_info(req, db)



@rankings_router.post("/pvp/half/match")
async def pvp_half_search(req:PvpHalfSearchReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):

    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)

    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d

    return await rankings_apis.rankings_pvp_half_search(req, db)



@rankings_router.post("/pvp/half/start")
async def pvp_half_score(req:BaseReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    return await rankings_apis.rankings_pvp_half_start(req, db)
    
    


@rankings_router.post("/pvp/half/result")
async def pvp_half_score(req:PvpHalfScoreReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.key:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    req.score =  -1 if not req.score and (req.score != 0) else req.score
    return await rankings_apis.rankings_pvp_half_score(req, db)    



@rankings_router.post("/pvp/half/revenge")
async def pvp_half_score(req:BaseReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    return await rankings_apis.rankings_pvp_half_revenge(req, db)



@rankings_router.post("/pvp/half/search")
async def pvp_half_search(req:HalfReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)
    
    return await rankings_apis.rankings_half_search(req, db)



# 더미 목록 중에서 DB에 저장되어 있는 사람들만 모아서 추려낸다.
@rankings_router.post("/pvp/half/dummy/match")
async def pvp_half_dummy_search(req:PvpHalfSearchReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):

    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED, uid=req.uid)

    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d

    return await rankings_apis.rankings_pvp_half_dummy_search(req, db)




####################################################################################################################################################################################




@rankings_router.post("/pvp/match")
async def pvp_search(req:PvpSearchReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):

    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED)
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d

    return await rankings_apis.rankings_pvp_search(req, db)




@rankings_router.post("/pvp/result")
async def pvp_score(req:PvpScoreReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.key:
        return get_response(code=ResponseCode.RES_BAD_REQUEST)
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED)
    
    
    req.platform = req.platform if req.platform else req.p
    req.device_id = req.device_id if req.device_id else req.d
    
    req.score =  -1 if not req.score and (req.score != 0) else req.score
    return await rankings_apis.rankings_pvp_score(req, db)    





@rankings_router.post("/pvp/dummy")
async def pvp_dummy(req:PvpSearchReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    if not req.key:
        return get_response(code=ResponseCode.RES_BAD_REQUEST)
    
    return rankings_apis.rankings_pvp_dummy(req, db)






@rankings_router.post("/season")
async def season(req:BaseReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    return get_response(code=ResponseCode.RES_SUCCESS)


@rankings_router.post("/dummy")
async def dummy(req:BaseReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    return get_response(code=ResponseCode.RES_SUCCESS)


@rankings_router.post("/daily")
async def daily(req:DailyReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED)
    
    if req.key == None:
        return get_response(code=ResponseCode.RES_BAD_REQUEST)
    
    req.score =  -1 if not req.score and (req.score != 0) else req.score
    
    req.day = None if not req.day else int(req.day)
    
    return await rankings_apis.rankings_daily(req, db)


@rankings_router.post("/daily/search")
async def daily_search(req:DailyReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    if not req.uid  and (req.uid != auth['uid']):
        return get_response(code=ResponseCode.RES_UNAUTHORIZED)
    
    return await rankings_apis.rankings_daily_search(req, db)



@rankings_router.post("/daily/dummy")
async def daily_dummy(req:BaseReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    return get_response(code=ResponseCode.RES_SUCCESS)


@rankings_router.post("/monthly")
async def monthly(req:BaseReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    return get_response(code=ResponseCode.RES_SUCCESS)


@rankings_router.post("/monthly/number")
async def current_month(req:BaseReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    return get_response(code=ResponseCode.RES_SUCCESS)


@rankings_router.post("/forever")
async def forever(req:BaseReqParam, db:Session = Depends(get_db), auth:dict=Depends(JWTBearer())):
    
    return get_response(code=ResponseCode.RES_SUCCESS)

