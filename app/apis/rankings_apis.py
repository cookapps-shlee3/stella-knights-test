# -*- coding: utf-8 -*-
import time
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.params.ResParam import get_response, ResponseCode
from app.params.ReqParam import *
from app.helper import rankings_helper
from app.config.settings import Constant
from app.redis.redisCache import redis
from app.crud.cache import crud_user_currency
from app.classes.CurrencyManager import CurrencyManager
from app.classes.UserDataManager import UserDataManager
from app.cache import CacheController
from app.util.util import get


async def rankings_pvp_search(req:PvpSearchReqParam, db:Session):
    
    ranking_info = await rankings_helper.get_pvp_user(db, redis, req.uid, req.key)
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=ranking_info, uid=req.uid)




async def rankings_pvp_score(req:PvpScoreReqParam, db:Session):
    
    result_info = await rankings_helper.set_pvp_score_ranking_list(db, redis, req.uid, req.key, req.score, req.data, req.target_uid, req.is_win)
    
    if not result_info:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
        
    return get_response(code=ResponseCode.RES_SUCCESS, data=result_info, uid=req.uid)




async def rankings_pvp_dummy(req:PvpSearchReqParam, db:Session):
    
    count = rankings_helper.set_pvp_dummy_rank_data(db, redis, 'afk-dungeon_ranking_PVP_18', 'afk-dungeon_ranking_profile_PVP_18', 1000)
    
    response = {
        'count' : count
    }
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=response, uid=req.uid)



async def rankings_weekly(req:WeeklyReqParam, db:Session):
    
    ranking_info = await rankings_helper.set_weekly_ranking_list(db, redis, req.uid, req.key, req.score, req.data, req.update, req.week)

    if not ranking_info:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=ranking_info, uid=req.uid)



async def rankings_weekly_info(req:WeeklyInfoReqParam, db:Session):
    
    ranking_info = await rankings_helper.get_ranking_info(db, redis, req.uid, req.key, req.week)

    if not ranking_info:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=ranking_info, uid=req.uid)




async def rankings_current_week():
    week_number = rankings_helper.get_week_number()
    date_number = int(datetime.now().strftime('%Y%m%d'))
    
    response = {
        'weekNumber' : week_number,
        'dateNumber' : date_number
    }
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=response)


async def rankings_weekly_search(req:WeeklyReqParam, db:Session):
    ranking_info = await rankings_helper.get_last_weekly_rakning_list(db, redis, req.uid, req.key)
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=ranking_info, uid=req.uid)







####################################################################################################################################################################
## custom weekly
####################################################################################################################################################################


async def rankings_current_custom_week(req:CustomWeekReqParam):
    week_number = rankings_helper.get_custom_week_number(req.day)
    date_number = int(datetime.now().strftime('%Y%m%d'))
    
    response = {
        'weekNumber' : week_number,
        'dateNumber' : date_number
    }
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=response, uid=req.uid)


async def rankings_custom_weekly(req:CustomWeeklyReqParam, db:Session):

    ranking_info = await rankings_helper.set_custom_weekly_ranking_list(db, redis, req.uid, req.key, req.score, req.day, req.data, req.update, req.week, req.multiple)

    if not ranking_info:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=ranking_info, uid=req.uid)



async def rankings_weekly_section_info(req:WeeklySectionReqParam, db:Session):
    arr_rankings = await rankings_helper.get_weekly_section_ranking_recommand(redis, req.key, req.week, req.multiple, req.section)
    
    if not arr_rankings:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    response = {
        'countList' : arr_rankings,
        'max' : Constant.RANKING_SECTION_MAX
    }
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=response, uid=req.uid)


async def rankings_custom_weekly_search(req:CustomWeeklyReqParam, db:Session):
    ranking_info = await rankings_helper.get_last_custom_weekly_rakning_list(db, redis, req.uid, req.key, req.day)
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=ranking_info, uid=req.uid)

####################################################################################################################################################################
## daily
####################################################################################################################################################################

async def rankings_daily(req:DailyReqParam, db:Session):
    ranking_info = await rankings_helper.set_daily_ranking_list(db, redis, req.uid, req.key, req.score, req.data, req.update, req.day, req.listing)
    
    if not ranking_info:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=ranking_info, uid=req.uid)


async def rankings_daily_search(req:DailyReqParam, db:Session):
    ranking_info = await rankings_helper.get_last_daily_ranking_list(db, redis, req.uid, req.key)
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=ranking_info, uid=req.uid)



async def rankings_forever(req:ForeverReqParam, db:Session):
   
    return get_response(code=ResponseCode.RES_SUCCESS, uid=req.uid)



####################################################################################################################################################################
## half
####################################################################################################################################################################



async def rankings_current_half(db:Session):
    
    pvp_data = await rankings_helper.get_half_number(db)
    date_number = int(datetime.now().strftime('%Y%m%d'))

    response = {
        'seconds' : int(time.mktime(pvp_data['end_date'].timetuple()) - time.mktime(datetime.now().timetuple())),
        'halfNumber' : pvp_data['id'],
        'dateNumber' : date_number
    }
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=response)



async def rankings_pvp_half_search(req:PvpHalfSearchReqParam, db:Session):
    
    ranking_info = await rankings_helper.get_half_pvp_user(db, redis, req.uid, req.key)
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=ranking_info, uid=req.uid)



async def rankings_pvp_half_start(req:BaseReqParam, db:Session):
    
    time_category = 'Time'
    pass_category = 'Pass'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()

    pass_datas = userdataManager.get(db, req.uid, pass_category)
    
    game_config_dict = await CacheController.game_config_info_map(db)
    game_config_info = get(game_config_dict, req.platform, None)
    
    pass_event = await CacheController.get_current_pass_event_info(db, req.platform)
    if not pass_event:
        vip_value = False
    else:
        pass_id = get(pass_event, 'id', None)
        
        find_pass = None
        
        for pass_value in pass_datas:
            current_id = get(pass_value, 'id', 0)
            if pass_id == current_id:
                find_pass = pass_value
                break

        if find_pass != None:
            vip_value = get(find_pass, 'vip', False)
        else:
            vip_value = False


    if vip_value:
        energy_info = get(game_config_info, Constant.GAME_CONFIG_PASS_ENABLE_PTICKET_MAX, None)
    else:
        energy_info = get(game_config_info, Constant.GAME_CONFIG_NORMAL_PTICKET_MAX, None)
    if not energy_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_GAME_CONFIG_VALUE, uid=req.uid)
    
    energy_max = get(energy_info, 'value', None)
    if energy_max == None:
        return get_response(code=ResponseCode.RES_NOT_FOUND_MAX_ENERGY_VALUE, uid=req.uid)
    
    energy_max = int(energy_max)
    energy = currencyManager.get_amount(db, req.uid, 'PTICKET')
    
    current_time = int(time.time()) + Constant.VALUE_OF_1970
                    
    if energy >= energy_max:
        userdataManager.change_user_data_value(db, req.uid, time_category, 'lastPVPTime', current_time)
    
    result = currencyManager.use_currency(db, req.uid, 'PTICKET', 1)
    if result == None:
        return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, uid=req.uid)
    
    # await set_reserve_value(redis, req.uid, "True")
    
    data = currencyManager.get_user_currency_data(db, req.uid)
    data['UserData'] = userdataManager.generate_user_save(db, req.uid)
    data['change'] = currencyManager.get_change()
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)


async def get_reserve_value(service:redis, uid:int):
    reserve_key = Constant.PROJECT_NAME + '_reserve'
    value = await service.get_hash(reserve_key, uid)
    
    return value


async def set_reserve_value(service:redis, uid:int, value:str):
    reserve_key = Constant.PROJECT_NAME + '_reserve'
    await service.set_hash(reserve_key, uid, value)




async def rankings_pvp_half_score(req:PvpHalfScoreReqParam, db:Session):
    
    # value = await get_reserve_value(redis, req.uid)
    # if (value == None) or (value != "True") :
    #     return get_response(code=ResponseCode.RES_INVALUD_PVP_GAME_END, uid=req.uid)
    
    # await set_reserve_value(redis, req.uid, "False")

    result_info = await rankings_helper.set_half_pvp_score_ranking_list(db, redis, req.uid, req.key, req.score, req.data, req.target_uid, req.is_win, req.is_revenge)
    
    if not result_info:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
        
    return get_response(code=ResponseCode.RES_SUCCESS, data=result_info, uid=req.uid)





async def rankings_pvp_half_revenge(req:BaseReqParam, db:Session):
    
    revenge_list = await rankings_helper.get_revenge_list(redis, db, req.uid)
    
    # if revenge_list:
    #     revenge_list = json.loads(revenge_list)
    # else:
    #     revenge_list = None
    
    data = {'revenge_list' : revenge_list}
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)



async def rankings_half(req:HalfReqParam, db:Session):
    
    ranking_info = await rankings_helper.set_half_ranking_list(db, redis, req.uid, req.key, req.score, req.data, req.update, req.half)

    if not ranking_info:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=ranking_info, uid=req.uid)



async def rankings_half_info(req:HalfInfoReqParam, db:Session):
    
    ranking_info = await rankings_helper.get_ranking_info(db, redis, req.uid, req.key, req.half)

    if not ranking_info:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=ranking_info, uid=req.uid)



async def rankings_half_search(req:HalfReqParam, db:Session):
    ranking_info = await rankings_helper.get_last_half_rakning_list(db, redis, req.uid, req.key)
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=ranking_info, uid=req.uid)




####################################################################################################################################################################
## rate ranking
####################################################################################################################################################################

async def rankings_weekly_rate(req:WeeklyReqParam, db:Session):
    
    ranking_info = await rankings_helper.set_weekly_rate_ranking_list(db, redis, req.uid, req.key, req.score, req.data, req.update, req.week)

    if not ranking_info:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=ranking_info, uid=req.uid)



async def rankings_weekly_rate_info(req:WeeklyInfoReqParam, db:Session):
    
    ranking_info = await rankings_helper.get_ranking_info(db, redis, req.uid, req.key, req.week)

    if not ranking_info:
        return get_response(code=ResponseCode.RES_BAD_REQUEST, uid=req.uid)
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=ranking_info, uid=req.uid)



async def rankings_weekly_rate_search(req:WeeklyReqParam, db:Session):
    ranking_info = await rankings_helper.get_last_weekly_rakning_list(db, redis, req.uid, req.key)

    return get_response(code=ResponseCode.RES_SUCCESS, data=ranking_info, uid=req.uid)




####################################################################################################################################################################
## dummy pvp ranking
####################################################################################################################################################################

async def rankings_pvp_half_dummy_search(req:PvpHalfSearchReqParam, db:Session):
    
    ranking_info = await rankings_helper.get_half_pvp_dummy_user(db, redis, req.uid, req.key)
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=ranking_info, uid=req.uid)
