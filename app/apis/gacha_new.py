from sqlalchemy.orm import Session
from app.classes.CurrencyManager import CurrencyManager
from app.classes.UserDataManager import UserDataManager
from functools import reduce
from pydantic import BaseModel
from random import sample, randrange
from app.params.ReqParam import BaseReqParam
from app.params.CurrencyReqParam import *
from app.cache import CacheController
from app.params.ResParam import get_response, ResponseCode
import pydash

async def get_parsheet(type, index):
   if(type == 'CHARACTER'):
       parsheet = (await CacheController.get_c_parsheet())[str(index)]
   elif(type == 'WEAPON'):
       parsheet = (await CacheController.get_w_parsheet())[str(index)]
   return parsheet


async def get_user_parsheet_info(db, um ,uid, prefix):
    userdataManager = um
    data = userdataManager.get(db, uid, 'User')

    parsheet_num = pydash.get(data, f'{prefix}ParsheetNum')
    start_index = pydash.get(data, f'{prefix}StartIndex')
    current_index = pydash.get(data, f'{prefix}CurrentIndex')
    
    info = {
        'parsheet_num': parsheet_num ,
        'start_index': start_index,
        'current_index': current_index,
    }
    p = await (getattr(CacheController, f'get_{prefix}_parsheet'))()
    parsheet_length = len(p['0'])
    while(not parsheet_num and not start_index and not current_index):
        parsheet_num = randrange(len(p))
        index = randrange(parsheet_length)
        info['parsheet_num'] = parsheet_num 
        info['start_index'] = index
        info['current_index'] = (index + 1) % parsheet_length
        set_user_parsheet_info(db, um, uid, info, prefix)
        parsheet_num = info['parsheet_num']
        start_index = info['start_index']
        current_index= info['current_index']
        

    return info


def set_user_parsheet_info(db, um, uid, parsheet_info_dict, prefix):
    userdataManager = um
    userdataManager.change_user_data_value(db, uid, 'User', f'{prefix}ParsheetNum', parsheet_info_dict['parsheet_num'])
    userdataManager.change_user_data_value(db, uid, 'User', f'{prefix}StartIndex', parsheet_info_dict['start_index'])
    userdataManager.change_user_data_value(db, uid, 'User', f'{prefix}CurrentIndex', parsheet_info_dict['current_index'])
    return parsheet_info_dict


def pick_items(start, count, array):
    length = len(array)
    end = start + count
    if end <= length:
        return array[start:end]
    else:
        return array[start:length] + array[:end - length]


def do_gacha(parsheet, start_index, count):
    
    parsheet_length = len(parsheet)
    end_index = (start_index + count) % parsheet_length
    items = pick_items(start_index, count, parsheet)
    return items, end_index


def dict_by_gacha_type (gacha_type, info_map, x, special_dict=None):
   
   consts = {
       'KNIGHT_PIECE': {
            'filter_func': lambda y: int(y['grade_value']) == (int(x / 1000)),
            'reward_amount': 20 if x % 10 == 4 else x % 10, # 아이디 끝자리 4면 20조각 지급 나머진 그대로 지급
            'special_id': special_dict['pickup_id'] if special_dict else None
       },
       'WEAPON': {
            'filter_func': lambda y: int(y['grade_value']) == x,
            'reward_amount': 1,
            'special_id': special_dict['weapon_id'] if special_dict else None
       },
   }
   consts = consts[gacha_type]
   return {
        "reward_type": gacha_type,
        "reward_key": pydash
            .chain(info_map)
            .filter(consts['filter_func'])
            .map(lambda x: [x] * int(special_dict['multiple']) if x['id'] == consts['special_id'] else [x] * x['odds'])
            .flatten()
            .sample()
            .get('id')
            .value(),
        "reward_amount": consts['reward_amount'] 
    }


async def gacha(req:GachaReqParam, db:Session):

    consts = {
        'CHARACTER': {
            'reward_type': 'KNIGHT_PIECE',
            'category': 'Character',
            'cache_controller_func_name': 'character_info_map',
            'currency_manager_func_name': 'add_character_piece',
            'bonus': 'GkCount',
            'prefix': 'c'
        },
        'WEAPON': {
            'reward_type': 'WEAPON',
            'category': 'Weapon',
            'cache_controller_func_name': 'weapon_info_map',
            'currency_manager_func_name': 'add_weapon',
            'bonus': 'GwCount',
            'prefix': 'w'
        }
    }
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()


    info = pydash.get(await CacheController.gacha_cost_info_map(db), f'{req.platform}.{str(req.id)}')

    if not info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_GACHA_COST_DATA, uid=req.uid)

    price_type = info['price_type']
    gacha_key = info['gacha_key']
    cost = info['cost']

    gacha_type = gacha_key.split('_')[0] # CHARACTER or WEAPON
    gacha_count = int(gacha_key.split('_')[2]) # 가챠키에서 횟수 바로 뽑아버리자 (CHARACTER_JEWEL_10)


    consts = consts[gacha_type]
    reward_type = consts['reward_type']
    category = consts['category']
    info_map = pydash.get((await getattr(CacheController, consts['cache_controller_func_name'])(db)), req.platform)

    if not price_type:
        return get_response(code=ResponseCode.RES_INVALID_CURRENCY_TYPE, uid=req.uid)
    
    # 재화 소모
    if not currencyManager.use_currency(db, req.uid, price_type, cost):
        data = currencyManager.get_user_currency_data(db, req.uid)
        return get_response(code=ResponseCode.RES_CURRENCY_NOT_ENOUGH, data=data, uid=req.uid)

    # 파시트 가져오기
    parsheet_info = await get_user_parsheet_info(db, userdataManager, req.uid, consts['prefix'])
    parsheet = await get_parsheet(gacha_type, parsheet_info['parsheet_num'])

    character_enhance_info = pydash.get((await CacheController.character_enhance_info_map(db)), req.platform)
    if not character_enhance_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_ENHANCE_DATA, uid=req.uid)
    
    #스페셜가차 처리
    is_special = True if req.extra_value > 0 else False
    if is_special:
        pickup_event_dict = pydash.get((await CacheController.pickup_event_info_map(db)), f'{req.platform}.{str(req.extra_value)}')
    
    start = parsheet_info['current_index']
    end = parsheet_info['current_index'] + gacha_count
    x = parsheet_info['start_index']

    if start <= x < end or (start > (end % len(parsheet)) and (0 <= x <= end % len(parsheet) or start <= x <= len(parsheet))):

        gacha_count_current = x - start + 1 if x > start else ( 0 if x == start else x + (len(parsheet) - start + 1))
        gacha_count_next = gacha_count - gacha_count_current
        
        gacha_result1, end_index = do_gacha(parsheet, parsheet_info['current_index'], gacha_count_current)

        p = await (getattr(CacheController, f"get_{consts['prefix']}_parsheet"))()
        
        parsheet_num = sample(list(filter(lambda x: x != parsheet_info['parsheet_num'], range(len(p)))), 1)[0]
        
        parsheet = p[str(parsheet_num)]
        parsheet_length = len(parsheet)
        index = randrange(parsheet_length)
        
        parsheet_info['parsheet_num'] = parsheet_num 
        parsheet_info['start_index'] = index 
        parsheet_info['current_index'] = (index + 1) % parsheet_length 

        set_user_parsheet_info(db, userdataManager, req.uid, {
            'parsheet_num': parsheet_info['parsheet_num'] ,
            'start_index': parsheet_info['start_index'],
            'current_index': parsheet_info['current_index'],
        }, consts['prefix'])

        gacha_result2, end_index = do_gacha(parsheet, parsheet_info['current_index'], gacha_count_next)

        gacha_result = gacha_result1 + gacha_result2

    else:
        gacha_result, end_index = do_gacha(parsheet, parsheet_info['current_index'], gacha_count)

    gacha_result = pydash.chain(gacha_result) \
    .map(lambda x: dict_by_gacha_type(reward_type, info_map, x, pickup_event_dict if is_special else None)) \
    .value()

    data = userdataManager.get(db, req.uid, category)

    key_by_data = pydash.chain(data).key_by('ID').value()

    # 데이터 추가
    for gacha_info in gacha_result:
        grade = str(round(gacha_info['reward_key'] / 10000))
        need_character_piece = pydash.get(character_enhance_info, f'{grade}.{grade}.piece') 
        is_piece = reward_type == 'KNIGHT_PIECE'
        if is_piece:
            is_not_exist = not key_by_data[gacha_info['reward_key']]['Level']
            gte_than_need_piece = gacha_info['reward_amount'] >= need_character_piece
        
        if is_piece and is_not_exist and gte_than_need_piece:
            userdataManager.set_update('CHARACTER')
            currencyManager.add_character('KNIGHT', gacha_info['reward_key'], 1, need_character_piece, data)
        else:
            getattr(currencyManager, consts['currency_manager_func_name']) \
            (consts['reward_type'], gacha_info['reward_key'], gacha_info['reward_amount'], data)
    
    if gacha_type =='CHARACTER':
        userdataManager.add_user_data_value(db, req.uid, 'User', 'KPickCount', gacha_count)

    userdataManager.add_user_data_value(db, req.uid, 'User', consts['bonus'], gacha_count)
    userdataManager.change_user_data_value(db, req.uid, 'User', f"{consts['prefix']}CurrentIndex", end_index)
    
    userdataManager.set_update(category)

    data = currencyManager.get_user_currency_data(db, req.uid)
    data['UserData'] = userdataManager.generate_user_save(db, req.uid)
    data['change'] = currencyManager.get_change()
    data['gacha_result'] = gacha_result

    return get_response(code=ResponseCode.RES_SUCCESS, uid=req.uid, data=data)
