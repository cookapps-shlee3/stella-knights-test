# -*- coding: utf-8 -*-
import os
import math
import json
import random
import time
from datetime import datetime
from loguru import logger
from functools import reduce
from sqlalchemy.orm import Session
from app.params.ResParam import get_response, ResponseCode
from app.params.ReqParam import BaseReqParam
from app.params.CurrencyReqParam import *
from app.util.util import get
from app.config.settings import Constant
from app.cache import CacheController
from app.crud import crud_user_data, crud_user_members
from app.crud.cache import crud_user_currency, crud_user_currency_log
from app.classes.CurrencyManager import CurrencyManager
from app.classes.UserDataManager import UserDataManager


## Set Timezone
os.environ['TZ'] = 'UTC'


#########################################################################################################################################################



async def refresh_energy(req:CurrencyEnergyRefreshReqParam, db:Session):
    time_category = 'Time'
  
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
  
    user_level_dict = await CacheController.level_up_info_map(db)
    user_level_info = get(user_level_dict, req.platform, None)
    if not user_level_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_UP_DATA, uid=req.uid)
    
    info = get(user_level_info, str(req.level), None)
    if not info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_UP_INFO_DATA, uid=req.uid)

    energy_max = get(info, 'bread_max', None)
    if energy_max == None:
        return get_response(code=ResponseCode.RES_NOT_FOUND_MAX_ENERGY_VALUE, uid=req.uid)
    
    energy_max = int(energy_max)
    energy = currencyManager.get_amount(db, req.uid, 'BREAD')
    
    if energy == None:
        return get_response(code=ResponseCode.RES_NOT_FOUND_USER_BREAD_DATA, uid=req.uid)
    
    if energy >= energy_max:
        return get_response(code=ResponseCode.RES_ALREADY_ENOUGH_ENERGY, uid=req.uid)
    
    time_datas = userdataManager.get(db, req.uid, time_category)
    
    energy_time = get(time_datas, 'lastEnergyTime', None)
    if energy_time == None:
        userdataManager.change_user_data_value(db, req.uid, time_category, 'lastEnergyTime', int(time.time()) + Constant.VALUE_OF_1970)
    
    current_time = int(time.time()) + Constant.VALUE_OF_1970
    
    # 5min
    game_config_dict = await CacheController.game_config_info_map(db)
    game_config_info = get(game_config_dict, req.platform, None)
    if not game_config_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_UP_DATA, uid=req.uid)
    
    term_info = get(game_config_info, Constant.GAME_CONFIG_BREAD_PER_MIN, None)
    if not term_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_GAME_CONFIG_VALUE, uid=req.uid)
    
    term_value = get(term_info, 'value', None)
    if not term_value:
        return get_response(code=ResponseCode.RES_NOT_FOUND_GAME_CONFIG_VALUE, uid=req.uid)
    
    term_value = int(term_value)
    
    five_min = int(term_value) * 60
    between_time = current_time - energy_time
    between_energy = int(between_time / five_min)
    
    if between_energy > 0:
        energy_gap = energy_max - energy
        if energy_gap <= between_energy:
            between_energy = energy_gap
            userdataManager.change_user_data_value(db, req.uid, time_category, 'lastEnergyTime', current_time)
        else:
            userdataManager.change_user_data_value(db, req.uid, time_category, 'lastEnergyTime', time_datas['lastEnergyTime'] + (between_energy * five_min))

        currencyManager.add_dict('BREAD', 0, between_energy)
        if currencyManager.get_rewards():
            currencyManager.get_currency_rewards(db, req.uid)
        data = currencyManager.get_user_currency_data(db, req.uid)
        data['UserData'] = userdataManager.generate_user_save(db, req.uid)
        data['change'] = currencyManager.get_change()
        return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
    else:
        data = currencyManager.get_user_currency_data(db, req.uid)
        data['UserData'] = userdataManager.generate_user_save(db, req.uid)
        return get_response(code=ResponseCode.RES_ENERGY_VALUE_IS_MAX, data=data, uid=req.uid)



#########################################################################################################################################################


async def refresh_pticket(req:CurrencyPVPTicketRefreshReqParam, db:Session):
    time_category = 'Time'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
  
    # 여기서 max 에너지 값을 가지고 오도록 한다.
    # 1인 경우는 pass가 활성화 되어 있는 상태
    game_config_dict = await CacheController.game_config_info_map(db)
    game_config_info = get(game_config_dict, req.platform, None)
    
    if req.id == 1:
        energy_info = get(game_config_info, Constant.GAME_CONFIG_PASS_ENABLE_PTICKET_MAX, None)
    else:
        energy_info = get(game_config_info, Constant.GAME_CONFIG_NORMAL_PTICKET_MAX, None)
    if not energy_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_GAME_CONFIG_VALUE, uid=req.uid)
    
    energy_max = get(energy_info, 'value', None)
    if energy_max == None:
        return get_response(code=ResponseCode.RES_NOT_FOUND_GAME_CONFIG_VALUE, uid=req.uid)
    
    energy_max = int(energy_max)
    
    energy = currencyManager.get_amount(db, req.uid, 'PTICKET')
   
    if energy >= energy_max:
        return get_response(code=ResponseCode.RES_ALREADY_ENOUGH_ENERGY, uid=req.uid)
    
    time_datas = userdataManager.get(db, req.uid, time_category)
    
    energy_time = get(time_datas, 'lastPVPTime', None)
    if energy_time == None :
        userdataManager.change_user_data_value(db, req.uid, time_category, 'lastPVPTime', int(time.time()) + Constant.VALUE_OF_1970)
    
    current_time = int(time.time()) + Constant.VALUE_OF_1970
    
    # 5min
    game_config_dict = await CacheController.game_config_info_map(db)
    game_config_info = get(game_config_dict, req.platform, None)
    if not game_config_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_UP_DATA, uid=req.uid)
    
    term_info = get(game_config_info, Constant.GAME_CONFIG_PTICKET_PER_MIN, None)
    if not term_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_GAME_CONFIG_VALUE, uid=req.uid)
    
    term_value = get(term_info, 'value', None)
    if not term_value:
        return get_response(code=ResponseCode.RES_NOT_FOUND_GAME_CONFIG_VALUE, uid=req.uid)
    
    term_value = int(term_value)
    
    five_min = int(term_value) * 60
    between_time = current_time - energy_time
    between_energy = int(between_time / five_min)
    
    if between_energy > 0:
        energy_gap = energy_max - energy
        if energy_gap <= between_energy:
            between_energy = energy_gap
            userdataManager.change_user_data_value(db, req.uid, time_category, 'lastPVPTime', current_time)
            time_datas['lastPVPTime'] = current_time
        else:
            userdataManager.change_user_data_value(db, req.uid, time_category, 'lastPVPTime', time_datas['lastPVPTime'] + (between_energy * five_min))
            
            
        currencyManager.add_dict('PTICKET', 0, between_energy)
        
        if currencyManager.get_rewards():
            currencyManager.get_currency_rewards(db, req.uid)
        
        data = currencyManager.get_user_currency_data(db, req.uid)
        data['UserData'] = userdataManager.generate_user_save(db, req.uid)
        data['change'] = currencyManager.get_change()
        return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
    else:
        data = currencyManager.get_user_currency_data(db, req.uid)
        data['UserData'] = userdataManager.generate_user_save(db, req.uid)
        return get_response(code=ResponseCode.RES_ENERGY_VALUE_IS_MAX, data=data, uid=req.uid)


#########################################################################################################################################################


async def refresh_daily_buy(req:CurrencyFreeReqParam, db:Session):
    time_category = 'Time'

    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()    

    shop_info_dict = await CacheController.shop_info_map(db)
    shop_info_list = get(shop_info_dict, req.platform, None)
    
    if not shop_info_list:
        return get_response(code=ResponseCode.RES_NOT_FOUND_SHOP_DATA, uid=req.uid)
    
    daily_buy_shop = get(shop_info_list, req.pid, None)
    
    if not daily_buy_shop:
        return get_response(code=ResponseCode.RES_NOT_FOUND_SHOP_INFO_DATA, uid=req.uid)
    
    
    daily_buy_id = None
    daily_buy_limit_count = 0
    
    for daily_buy in daily_buy_shop:
        if daily_buy_id == None:
           daily_buy_id = get(daily_buy, 'id', None)
           daily_buy_limit_count = get(daily_buy, 'limit_count', 0)
        _price_type = get(daily_buy, 'price_type', None)
        _price = get(daily_buy, 'price', None)
        if (_price_type == 'CASH'):
            return get_response(code=ResponseCode.RES_INVALID_DAILY_BUY, uid=req.uid)
        if (_price_type != 'NONE') and (_price_type != 'AD'):
            user_currency = currencyManager.use_currency(db, req.uid, _price_type, int(_price))
            if not user_currency:
                data = currencyManager.get_user_currency_data(db, req.uid)
                return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
            
    time_datas = userdataManager.get(db, req.uid, time_category)
    
    daily_purchases = get(time_datas, 'dailyPurchases', None)
    
    if daily_purchases == None:
        daily_purchases = []
        userdataManager.set_update(time_category)
    
    if daily_buy_id == None:
        return get_response(code=ResponseCode.RES_NOT_FOUND_SHOP_INFO_DATA, uid=req.uid)
    
    if daily_buy_limit_count > 0:
        if daily_purchases.count(daily_buy_id) < daily_buy_limit_count:
            logger.warning(daily_purchases.count(daily_buy_id))
            daily_purchases.append(daily_buy_id)
            time_datas['dailyPurchases'] = daily_purchases
            userdataManager.set_update(time_category)
        else:
            return get_response(code=ResponseCode.RES_ALREADY_REWARDED_DAILY_BUY, uid=req.uid)
    
    
    
    for daily_buy in daily_buy_shop:
        _type = get(daily_buy, 'reward_type', None)
        _amount = get(daily_buy, 'reward_amount', None)
        if (_type != None) and (_amount != None):
            currencyManager.add_dict(_type, 0, _amount)
    
    if currencyManager.get_rewards():
        currencyManager.get_currency_rewards(db, req.uid)
    
    data = currencyManager.get_user_currency_data(db, req.uid)
    data['UserData'] = userdataManager.generate_user_save(db, req.uid)
    data['change'] = currencyManager.get_change()
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)







#########################################################################################################################################################


async def refresh_weekly_buy(req:CurrencyFreeReqParam, db:Session):
    time_category = 'Time'

    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()    

    shop_info_dict = await CacheController.shop_info_map(db)
    shop_info_list = get(shop_info_dict, req.platform, None)
    
    if not shop_info_list:
        return get_response(code=ResponseCode.RES_NOT_FOUND_SHOP_DATA, uid=req.uid)
    
    weekly_buy_shop = get(shop_info_list, req.pid, None)
    
    if not weekly_buy_shop:
        return get_response(code=ResponseCode.RES_NOT_FOUND_SHOP_INFO_DATA, uid=req.uid)
    
    
    weekly_buy_id = None
    weekly_buy_limit_count = 0
    
    for weekly_buy in weekly_buy_shop:
        if weekly_buy_id == None:
           weekly_buy_id = get(weekly_buy, 'id', None)
           weekly_buy_limit_count = get(weekly_buy, 'limit_count', 0)
        _price_type = get(weekly_buy, 'price_type', None)
        _price = get(weekly_buy, 'price', None)
        if (_price_type == 'CASH'):
            return get_response(code=ResponseCode.RES_INVALID_WEEKLY_BUY, uid=req.uid)
        if (_price_type != 'NONE') and (_price_type != 'AD'):
            user_currency = currencyManager.use_currency(db, req.uid, _price_type, int(_price))
            if not user_currency:
                data = currencyManager.get_user_currency_data(db, req.uid)
                return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
            
    time_datas = userdataManager.get(db, req.uid, time_category)
    
    weekly_purchases = get(time_datas, 'weeklyPurchases', None)
    
    if weekly_purchases == None:
        weekly_purchases = []
        userdataManager.set_update(time_category)
    
    if weekly_buy_id == None:
        return get_response(code=ResponseCode.RES_NOT_FOUND_SHOP_INFO_DATA, uid=req.uid)
    
    if weekly_buy_limit_count > 0:
        if weekly_purchases.count(weekly_buy_id) < weekly_buy_limit_count:
            logger.warning(weekly_purchases.count(weekly_buy_id))
            weekly_purchases.append(weekly_buy_id)
            time_datas['weeklyPurchases'] = weekly_purchases
            userdataManager.set_update(time_category)
        else:
            return get_response(code=ResponseCode.RES_ALREADY_REWARDED_WEEKLY_BUY, uid=req.uid)
    
    
    for weekly_buy in weekly_buy_shop:
        _type = get(weekly_buy, 'reward_type', None)
        _amount = get(weekly_buy, 'reward_amount', None)
        if (_type != None) and (_amount != None):
            currencyManager.add_dict(_type, 0, _amount)
    
    if currencyManager.get_rewards():
        currencyManager.get_currency_rewards(db, req.uid)
    
    data = currencyManager.get_user_currency_data(db, req.uid)
    data['UserData'] = userdataManager.generate_user_save(db, req.uid)
    data['change'] = currencyManager.get_change()
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)





#########################################################################################################################################################


async def refresh_monthly_buy(req:CurrencyFreeReqParam, db:Session):
    time_category = 'Time'

    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()    

    shop_info_dict = await CacheController.shop_info_map(db)
    shop_info_list = get(shop_info_dict, req.platform, None)
    
    if not shop_info_list:
        return get_response(code=ResponseCode.RES_NOT_FOUND_SHOP_DATA, uid=req.uid)
    
    monthly_buy_shop = get(shop_info_list, req.pid, None)
    
    if not monthly_buy_shop:
        return get_response(code=ResponseCode.RES_NOT_FOUND_SHOP_INFO_DATA, uid=req.uid)
    
    
    monthly_buy_id = None
    monthly_buy_limit_count = 0
    
    for monthly_buy in monthly_buy_shop:
        if monthly_buy_id == None:
           monthly_buy_id = get(monthly_buy, 'id', None)
           monthly_buy_limit_count = get(monthly_buy, 'limit_count', 0)
        _price_type = get(monthly_buy, 'price_type', None)
        _price = get(monthly_buy, 'price', None)
        if (_price_type == 'CASH'):
            return get_response(code=ResponseCode.RES_INVALID_MONTHLY_BUY, uid=req.uid)
        if (_price_type != 'NONE') and (_price_type != 'AD'):
            user_currency = currencyManager.use_currency(db, req.uid, _price_type, int(_price))
            if not user_currency:
                data = currencyManager.get_user_currency_data(db, req.uid)
                return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
            
    time_datas = userdataManager.get(db, req.uid, time_category)
    
    monthly_purchases = get(time_datas, 'monthlyPurchases', None)
    
    if monthly_purchases == None:
        monthly_purchases = []
        userdataManager.set_update(time_category)
    
    if monthly_buy_id == None:
        return get_response(code=ResponseCode.RES_NOT_FOUND_SHOP_INFO_DATA, uid=req.uid)
    
    if monthly_buy_limit_count > 0:
        if monthly_purchases.count(monthly_buy_id) < monthly_buy_limit_count:
            logger.warning(monthly_purchases.count(monthly_buy_id))
            monthly_purchases.append(monthly_buy_id)
            time_datas['monthlyPurchases'] = monthly_purchases
            userdataManager.set_update(time_category)
        else:
            return get_response(code=ResponseCode.RES_ALREADY_REWARDED_MONTHLY_BUY, uid=req.uid)
    
    
    
    for monthly_buy in monthly_buy_shop:
        _type = get(monthly_buy, 'reward_type', None)
        _amount = get(monthly_buy, 'reward_amount', None)
        if (_type != None) and (_amount != None):
            currencyManager.add_dict(_type, 0, _amount)
    
    if currencyManager.get_rewards():
        currencyManager.get_currency_rewards(db, req.uid)
    
    data = currencyManager.get_user_currency_data(db, req.uid)
    data['UserData'] = userdataManager.generate_user_save(db, req.uid)
    data['change'] = currencyManager.get_change()
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)





#########################################################################################################################################################


async def refresh_special_buy(req:CurrencyFreeReqParam, db:Session):
    time_category = 'Time'

    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()    

    shop_info_dict = await CacheController.shop_info_map(db)
    shop_info_list = get(shop_info_dict, req.platform, None)
    
    if not shop_info_list:
        return get_response(code=ResponseCode.RES_NOT_FOUND_SHOP_DATA, uid=req.uid)
    
    special_buy_shop = get(shop_info_list, req.pid, None)
    
    if not special_buy_shop:
        return get_response(code=ResponseCode.RES_NOT_FOUND_SHOP_INFO_DATA, uid=req.uid)
    
    
    special_buy_id = None
    special_buy_limit_count = 0
    
    for special_buy in special_buy_shop:
        if special_buy_id == None:
           special_buy_id = get(special_buy, 'id', None)
           special_buy_limit_count = get(special_buy, 'limit_count', 0)
        _price_type = get(special_buy, 'price_type', None)
        _price = get(special_buy, 'price', None)
        if (_price_type == 'CASH'):
            return get_response(code=ResponseCode.RES_INVALID_SPECIAL_BUY, uid=req.uid)
        if (_price_type != 'NONE') and (_price_type != 'AD'):
            user_currency = currencyManager.use_currency(db, req.uid, _price_type, int(_price))
            if not user_currency:
                data = currencyManager.get_user_currency_data(db, req.uid)
                return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
            
    time_datas = userdataManager.get(db, req.uid, time_category)
    
    special_purchases = get(time_datas, 'specialPurchases', None)
    
    if special_purchases == None:
        special_purchases = []
        userdataManager.set_update(time_category)
    
    if special_buy_id == None:
        return get_response(code=ResponseCode.RES_NOT_FOUND_SHOP_INFO_DATA, uid=req.uid)
    
    if special_buy_limit_count > 0:
        if special_purchases.count(special_buy_id) < special_buy_limit_count:
            special_purchases.append(special_buy_id)
            time_datas['specialPurchases'] = special_purchases
            userdataManager.set_update(time_category)
        else:
            return get_response(code=ResponseCode.RES_ALREADY_REWARDED_SPECIAL_BUY, uid=req.uid)
    
    
    
    for special_buy in special_buy_shop:
        _type = get(special_buy, 'reward_type', None)
        _amount = get(special_buy, 'reward_amount', None)
        if (_type != None) and (_amount != None):
            currencyManager.add_dict(_type, 0, _amount)
    
    if currencyManager.get_rewards():
        currencyManager.get_currency_rewards(db, req.uid)
    
    data = currencyManager.get_user_currency_data(db, req.uid)
    data['UserData'] = userdataManager.generate_user_save(db, req.uid)
    data['change'] = currencyManager.get_change()
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)




#########################################################################################################################################################






async def refresh_reset_daily(req:BaseReqParam, db:Session):
    time_category = 'Time'
    user_category = 'User'
    quest_category = 'Quest'
    pvp_category = 'PVP'
    stage_category = 'Stage'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    time_datas = userdataManager.get(db, req.uid, time_category)
    
    now = datetime.now()
    today = int(now.strftime('%Y%m%d'))
    
    is_weekly = False
    is_monthly = False
    
    if time_datas['timeLastDay'] == today:
        return get_response(code=ResponseCode.RES_ALREADY_DAILY_RESET_FINISHED, uid=req.uid)
    
    last_day = None
    if time_datas['timeLastDay']:
        last_day = datetime.strptime(str(time_datas['timeLastDay']), '%Y%m%d')
    
    if last_day != None:
        if now.isocalendar()[1] != last_day.isocalendar()[1]:
            is_weekly = True
        else:
            if int(now.strftime('%Y')) != int(now.strftime('%Y')):
                is_weekly = True
                
        this_month = int(now.strftime('%Y%m'))
        last_month = int(last_day.strftime('%Y%m'))
        
        if last_month != this_month:
            is_monthly = True
    
    if not get(time_datas, 'attAccLogin', None):
        time_datas['attAccLogin'] = 1
    else:
        time_datas['attAccLogin'] = time_datas['attAccLogin'] + 1
    
    time_datas['lastLogout'] = time_datas['timeLastDay']
    time_datas['timeLastDay'] = today
    time_datas['freeJewel'] = False
    time_datas['accLogin'] = time_datas['accLogin'] + 1
    time_datas['dailyPurchases'] = []
    # temp
    time_datas['breadFreeC'] = 0
    time_datas['breadJewelC'] = 0
    time_datas['accWallC'] = 0
    
    if is_weekly:
        time_datas['weeklyPurchases'] = []
    
    if is_monthly:
        time_datas['monthlyPurchases'] = []
    
    userdataManager.set_update(time_category)
    
    
    pvp_datas = userdataManager.get(db, req.uid, pvp_category)
    
    if pvp_datas:
        pvp_datas['IsDailyReward'] = False
    
    userdataManager.set_update(pvp_category)
    
    user_datas = userdataManager.get(db, req.uid, user_category)
    
    user_datas['DailyHomeShopCount'] = 0
    user_datas['DailyPvpMatchCount'] = 0
    user_datas['DailyPvpShopCount'] = 0

    userdataManager.set_update(user_category)
    
    
    quest_info_dict = await CacheController.quest_info_map(db)
    quest_info_list = get(quest_info_dict, req.platform, None)
    if not quest_info_list:
        return get_response(code=ResponseCode.RES_NOT_FOUND_QUEST_DATA, data=data, uid=req.uid)
    
    check_daily_quest_ids = []
    check_weekly_quest_ids = []
    for quest_info in quest_info_list:
        if quest_info_list[quest_info]['term'] == 'DAILY':
            check_daily_quest_ids.append(quest_info_list[quest_info]['id'])
        if is_weekly:
            if quest_info_list[quest_info]['term'] == 'WEEKLY':
                check_weekly_quest_ids.append(quest_info_list[quest_info]['id'])
        else:continue
    
    quest_datas = userdataManager.get(db, req.uid, quest_category)
    
    for quest in quest_datas:
        if quest['id'] in check_daily_quest_ids:
            quest['cur'] = 0
            quest['rewarded'] = False
            quest['rewardedAd'] = False
        # 오늘은 월요인 인경우에는 주간 랭킹도 삭제한다.
        if is_weekly:
            if quest['id'] in check_weekly_quest_ids:
                quest['cur'] = 0
                quest['rewarded'] = False
                quest['rewardedAd'] = False
    
    userdataManager.set_update(quest_category)
    
    stage_datas = userdataManager.get(db, req.uid, stage_category)
    
    for stage in stage_datas:
        stage['pCount'] = 0
        stage['phCount'] = 0
    
    userdataManager.set_update(stage_category)
    
    # daily reset
    if os.environ.get('PRODUCTION') == 'prod':
        user_currencys = crud_user_currency.get_user_currency_all(db, req.uid)
        for user_currency in user_currencys:
            if user_currency.type == 'BREAD':
                if user_currency.amount > 15000:
                    logger.warning(str(req.uid) + ' : ' + str(user_currency.type) + ' is invalid = ' + str(user_currency.amount))
            elif user_currency.type == 'COIN':
                if user_currency.amount > 10000000:
                    logger.warning(str(req.uid) + ' : ' + str(user_currency.type) + ' is invalid = ' + str(user_currency.amount))
            elif user_currency.type == 'JEWEL':
                if user_currency.amount > 100000:
                    logger.warning(str(req.uid) + ' : ' + str(user_currency.type) + ' is invalid = ' + str(user_currency.amount))
            elif user_currency.type == 'RANDOM_KNIGHT':
                if user_currency.amount > 200:
                    logger.warning(str(req.uid) + ' : ' + str(user_currency.type) + ' is invalid = ' + str(user_currency.amount))
            elif user_currency.type == 'RANDOM_WEAPON':
                if user_currency.amount > 200:
                    logger.warning(str(req.uid) + ' : ' + str(user_currency.type) + ' is invalid = ' + str(user_currency.amount))
            elif user_currency.type == 'BUILDING_SUPPLIES':
                if user_currency.amount > 200:
                    logger.warning(str(req.uid) + ' : ' + str(user_currency.type) + ' is invalid = ' + str(user_currency.amount))
            
            crud_user_currency_log.insert(db, req.uid, user_currency.type, user_currency.amount, user_currency.daily_get, user_currency.daily_use, user_currency.total_get, user_currency.total_use)
    
    ## 일일 초기화 작업을 처리하도록 한다.
    crud_user_currency.reset_user_daily_currency(db, req.uid)
    
    data = currencyManager.get_user_currency_data(db, req.uid)
    data['UserData'] = userdataManager.generate_user_save(db, req.uid)
    data['change'] = currencyManager.get_change()
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
    




#########################################################################################################################################################

