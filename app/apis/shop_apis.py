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



async def shop_refresh_homeshop(req:CurrencyHomeShopRefreshReqParam, db:Session):
    homeshop_category = 'HomeShop'
    user_category = 'User'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
  
    user_datas = userdataManager.get(db, req.uid, user_category)
    

    count = user_datas['DailyHomeShopCount']
    
    count_refresh_dict = await CacheController.count_refresh_info_map(db)
    count_refresh_info = get(count_refresh_dict, req.platform, None)
    if not count_refresh_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_COUNT_REFRESH_DATA, uid=req.uid)
    
    count_refresh_value = get(count_refresh_info, '3', None)
    free_count = get(count_refresh_value, 'free_count', None)

    homeshop_datas = userdataManager.get(db, req.uid, homeshop_category)
        
    
    # 무료로 업데이트 하도록 한다.
    if not homeshop_datas['HomeShopItemDatas']:
        homeshop_datas['HomeShopItemDatas'] = await __generate_home_shop(db, req.level, req.platform, True)
        userdataManager.set_update(homeshop_category)
        data = currencyManager.get_user_currency_data(db, req.uid)
        data['UserData'] = userdataManager.generate_user_save(db, req.uid)
        data['change'] = currencyManager.get_change()
        return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
    elif (free_count != None) and (free_count <= count):
        price_type = get(count_refresh_value, 'price_type', None)
        start_cost = get(count_refresh_value, 'start_cost', None)
        inc_cost =get(count_refresh_value, 'inc_cost', None)
        amount = start_cost + (inc_cost *(count - free_count))
        result = currencyManager.use_currency(db, req.uid, price_type, amount)
        if not result:
            return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, uid=req.uid)
        
        homeshop_datas['HomeShopItemDatas'] = await __generate_home_shop(db, req.level, req.platform, False)
        userdataManager.set_update(homeshop_category)
        
    elif (free_count != None) and (free_count > count):
        homeshop_datas['HomeShopItemDatas'] = await __generate_home_shop(db, req.level, req.platform, False)
        userdataManager.set_update(homeshop_category)
    else:
        return get_response(code=ResponseCode.RES_NOT_FOUND_USER_HOMESHOP_DATA, uid=req.uid)
    
    userdataManager.add_user_data_value(db, req.uid, user_category, 'DailyHomeShopCount', 1)
        
    data = currencyManager.get_user_currency_data(db, req.uid)
    data['UserData'] = userdataManager.generate_user_save(db, req.uid)
    data['change'] = currencyManager.get_change()
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
    
        
async def __generate_home_shop(db:Session, level:int, platform:str, is_first:False):
    
    homeshop_dict = await CacheController.homeshop_info_map(db)
    homeshop_info = get(homeshop_dict, platform)
    if not homeshop_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_HOMESHOP_DATA)
    
    home_content_dict = await CacheController.home_contents_lv_info_map(db)
    home_content_info = get(home_content_dict, platform, None)
    if not home_content_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_HOMESHOP_CONTENT_DATA)
    
    info = get(home_content_info, 'STORE', None)
    if not info:
        return

    find_home_content = None
    for home_content in info:
        if home_content['lv'] == level:
            find_home_content = home_content
            break
        
    if not find_home_content:
        return
    
    grade_1 = get(home_content, 'grade_1', None)
    grade_2 = get(home_content, 'grade_2', None)
    grade_3 = get(home_content, 'grade_3', None)
    grade_4 = get(home_content, 'grade_4', None)
    
    total_prob = grade_1 + grade_2 + grade_3 + grade_4
    
    homeshop_list = []
    first_jewel = is_first
    for i in range(0, 8):
        if first_jewel:
            homeshop_list.append({"ID":1,"IsPurchased":False})
            first_jewel = False
            continue
            
        random_probs = random.randint(0, total_prob-1)
        if random_probs - grade_1 <= 0:
            homeshop_value = get(homeshop_info, '1', None)
            if homeshop_value:
                total_value = 0
                for value in homeshop_value:
                    total_value += value['weight']
                
                item_random_probs = random.randint(0, total_value-1)
                
                for value in homeshop_value:
                    if (item_random_probs - value['weight']) <= 0:
                        homeshop_list.append({"ID":value['id'],"IsPurchased":False})
                        break
                    else: item_random_probs = item_random_probs - value['weight']
                continue
                    
        else:
            random_probs = random_probs - grade_1
            
        if random_probs - grade_2 <= 0:
            homeshop_value = get(homeshop_info, '2', None)
            if homeshop_value:
                total_value = 0
                for value in homeshop_value:
                    total_value += value['weight']
                    
                item_random_probs = random.randint(0, total_value-1)
                
                for value in homeshop_value:
                    if (item_random_probs - value['weight']) <= 0:
                        homeshop_list.append({"ID":value['id'],"IsPurchased":False})
                        break
                    else: item_random_probs = item_random_probs - value['weight']
                continue
        else:
            random_probs = random_probs - grade_2
            
        if random_probs - grade_3 <= 0:
            homeshop_value = get(homeshop_info, '3', None)
            if homeshop_value:
                total_value = 0
                for value in homeshop_value:
                    total_value += value['weight']
                
                item_random_probs = random.randint(0, total_value-1)
                
                for value in homeshop_value:
                    if (item_random_probs - value['weight']) <= 0:
                        homeshop_list.append({"ID":value['id'],"IsPurchased":False})
                        break
                    else: item_random_probs = item_random_probs - value['weight']
                continue
        else:
            random_probs = random_probs - grade_3
            
        if random_probs - grade_4 <= 0:
            homeshop_value = get(homeshop_info, '4', None)
            if homeshop_value:
                total_value = 0
                for value in homeshop_value:
                    total_value += value['weight']
                
                item_random_probs = random.randint(0, total_value-1)
                
                for value in homeshop_value:
                    if (item_random_probs - value['weight']) <= 0:
                        homeshop_list.append({"ID":value['id'],"IsPurchased":False})
                        break
                    else: item_random_probs = item_random_probs - value['weight']
                continue
        else:
            # 에러 확인이 안된다.
            return get_response(code=ResponseCode.RES_NOT_FOUND_HOMESHOP_RANDOM_DATA)
    
    return homeshop_list
    
    
    
    

#########################################################################################################################################################



async def shop_buy_homeshop(req:CurrencyHomeShopBuyReqParam, db:Session):
    hoemshop_category = 'HomeShop'
    character_category = 'Character'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    homeshop_dict = await CacheController.homeshop_info_by_id_map(db)
    homeshop_info = get(homeshop_dict, req.platform)
    if not homeshop_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_HOMESHOP_DATA, uid=req.uid)
    
    info = get(homeshop_info, str(req.id))
    if not info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_HOMESHOP_CONTENT_DATA, uid=req.uid)
    
    homeshop_datas = userdataManager.get(db, req.uid, hoemshop_category)
    
    homeshop_item_datas = homeshop_datas['HomeShopItemDatas']
    if homeshop_item_datas == None:
        return
    
    find_homeshop_item = homeshop_item_datas[req.extra_value]
    if find_homeshop_item['ID'] != req.id:
        pass
        
    if find_homeshop_item['IsPurchased'] == False:
        price_type = get(info, 'price_type', None)
        price_amount = get(info, 'price', None)
        
        character_datas = None
        
        if (price_type != None) and (price_amount != None):
            if (price_type != 'AD'):
                user_currency = currencyManager.use_currency(db, req.uid, price_type, price_amount)
                if not user_currency:
                    data = currencyManager.get_user_currency_data(db, req.uid)
                    return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
            
            reward_type = get(info, 'reward_type', None)
            reward_amount = get(info, 'reward_count', None)
            if (reward_type != None) and (reward_amount != None):
                if reward_type == 'KNIGHT_PIECE':
                    reward_key = get(info, 'reward_key', None)
                    character_datas = userdataManager.get(db, req.uid, character_category)
                    character_datas = currencyManager.add_character_piece(reward_type, reward_key, reward_amount, character_datas)
                    userdataManager.set_update(character_category)
                else:
                    currencyManager.add_dict(reward_type, 0, reward_amount)
                    
                if currencyManager.get_rewards():
                    currencyManager.get_currency_rewards(db, req.uid)
                        
            find_homeshop_item['IsPurchased'] = True
            userdataManager.set_update(hoemshop_category)
            
            data = currencyManager.get_user_currency_data(db, req.uid)
            data['UserData'] = userdataManager.generate_user_save(db, req.uid)
            data['change'] = currencyManager.get_change()
            return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
            
    else:
        # 이미 결재된 상품 입니다.
        pass
            
        
    
    

#########################################################################################################################################################





async def shop_refresh_pvpshop(req:CurrencyPvpShopRefreshReqParam, db:Session):
    pvp_category = 'PVP'
    user_category = 'User'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()

    homeshop_dict = await CacheController.homeshop_info_map(db)
    homeshop_info = get(homeshop_dict, req.platform)
    if not homeshop_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_UP_DATA, uid=req.uid)
    
    user_datas = userdataManager.get(db, req.uid, user_category)
        
    count = user_datas['DailyHomeShopCount']
    
    count_refresh_dict = await CacheController.count_refresh_info_map(db)
    count_refresh_info = get(count_refresh_dict, req.platform, None)
    if not count_refresh_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_UP_DATA, uid=req.uid)
    
    count_refresh_value = get(count_refresh_info, '3', None)
    free_count = get(count_refresh_value, 'free_count', None)
    if (free_count != None) and (free_count <= count) and home_shop_item_datas:
        price_type = get(count_refresh_value, 'free_count', None)
        start_cost = get(count_refresh_value, 'start_cost', None)
        inc_cost =get(count_refresh_value, 'inc_cost', None)
        amount = start_cost + (inc_cost *(count - free_count))
        user_currency = currencyManager.use_currency(db, req.uid, price_type, amount)
        if not user_currency:
            data = currencyManager.get_user_currency_data(db, req.uid)
            return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
    elif (free_count != None):
        pass
    
    
    if not home_shop_item_datas:
        user_datas['DailyHomeShopCount'] = user_datas['DailyHomeShopCount'] + 1
    
    homeshop_datas = userdataManager.get(db, req.uid, pvp_category)
    home_shop_item_datas = homeshop_datas['HomeShopItemDatas']
    
    pvpshop_dict = await CacheController.pvpshop_info_map(db)
    pvpshop_info = get(pvpshop_dict, req.platform, None)
    
    data_type = {"ID":0,"IsPurchased":False}
    if not home_shop_item_datas:
        # 무료 refresh 처리하도록 수정함.

        pass
    else:
        # 돈내고 해라
        pass
    


async def __generate_pvp_shop(db:Session, level:int, platform:str):
    
    pass



#########################################################################################################################################################



async def shop_buy_pvpshop(req:CurrencyPvpShopBuyReqParam, db:Session):
    pvp_category = 'PVP'
    character_category = 'Character'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    pvpshop_dict = await CacheController.pvpshop_info_map(db)
    pvpshop_info = get(pvpshop_dict, req.platform)
    if not pvpshop_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_UP_DATA, uid=req.uid)
    
    info = get(pvpshop_info, str(req.id))
    if not info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_STAGE_DATA, uid=req.uid)
    
    pvpshop_datas = userdataManager.get(db, req.uid, pvp_category)
    
    pvpshop_item_datas = pvpshop_datas['pvpShopDatas']
    if pvpshop_item_datas == None:
        return
    
    find_pvpshop_item = pvpshop_item_datas[req.index]
    if find_pvpshop_item['id'] != req.id:
        pass
        
    if find_pvpshop_item['IsPurchased'] == False:
        price_type = get(info, 'price_type', None)
        price_amount = get(info, 'price', None)
        
        character_datas = None
        
        if (price_type != None) and (price_amount != None):
            if (price_type != 'AD'):
                user_currency = currencyManager.use_currency(db, req.uid, price_type, price_amount)
                if not user_currency:
                    data = currencyManager.get_user_currency_data(db, req.uid)
                    return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
            
            reward_type = get(info, 'reward_type', None)
            reward_amount = get(info, 'reward_count', None)
            if (reward_type != None) and (reward_amount != None):
                if reward_type == 'KNIGHT_PIECE':
                    reward_key = get(info, 'reward_key', None)
                    character_datas = userdataManager.get(db, req.uid, character_category)
                    character_datas = currencyManager.add_character_piece(reward_type, reward_key, reward_amount, character_datas)
                    userdataManager.set_update(character_category)
                else:
                    currencyManager.add_dict(reward_type, 0, reward_amount)
                    
                if currencyManager.get_rewards():
                    currencyManager.get_currency_rewards(db, req.uid)
            
            find_pvpshop_item['IsPurchased'] = True
            userdataManager.set_update(pvp_category)
            
            data = currencyManager.get_user_currency_data(db, req.uid)
            data['UserData'] = userdataManager.generate_user_save(db, req.uid)
            data['change'] = currencyManager.get_change()
            return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)

    else:
        # 이미 결재된 상품 입니다.
        pass
            
        
    
    

#########################################################################################################################################################






async def shop_refresh_expedition(req:ExpiditionShopRefreshReqParam, db:Session):
    expedition_category = 'Expedition'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()

    expedition_shop_dict = await CacheController.expedition_shop_info_map(db)
    expedition_shop_info = get(expedition_shop_dict, req.platform)
    if not expedition_shop_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_UP_DATA, uid=req.uid)
    
    expedition_datas = userdataManager.get(db, req.uid, expedition_category)

    expedition_shop_datas = get(expedition_datas, 'ExpeditionShopDatas', [])

    expedition_shop_list = []
    if not expedition_shop_datas:
        for value in expedition_shop_info.values():
            expedition_shop_list.append({"ID":value['id'],"count":0})
            
        expedition_datas['ExpeditionShopDatas'] = expedition_shop_list
        # 종료시간을 추가해야 함.
        userdataManager.set_update(expedition_category)
    else:
        # 시간 체크를 하는 로직이 필요함.
        expedition_shop_time = get(expedition_datas, 'ExpeditionShopTime', None)
        # 시간이 지났는지 확인해서 지났으면 업데이트 해줌
        for value in expedition_shop_info.values():
            expedition_shop_list.append({"ID":value['id'],"count":0})
        userdataManager.change_user_data_value(db, req.uid, expedition_category, 'ExpeditionShopTime', (int(time.time()) + Constant.VALUE_OF_1970))
        
    data = currencyManager.get_user_currency_data(db, req.uid)
    data['UserData'] = userdataManager.generate_user_save(db, req.uid)
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)



#########################################################################################################################################################



async def shop_buy_expedition(req:ExpiditionShopBuyReqParam, db:Session):
    character_category = 'Character'
    rune_category = 'Rune'
    expedition_category = 'Expedition'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    expedition_shop_dict = await CacheController.expedition_shop_info_map(db)
    expedition_shop_info = get(expedition_shop_dict, req.platform)
    if not expedition_shop_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_EXPEDITION_DATA, uid=req.uid)
    
    info = get(expedition_shop_info, str(req.id))
    if not info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_EXPEDITION_INFO_DATA, uid=req.uid)
    
    expidition_datas = userdataManager.get(db, req.uid, expedition_category)
    
    expidition_item_datas = expidition_datas['ExpeditionShopDatas']
    if expidition_item_datas == None:
        return get_response(code=ResponseCode.RES_NOT_FOUND_EXPEDITION_SHOP_DATA, uid=req.uid)
    
    
    find_shop_item = expidition_item_datas[req.index]
    if find_shop_item['ID'] != req.id:
        return get_response(code=ResponseCode.RES_NOT_FOUND_EXPEDITION_INVALID_ID_DATA, uid=req.uid)
    
    count = find_shop_item['count']
    limit_count = info['limit_count']
    
    if count < limit_count:
        price_type = get(info, 'price_type', None)
        price_amount = get(info, 'price', None)
        
        character_datas = None
        rune_datas = userdataManager.get(db, req.uid, rune_category)
        
        if (price_type != None) and (price_amount != None):
            if (price_type != 'AD'):
                user_currency = currencyManager.use_currency(db, req.uid, price_type, price_amount)
                if not user_currency:
                    data = currencyManager.get_user_currency_data(db, req.uid)
                    return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
            
            reward_type = get(info, 'reward_type', None)
            reward_amount = get(info, 'reward_count', None)
            if (reward_type != None) and (reward_amount != None):
                if reward_type == 'KNIGHT_PIECE':
                    reward_key = get(info, 'reward_key', None)
                    character_datas = userdataManager.get(db, req.uid, character_category)
                    character_datas = currencyManager.add_character_piece(reward_type, reward_key, reward_amount, character_datas)
                    userdataManager.set_update(character_category)
                elif reward_type == 'RANDOM_RUNE':
                    random_rune_dict = await CacheController.expedition_shop_info_map(db)
                    random_rune_list = get(random_rune_dict, req.platform)
                    select_rune = currencyManager.get_random_rune_by_data(random_rune_list)
                    rune_datas = currencyManager.add_rune('RUNE', select_rune['id'], 1, rune_datas)
                    userdataManager.set_update(rune_category)
                else:
                    currencyManager.add_dict(reward_type, 0, reward_amount)
                    
                if currencyManager.get_rewards():
                    currencyManager.get_currency_rewards(db, req.uid)
            
            find_shop_item['count'] = find_shop_item['count'] + 1
            userdataManager.set_update(expedition_category)
            
            data = currencyManager.get_user_currency_data(db, req.uid)
            data['UserData'] = userdataManager.generate_user_save(db, req.uid)
            data['change'] = currencyManager.get_change()
            return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
    else:
        return get_response(code=ResponseCode.RES_CAN_NOT_BUY_SHOP_ITEM, uid=req.uid)
    

#########################################################################################################################################################



