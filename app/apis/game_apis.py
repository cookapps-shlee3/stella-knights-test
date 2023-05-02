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
from app.classes.CurrencyManager import CurrencyManager
from app.classes.UserDataManager import UserDataManager


## Set Timezone
os.environ['TZ'] = 'UTC'

#########################################################################################################################################################



#스테이지 클리어
async def game_stage_clear(req:CurrencyClearReqParam, db:Session):
    stage_category = 'Stage'        
    user_category = 'User'
    rune_category = 'Rune'
    quest_category = 'Quest'
    character_category = 'Character'
    time_category = 'Time'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    
    stage_tile_dict = await CacheController.stage_tile_info_map(db)
    stage_tile_info = get(stage_tile_dict, req.platform)
    if not stage_tile_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_STAGE_TILE_DATA, uid=req.uid)
    
    info = get(stage_tile_info, str(req.id))
    if not info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_STAGE_TILE_INFO_DATA, uid=req.uid)
    
    stage_dict = await CacheController.stage_info_map(db)
    stage_info = get(stage_dict, req.platform)
    if not stage_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_STAGE_INFO_DATA, uid=req.uid)
    
    chest_dict = await CacheController.chest_info_map(db)
    chest_info = get(chest_dict, req.platform)
    if not chest_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHEST_INFO_DATA, uid=req.uid)
    
    tile_type = get(info, 'tile_type', None)
    if (not tile_type) or (tile_type == 'OBSTACLE'):
        return get_response(code=ResponseCode.RES_NOT_FOUND_STAGE_TILE_TYPE_DATA, uid=req.uid)
            
    stage_datas = userdataManager.get(db, req.uid, stage_category)
    
    current_data = None
    
    for stage_data in stage_datas:
        if stage_data['ID'] == req.id:
            current_data = stage_data
            break
    
    if not current_data:
        return get_response(code=ResponseCode.RES_NOT_FOUND_USER_STAGE_DATA, uid=req.uid)    
    
    if (req.extra_value) > 3 or (req.extra_value <= 0):
        return get_response(code=ResponseCode.RES_STAGE_STAR_INVALID_VALUE, uid=req.uid)
    
    if info['tile_type'] == 'CHEST':
        # 하드모드다~
        if req.extra_value_2nd == 1:
            # 이미 열었답니다.
            if current_data['hStar'] == Constant.STAGE_MAX_STAR:
                return get_response(code=ResponseCode.RES_ALREADY_OPEN_CHEST_BOX, uid=req.uid)
            
            current_data['hStar'] = Constant.STAGE_MAX_STAR
            userdataManager.set_update(stage_category)
            
            # 보상 지급 대신 별 갯수별 보상 지급은 취소
            chest_rewards = get(chest_info, str(info['tile_key']))
            if not chest_rewards:
                return get_response(code=ResponseCode.RES_NOT_FOUND_HARD_CHEST_REWARD_DATA, uid=req.uid)
            
            for reward in chest_rewards:
                _type = get(reward, 'type', None)
                currencyManager.add_dict(_type, 0, get(reward, 'value', 0))
            
            
            if currencyManager.get_rewards():
                currencyManager.get_currency_rewards(db, req.uid)
                userdataManager.add_user_data_value(db, req.uid, user_category, 'BestStageHardTileKey', 1)
                data = currencyManager.get_user_currency_data(db, req.uid)
                data['UserData'] = userdataManager.generate_user_save(db, req.uid)
                data['change'] = currencyManager.get_change()
                return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
            else:
                data = currencyManager.get_user_currency_data(db, req.uid)
                return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
            
            
        else:
            # 이미 열었답니다.
            if current_data['Star'] == Constant.STAGE_MAX_STAR:
                return get_response(code=ResponseCode.RES_ALREADY_OPEN_CHEST_BOX, uid=req.uid)
            
            current_data['Star'] = Constant.STAGE_MAX_STAR
            userdataManager.set_update(stage_category)
            
            # 보상 지급 대신 별 갯수별 보상 지급은 취소
            chest_rewards = get(chest_info, str(info['tile_key']))
            if not chest_rewards:
                return get_response(code=ResponseCode.RES_NOT_FOUND_CHEST_REWARD_DATA, uid=req.uid)
            
            
            for reward in chest_rewards:
                _type = get(reward, 'type', None)
                currencyManager.add_dict(_type, 0, get(reward, 'value', 0))
            
            if currencyManager.get_rewards():
                userdataManager.add_user_data_value(db, req.uid, user_category, 'BestStageTileKey', 1)
                
                currencyManager.get_currency_rewards(db, req.uid)
                data = currencyManager.get_user_currency_data(db, req.uid)
                data['UserData'] = userdataManager.generate_user_save(db, req.uid)
                data['change'] = currencyManager.get_change()
                return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
            else:
                data = currencyManager.get_user_currency_data(db, req.uid)
                return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)

    else:
        
        stage_detail_info = get(stage_info, str(info['tile_key']))
        if not stage_detail_info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_STAGE_TILE_DATA, uid=req.uid)

        if req.extra_value_2nd == 1:
            amount = get(stage_detail_info, 'cost_hard', None)
        elif req.extra_value_2nd == 0:
            amount = get(stage_detail_info, 'cost', None)
        else:
            return get_response(code=ResponseCode.RES_INVALID_GAME_START_PARAM, uid=req.uid)
        
        if amount == None:
            return get_response(code=ResponseCode.RES_NOT_FOUNG_GAME_START_COST, uid=req.uid)
        
        
        ## 우선 사용자 던전키를 깐다
        user_level_dict = await CacheController.level_up_info_map(db)
        user_level_info = get(user_level_dict, req.platform, None)
        if not user_level_info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_UP_DATA, uid=req.uid)
        
        level_info = get(user_level_info, str(req.level), None)
        if not level_info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_UP_INFO_DATA, uid=req.uid)

        energy_max = get(level_info, 'bread_max', None)
        if energy_max == None:
            return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_MAX_BREAD_DATA, uid=req.uid)
        
        energy_max = int(energy_max)
        
        energy = currencyManager.get_amount(db, req.uid, 'BREAD')

        
        time_datas = userdataManager.get(db, req.uid, time_category)
        if ((energy - amount) < energy_max) and (energy >= energy_max):
            userdataManager.change_user_data_value(db, req.uid, time_category, 'lastEnergyTime', int(time.time()) + Constant.VALUE_OF_1970)
        elif ((energy - amount) >= energy_max) and (energy >= energy_max):
            userdataManager.change_user_data_value(db, req.uid, time_category, 'lastEnergyTime', int(time.time()) + Constant.VALUE_OF_1970)
        elif (energy - amount) < 0:
            return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)

        user_currency = currencyManager.use_currency(db, req.uid, 'BREAD', amount)
        if not user_currency:
            data = currencyManager.get_user_currency_data(db, req.uid)
            return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
       
        
        if req.extra_value_2nd == 1:
            
            user_datas = None
            
            if (current_data['hStar'] == 0) and (req.extra_value > 0):
                user_datas = userdataManager.add_user_data_value(db, req.uid, user_category, 'BestStageHardTileKey', 1)
            
            can_reward = False
            
            # 현재 보유 별수와 입력으로 들어온 별의 수를 비교하여 첫 별 보상 수령을 지급하도록 수정함.
            if (current_data['hStar'] < Constant.STAGE_MAX_STAR) and (current_data['hStar'] < req.extra_value) :
                currencyManager.star_reward(db, req.uid, current_data['hStar'], req.extra_value, stage_detail_info)
                current_data['hStar'] = req.extra_value
                userdataManager.set_update(stage_category)
                can_reward = True
            
            hard_chest_id = get(stage_detail_info, 'hard_chest_id', None)
            if not hard_chest_id:
                return get_response(code=ResponseCode.RES_NOT_FOUND_HARD_CHEST_DATA, uid=req.uid)

            chest_rewards = get(chest_info, str(hard_chest_id), None)
            if not chest_rewards:
                return get_response(code=ResponseCode.RES_NOT_FOUND_HARD_CHEST_REWARD_DATA, uid=req.uid)
            
            rune_datas = userdataManager.get(db, req.uid, rune_category)
            total_prob = 10000
            
            for reward in chest_rewards:
                _type = get(reward, 'type', None)
                _key = get(reward, 'key', 0)
                _value = get(reward, 'value', None)
                _rate =  get(reward, 'rate', 0)
                if _type == 'RUNE':
                    if (can_reward) :
                        prob = int(_rate * total_prob)
                        item_random_probs = random.randint(0, total_prob-1)
                        
                        if (item_random_probs - prob) <= 0:
                            # currencyManager.add_random_rune(_type, _key, _value, _rate)
                            rune_datas = userdataManager.get(db, req.uid, rune_category)
                            rune_datas = currencyManager.add_rune(_type, _key, _value, rune_datas)
                            userdataManager.set_update(rune_category)
                elif _type == 'KNIGHT_PIECE':
                    if (can_reward) :
                        currencyManager.add_random_character_piece(_type, _key, _value, _rate)
                else:
                    currencyManager.add_dict(_type, _key, _value)

            if currencyManager.get_rewards():
                
                # if currencyManager.get_random_rune_list():
                #     add_rune = currencyManager.get_random_rune()
                    
                #     if add_rune:
                #         rune_datas = userdataManager.get(db, req.uid, rune_category)
                #         rune_datas = currencyManager.add_rune(add_rune['reward_type'], add_rune['reward_key'], add_rune['reward_amount'], rune_datas)
                #         userdataManager.set_update(rune_category)
                
                if currencyManager.get_random_character_piece_list():
                    add_character_piece =  currencyManager.get_random_character_piece()
                    
                    if add_character_piece:
                        character_datas = userdataManager.get(db, req.uid, character_category)
                        character_datas = currencyManager.add_character_piece(add_character_piece['reward_type'], add_character_piece['reward_key'], add_character_piece['reward_amount'], character_datas)
                        userdataManager.set_update(character_category)

                quest_info_dict = await CacheController.quest_info_map(db)
                quest_info_map = get(quest_info_dict, req.platform, None)
                if not quest_info_map:
                    return get_response(code=ResponseCode.RES_NOT_FOUND_QUEST_DATA, data=data, uid=req.uid)
                
                check_quest_ids = []
                for quest_info in quest_info_map:
                    if quest_info_map[quest_info]['qid'] == 'STAGE_CLEAR':
                        check_quest_ids.append(quest_info_map[quest_info]['id'])
                    else:continue
                
                quest_datas = userdataManager.get(db, req.uid, quest_category)
                
                for quest in quest_datas:
                    if quest['id'] in check_quest_ids:
                        quest_info = quest_info_map[str(quest['id'])]
                        if quest_info['value'] > quest['cur']:
                            quest['cur'] = quest['cur'] + 1
                            userdataManager.set_update(quest_category)
                        
                        # if quest['cur'] >= quest_info['value']:
                        #     quest['rewarded'] = True
                        #     userdataManager.set_update(quest_category)
                
                
                if req.extra_value_3rd != 0:
                    user_datas = userdataManager.get(db, req.uid, user_category)
                        
                    if user_datas['GuideMission']['id'] == req.extra_value_3rd:
                        user_datas['GuideMission']['c'] = 1
                        user_datas['GuideMission']['d'] = True
                        userdataManager.set_update(user_category)
                        
                if currencyManager.get_rewards():
                    currencyManager.get_currency_rewards(db, req.uid)
                    
                data = currencyManager.get_user_currency_data(db, req.uid)
                data['UserData'] = userdataManager.generate_user_save(db, req.uid)
                data['change'] = currencyManager.get_change()
                return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
            else:
                data = currencyManager.get_user_currency_data(db, req.uid)
                return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
        else:
            if (current_data['Star'] == 0) and (req.extra_value > 0):
                user_datas = userdataManager.add_user_data_value(db, req.uid, user_category, 'BestStageTileKey', 1)
            
            can_reward = False
            
            if (current_data['Star'] < Constant.STAGE_MAX_STAR) and (current_data['Star'] < req.extra_value) :
                currencyManager.star_reward(db, req.uid, current_data['Star'], req.extra_value, stage_detail_info)
                current_data['Star'] = req.extra_value
                userdataManager.set_update(stage_category)
                can_reward = True
            
            # 보상 지급 대신 별 갯수별 보상 지급은 취소
            chest_id = get(stage_detail_info, 'chest_id', None)
            if not chest_id:
                return get_response(code=ResponseCode.RES_NOT_FOUND_CHEST_DATA, uid=req.uid)
            
            chest_rewards = get(chest_info, str(chest_id), None)
            if not chest_rewards:
                return get_response(code=ResponseCode.RES_NOT_FOUND_CHEST_REWARD_DATA, uid=req.uid)
            
            rune_datas = userdataManager.get(db, req.uid, rune_category)
            total_prob = 10000
            
            for reward in chest_rewards:
                _type = get(reward, 'type', None)
                _key = get(reward, 'key', 0)
                _value = get(reward, 'value', None)
                _rate =  get(reward, 'rate', 0)
                if _type == 'RUNE':
                    if (can_reward) :
                        prob = int(_rate * total_prob)
                        item_random_probs = random.randint(0, total_prob-1)
                        
                        if (item_random_probs - prob) <= 0:
                            # currencyManager.add_random_rune(_type, _key, _value, _rate)
                            rune_datas = userdataManager.get(db, req.uid, rune_category)
                            rune_datas = currencyManager.add_rune(_type, _key, _value, rune_datas)
                            userdataManager.set_update(rune_category)
                elif _type == 'KNIGHT_PIECE':
                    if (can_reward) :
                        currencyManager.add_random_character_piece(_type, _key, _value, _rate)
                else:
                    currencyManager.add_dict(_type, _key, _value)
            

            if currencyManager.get_rewards():
                
                # if currencyManager.get_random_rune_list():
                #     add_rune = currencyManager.get_random_rune()
                    
                #     if add_rune:
                #         rune_datas = userdataManager.get(db, req.uid, rune_category)
                #         rune_datas = currencyManager.add_rune(add_rune['reward_type'], add_rune['reward_key'], add_rune['reward_amount'], rune_datas)
                        # userdataManager.set_update(rune_category)
                
                if currencyManager.get_random_character_piece_list():
                    add_character_piece =  currencyManager.get_random_character_piece()
                    
                    if add_character_piece:
                        character_datas = userdataManager.get(db, req.uid, character_category)
                        character_datas = currencyManager.add_character_piece(add_character_piece['reward_type'], add_character_piece['reward_key'], add_character_piece['reward_amount'], character_datas)
                        userdataManager.set_update(character_category)

                quest_info_dict = await CacheController.quest_info_map(db)
                quest_info_map = get(quest_info_dict, req.platform, None)
                if not quest_info_map:
                    return get_response(code=ResponseCode.RES_NOT_FOUND_QUEST_DATA, data=data, uid=req.uid)
                
                check_quest_ids = []
                for quest_info in quest_info_map:
                    if quest_info_map[quest_info]['qid'] == 'STAGE_CLEAR':
                        check_quest_ids.append(quest_info_map[quest_info]['id'])
                    else:continue
                
                quest_datas = userdataManager.get(db, req.uid, quest_category)
                
                for quest in quest_datas:
                    if quest['id'] in check_quest_ids:
                        quest_info = quest_info_map[str(quest['id'])]
                        if quest_info['value'] > quest['cur']:
                            quest['cur'] = quest['cur'] + 1
                            userdataManager.set_update(quest_category)
                        
                        # if quest['cur'] >= quest_info['value']:
                        #     quest['rewarded'] = True
                        #     userdataManager.set_update(quest_category)
                
                if req.extra_value_3rd != 0:
                    user_datas = userdataManager.get(db, req.uid, user_category)
                        
                    if user_datas['GuideMission']['id'] == req.extra_value_3rd:
                        user_datas['GuideMission']['c'] = 1
                        user_datas['GuideMission']['d'] = True
                        userdataManager.set_update(user_category)
               
                if currencyManager.get_rewards():
                    currencyManager.get_currency_rewards(db, req.uid)
                data = currencyManager.get_user_currency_data(db, req.uid)
                data['UserData'] = userdataManager.generate_user_save(db, req.uid)
                data['change'] = currencyManager.get_change()
                return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
            else:
                data = currencyManager.get_user_currency_data(db, req.uid)
                return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
        



#########################################################################################################################################################



#스테이지 소탕 클리어
async def game_stage_sweep(req:CurrencySweepReqParam, db:Session):
    stage_category = 'Stage'
    rune_category = 'Rune'
    quest_category = 'Quest'
    character_category = 'Character'
    time_category = 'Time'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()

    stage_tile_dict = await CacheController.stage_tile_info_map(db)
    stage_tile_info = get(stage_tile_dict, req.platform)
    if not stage_tile_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_STAGE_TILE_DATA, uid=req.uid)
    
    info = get(stage_tile_info, str(req.id))
    if not info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_STAGE_TILE_INFO_DATA, uid=req.uid)
    
    tile_type = get(info, 'tile_type', None)
    if (not tile_type) or (tile_type == 'OBSTACLE') or (tile_type == 'CHEST'):
        return get_response(code=ResponseCode.RES_NOT_FOUND_STAGE_TILE_TYPE_DATA, uid=req.uid)
    
    tile_key = get(info, 'tile_key', None)
    if not tile_type:
        return get_response(code=ResponseCode.RES_NOT_FOUND_STAGE_TILE_TYPE_DATA, uid=req.uid)
    
    stage_dict = await CacheController.stage_info_map(db)
    stage_info = get(stage_dict, req.platform)
    if not stage_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_STAGE_DATA, uid=req.uid)
    
    cost_info = get(stage_info, str(tile_key))
    if not cost_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_STAGE_INFO_DATA, uid=req.uid)
    
    stage_datas = userdataManager.get(db, req.uid, stage_category)
    
    find_stage = None
    
    for stage in stage_datas:
        if stage['ID'] == req.id:
            find_stage = stage
            break
        
    if not find_stage:
        return get_response(code=ResponseCode.RES_NOT_FOUND_USER_STAGE_DATA, uid=req.uid)
    
    current_sweep_count = 0
    if req.extra_value_2nd == 1:
        current_sweep_count = get(find_stage, 'phCount', None)
    
        if current_sweep_count == None:
            find_stage['phCount'] = 0
            current_sweep_count = find_stage['phCount']
            userdataManager.set_update(stage_category)
    elif req.extra_value_2nd == 0:
        current_sweep_count = get(find_stage, 'pCount', None)

        if current_sweep_count == None:
            find_stage['pCount'] = 0
            current_sweep_count = find_stage['pCount']
            userdataManager.set_update(stage_category)
    else:
        return get_response(code=ResponseCode.RES_INVALID_GAME_START_PARAM, uid=req.uid)
    
        
    limit_count = get(cost_info, 'limit_count', 0)
    
    if limit_count == 0:
        return get_response(code=ResponseCode.RES_USE_LIMIT_COUNT_SWEEP_IS_ZERO, uid=req.uid)
    elif current_sweep_count == limit_count:
        return get_response(code=ResponseCode.RES_USE_LIMIT_COUNT_SWEEP, uid=req.uid)
    elif (current_sweep_count + req.extra_value) > limit_count:
        # 요청값이 limit보다 큰 경우는 그냥 맞춰서 변경해 놓도록 우선 수정한다.
        req.extra_value = limit_count - current_sweep_count
    
    
    if req.extra_value_2nd == 1:
        find_stage['phCount'] = find_stage['phCount'] + req.extra_value
        userdataManager.set_update(stage_category)
        amount = get(cost_info, 'cost_hard', None)
    elif req.extra_value_2nd == 0:
        find_stage['pCount'] = find_stage['pCount'] + req.extra_value
        userdataManager.set_update(stage_category)
        amount = get(cost_info, 'cost', None)
    else:
        return get_response(code=ResponseCode.RES_INVALID_GAME_START_PARAM, uid=req.uid)
    
    if amount == None:
        return get_response(code=ResponseCode.RES_NOT_FOUNG_GAME_START_COST, uid=req.uid)
    
    amount = amount * req.extra_value
    
    chest_dict = await CacheController.chest_info_map(db)
    chest_info = get(chest_dict, req.platform)
    if not chest_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHEST_INFO_DATA, uid=req.uid)

    ## 우선 사용자 던전키를 깐다
    user_level_dict = await CacheController.level_up_info_map(db)
    user_level_info = get(user_level_dict, req.platform, None)
    if not user_level_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_UP_DATA, uid=req.uid)
    
    level_info = get(user_level_info, str(req.level), None)
    if not level_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_UP_INFO_DATA, uid=req.uid)

    energy_max = get(level_info, 'bread_max', None)
    if energy_max == None:
        return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_MAX_BREAD_DATA, uid=req.uid)
    
    energy_max = int(energy_max)
    
    energy = currencyManager.get_amount(db, req.uid, 'BREAD')
    if ((energy - amount) >= 0):
        time_datas = userdataManager.get(db, req.uid, time_category)
        
        if ((energy - amount) < energy_max) and (energy >= energy_max):
            userdataManager.change_user_data_value(db, req.uid, time_category, 'lastEnergyTime', int(time.time()) + Constant.VALUE_OF_1970)
        elif ((energy - amount) >= energy_max) and (energy >= energy_max):
            userdataManager.change_user_data_value(db, req.uid, time_category, 'lastEnergyTime', int(time.time()) + Constant.VALUE_OF_1970)

        user_currency = currencyManager.use_currency(db, req.uid, 'BREAD', amount)
        if not user_currency:
            data = currencyManager.get_user_currency_data(db, req.uid)
            return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
    else:
        data = currencyManager.get_user_currency_data(db, req.uid)
        return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
    
    
    
    if req.extra_value_2nd == 1:
        stage_detail_info = get(stage_info, str(info['tile_key']))
        if not stage_detail_info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_STAGE_TILE_INFO_DATA, uid=req.uid)
        
        hard_chest_id = get(stage_detail_info, 'hard_chest_id', None)
        if not hard_chest_id:
            return get_response(code=ResponseCode.RES_NOT_FOUND_HARD_CHEST_DATA, uid=req.uid)

        chest_rewards = get(chest_info, str(hard_chest_id), None)
        if not chest_rewards:
            return get_response(code=ResponseCode.RES_NOT_FOUND_HARD_CHEST_REWARD_DATA, uid=req.uid)
        
        rune_datas = userdataManager.get(db, req.uid, rune_category)
        total_prob = 10000
        
        for reward in chest_rewards:
            _type = get(reward, 'type', None)
            _key = get(reward, 'key', 0)
            _value = get(reward, 'value', None)
            _rate =  get(reward, 'rate', 0)
            if _type == 'RUNE':
                prob = int(_rate * total_prob)
                item_random_probs = random.randint(0, total_prob-1)
                
                if (item_random_probs - prob) <= 0:
                    # currencyManager.add_random_rune(_type, _key, _value, _rate)
                    rune_datas = userdataManager.get(db, req.uid, rune_category)
                    rune_datas = currencyManager.add_rune(_type, _key, _value, rune_datas)
                    userdataManager.set_update(rune_category)
            elif _type == 'KNIGHT_PIECE':
                currencyManager.add_random_character_piece(_type, _key, _value, _rate)
            else:
                currencyManager.add_dict(_type, _key, _value * req.extra_value)

        if currencyManager.get_rewards():
            
            # if currencyManager.get_random_rune_list():
            #     add_rune = currencyManager.get_random_rune()
                
            #     if add_rune:
            #         rune_datas = userdataManager.get(db, req.uid, rune_category)
            #         rune_datas = currencyManager.add_rune(add_rune['reward_type'], add_rune['reward_key'], add_rune['reward_amount'], rune_datas)
            #         userdataManager.set_update(rune_category)
            
            if currencyManager.get_random_character_piece_list():
                for i in range(0, req.extra_value):
                    add_character_piece =  currencyManager.get_random_character_piece()
                    
                    if add_character_piece:
                        character_datas = userdataManager.get(db, req.uid, character_category)
                        character_datas = currencyManager.add_character_piece(add_character_piece['reward_type'], add_character_piece['reward_key'], add_character_piece['reward_amount'], character_datas)
                        userdataManager.set_update(character_category)
                
            quest_info_dict = await CacheController.quest_info_map(db)
            quest_info_map = get(quest_info_dict, req.platform, None)
            if not quest_info_map:
                return get_response(code=ResponseCode.RES_NOT_FOUND_QUEST_DATA, data=data, uid=req.uid)
            
            check_quest_ids = []
            for quest_info in quest_info_map:
                if quest_info_map[quest_info]['qid'] == 'STAGE_CLEAR':
                    check_quest_ids.append(quest_info_map[quest_info]['id'])
                else:continue
            
            quest_datas = userdataManager.get(db, req.uid, quest_category)
            
            
            for quest in quest_datas:
                if quest['id'] in check_quest_ids:
                    quest_info = quest_info_map[str(quest['id'])]
                    if quest_info['value'] > quest['cur']:
                        quest['cur'] = ((quest['cur'] + req.extra_value) if ((quest['cur'] + req.extra_value) <= quest_info['value']) else quest_info['value'])
                        userdataManager.set_update(quest_category)
                    
                    # if quest['cur'] >= quest_info['value']:
                    #     quest['rewarded'] = True
                    #     userdataManager.set_update(quest_category)
                
            currencyManager.get_currency_rewards(db, req.uid)
            data = currencyManager.get_user_currency_data(db, req.uid)
            data['UserData'] = userdataManager.generate_user_save(db, req.uid)
            data['change'] = currencyManager.get_change()
            return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
        else:
            data = currencyManager.get_user_currency_data(db, req.uid)
            return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
    else:
        stage_detail_info = get(stage_info, str(info['tile_key']))
        if not stage_detail_info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_STAGE_TILE_INFO_DATA, uid=req.uid)
        
        chest_id = get(stage_detail_info, 'chest_id', None)
        if not chest_id:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHEST_DATA, uid=req.uid)
        
        chest_rewards = get(chest_info, str(chest_id), None)
        if not chest_rewards:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHEST_REWARD_DATA, uid=req.uid)
        
        rune_datas = userdataManager.get(db, req.uid, rune_category)
        
        total_prob = 10000
        
        for reward in chest_rewards:
            _type = get(reward, 'type', None)
            _key = get(reward, 'key', 0)
            _value = get(reward, 'value', None)
            _rate =  get(reward, 'rate', 0)
            if _type == 'RUNE':
                prob = int(_rate * total_prob)
                item_random_probs = random.randint(0, total_prob-1)
                
                if (item_random_probs - prob) <= 0:
                    # currencyManager.add_random_rune(_type, _key, _value, _rate)
                    rune_datas = userdataManager.get(db, req.uid, rune_category)
                    rune_datas = currencyManager.add_rune(_type, _key, _value, rune_datas)
                    userdataManager.set_update(rune_category)
                    
            elif _type == 'KNIGHT_PIECE':
                currencyManager.add_random_character_piece(_type, _key, _value, _rate)
            else:
                currencyManager.add_dict(_type, _key, _value* req.extra_value)
        

        if currencyManager.get_rewards():
            # if currencyManager.get_random_rune_list():
            #     add_rune = currencyManager.get_random_rune()
                
            #     if add_rune:
            #         rune_datas = userdataManager.get(db, req.uid, rune_category)
            #         rune_datas = currencyManager.add_rune(add_rune['reward_type'], add_rune['reward_key'], add_rune['reward_amount'], rune_datas)
            #         userdataManager.set_update(rune_category)
            
            if currencyManager.get_random_character_piece_list():
                for i in range(0, req.extra_value):
                    add_character_piece =  currencyManager.get_random_character_piece()
                    
                    if add_character_piece:
                        character_datas = userdataManager.get(db, req.uid, character_category)
                        character_datas = currencyManager.add_character_piece(add_character_piece['reward_type'], add_character_piece['reward_key'], add_character_piece['reward_amount'], character_datas)
                        userdataManager.set_update(character_category)

            quest_info_dict = await CacheController.quest_info_map(db)
            quest_info_map = get(quest_info_dict, req.platform, None)
            if not quest_info_map:
                return get_response(code=ResponseCode.RES_NOT_FOUND_QUEST_DATA, data=data, uid=req.uid)
            
            check_quest_ids = []
            for quest_info in quest_info_map:
                if quest_info_map[quest_info]['qid'] == 'STAGE_CLEAR':
                    check_quest_ids.append(quest_info_map[quest_info]['id'])
                else:continue
            
            
            quest_datas = userdataManager.get(db, req.uid, quest_category)
            
            for quest in quest_datas:
                if quest['id'] in check_quest_ids:
                    quest_info = quest_info_map[str(quest['id'])]
                    if quest_info['value'] > quest['cur']:
                        quest['cur'] = ((quest['cur'] + req.extra_value) if ((quest['cur'] + req.extra_value) <= quest_info['value']) else quest_info['value'])
                        userdataManager.set_update(quest_category)
                    
                    # if quest['cur'] >= quest_info['value']:
                    #     quest['rewarded'] = True
                    #     userdataManager.set_update(quest_category)
            
            if currencyManager.get_rewards():
                currencyManager.get_currency_rewards(db, req.uid)
                
            data = currencyManager.get_user_currency_data(db, req.uid)
            data['UserData'] = userdataManager.generate_user_save(db, req.uid)
            data['change'] = currencyManager.get_change()
            return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
        else:
            data = currencyManager.get_user_currency_data(db, req.uid)
            return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)

    


#########################################################################################################################################################






# 챕터 클리어
async def game_chapter_clear(req:CurrencyClearReqParam, db:Session):
    user_category = 'User'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    chapter_dict = await CacheController.chapter_info_map(db)
    chapter_info = get(chapter_dict, req.platform)
    if not chapter_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHAPTER_DATA, uid=req.uid)
    
    info = get(chapter_info, str(req.id))
    if not info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHAPTER_INFO_DATA, uid=req.uid)
    
    user_datas = userdataManager.get(db, req.uid, user_category)
    
    ## 현재 최고 chapter 값보다 작은 값이 요청으로 들어온 경우에는 깔끔하게 무시한다.
    if (req.id < user_datas['BestChapter']):
        return get_response(code=ResponseCode.RES_INVALID_CHAPTER, uid=req.uid)
    
    
    
    userdataManager.change_user_data_value(db, req.uid, user_category, 'BestChapter', req.id)
    
    for item in range(1,4):
        reward_type = get(info, 'reward_type_'+str(item))
        if reward_type:
            reward_count = get(info, 'reward_count_'+str(item), 0)
            currencyManager.add_dict(reward_type, 0, reward_count)
            
    if currencyManager.get_rewards():
        currencyManager.get_currency_rewards(db, req.uid)
    
    data = currencyManager.get_user_currency_data(db, req.uid)
    data['UserData'] = userdataManager.generate_user_save(db, req.uid)
    data['change'] = currencyManager.get_change()
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
        
    
#########################################################################################################################################################


#퀘스트 클리어
async def game_quest_clear(req:CurrencyClearReqParam, db:Session):
    quest_category = 'Quest'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
        
    quest_dict = await CacheController.quest_info_map(db)
    quest_info = get(quest_dict, req.platform)
    if not quest_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_QUEST_DATA, uid=req.uid)
    
    info = get(quest_info, str(req.id))
    if not info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_QUEST_INFO_DATA, uid=req.uid)
    else:
        # 보상정보를 받도록 한다.
        reward_type = get(info, 'reward_type')
        reward_count = get(info, 'reward_count', 0)
        term = get(info, 'term', None)
        if (not reward_type):
            return get_response(code=ResponseCode.RES_INVALID_CURRENCY_TYPE, uid=req.uid)

        quest_datas = userdataManager.get(db, req.uid, quest_category)
        
        for quest_data in quest_datas:
            quest_id = get(quest_data, 'id', None)
            if not quest_id:
                return get_response(code=ResponseCode.RES_NOT_FOUND_USER_QUEST_DATA, uid=req.uid)
            
            if quest_id != req.id:
                continue

            quest_data['cur'] = quest_data['cur'] + 1
            userdataManager.set_update(quest_category)
            
            if req.extra_value == 1:
                if quest_data['rewardedAd'] == False:
                    quest_data['rewardedAd'] = True
                    currencyManager.add_dict(reward_type, 0, reward_count)
                    userdataManager.set_update(quest_category)
                else:
                    return get_response(code=ResponseCode.RES_ALREADY_REWARDED_QUEST, uid=req.uid)
            else:
                if quest_data['rewarded'] == False:
                    quest_data['rewarded'] = True
                    for total_quest_data in quest_datas:
                        total_quest_id = get(total_quest_data, 'id', None)
                        total_info = get(quest_info, str(total_quest_id))
                        total_qid = get(total_info,'qid', None)
                        if total_qid:
                            if ((total_qid == 'QUEST_DAILY_DONE_1') or (total_qid == 'QUEST_DAILY_DONE_2') or (total_qid == 'QUEST_DAILY_DONE_3')) and (term == 'DAILY'):
                                quest_data['cur'] = quest_data['cur'] + 1
                            elif ((total_qid == 'QUEST_WEEKLY_DONE_1') or (total_qid == 'QUEST_WEEKLY_DONE_2') or (total_qid == 'QUEST_WEEKLY_DONE_3')) and (term == 'WEEKLY'):
                                quest_data['cur'] = quest_data['cur'] + 1
                    currencyManager.add_dict(reward_type, 0, reward_count)
                    userdataManager.set_update(quest_category)
                else:
                    return get_response(code=ResponseCode.RES_ALREADY_REWARDED_QUEST, uid=req.uid)
            
            if currencyManager.get_rewards():
                currencyManager.get_currency_rewards(db, req.uid)
             
            data = currencyManager.get_user_currency_data(db, req.uid)
            data['UserData'] = userdataManager.generate_user_save(db, req.uid)
            data['change'] = currencyManager.get_change()
            return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)


#########################################################################################################################################################

#가이드미션 클리어
async def game_guide_mission_clear(req:CurrencyClearReqParam, db:Session):
    user_category = 'User'
    character_category = 'Character'
    rune_category = 'Rune'
    weapon_category = 'Weapon'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    guide_mission_dict = await CacheController.guide_mission_info_map(db)
    guide_mission_info = get(guide_mission_dict, req.platform)
    if not guide_mission_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_GUIDE_MISSION_DATA, uid=req.uid)
    
    
    character_enhance_dict = await CacheController.character_enhance_info_map(db)
    character_enhance_info = get(character_enhance_dict, req.platform)
    if not character_enhance_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_ENHANCE_DATA, uid=req.uid)
    
    character_info_dict = await CacheController.character_info_map(db)
    character_info = get(character_info_dict, req.platform)
    if not character_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_ENHANCE_DATA, uid=req.uid)
    
    info = get(guide_mission_info, str(req.id))
    if not info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_GUIDE_MISSION_INFO_DATA, uid=req.uid)
    
    reward_type = get(info, 'reward_type')
    if (not reward_type):
        return get_response(code=ResponseCode.RES_INVALID_CURRENCY_TYPE, uid=req.uid)
    
    reward_amount = get(info, 'reward_amount', 0)
    
    
    user_datas = userdataManager.get(db, req.uid, user_category)
    guide_misison_data = get(user_datas, 'GuideMission', None)
    
    if not guide_misison_data:
        return get_response(code=ResponseCode.RES_NOT_FOUND_USER_GUIDE_MISSION_DATA, uid=req.uid)
    
    
    if guide_misison_data['id'] != req.id:
        return get_response(code=ResponseCode.RES_GUIDE_MISSION_ID_MISMATCH, uid=req.uid)
    
    
    if guide_misison_data['r'] == True:
        return get_response(code=ResponseCode.RES_ALREADY_REWARDED_GUIDE_MISSION, uid=req.uid)

    guide_misison_data['r'] = True
    guide_mission_order_dict = await CacheController.guide_mission_info_map_by_order(db)
    guide_mission_order_info = get(guide_mission_order_dict, req.platform)
    if not guide_mission_order_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_GUIDE_MISSION_DATA, uid=req.uid)
        
    
    if reward_type == 'KNIGHT_PIECE':
        reward_key = get(info, 'reward_key', None)
        character_datas = userdataManager.get(db, req.uid, character_category)
        character_datas = currencyManager.add_character_piece(reward_type, reward_key, reward_amount, character_datas)
        userdataManager.set_update(character_category)
    elif reward_type == 'RUNE':
        reward_key = get(info, 'reward_key', None)
        rune_datas = userdataManager.get(db, req.uid, rune_category)
        rune_datas = currencyManager.add_rune(reward_type, reward_key, reward_amount, rune_datas)
        userdataManager.set_update(rune_category)
    elif reward_type == 'KNIGHT':
        reward_key = get(info, 'reward_key', None)
        character_datas = userdataManager.get(db, req.uid, character_category)
        character_info_data = get(character_info, str(reward_key), None)
        if character_info_data:
            character_grade = get(character_info_data, 'grade_value', None)
            if character_grade:
                character_enhance = get(character_enhance_info, str(character_grade), None)
                if character_enhance == None:
                    return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)
                character_enhance = get(character_enhance, str(character_grade), None)
                if character_enhance == None:
                    return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)
                default_character_piece = get(character_enhance, 'piece', None)
                character_datas = currencyManager.add_character(reward_type, reward_key, reward_amount, default_character_piece, character_datas)
                userdataManager.set_update(character_category)
    elif reward_type == 'WEAPON':
        reward_key = get(info, 'reward_key', None)
        weapon_datas = userdataManager.get(db, req.uid, weapon_category)
        weapon_datas = currencyManager.add_weapon(reward_type, reward_key, reward_amount, weapon_datas)
        userdataManager.set_update(weapon_category)

    else:                    
        currencyManager.add_dict(reward_type, 0, reward_amount)
    
    next_info = get(guide_mission_order_info, str(info['order'] + 1), None)
    if next_info:
        if get(next_info, 'order', None) == None:
            return get_response(code=ResponseCode.RES_NOT_FOUND_GUIDE_MISSION_INFO_DATA, uid=req.uid)

        guide_misison_data['id'] = next_info['id']
        guide_misison_data['c'] = 0
        guide_misison_data['r'] = False
        guide_misison_data['d'] = False
        userdataManager.set_update(user_category)
    
    if currencyManager.get_rewards():
        currencyManager.get_currency_rewards(db, req.uid)
    
    data = currencyManager.get_user_currency_data(db, req.uid)
    data['UserData'] = userdataManager.generate_user_save(db, req.uid)
    data['change'] = currencyManager.get_change()
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
        
    
#########################################################################################################################################################




async def game_start(req:CurrencyStartReqParam, db:Session):
    
    currencyManager = CurrencyManager()
    
    if req.type.upper() == 'STAGE':
        stage_dict = await CacheController.stage_info_map(db)
        stage_info = get(stage_dict, req.platform)
        if not stage_info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_STAGE_DATA, uid=req.uid)
        
        info = get(stage_info, str(req.id))
        if not info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_STAGE_INFO_DATA, uid=req.uid)
        
        
        if req.extra_value == 1:
            amount = get(info, 'cost_hard', None)
        elif req.extra_value == 0:
            amount = get(info, 'cost', None)
        else:
            return get_response(code=ResponseCode.RES_INVALID_GAME_START_PARAM, uid=req.uid)
        
        if amount == None:
            return get_response(code=ResponseCode.RES_NOT_FOUNG_GAME_START_COST, uid=req.uid)
        
        
        energy = currencyManager.get_amount(db, req.uid, 'BREAD')

        if (energy - amount) < 0:
            return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, uid=req.uid)
        
        return get_response(code=ResponseCode.RES_SUCCESS, uid=req.uid)
    
    
    else:
        return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_UP_DATA, uid=req.uid)





#########################################################################################################################################################





async def game_dungeon_end(req:CurrencyEndReqParam, db:Session):
    user_category = 'User'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    user_datas = userdataManager.get(db, req.uid, user_category)
    guide_misison_data = get(user_datas, 'GuideMission', None)
    guide_mission_dict = await CacheController.guide_mission_info_map(db)
    guide_mission_info = get(guide_mission_dict, req.platform)
    current_info = get(guide_mission_info, str(guide_misison_data['id']))
    if not guide_mission_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_GUIDE_MISSION_DATA, uid=req.uid)
    if req.type.upper() == 'DEFENSE':
        
        current_type = get(current_info, 'type', '')
        if current_type == 'ENTER_DEFENSEDUNGEON':
            guide_misison_data['c'] = 1
            userdataManager.set_update(user_category)
        
        defense_reward_dict = await CacheController.defense_reward_info_map(db)
        defense_reward_info = get(defense_reward_dict, req.platform)
        if not defense_reward_info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_DEFENSE_DUNGEON_DATA, uid=req.uid)
        
        info = get(defense_reward_info, str(req.id))
        if not info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_DEFENSE_DUNGEON_INFO_DATA, uid=req.uid)
        
        ## 우선 사용자 던전키를 깐다
        user_currency = currencyManager.use_currency(db, req.uid, 'DUNGEON_KEY1', req.extra_value)
        if not user_currency:
            data = currencyManager.get_user_currency_data(db, req.uid)
            return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
        
        for defense_reward in info:
            _type = get(defense_reward, 'reward_type', None)
            currencyManager.add_dict(_type, 0, get(defense_reward, 'reward_amount', 0) * req.extra_value)
                
        if currencyManager.get_rewards():
            currencyManager.get_currency_rewards(db, req.uid)
            
        if (user_datas['DungeonDefLv'] == req.id) and (req.extra_value == 1):
            info = get(defense_reward_info, str(req.id + 1), None)
        # check next stage
            if info:
                userdataManager.add_user_data_value(db, req.uid, user_category, 'DungeonDefLv', 1)

        data = currencyManager.get_user_currency_data(db, req.uid)
        data['UserData'] = userdataManager.generate_user_save(db, req.uid)
        data['change'] = currencyManager.get_change()
        return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
            
    
    elif req.type.upper() == 'STONE':
        
        current_type = get(current_info, 'type', '')
        if current_type == 'ENTER_STONEDUNGEON':
            guide_misison_data['c'] = 1
            userdataManager.set_update(user_category)
            
            
        stone_reward_dict = await CacheController.stone_reward_info_map(db)
        stone_reward_info = get(stone_reward_dict, req.platform)
        if not stone_reward_info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_STONE_DUNGEON_DATA, uid=req.uid)
        
        info = get(stone_reward_info, str(req.id))
        if not info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_STONE_DUNGEON_INFO_DATA, uid=req.uid)
        
        ## 우선 사용자 던전키를 깐다
        user_currency = currencyManager.use_currency(db, req.uid, 'DUNGEON_KEY2', req.extra_value)
        if not user_currency:
            data = currencyManager.get_user_currency_data(db, req.uid)
            return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
            
        for defense_reward in info:
            _type = get(defense_reward, 'reward_type', None)
            currencyManager.add_dict(_type, 0, get(defense_reward, 'reward_amount', 0) * req.extra_value)
                
        if currencyManager.get_rewards():
            currencyManager.get_currency_rewards(db, req.uid)
            
        if (user_datas['DungeonStoneLv'] == req.id) and (req.extra_value == 1):
            info = get(stone_reward_info, str(req.id + 1), None)
        # check next stage
            if info:
                userdataManager.add_user_data_value(db, req.uid, user_category, 'DungeonStoneLv', 1)
                
        data = currencyManager.get_user_currency_data(db, req.uid)
        data['UserData'] = userdataManager.generate_user_save(db, req.uid)
        data['change'] = currencyManager.get_change()
        return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
       
        
    elif req.type.upper() == 'MINE':
        
        current_type = get(current_info, 'type', '')
        if current_type == 'ENTER_MINEDUNGEON':
            guide_misison_data['c'] = 1
            userdataManager.set_update(user_category)
            
            
        mine_reward_dict = await CacheController.mine_reward_info_map(db)
        mine_reward_info = get(mine_reward_dict, req.platform)
        if not mine_reward_info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_MINE_DUNGEON_DATA, uid=req.uid)
        
        info = get(mine_reward_info, str(req.id))
        if not info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_MINE_DUNGEON_INFO_DATA, uid=req.uid)
        
        ## 우선 사용자 던전키를 깐다
        user_currency = currencyManager.use_currency(db, req.uid, 'DUNGEON_KEY3', req.extra_value)
        if not user_currency:
            data = currencyManager.get_user_currency_data(db, req.uid)
            return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
            
        for defense_reward in info:
            _type = get(defense_reward, 'reward_type', None)
            currencyManager.add_dict(_type, 0, get(defense_reward, 'reward_amount', 0) * req.extra_value)
                
        if currencyManager.get_rewards():
            currencyManager.get_currency_rewards(db, req.uid)
            
        
        if (user_datas['DungeonMineLv'] == req.id) and (req.extra_value == 1):
            info = get(mine_reward_info, str(req.id + 1), None)
            # check next stage
            if info:
                userdataManager.add_user_data_value(db, req.uid, user_category, 'DungeonMineLv', 1)

        data = currencyManager.get_user_currency_data(db, req.uid)
        data['UserData'] = userdataManager.generate_user_save(db, req.uid)
        data['change'] = currencyManager.get_change()
        return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)

    else:
        return get_response(code=ResponseCode.RES_CURRENCY_NOT_FOUND_END_TYPE, uid=req.uid)



#########################################################################################################################################################    
    
    
async def game_quest_clear_list(req:CurrencyClearListReqParam, db:Session):
    quest_category = 'Quest'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    quest_dict = await CacheController.quest_info_map(db)
    quest_info = get(quest_dict, req.platform)
    if not quest_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_QUEST_DATA, uid=req.uid)
    
    quest_datas = userdataManager.get(db, req.uid, quest_category)
    
    for id in req.ids:
        info = get(quest_info, str(id))
        if not info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_QUEST_INFO_DATA, uid=req.uid)
        else:
            # 보상정보를 받도록 한다.
            reward_type = get(info, 'reward_type')
            reward_count = get(info, 'reward_count', 0)
            
            for quest_data in quest_datas:
                quest_id = get(quest_data, 'id', None)
                if not quest_id:
                    return get_response(code=ResponseCode.RES_NOT_FOUND_QUEST_ID_DATA, uid=req.uid)
                
                if quest_id != id:
                    continue
                
                quest_data['cur'] = quest_data['cur'] + 1
                userdataManager.set_update(quest_category)
                
                if (not reward_type):
                    continue
                
                # 조회가 되었다면 break를 걸어준다.
                if req.extra_value == 1:
                    if quest_data['rewardedAd'] == False:
                        quest_data['rewardedAd'] = True
                        userdataManager.set_update(quest_category)
                        currencyManager.add_dict(reward_type, 0, reward_count)
                    else:
                        return get_response(code=ResponseCode.RES_ALREADY_REWARDED_QUEST, uid=req.uid)
                else:
                    if quest_data['rewarded'] == False:
                        quest_data['rewarded'] = True
                        userdataManager.set_update(quest_category)
                        currencyManager.add_dict(reward_type, 0, reward_count)
                    else:
                        return get_response(code=ResponseCode.RES_ALREADY_REWARDED_QUEST, uid=req.uid)
    
    
    # daily_complete = 0
    # weekly_complete = 0
    
    # for check_quest_data in quest_datas:
    #     check_quest_id = get(check_quest_data, 'id', None)
    #     check_complete_info = get(quest_info, str(check_quest_id))
    #     check_complete_qid = get(check_complete_info,'qid', None)
    #     if (check_complete_qid != 'QUEST_DAILY_DONE_1') and (check_complete_qid != 'QUEST_DAILY_DONE_2') and (check_complete_qid != 'QUEST_DAILY_DONE_3') and (check_complete_qid != 'QUEST_WEEKLY_DONE_1') and (check_complete_qid != 'QUEST_WEEKLY_DONE_2') and (check_complete_qid != 'QUEST_WEEKLY_DONE_3'):
    #         _term = get(check_complete_info, 'term', None)
    #         check_quest_reward = get(check_quest_data, 'rewarded', False)
    #         if check_quest_reward:
    #             if _term == 'DAILY':
    #                 daily_complete += 1
    #             elif _term == 'WEEKLY':
    #                 weekly_complete += 1
    #             else:
    #                 continue
            
    
    
    # for total_quest_data in quest_datas:
    #     total_quest_id = get(total_quest_data, 'id', None)
    #     total_info = get(quest_info, str(total_quest_id))
    #     total_qid = get(total_info,'qid', None)
    #     if total_qid:
    #         if (total_qid == 'QUEST_DAILY_DONE_1') or (total_qid == 'QUEST_DAILY_DONE_2') or (total_qid == 'QUEST_DAILY_DONE_3'):
    #             quest_data['cur'] = daily_complete
    #         elif (total_qid == 'QUEST_WEEKLY_DONE_1') or (total_qid == 'QUEST_WEEKLY_DONE_2') or (total_qid == 'QUEST_WEEKLY_DONE_3'):
    #             quest_data['cur'] = weekly_complete
    
    # userdataManager.set_update(quest_category)
    
    if currencyManager.get_rewards():
        currencyManager.get_currency_rewards(db, req.uid)

        
        data = currencyManager.get_user_currency_data(db, req.uid)
        data['UserData'] = userdataManager.generate_user_save(db, req.uid)
        data['change'] = currencyManager.get_change()
        return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
    else:
        data = currencyManager.get_user_currency_data(db, req.uid)
        return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
   
    

#########################################################################################################################################################
async def run_gacha_temp(req:GachaReqParam, db:Session):
    return get_response(code=ResponseCode.RES_SUCCESS, uid=req.uid)    
    

async def run_gacha(req:GachaReqParam, db:Session):

    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()

    gacha_cost_dict = await CacheController.gacha_cost_info_map(db)
    gacha_cost_info = get(gacha_cost_dict, req.platform)
    
    if not gacha_cost_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_GACHA_COST_DATA, uid=req.uid)
        
    info = get(gacha_cost_info, str(req.id))
    
    character_enhance_dict = await CacheController.character_enhance_info_map(db)
    character_enhance_info = get(character_enhance_dict, req.platform)
    if not character_enhance_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_ENHANCE_DATA, uid=req.uid)
    
    gacha_key = get(info, 'gacha_key', None)
    price_type = get(info, 'price_type')
    if (not price_type):
        return get_response(code=ResponseCode.RES_INVALID_CURRENCY_TYPE, uid=req.uid)
    
    cost = get(info, 'cost', 0)
    
    
    # 캐릭터 1연차
    if (gacha_key == 'CHARACTER_JEWEL_1') or (gacha_key == 'CHARACTER_TICKET_1'):
        gacha_type = 'PIECE'
        character_category = 'Character'
        user_category = 'User'
        
        count = 1
        character_grade_prob = await CacheController.gacha_info_map(db)
        character_platform_grade = get(character_grade_prob, req.platform, None)
        
        if not character_platform_grade:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_PLATFORM_GACHA_DATA, uid=req.uid)
        
        gacha_grade_prob = get(character_platform_grade, gacha_type, None)
        if not gacha_grade_prob:
            # 문제가 있다고 생각되기 때문에 여기서 에러를 보내고 리턴을 한다.
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_GACHA_GRADE_PROB_DATA, uid=req.uid)
        
        user_datas = userdataManager.get(db, req.uid, user_category)
        character_datas = userdataManager.get(db, req.uid, character_category)
        
        grade = __calculate_random_grade(1, gacha_grade_prob, req.v)
        if not grade:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_GACHA_PROB_DATA, uid=req.uid)
       
        
        if req.extra_value > 0:
            gacha_result = await __calculate_random_special(db, req.platform, gacha_type, grade, req.v, req.extra_value)
        else:
            gacha_result = await __calculate_random(db, req.platform, gacha_type, grade, req.v)
        
        temp_grade = [{'grade':4, 'count':20}]
        
        pick_count = get(user_datas, 'KPickCount', None)
        if pick_count == None:
            user_datas['KPickCount'] = 0
        
        if (user_datas['KPickCount'] + 1) == 10:
            if req.extra_value > 0:
                temp_gacha_result = await __calculate_random_special(db, req.platform, 'CHARACTER', temp_grade, req.v, req.extra_value)
            else:
                temp_gacha_result = await __calculate_random(db, req.platform, 'CHARACTER', temp_grade, req.v)
            gacha_result = temp_gacha_result
        
        
        
        if not gacha_result:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_GACHA_RESULT, uid=req.uid)
                
        user_currency = currencyManager.use_currency(db, req.uid, price_type, cost)
        if not user_currency:
            data = currencyManager.get_user_currency_data(db, req.uid)
            return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
        else:
            userdataManager.add_user_data_value(db, req.uid, user_category, 'GkCount', count)
            
            find_character = None
            
            if character_datas:
                for character_data in character_datas:
                    character_id = get(character_data, 'ID', None)
                    if character_id == gacha_result[0]['id']:
                        find_character = character_data
                        break
            
            if not find_character:
                return
            
            if find_character['Level'] == 0:
                character_enhance = get(character_enhance_info, str(gacha_result[0]['grade']), None)
                if character_enhance == None:
                    return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)
                
                character_enhance = get(character_enhance, str(gacha_result[0]['grade']), None)
                if character_enhance == None:
                    return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)
                need_character_piece = get(character_enhance, 'piece', None)
                
                if (gacha_result[0]['count']) >= need_character_piece:
                    find_character['Level'] = 1
                    userdataManager.set_update(character_category)
                    currencyManager.add_dict('KNIGHT', gacha_result[0]['id'], 1)
                else:
                    character_datas = currencyManager.add_character_piece('KNIGHT_PIECE', gacha_result[0]['id'], gacha_result[0]['count'], character_datas)
                    userdataManager.set_update(character_category)
                    
            else:
                character_datas = currencyManager.add_character_piece('KNIGHT_PIECE', gacha_result[0]['id'], gacha_result[0]['count'], character_datas)
                userdataManager.set_update(character_category)
                        
            userdataManager.add_user_data_value(db, req.uid, user_category, 'KPickCount', count)
            
            data = currencyManager.get_user_currency_data(db, req.uid)
            data['UserData'] = userdataManager.generate_user_save(db, req.uid)
            data['change'] = currencyManager.get_change()
            data['gacha_result'] = gacha_result
            return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
    
    #캐릭터 10연차
    elif (gacha_key == 'CHARACTER_JEWEL_10') or (gacha_key == 'CHARACTER_TICKET_10'):
        gacha_type = 'PIECE'
        character_category = 'Character'
        user_category = 'User'
        count = 10
        character_grade_prob = await CacheController.gacha_info_map(db)
        character_platform_grade = get(character_grade_prob, req.platform, None)
        
        user_datas = userdataManager.get(db, req.uid, user_category)
        character_datas = userdataManager.get(db, req.uid, character_category)
        
        if not character_platform_grade:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_PLATFORM_GACHA_DATA, uid=req.uid)
        
        gacha_grade_prob = get(character_platform_grade, gacha_type, None)
        if not gacha_grade_prob:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_GACHA_GRADE_PROB_DATA, uid=req.uid)
        
        
        grades = __calculate_random_grade(10, gacha_grade_prob, req.v)
        if not grades:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_GACHA_PROB_DATA, uid=req.uid)
        
        if (user_datas['KPickCount'] < 10) and (user_datas['KPickCount'] + count) >= 10:
            for i in range(0, len(grades)):
                value = grades[i]
                if value['grade'] == 4:
                    value['grade'] == 3
        
        if req.extra_value > 0:
            gacha_result = await __calculate_random_special(db, req.platform, gacha_type, grades, req.v, req.extra_value)
        else:
            gacha_result = await __calculate_random(db, req.platform, gacha_type, grades, req.v)
        
        
        temp_grade = [{'grade':4, 'count':20}]
        
        pick_count = get(user_datas, 'KPickCount', None)
        if pick_count == None:
            user_datas['KPickCount'] = 0
        
        if (user_datas['KPickCount'] < 10) and (user_datas['KPickCount'] + count) >= 10:
               
            index = random.randint(0, len(grades)-1)
            del gacha_result[index]
            if req.extra_value > 0:
                temp_gacha_result = await __calculate_random_special(db, req.platform, 'CHARACTER', temp_grade, req.v, req.extra_value)
            else:
                temp_gacha_result = await __calculate_random(db, req.platform, 'CHARACTER', temp_grade, req.v)
            gacha_result = gacha_result + temp_gacha_result
        
        if not gacha_result:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_GACHA_RESULT, uid=req.uid)
        
        user_currency = currencyManager.use_currency(db, req.uid, price_type, cost)
        if not user_currency:
            data = currencyManager.get_user_currency_data(db, req.uid)
            return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
        else:
            
            userdataManager.add_user_data_value(db, req.uid, user_category, 'GkCount', count)
            
            gacha_id_list = [item['id'] for item in gacha_result]
            new_character_datas = list(filter(lambda x: x['ID'] in gacha_id_list , character_datas))
            
            for gacha_info in gacha_result:
                # character_datas = currencyManager.add_character_piece('KNIGHT_PIECE', gacha_id['id'], gacha_id['count'], character_datas)
                for character in new_character_datas:
                    if character['ID'] == gacha_info['id']:
                        if character['Level'] == 0:
                            character_enhance = get(character_enhance_info, str(gacha_info['grade']), None)
                            if character_enhance == None:
                                return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)
                            
                            character_enhance = get(character_enhance, str(gacha_info['grade']), None)
                            if character_enhance == None:
                                return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)
                            need_character_piece = get(character_enhance, 'piece', None)
                            
                            if (gacha_info['count']) >= need_character_piece:
                                character['Level'] = 1
                                userdataManager.set_update(character_category)
                                currencyManager.add_dict('KNIGHT', gacha_info['id'], 1)
                            else:
                                character_datas = currencyManager.add_character_piece('KNIGHT_PIECE', gacha_info['id'], gacha_info['count'], character_datas)
                                userdataManager.set_update(character_category)
                                
                        else:
                            character_datas = currencyManager.add_character_piece('KNIGHT_PIECE', gacha_info['id'], gacha_info['count'], character_datas)
                            userdataManager.set_update(character_category)
           
            userdataManager.set_update(character_category)
            userdataManager.add_user_data_value(db, req.uid, user_category, 'KPickCount', count)
            
            data = currencyManager.get_user_currency_data(db, req.uid)
            data['UserData'] = userdataManager.generate_user_save(db, req.uid)
            data['change'] = currencyManager.get_change()
            data['gacha_result'] = gacha_result
            return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
        
    
    #무기 1연차
    elif (gacha_key == 'WEAPON_JEWEL_1') or (gacha_key == 'WEAPON_TICKET_1'):
        gacha_type = 'WEAPON'
        weapon_category = 'Weapon'
        user_category = 'User'
        count = 1
        
        weapon_grade_prob = await CacheController.gacha_info_map(db)
        weapon_platform_grade = get(weapon_grade_prob, req.platform, None)
        if not weapon_platform_grade:
            return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_PLATFORM_GACHA_DATA, uid=req.uid)
            
        gacha_grade_prob = get(weapon_platform_grade, gacha_type, None)
        if not gacha_grade_prob:
            return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_GACHA_GRADE_PROB_DATA, uid=req.uid)
        
        grade = __calculate_random_grade(1, gacha_grade_prob, req.v)
        if not grade:
            return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_GACHA_PROB_DATA, uid=req.uid)
        
        
        if req.extra_value > 0:
            gacha_result = await __calculate_random_special(db, req.platform, gacha_type, grade, req.v, req.extra_value)
        else:
            gacha_result = await __calculate_random(db, req.platform, gacha_type, grade, req.v)
        
        if not gacha_result:
            return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_GACHA_RESULT, uid=req.uid)
        
        
        userdataManager.add_user_data_value(db, req.uid, user_category, 'GwCount', count)
        
        user_currency = currencyManager.use_currency(db, req.uid, price_type, cost)
        if not user_currency:
            data = currencyManager.get_user_currency_data(db, req.uid)
            return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
        else:
                        
            user_datas = userdataManager.get(db, req.uid, user_category)
            weapon_datas = userdataManager.get(db, req.uid, weapon_category)
            
            weapon_datas = currencyManager.add_weapon('WEAPON', gacha_result[0]['id'], gacha_result[0]['count'], weapon_datas)
            userdataManager.set_update(weapon_category)

            data = currencyManager.get_user_currency_data(db, req.uid)
            data['UserData'] = userdataManager.generate_user_save(db, req.uid)
            data['change'] = currencyManager.get_change()
            data['gacha_result'] = gacha_result
            return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
    
    
    #무기 10연차
    elif (gacha_key == 'WEAPON_JEWEL_10') or (gacha_key == 'WEAPON_TICKET_10'):
        gacha_type = 'WEAPON'
        weapon_category = 'Weapon'
        user_category = 'User'
        count = 10
        
        weapon_grade_prob = await CacheController.gacha_info_map(db)
        weapon_platform_grade = get(weapon_grade_prob, req.platform, None)
        if not weapon_platform_grade:
            return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_PLATFORM_GACHA_DATA, uid=req.uid)
            
        gacha_grade_prob = get(weapon_platform_grade, gacha_type, None)
        if not gacha_grade_prob:
            return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_GACHA_GRADE_PROB_DATA, uid=req.uid)
        
        grades = __calculate_random_grade(10, gacha_grade_prob, req.v)
        if not grades:
            return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_GACHA_PROB_DATA, uid=req.uid)
        legend_count = 0
        for grade in grades:
            if grade['grade'] == 4:
                legend_count += 1
            
            if legend_count > 3:
                grade['grade'] = 3
        
        if req.extra_value > 0:
            gacha_result = await __calculate_random_special(db, req.platform, gacha_type, grades, req.v, req.extra_value)
        else:
            gacha_result = await __calculate_random(db, req.platform, gacha_type, grades, req.v)
        
        if not gacha_result:
            return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_GACHA_RESULT, uid=req.uid)
        
        userdataManager.add_user_data_value(db, req.uid, user_category, 'GwCount', count)
        
        user_currency = currencyManager.use_currency(db, req.uid, price_type, cost)
        if not user_currency:
            data = currencyManager.get_user_currency_data(db, req.uid)
            return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
        else:
            
            user_datas = userdataManager.get(db, req.uid, user_category)
            weapon_datas = userdataManager.get(db, req.uid, weapon_category)
            max_uid = 0
            if weapon_datas:
                max_uid = reduce(lambda x, y : x if int(x['UID']) > int(y['UID']) else y, weapon_datas)
                max_uid = max_uid['UID']
            else:
                max_uid = 0
            
            for gacha_id in gacha_result:
                max_uid = max_uid + 1
                weapon_datas = currencyManager.add_weapon_def_uid('WEAPON', gacha_id['id'], gacha_id['count'], max_uid, weapon_datas)
                userdataManager.set_update(weapon_category)

            data = currencyManager.get_user_currency_data(db, req.uid)
            data['UserData'] = userdataManager.generate_user_save(db, req.uid)
            data['change'] = currencyManager.get_change()
            data['gacha_result'] = gacha_result
            return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
    
    else:
        return get_response(code=ResponseCode.RES_NOT_FOUND_GACHA_COST_TYPE, uid=req.uid)



#########################################################################################################################################################



async def get_gacha_reward(req:GachaRewardReqParam, db:Session):

    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()

    if req.type == 'CHARACTER':

        character_category = 'Character'
        user_category = 'User'

        character_enhance_dict = await CacheController.character_enhance_info_map(db)
        character_enhance_info = get(character_enhance_dict, req.platform)
        if not character_enhance_info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_ENHANCE_DATA, uid=req.uid)

        game_config_dict = await CacheController.game_config_info_map(db)
        game_config_info = get(game_config_dict, req.platform, None)
        
        max_gk_object = get(game_config_info, Constant.GAME_CONFIG_GACHA_KNIGHT_HARD_PITY, None)
        
        max_gk = int(get(max_gk_object, 'value', None))

        
        user_datas = userdataManager.get(db, req.uid, user_category)
        character_datas = userdataManager.get(db, req.uid, character_category)

        
        temp_grade = [{'grade':4, 'count':20}]
        gk_count = get(user_datas, 'GkCount', None)
        gacha_result = None
        if max_gk > 0:
            if gk_count and (gk_count >= max_gk):
                user_datas['GkCount'] = user_datas['GkCount'] - max_gk
                gacha_result = await __calculate_random(db, req.platform, 'CHARACTER', temp_grade, req.v)
                userdataManager.set_update(user_category)
            else:
                return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, uid=req.uid)
        
        
        if not gacha_result:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_GACHA_RESULT, uid=req.uid)
        
        
        gacha_id_list = [item['id'] for item in gacha_result]
        new_character_datas = list(filter(lambda x: x['ID'] in gacha_id_list , character_datas))
        
        for gacha_info in gacha_result:
            # character_datas = currencyManager.add_character_piece('KNIGHT_PIECE', gacha_id['id'], gacha_id['count'], character_datas)
            for character in new_character_datas:
                if character['ID'] == gacha_info['id']:
                    if character['Level'] == 0:
                        character_enhance = get(character_enhance_info, str(gacha_info['grade']), None)
                        if character_enhance == None:
                            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)
                        
                        character_enhance = get(character_enhance, str(gacha_info['grade']), None)
                        if character_enhance == None:
                            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)
                        need_character_piece = get(character_enhance, 'piece', None)
                        
                        if (gacha_info['count']) >= need_character_piece:
                            character['Level'] = 1
                            userdataManager.set_update(character_category)
                            currencyManager.add_dict('KNIGHT', gacha_info['id'], 1)
                        else:
                            character_datas = currencyManager.add_character_piece('KNIGHT_PIECE', gacha_info['id'], gacha_info['count'], character_datas)
                            userdataManager.set_update(character_category)
                            
                    else:
                        character_datas = currencyManager.add_character_piece('KNIGHT_PIECE', gacha_info['id'], gacha_info['count'], character_datas)
                        userdataManager.set_update(character_category)
        
        userdataManager.set_update(character_category)
        
        data = currencyManager.get_user_currency_data(db, req.uid)
        data['UserData'] = userdataManager.generate_user_save(db, req.uid)
        data['change'] = currencyManager.get_change()
        data['gacha_result'] = gacha_result
        return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
    
    elif req.type == 'WEAPON':
        gacha_type = 'WEAPON'
        weapon_category = 'Weapon'
        user_category = 'User'

        weapon_grade_prob = await CacheController.gacha_info_map(db)
        weapon_platform_grade = get(weapon_grade_prob, req.platform, None)
        if not weapon_platform_grade:
            return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_PLATFORM_GACHA_DATA, uid=req.uid)
        
        game_config_dict = await CacheController.game_config_info_map(db)
        game_config_info = get(game_config_dict, req.platform, None)
        
        max_wk_object = get(game_config_info, Constant.GAME_CONFIG_GACHA_WEAPON_HARD_PITY, None)
        
        max_wk = int(get(max_wk_object, 'value', None))
        
        gacha_grade_prob = get(weapon_platform_grade, gacha_type, None)
        if not gacha_grade_prob:
            return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_GACHA_GRADE_PROB_DATA, uid=req.uid)
        
        user_datas = userdataManager.get(db, req.uid, user_category)
        weapon_datas = userdataManager.get(db, req.uid, weapon_category)        
        
        temp_grade = [{'grade':4, 'count':1}]
        gw_count = get(user_datas, 'GwCount', None)
        gacha_result = None
        if max_wk > 0:
            if gw_count and (gw_count >= max_wk):
                user_datas['GwCount'] = user_datas['GwCount'] - max_wk
                gacha_result = await __calculate_random(db, req.platform, 'WEAPON', temp_grade, req.v)
                userdataManager.set_update(user_category)
            else:
                return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, uid=req.uid)
        
        if not gacha_result:
            return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_GACHA_RESULT, uid=req.uid)
        
        max_uid = 0
        if weapon_datas:
            max_uid = reduce(lambda x, y : x if int(x['UID']) > int(y['UID']) else y, weapon_datas)
            max_uid = max_uid['UID']
        else:
            max_uid = 0
        
        for gacha_id in gacha_result:
            max_uid = max_uid + 1
            weapon_datas = currencyManager.add_weapon_def_uid('WEAPON', gacha_id['id'], gacha_id['count'], max_uid, weapon_datas)
            userdataManager.set_update(weapon_category)

        data = currencyManager.get_user_currency_data(db, req.uid)
        data['UserData'] = userdataManager.generate_user_save(db, req.uid)
        data['change'] = currencyManager.get_change()
        data['gacha_result'] = gacha_result
        return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
    



#########################################################################################################################################################





async def exchange_item(req:ExchangeItemReqParam, db:Session):

    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()

    
    character_enhance_dict = await CacheController.character_enhance_info_map(db)
    character_enhance_info = get(character_enhance_dict, req.platform)
    if not character_enhance_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_ENHANCE_DATA, uid=req.uid)
    
    
    # 캐릭터 1연차
    if (req.type == 'RANDOM_KNIGHT'):
        gacha_type = 'CHARACTER'
        character_category = 'Character'
       
        character_enhance_dict = await CacheController.character_enhance_info_map(db)
        character_enhance_info = get(character_enhance_dict, req.platform)
        if not character_enhance_info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_ENHANCE_DATA, uid=req.uid)
        
        character_info_dict = await CacheController.character_info_map(db)
        character_info = get(character_info_dict, req.platform)
        if not character_info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_ENHANCE_DATA, uid=req.uid)
        
        random_character_list = []
        for i in range(0, req.extra_value):
            random_character_list.append({'grade':4, 'count':20})
        
        gacha_result = await __calculate_random(db, req.platform, gacha_type, random_character_list, req.v)
        
        if not gacha_result:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_GACHA_RESULT, uid=req.uid)
                
        user_currency = currencyManager.use_currency(db, req.uid, req.type, req.extra_value)
        if not user_currency:
            data = currencyManager.get_user_currency_data(db, req.uid)
            return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
        else:
            character_datas = userdataManager.get(db, req.uid, character_category)

            for result in gacha_result:
                character_grade = result['grade']
                if character_grade:
                    character_enhance = get(character_enhance_info, str(character_grade), None)
                    if character_enhance == None:
                        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)
                    character_enhance = get(character_enhance, str(character_grade), None)
                    if character_enhance == None:
                        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)
                    default_character_piece = get(character_enhance, 'piece', None)
                    currencyManager.add_character('KNIGHT', result['id'], result['count'], default_character_piece, character_datas)
                    userdataManager.set_update(character_category)
            
            data = currencyManager.get_user_currency_data(db, req.uid)
            data['UserData'] = userdataManager.generate_user_save(db, req.uid)
            data['change'] = currencyManager.get_change()
            return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
   
    elif (req.type == 'RANDOM_WEAPON'):
        gacha_type = 'WEAPON'
        weapon_category = 'Weapon'
        
        
        random_weapon_list = []
        for i in range(0, req.extra_value):
            random_weapon_list.append({'grade':4, 'count':1})
        
        gacha_result = await __calculate_random(db, req.platform, gacha_type, random_weapon_list, req.v)
        
        if not gacha_result:
            return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_GACHA_RESULT, uid=req.uid)
        
        user_currency = currencyManager.use_currency(db, req.uid, req.type, req.extra_value)
        if not user_currency:
            data = currencyManager.get_user_currency_data(db, req.uid)
            return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
        else:
            weapon_datas = userdataManager.get(db, req.uid, weapon_category)
            if len(gacha_result) > 1:
                max_uid = 0
                if rune_datas:
                    max_uid = reduce(lambda x, y : x if int(x['UID']) > int(y['UID']) else y, rune_datas)
                    max_uid = max_uid['UID']
                for gacha_id in gacha_result:
                    max_uid = max_uid + 1
                    weapon_datas = currencyManager.add_weapon_def_uid('WEAPON', gacha_id['id'], gacha_id['count'], max_uid, weapon_datas)
                    userdataManager.set_update(weapon_category)
            else:
                weapon_datas = currencyManager.add_weapon('WEAPON', gacha_result[0]['id'], gacha_result[0]['count'], weapon_datas)
                userdataManager.set_update(weapon_category)

            data = currencyManager.get_user_currency_data(db, req.uid)
            data['UserData'] = userdataManager.generate_user_save(db, req.uid)
            data['change'] = currencyManager.get_change()
            return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
    elif (req.type == 'RANDOM_RUNE'):
        gacha_type = 'RUNE'
        rune_category = 'Rune'
       
        random_rune_list = []
        for i in range(0, req.extra_value):
            random_rune_list.append({'grade':3, 'count':1})
        
        gacha_result = await __calculate_random(db, req.platform, gacha_type, random_rune_list, req.v)
        
        if not gacha_result:
            return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_GACHA_RESULT, uid=req.uid)
        
        user_currency = currencyManager.use_currency(db, req.uid, req.type, req.extra_value)
        if not user_currency:
            data = currencyManager.get_user_currency_data(db, req.uid)
            return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
        else:
            rune_datas = userdataManager.get(db, req.uid, rune_category)
            if len(gacha_result) > 1:
                max_uid = 0
                if rune_datas:
                    max_uid = reduce(lambda x, y : x if int(x['UID']) > int(y['UID']) else y, rune_datas)
                    max_uid = max_uid['UID']
                for result in gacha_result:    
                    max_uid += 1
                    rune_datas = currencyManager.add_rune_def_uid('RUNE', result['id'], result['count'], max_uid, rune_datas)
                userdataManager.set_update(rune_category)
            else:
                rune_datas = currencyManager.add_rune('RUNE', gacha_result[0]['id'], gacha_result[0]['count'], rune_datas)
                userdataManager.set_update(rune_category)

            data = currencyManager.get_user_currency_data(db, req.uid)
            data['UserData'] = userdataManager.generate_user_save(db, req.uid)
            data['change'] = currencyManager.get_change()
            return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
        
    elif (req.type == 'RANDOM_KNIGHT_PIECE'):
        user_currency = currencyManager.use_currency(db, req.uid, req.type, 20)
        if not user_currency:
            data = currencyManager.get_user_currency_data(db, req.uid)
            return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
        else:
            currencyManager.add_dict('RANDOM_KNIGHT', 0, 1)
            if currencyManager.get_rewards():
                currencyManager.get_currency_rewards(db, req.uid)
            data = currencyManager.get_user_currency_data(db, req.uid)
            data['UserData'] = userdataManager.generate_user_save(db, req.uid)
            data['change'] = currencyManager.get_change()
            return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
        
    elif (req.type == 'RANDOM_WEAPON_PIECE'):
        user_currency = currencyManager.use_currency(db, req.uid, req.type, 20)
        if not user_currency:
            data = currencyManager.get_user_currency_data(db, req.uid)
            return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
        else:
            currencyManager.add_dict('RANDOM_WEAPON', 0, 1)
            if currencyManager.get_rewards():
                currencyManager.get_currency_rewards(db, req.uid)
            data = currencyManager.get_user_currency_data(db, req.uid)
            data['UserData'] = userdataManager.generate_user_save(db, req.uid)
            data['change'] = currencyManager.get_change()
            return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
        
    elif (req.type == 'RANDOM_RUNE_PIECE'):
        user_currency = currencyManager.use_currency(db, req.uid, req.type, 20)
        if not user_currency:
            data = currencyManager.get_user_currency_data(db, req.uid)
            return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)
        else:
            currencyManager.add_dict('RANDOM_RUNE', 0, 1)
            if currencyManager.get_rewards():
                currencyManager.get_currency_rewards(db, req.uid)
            data = currencyManager.get_user_currency_data(db, req.uid)
            data['UserData'] = userdataManager.generate_user_save(db, req.uid)
            data['change'] = currencyManager.get_change()
            return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
    else:
        return get_response(code=ResponseCode.RES_NOT_FOUND_GACHA_COST_TYPE, uid=req.uid)



#########################################################################################################################################################




async def __calculate_random(db:Session, platform:str, gacha_type:str, grades:list, version:int):
    result = []
    if gacha_type == 'PIECE':
        character_dict = await CacheController.character_gacha_info_map(db)
        character_platform_dict = get(character_dict, platform, None)
        # character_grade_target = get(character_platform_dict, str(grade['grade']), None)
        if not character_platform_dict:
            return None
        total_prob = __pre_total_random_value(character_platform_dict.values(), version)
        for grade in grades:
            character_info = __calculate_random_target_piece(character_platform_dict.values(), version, total_prob)
            if not character_info:
                return None
        
            result.append({'id':character_info['id'], 'count':grade['count'], 'grade':character_info['grade_value']})
    elif gacha_type == 'CHARACTER':
        character_dict = await CacheController.character_info_grade_list_map(db)
        for grade in grades:
            character_platform_dict = get(character_dict, platform, None)
            character_grade_target = get(character_platform_dict, str(grade['grade']), None)
            if not character_grade_target:
                return None
            character_id = __calculate_random_target(character_grade_target, version)
                       
            if not character_id:
                return None

            result.append({'id':character_id, 'count':grade['count'], 'grade':grade['grade']})
    elif gacha_type == 'WEAPON':
        weapon_dict = await CacheController.weapon_gacha_info_map(db)
        for grade in grades:
            weapon_platform_dict = get(weapon_dict, platform, None)
            weapon_grade_list = get(weapon_platform_dict, str(grade['grade']), None)
            if not weapon_grade_list:
                return None
            weapon_id = __calculate_random_target(weapon_grade_list, version)
            
            if not weapon_id:
                return None
            
            result.append({'id':weapon_id, 'count':grade['count'], 'grade':grade['grade']})
    elif gacha_type == 'RUNE':
        rune_dict = await CacheController.rune_gacha_info_map(db)
        for grade in grades:
            rune_platform_dict = get(rune_dict, platform, None)
            rune_grade_list = get(rune_platform_dict, str(grade['grade']), None)
            if not rune_grade_list:
                return None
            rune_id = __calculate_random_target(rune_grade_list, version)
            
            if not rune_id:
                return None
            
            result.append({'id':rune_id, 'count':grade['count'], 'grade':grade['grade']})
    else:
        return None
        
    
    return result


async def __calculate_random_special(db:Session, platform:str, gacha_type:str, grades:list, version:int, sp:int):
    result = []
    pickup_event_dict = await CacheController.pickup_event_info_map(db)
    pickup_event_dict = get(pickup_event_dict, platform, None)
    pickup_event_target = get(pickup_event_dict, str(sp), None)
    
    if gacha_type == 'PIECE':
        target_character_id = 0
        target_character_multiple = 1
        if pickup_event_target != None:
            target_character_id = get(pickup_event_target, 'pickup_id', 0)
            target_character_multiple = get(pickup_event_target, 'multiple', 1)
        
        character_dict = await CacheController.character_gacha_info_map(db)
        character_platform_dict = get(character_dict, platform, None)
        # character_grade_target = get(character_platform_dict, str(grade['grade']), None)
        if not character_platform_dict:
            return None
        total_prob = __pre_total_random_value_special(character_platform_dict.values(), version, target_character_id, target_character_multiple)
        for grade in grades:
            character_info = __calculate_random_target_special_piece(character_platform_dict.values(), version, target_character_id, target_character_multiple, total_prob)
            if not character_info:
                return None
        
            result.append({'id':character_info['id'], 'count':grade['count'], 'grade':character_info['grade_value']})

    elif gacha_type == 'CHARACTER':
        character_dict = await CacheController.character_info_grade_list_map(db)
        for grade in grades:
            character_platform_dict = get(character_dict, platform, None)
            character_grade_target = get(character_platform_dict, str(grade['grade']), None)
            if not character_grade_target:
                return None
            character_id = __calculate_random_target(character_grade_target, version)
                       
            if not character_id:
                return None

            result.append({'id':character_id, 'count':grade['count'], 'grade':grade['grade']})
    elif gacha_type == 'WEAPON':
        
        target_weapon_id = 0
        target_weapon_multiple = 1
        if pickup_event_target != None:
            target_weapon_id = get(pickup_event_target, 'weapon_id', 0)
            target_weapon_multiple = get(pickup_event_target, 'multiple', 1)
        
        weapon_dict = await CacheController.weapon_gacha_info_map(db)
        for grade in grades:
            weapon_platform_dict = get(weapon_dict, platform, None)
            weapon_grade_list = get(weapon_platform_dict, str(grade['grade']), None)
            if not weapon_grade_list:
                return None
            weapon_id = __calculate_random_target_special(weapon_grade_list, version, target_weapon_id, target_weapon_multiple)
            
            if not weapon_id:
                return None
            
            result.append({'id':weapon_id, 'count':grade['count'], 'grade':grade['grade']})
    else:
        return None
        
    
    return result


def __pre_total_random_value(targets:list, version:int):
    total_prob = 0
    for item in targets:
        prob = get(item, 'odds', None)
        ver = get(item, 'app_version', None)
        if not prob or not ver:
            return None
        if ver <= version:
            total_prob += prob
            
    return total_prob

def __calculate_random_target_piece(targets:list, version:int, total_prob:int):
    # 특정 범위의 값을 임의로 구한다.
    random_probs = random.randint(1, total_prob)

    for target in targets:
        prob = get(target, 'odds', None)
        ver = get(target, 'app_version', None)
        if not prob or not ver:
            return None
        
        if ver > version:
            continue
        
        if (random_probs - prob) <= 0:
            return target
        else:
            # 없는 경우는 갱신하자.
            random_probs = random_probs - prob
    
    return None


def __pre_total_random_value_special(targets:list, version:int, target_id:int, multiple:float):
    # 총 랜덤값을 구한다.
    total_prob = 0
    for item in targets:
        id = get(item, 'id', 0)
        prob = get(item, 'odds', None)
        ver = get(item, 'app_version', None)
        if not prob or not ver:
            return None
        if ver <= version:
            if id == target_id:
                total_prob += (prob * multiple)
            else:
                total_prob += prob
    return total_prob


def __calculate_random_target_special_piece(targets:list, version:int, target_id:int, multiple:float, total_prob:int):
    random_probs = random.randint(1, total_prob)
    for target in targets:
        id = get(target, 'id', 0)
        prob = get(target, 'odds', None)
        ver = get(target, 'app_version', None)
        if not prob or not ver:
            return None
        
        if ver > version:
            continue
        
        if target_id == id:
            prob = (prob * multiple)
        
        if (random_probs - prob) <= 0:
            return target
        else:
            # 없는 경우는 갱신하자.
            random_probs = random_probs - prob
    
    return None





def __calculate_random_target(targets:list, version:int):
    # 총 랜덤값을 구한다.
    total_prob = 0
    for item in targets:
        prob = get(item, 'odds', None)
        ver = get(item, 'app_version', None)
        if prob == None or ver == None:
            return None
        if ver <= version:
            total_prob += prob
        
    # 특정 범위의 값을 임의로 구한다.
    random_probs = random.randint(1, total_prob)

    for target in targets:
        prob = get(target, 'odds', None)
        ver = get(target, 'app_version', None)
        if not prob or not ver:
            return None
        
        if ver > version:
            continue
        
        if (random_probs - prob) <= 0:
            id = get(target, 'id', 0)
            return id
        else:
            # 없는 경우는 갱신하자.
            random_probs = random_probs - prob
    
    return None


def __calculate_random_target_special(targets:list, version:int, target_id:int, multiple:float):
    # 총 랜덤값을 구한다.
    total_prob = 0
    for item in targets:
        id = get(item, 'id', 0)
        prob = get(item, 'odds', None)
        ver = get(item, 'app_version', None)
        if not prob or not ver:
            return None
        if ver <= version:
            if id == target_id:
                total_prob += (prob * multiple)
            else:
                total_prob += prob
        
    # 특정 범위의 값을 임의로 구한다.
    random_probs = random.randint(1, total_prob)

    for target in targets:
        id = get(target, 'id', 0)
        prob = get(target, 'odds', None)
        ver = get(target, 'app_version', None)
        if not prob or not ver:
            return None
        
        if ver > version:
            continue
        
        if target_id == id:
            prob = (prob * multiple)
        
        if (random_probs - prob) <= 0:
            return id
        else:
            # 없는 경우는 갱신하자.
            random_probs = random_probs - prob
    
    return None


#특수한 목적으로 grade만 추출함.
def __calculate_random_grade(count:int, targets:list, version:int):
    result = []
    # 총 랜덤값을 구한다.
    total_prob = 0
    for item in targets:
        prob = get(item, 'rate', None)
        ver = get(item, 'app_version', None)
        if not prob or not ver:
            return None
        if ver <= version:
            total_prob += int(prob * 1000)
        
    for i in range(0, count):
        random_probs = random.randint(0, total_prob-1)

        if not targets:
            return None
        
        for target in targets:
            prob = get(target, 'rate', None)
            ver = get(target, 'app_version', None)
            count = get(target, 'count', None)
            if not prob or not ver:
                return None
            
            if ver > version:
                continue
            
            prob = prob*1000
            if random_probs - prob <= 0:
                grade = get(target, 'grade_value', None)
                if not grade:
                    return None
                result.append({'grade':grade, 'count':count})
                break
            else:
                # 없는 경우는 갱신하자.
                random_probs = random_probs - prob
    
    return result



#########################################################################################################################################################
# Expidition
#########################################################################################################################################################


async def game_expedition_start(req:BaseReqParam, db:Session):
    expedition_category = 'Expedition'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    expedition_datas = userdataManager.get(db, req.uid, expedition_category)
    
    now = datetime.now()
    today = int(now.strftime('%Y%m%d'))
    
    date_value = get(expedition_datas, 'ExpeditionDay', 0)
    
    if today != date_value:
        expedition_datas['ExpeditionDay'] = today
        userdataManager.set_update(expedition_category)
    else:
        return get_response(code=ResponseCode.RES_ALREADY_OPEN_EXPEDITION, uid=req.uid)
   
    result = currencyManager.use_currency(db, req.uid, 'COMPASS', 1) 
    if result == None:
        return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, uid=req.uid)

    data = currencyManager.get_user_currency_data(db, req.uid)
    data['UserData'] = userdataManager.generate_user_save(db, req.uid)
    data['change'] = currencyManager.get_change()
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)


#########################################################################################################################################################


async def game_expedition_end(req:ExpiditionEndReqParam, db:Session):
    expedition_category = 'Expedition'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    
    expedition_info_map = await CacheController.expedition_battle_info_map(db)
    expedition_info = get(expedition_info_map, req.platform, None)
    if not expedition_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_EXPEDITION_BATTLE_DATA, uid=req.uid)

    current_info = get(expedition_info, str(req.id), None)
    if current_info == None:
        return get_response(code=ResponseCode.RES_NOT_FOUND_EXPEDITION_BATTLE_DATA, uid=req.uid)
    
    expedition_difficulty_map = await CacheController.expedition_difficulty_info_map(db)
    expedition_difficulty_info = get(expedition_difficulty_map, req.platform, None)
    if not expedition_difficulty_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_EXPEDITION_DIFFICULTY_DATA, uid=req.uid)
    
    current_difficulty_info = expedition_difficulty_info[str(current_info['set_id'])]
    if current_difficulty_info == None:
        return get_response(code=ResponseCode.RES_NOT_FOUND_EXPEDITION_DIFFICULTY_DATA, uid=req.uid)
    
    expedition_datas = userdataManager.get(db, req.uid, expedition_category)
    
    best_score = expedition_datas['BestScore']
    
    if current_info['type'] == 'BATTLE':
        score = current_info['score']
        multiple = float(current_difficulty_info['multiple'])
        current_seq = current_info['seq']
        
        if current_seq == 1:
            current_score = score * multiple
            if int(current_score) > best_score:
                expedition_datas['BestScore'] = int(current_score)
        else:
            current_score = current_score + (score * multiple)
        
        expedition_datas['CurrentStep'] = current_seq +  1
        expedition_datas['CurScore'] = current_score
        expedition_datas['Multiple'] = multiple
        userdataManager.set_update(expedition_category)
    elif current_info['type'] == 'BOSS':
        score = current_info['score']
        multiple = float(current_difficulty_info['multiple'])
        current_seq = current_info['seq']
        current_score = score * multiple
        if int(current_score) > best_score:
            expedition_datas['BestScore'] = int(current_score)
        else:
            current_score = current_score + (score * multiple)
        
        expedition_datas['CurrentStep'] = current_seq +  1
        expedition_datas['CurScore'] = current_score
        expedition_datas['Multiple'] = multiple
        userdataManager.set_update(expedition_category)
        
        if not req.otherData:
            current_score = current_score + score
            if int(current_score * multiple) > best_score:
                expedition_datas['BestScore'] = int(current_score * multiple)
            
        
    elif current_info['type'] == 'RESURRECTION':
        multiple = float(current_difficulty_info['multiple'])
        current_seq = current_info['seq']
        
        expedition_datas['CurrentStep'] = current_seq +  1
        expedition_datas['Multiple'] = multiple
        userdataManager.set_update(expedition_category)
    elif current_info['type'] == 'HEAL':
        multiple = float(current_difficulty_info['multiple'])
        current_seq = current_info['seq']
        
        expedition_datas['CurrentStep'] = current_seq +  1
        expedition_datas['Multiple'] = multiple
        userdataManager.set_update(expedition_category)
    else:
        return get_response(code=ResponseCode.RES_INVALID_EXPEDITION_TYPE, uid=req.uid)
    
    
    expedition_datas['OwnCharacterStats'] = req.characterData
    expedition_datas['OtherCharacterStats'] = req.otherData
    userdataManager.set_update(expedition_category)
    
    
    data = currencyManager.get_user_currency_data(db, req.uid)
    data['UserData'] = userdataManager.generate_user_save(db, req.uid)
    data['change'] = currencyManager.get_change()
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)


#########################################################################################################################################################


async def game_expedition_sweep(req:ExpiditionSweepReqParam, db:Session):
    expedition_category = 'Expedition'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    
    

    data = currencyManager.get_user_currency_data(db, req.uid)
    data['UserData'] = userdataManager.generate_user_save(db, req.uid)
    data['change'] = currencyManager.get_change()
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)


#########################################################################################################################################################


async def game_expedition_gacha(req:CardGachaReqParam, db:Session):
    expedition_category = 'Expedition'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    expedition_grade_prob = await CacheController.expedition_card_info_list(db)
    expedition_platform_grade = get(expedition_grade_prob, req.platform, None)
    if not expedition_platform_grade:
        return 
    
    expedition_datas = userdataManager.get(db, req.uid, expedition_category)
    
    available_card_list = get(expedition_datas, 'AvailableCardList', [])
    
    card_ids = []
    
    if not req.first:
        currencyManager.use_currency(db, req.uid, 'BUFF_COIN', 10)

    card_ids = __generate_card_gacha(expedition_platform_grade, req.grade, req.count)
    
    
    data = currencyManager.get_user_currency_data(db, req.uid)
    data['change'] = currencyManager.get_change()
    data['cards'] = card_ids
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)



def __generate_card_gacha(gacha_card_map:dict, grade:int, count:int=3):
    result_card = []
    target_card_list = []
    
    for i in range(1, grade+1):
        target_card_list = target_card_list + gacha_card_map[str(i)]
    
    total_prob = 0
    for target in target_card_list:
        total_prob += target['odds']
        
    for i in range(0, count):
        random_prob = random.randint(0, total_prob - 1)
        
        for target in target_card_list:
            if random_prob - target['odds'] < 0:
                result_card.append(target['id'])
                break
            else:
                random_prob -= target['odds']
    
    return result_card
        

#########################################################################################################################################################


async def game_expedition_card_select(req:CardGachaSelectReqParam, db:Session):
    expedition_category = 'Expedition'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    expedition_datas = userdataManager.get(db, req.uid, expedition_category)
    
    available_card_list = get(expedition_datas, 'AvailableCardList', [])
    
    available_card_list = available_card_list + req.ids
    expedition_datas['AvailableCardList'] = available_card_list
    userdataManager.set_update(expedition_category)
    
    data = currencyManager.get_user_currency_data(db, req.uid)
    data['UserData'] = userdataManager.generate_user_save(db, req.uid)
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)


#########################################################################################################################################################


async def game_expedition_card_giveup(req:CardGachaGiveupReqParam, db:Session):
   
    currencyManager = CurrencyManager()
    
    # 우선 사용자의 ExpeditionID를 보고 변경시에는 무료로 뽑이서 알려준다.
    expedition_card_map = await CacheController.expedition_card_info_map(db)
    expedition_card = get(expedition_card_map, req.platform, None)
    if not expedition_card:
        return
    
    total_cost = 0
    
    if req.ids:
        for card_id in req.ids:
            card_info = get(expedition_card, str(card_id), None)
            if card_info == None:
                continue
            total_cost += card_info['sell_cost']
    
    
    currencyManager.add_dict('BUFF_COIN', 0, total_cost)

    data = currencyManager.get_user_currency_data(db, req.uid)
    data['change'] = currencyManager.get_change()
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)



