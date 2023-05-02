# -*- coding: utf-8 -*-
import os
import math
from loguru import logger
from functools import reduce
from sqlalchemy.orm import Session
from app.params.ResParam import get_response, ResponseCode
from app.params.CurrencyReqParam import *
from app.util.util import get
from app.config.settings import Constant
from app.cache import CacheController
from app.crud import crud_user_members
from app.classes.CurrencyManager import CurrencyManager
from app.classes.UserDataManager import UserDataManager


## Set Timezone
os.environ['TZ'] = 'UTC'



async def control_user_level(req:CurrencyUserLevelReqParam, db:Session):
    user_category = 'User'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    level_up_dict = await CacheController.level_up_info_map(db)
    level_up_info = get(level_up_dict, req.platform)
    if not level_up_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_UP_DATA, uid=req.uid)
        
    user_datas = userdataManager.get(db, req.uid, user_category)
    
    if user_datas['Level'] >= req.id:
        return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_UP_INFO_DATA, uid=req.uid)
    
    current_level = user_datas['Level']
    user_datas['Level'] = req.id
    userdataManager.set_update(user_category)
    await crud_user_members.update_level(db, req.uid, req.id)
    
    # DB상으로 3개이지만 마지막을 무시하도록 설정함.
    for level in range(current_level + 1, req.id + 1):
        info = get(level_up_info, str(level))
        if not info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_UP_REWARD_DATA, uid=req.uid)
        for item in range(1,3):
            reward_type = get(info, 'reward_type_'+str(item))
            if (not reward_type):
                continue
            
            reward_count = get(info, 'reward_amount_'+str(item), 0)
            currencyManager.add_dict(reward_type, 0, reward_count)

    if currencyManager.get_rewards():
        currencyManager.get_currency_rewards(db, req.uid)
    
    data = currencyManager.get_user_currency_data(db, req.uid)
    data['UserData'] = userdataManager.generate_user_save(db, req.uid)
    data['change'] = currencyManager.get_change()
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
        
   



#########################################################################################################################################################




async def control_character_level(req:CurrencyCharacterLevelReqParam, db:Session):
    character_category = 'Character'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    character_level_dict = await CacheController.character_level_info_map(db)
    character_level_info = get(character_level_dict, req.platform)
    if not character_level_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_LEVEL_UP_DATA, uid=req.uid)
    
    character_enhance_dict = await CacheController.character_enhance_info_map(db)
    character_enhance_info = get(character_enhance_dict, req.platform)
    if not character_enhance_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_ENHANCE_DATA, uid=req.uid)
    
    character_data_dict = await CacheController.character_info_map(db)
    character_data_info = get(character_data_dict, req.platform)
    if not character_data_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)

    character_datas = userdataManager.get(db, req.uid, character_category)
    
    find_character = None
    
    for character_data in character_datas:
        character_id = get(character_data, 'ID', None)
        if not character_id:
            return get_response(code=ResponseCode.RES_INVALID_CURRENCY_TYPE, uid=req.uid)
        
        if character_id != req.id:
            continue
        
        if character_id == req.id:
            find_character = character_data
            break
        
    if not find_character:
        return get_response(code=ResponseCode.RES_NOT_FOUND_USER_CHARACTER_DATA, uid=req.uid)
        
    find_character_level = get(find_character, 'Level', None)
    if find_character_level == None:
        return get_response(code=ResponseCode.RES_NOT_FOUND_USER_CHARACTER_LEVEL_DATA, uid=req.uid)
    
    find_character_exp = get(find_character, 'Exp', None)
    if find_character_exp == None:
        return get_response(code=ResponseCode.RES_NOT_FOUND_USER_CHARACTER_LEVEL_DATA, uid=req.uid)
    
    
    find_character_data = get(character_data_info, str(find_character['ID']), None)
    
    find_character_grade = get(find_character_data, 'grade_value', None)
    
    find_character_star = get(find_character, 'Star', None)
    max_star  = get(character_enhance_info, str(find_character_grade),  None)
    max_data = get(max_star, str(find_character_star), None)
    
    max_level = get(max_data, 'max_level', None)
    
    if (find_character_level != req.extra_value) or ((req.extra_value + 1) > (max_level)) or (req.extra_value_2nd  > (max_level)):
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_LEVEL_MISMATCH, uid=req.uid)
    
    
    total_need_exp_item = 0
    total_need_coin = 0

    for level_value in range(req.extra_value, req.extra_value_2nd):
        info = get(character_level_info, str(level_value))
        if not info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_LEVEL_UP_INFO_DATA, uid=req.uid)
        
        coin = get(info, 'coin', None)
        exp_item = get(info, 'exp_item', None)
        # max_exp = get(info, 'max_exp', None)
        
        # if (coin == None) or (exp_item == None) or (max_exp == None):
        if (coin == None) or (exp_item == None):
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_LEVEL_UP_DATA, uid=req.uid)
        
        # exp_rate = float(find_character_exp / float(max_exp))
        # need_coin = math.floor(coin * (1 - exp_rate))
        # need_exp_item = math.floor(exp_item * ( 1 - exp_rate))
        
        find_character_exp = 0
        
        total_need_coin += coin
        total_need_exp_item += exp_item
    
    
    result = currencyManager.use_currency(db, req.uid, 'COIN', total_need_coin)
    if result == None:
        return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, uid=req.uid)
    result = currencyManager.use_currency(db, req.uid, 'EXPITEM', total_need_exp_item)
    if result == None:
        # 여기서 에러 나면 다시 넣어줘야 할듯
        currencyManager.add_dict('COIN', 0, total_need_coin)
        return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, uid=req.uid)
    
    if currencyManager.get_rewards():
        currencyManager.get_currency_rewards(db, req.uid)
    
    find_character['Level'] = req.extra_value_2nd
    find_character['Exp'] = 0
    userdataManager.set_update(character_category)
    
    
    data = currencyManager.get_user_currency_data(db, req.uid)
    data['UserData'] = userdataManager.generate_user_save(db, req.uid)
    data['change'] = currencyManager.get_change()
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
    



#########################################################################################################################################################




async def control_character_enhance(req:CurrencyCharacterEnhanceReqParam, db:Session):
    character_category = 'Character'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    character_enhance_dict = await CacheController.character_enhance_info_map(db)
    character_enhance_info = get(character_enhance_dict, req.platform)
    if not character_enhance_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_ENHANCE_DATA, uid=req.uid)
    
    character_data_dict = await CacheController.character_info_map(db)
    character_data_info = get(character_data_dict, req.platform)
    if not character_data_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)

    character_datas = userdataManager.get(db, req.uid, character_category)
    
    find_character = None
    
    for character_data in character_datas:
        character_id = get(character_data, 'ID', None)
        if not character_id:
            return get_response(code=ResponseCode.RES_INVALID_CURRENCY_TYPE, uid=req.uid)
        
        if character_id != req.id:
            continue
        
        if character_id == req.id:
            find_character = character_data
            break
        
    if not find_character:
        return get_response(code=ResponseCode.RES_NOT_FOUND_USER_CHARACTER_DATA, uid=req.uid)
        
    find_character_level = get(find_character, 'Level', None)
    if find_character_level == None:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_ENHANCE_DATA, uid=req.uid)
    
    find_character_piece = get(find_character, 'Piece', None)
    if find_character_piece == None:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_ENHANCE_DATA, uid=req.uid)
    
    find_character_star = get(find_character, 'Star', None)
    if find_character_star == None:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_ENHANCE_DATA, uid=req.uid)
    
    #1차 조건 캐릭터 완성
    if (find_character_level == 0):
        character_info = character_data_info[str(req.id)]
        character_grade = get(character_info, 'grade_value', None)
        if not character_grade:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)
        
        temp = get(character_enhance_info, str(character_grade), None)
        if temp == None:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)
        
        temp = get(temp, str(character_grade), None)
        if temp == None:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)
        
        character_enhance = temp
        need_character_piece = get(character_enhance, 'piece', None)
        if not need_character_piece:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)
        if find_character_piece >= need_character_piece:
            find_character['Level'] = 1
            find_character['Piece'] = find_character['Piece'] - need_character_piece
            userdataManager.set_update(character_category)
        else:
            return get_response(code=ResponseCode.RES_NOT_ENOUGH_CHARACTER_PIECE, uid=req.uid)
        
    elif (find_character_level > 0):
        character_info = character_data_info[str(req.id)]
        character_grade = get(character_info, 'grade_value', None)
        if not character_grade:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)
        
        temp = get(character_enhance_info, str(character_grade), None)
        if temp == None:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)
        
        temp = get(temp, str(find_character_star+1), None)
        if temp == None:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)
        
        character_enhance = temp
        need_character_piece = get(character_enhance, 'piece', None)
        if not need_character_piece:
            return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)
        
        if find_character_piece >= need_character_piece:
            find_character['Star'] = find_character['Star'] + 1
            find_character['Piece'] = find_character['Piece'] - need_character_piece
            userdataManager.set_update(character_category)
        else:
            return get_response(code=ResponseCode.RES_NOT_ENOUGH_CHARACTER_PIECE, uid=req.uid)
    
    data = currencyManager.get_user_currency_data(db, req.uid)
    data['UserData'] = userdataManager.generate_user_save(db, req.uid)
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)


#########################################################################################################################################################




async def control_weapon_level(req:CurrencyWeaponLevelReqParam, db:Session):
    weapon_category = 'Weapon'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    weapon_dict = await CacheController.weapon_info_map(db)
    weapon_info = get(weapon_dict, req.platform)
    if not weapon_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_LEVEL_UP_DATA, uid=req.uid)
    
    
    weapon_level_dict = await CacheController.weapon_level_info_map(db)
    weapon_level_info = get(weapon_level_dict, req.platform)
    if not weapon_level_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_LEVEL_UP_DATA, uid=req.uid)
    

    weapon_datas = userdataManager.get(db, req.uid, weapon_category)
    
    find_weapon = None
    
    if weapon_datas:
        for weapon_data in weapon_datas:
            if weapon_data['UID'] == req.id:
                find_weapon = weapon_data
                break
    else:
        return get_response(code=ResponseCode.RES_NOT_FOUND_USER_WEAPON_DATA, uid=req.uid)
    
    
    
    info = get(weapon_info, str(find_weapon['ID']))
    if not info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_USER_WEAPON_ID_DATA, uid=req.uid)
    
    weapon_level = get(find_weapon, 'Level', None)
    weapon_max_level = get(info, 'max_lv', None)
    weapon_inc_max_lv = get(info, 'inc_max_lv', None)
    
    weapon_reinforce = get(find_weapon, 'Reinforce', None)
    
    if (weapon_level != None) and (req.extra_value > weapon_level) and (req.extra_value <= (weapon_max_level + (weapon_reinforce * weapon_inc_max_lv))):
        
        current_level_info = get(weapon_level_info, str(weapon_level), None)
        next_level_info = get(weapon_level_info, str(weapon_level+1), None)
        if not current_level_info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_USER_WEAPON_DATA, uid=req.uid)
        
        if not next_level_info:
            return get_response(code=ResponseCode.RES_NOT_WEAPON_MAX_LEVEL, uid=req.uid)
        
        
        coin_amount = get(current_level_info, 'coin', None)
        powder_amount = get(current_level_info, 'powder', None)
        if(coin_amount != None) and (powder_amount != None):
            
            result = currencyManager.use_currency(db, req.uid, 'COIN', coin_amount)
            if result == None:
                return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, uid=req.uid)
            
            result = currencyManager.use_currency(db, req.uid, 'POWDER', powder_amount)
            if result != None :
                find_weapon['Level'] = req.extra_value
                userdataManager.set_update(weapon_category)

                data = currencyManager.get_user_currency_data(db, req.uid)
                data['UserData'] = userdataManager.generate_user_save(db, req.uid)
                data['change'] = currencyManager.get_change()
                return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
            else:
                return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, uid=req.uid)
    else:
        return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_LEVEL_UP_INFO_DATA, uid=req.uid)
    
        
   



#########################################################################################################################################################


async def control_weapon_sell(req:CurrencyWeaponSellReqParam, db:Session):
    weapon_category = 'Weapon'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    weapon_dict = await CacheController.weapon_info_map(db)
    weapon_info = get(weapon_dict, req.platform)
    if not weapon_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_DATA, uid=req.uid)
    
    weapon_level_dict = await CacheController.weapon_level_info_map(db)
    weapon_level_info = get(weapon_level_dict, req.platform)
    if not weapon_level_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_LEVEL_UP_DATA, uid=req.uid)
    
    game_config_dict = await CacheController.game_config_info_map(db)
    game_config_info = get(game_config_dict, req.platform, None)
    if not game_config_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_UP_DATA, uid=req.uid)
    
    config_info = get(game_config_info, '36', 0)
    if not config_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_GAME_CONFIG_VALUE, uid=req.uid)
    
    rate_value = float(get(config_info, 'value', 0))
    
    weapon_datas = userdataManager.get(db, req.uid, weapon_category)
    
    find_weapon = None
    
    if weapon_datas:
        for weapon_data in weapon_datas:
            if weapon_data['UID'] == req.id:
                find_weapon = weapon_data
                break
    else:
        return get_response(code=ResponseCode.RES_NOT_FOUND_USER_WEAPON_DATA, uid=req.uid)
    
    info = get(weapon_info, str(find_weapon['ID']))
    if not info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_USER_WEAPON_ID_DATA, uid=req.uid)
    
    sell_cost_type = get(info, 'sell_cost_type', None)
    sell_amount = get(info, 'sell_amount', None)
    
    
    weapon_level = 1
    
    if sell_cost_type and sell_amount:
        # 이미 찾았으니 삭제만 하면됨.
        for i in range(len(weapon_datas)):
            if weapon_datas[i]['UID'] == req.id:
                weapon_level = weapon_datas[i]['Level']
                del weapon_datas[i]
                userdataManager.set_update(weapon_category)
                break
        
        current_level_info = get(weapon_level_info, str(weapon_level), None)
        if not current_level_info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_USER_WEAPON_DATA, uid=req.uid)
        cost_amount = get(current_level_info, 'powder_sum', 0)
        sell_amount = sell_amount + int(cost_amount*rate_value)
        currencyManager.add_dict(sell_cost_type, 0, sell_amount)
        
        if currencyManager.get_rewards():
            currencyManager.get_currency_rewards(db, req.uid)

        data = currencyManager.get_user_currency_data(db, req.uid)
        data['UserData'] = userdataManager.generate_user_save(db, req.uid)
        data['change'] = currencyManager.get_change()
        return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)
    else:
        return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_LEVEL_UP_DATA, uid=req.uid)
    

#########################################################################################################################################################



async def control_weapon_list_sell(req:CurrencyWeaponListSellReqParam, db:Session):
    weapon_category = 'Weapon'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    weapon_dict = await CacheController.weapon_info_map(db)
    weapon_info = get(weapon_dict, req.platform)
    if not weapon_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_UP_DATA, uid=req.uid)
    
    weapon_level_dict = await CacheController.weapon_level_info_map(db)
    weapon_level_info = get(weapon_level_dict, req.platform)
    if not weapon_level_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_LEVEL_UP_DATA, uid=req.uid)
    
    game_config_dict = await CacheController.game_config_info_map(db)
    game_config_info = get(game_config_dict, req.platform, None)
    if not game_config_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_UP_DATA, uid=req.uid)
    
    config_info = get(game_config_info, '36', 0)
    if not config_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_GAME_CONFIG_VALUE, uid=req.uid)
    
    rate_value = float(get(config_info, 'value', 0))
    
    weapon_datas = userdataManager.get(db, req.uid, weapon_category)
    
    find_weapons = []
    
    if weapon_datas:
        for weapon_data in weapon_datas:
            if weapon_data['UID'] in req.ids:
                find_weapons.append(weapon_data)
    else:
        return get_response(code=ResponseCode.RES_NOT_FOUND_USER_WEAPON_DATA, uid=req.uid)
    
    
    # 사이즈가 다르면 값이 다르게 되어 있다고 판단
    if len(find_weapons) != len(req.ids):
        return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_ID_LENGTH_MISMATCH, uid=req.uid)
    
    
    total_sell_amount = 0
    
    for find_weapon in find_weapons:
        info = get(weapon_info, str(find_weapon['ID']))
        if not info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_USER_WEAPON_DATA, uid=req.uid)
        
        sell_cost_type = get(info, 'sell_cost_type', None)
        sell_amount = get(info, 'sell_amount', None)
        # 반환타입은 고정으로 생각한다.(추가될 경우 로직 변경 필요)
        if sell_cost_type and sell_amount:
            total_sell_amount += sell_amount
        else:
            return get_response(code=ResponseCode.RES_NOT_FOUND_WEAPON_SELL_DATA, uid=req.uid)
    
    
    del_weapon_datas = list(filter(lambda x: x['UID'] in req.ids , weapon_datas))
    
    for del_weapon in del_weapon_datas:
        info = get(weapon_info, str(find_weapon['ID']))
        cost_amount = get(info, 'cost_amount', None)
        weapon_level = get(del_weapon, 'Level', 1)
        current_level_info = get(weapon_level_info, str(weapon_level), None)
        if not current_level_info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_USER_WEAPON_DATA, uid=req.uid)
        cost_amount = get(current_level_info, 'powder_sum', 0)
        total_sell_amount += int(cost_amount*rate_value)
        
        
    
    ## 좋은 방법
    userdataManager.set(weapon_category, list(filter(lambda x: x['UID'] not in req.ids , weapon_datas)))
    userdataManager.set_update(weapon_category)
    
    currencyManager.add_dict(sell_cost_type, 0, total_sell_amount)
    if currencyManager.get_rewards():
        currencyManager.get_currency_rewards(db, req.uid)

    data = currencyManager.get_user_currency_data(db, req.uid)
    data['UserData'] = userdataManager.generate_user_save(db, req.uid)
    data['change'] = currencyManager.get_change()
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=req.uid)

        
    
    

#########################################################################################################################################################

