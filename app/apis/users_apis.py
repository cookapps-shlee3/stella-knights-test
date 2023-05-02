# -*- coding: utf-8 -*-
import json
import time
from fastapi import Request
from loguru import logger
from sqlalchemy.orm import Session
from app.params.ResParam import get_response, ResponseCode
from app.config.settings import Constant
from app.params.ReqParam import BaseReqParam, DataSaveReqParam, NicknameSaveReqParam, BattleInfosReqParam, BattleSaveReqParam, CouponReqParam, ReviewReqParam
from app.crud import crud_user_members, crud_user_server, crud_user_data, crud_postbox, crud_coupon, crud_retention, crud_user_platforms, crud_user_devices
from app.crud.cache import crud_user_currency
from app.util.util import get
from app.config.settings import Constant
from app.config.settings import settings
from app.cache import CacheController
from app.classes.CurrencyManager import CurrencyManager
from app.rabbit_mq import rabbit_api


def __get_currency(db:Session, uid:int, type:str, amount:int, change:list):
    user_currency = crud_user_currency.update_get_user_currency(db, uid, type, amount)
    # 추가로 로그를 남길수 있는 방법을 생각해 보자.
    return user_currency

# 처음에 확인해서 데이터가 없는 경우에 여기서 미리 생성을 해주면 추후에는 업데이트만 할 수 있도록 변경이 가능해 진다.
# 기능 추가 여기에서 currency에 대한 정보들을 전부 반환하도록 수정한다.
def __init_currency(db:Session, uid:int):
    if CurrencyManager.get_currency_type():
        for item in CurrencyManager.get_currency_type():
            if not crud_user_currency.get(db, uid, item):
                if item == 'BREAD':
                    crud_user_currency.insert(db, uid, item, Constant.INIT_BREAD_COUNT)
                elif item == 'PTICKET':
                    crud_user_currency.insert(db, uid, item, Constant.INIT_PTICKET_COUNT)
                else:
                    crud_user_currency.insert(db, uid, item, 0)


async def users_lobby(req:BaseReqParam, db:Session):
    
    user_member_info = await crud_user_members.get(db, req.uid)
    if not user_member_info:
        return
    
    # if user_member_info.is_terms_agree == 0:
    #     base_uid = crud_user_server.base_uid(db, req.uid)
    #     server_infos = crud_user_server.get_all(db, base_uid.uid)
    #     if server_infos and (len(server_infos) > 0):
    #         uids = []
    #         for info in server_infos:
    #             uids.append(info.uid)
    #         await crud_user_members.update_term_agree_lst(db, uids)
    
    
    nickname = user_member_info.nickname if user_member_info.is_nickname == 1 else ''
    
    # test_data = crud_user_data.get_all(db, req.uid)
    
    user_datas = crud_user_data.get_all(db, req.uid)

    need_update_time = False
    
    time_category = 'Time'
    pass_category = 'Pass'
    user_category = 'User'
    stage_category = 'Stage'
    
    time_data = get(user_datas, time_category, None)
    pass_data = get(user_datas, pass_category, None)
    user_data = get(user_datas, user_category, None)
    stage_data = get(user_datas, stage_category, None)
    
    
    game_config_dict = await CacheController.game_config_info_map(db)
    game_config_info = get(game_config_dict, req.platform, None)
    
    user_level_dict = await CacheController.level_up_info_map(db)
    user_level_info = get(user_level_dict, req.platform, None)
    if not user_level_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_UP_DATA, uid=req.uid)
    
    info = get(user_level_info, str(user_member_info.level), None)
    if not info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_LEVEL_UP_DATA, uid=req.uid)

    energy_max = get(info, 'bread_max', None)
    if energy_max == None:
        return get_response(code=ResponseCode.RES_NOT_FOUND_MAX_ENERGY_VALUE, uid=req.uid)
    
    energy_max = int(energy_max)
    
    energy = crud_user_currency.get(db, req.uid, 'BREAD')
    
    if (energy) and (time_data):
        if energy.amount >= energy_max:
            pass
        else:
            energy_time = get(time_data, 'lastEnergyTime', None)
            current_time = int(time.time()) + Constant.VALUE_OF_1970
            
            if not energy_time:
                time_data['lastEnergyTime'] = current_time
                crud_user_data.save(db, req.uid, time_category, json.dumps(time_data))
                need_update_time = True
            else:
                # 5min
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
                    energy_gap = energy_max - energy.amount
                    if energy_gap <= between_energy:
                        between_energy = energy_gap
                        time_data['lastEnergyTime'] = current_time
                    else:
                        time_data['lastEnergyTime'] = time_data['lastEnergyTime'] + (between_energy * five_min)
                                
                    __get_currency(db, req.uid, 'BREAD', between_energy, None)
                    need_update_time = True
                
    energy = crud_user_currency.get(db, req.uid, 'PTICKET')
    
    if (energy) and (time_data) and (pass_data):
        
        pass_event = await CacheController.get_current_pass_event_info(db, req.platform)
        if not pass_event:
            vip_value = False
        else:
            pass_id = get(pass_event, 'id', None)
            
            find_pass = None
            
            for pass_value in pass_data:
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
        if energy_max != None:
            energy_max = int(energy_max)
                        
        if energy.amount >= energy_max:
            pass
        else:
            energy_time = get(time_data, 'lastPVPTime', None)
            current_time = int(time.time()) + Constant.VALUE_OF_1970
            
            if not energy_time:
                time_data['lastPVPTime'] = current_time
                need_update_time = True
            else:
                # 5min
                term_info = get(game_config_info, Constant.GAME_CONFIG_PTICKET_PER_MIN, None)
                if not term_info:
                    return get_response(code=ResponseCode.RES_NOT_FOUND_GAME_CONFIG_VALUE, uid=req.uid)
                
                term_value = get(term_info, 'value', None)
                if not term_value:
                    return get_response(code=ResponseCode.RES_NOT_FOUND_GAME_CONFIG_VALUE, uid=req.uid)
                
                five_min = int(term_value) * 60
                between_time = current_time - energy_time
                between_energy = int(between_time / five_min)
                
                if between_energy > 0:
                    energy_gap = energy_max - energy.amount
                    if energy_gap <= between_energy:
                        between_energy = energy_gap
                        time_data['lastPVPTime'] = current_time
                    else:
                        time_data['lastPVPTime'] = time_data['lastPVPTime'] + (between_energy * five_min)
                                
                    __get_currency(db, req.uid, 'PTICKET', between_energy, None)
                    need_update_time = True
    
    if need_update_time:
        crud_user_data.save(db, req.uid, time_category, json.dumps(time_data))
    
    need_update_user = False
    
    if (user_data):
        guide_misison_data = get(user_data, 'GuideMission', None)
        if guide_misison_data:
            guide_mission_dict = await CacheController.guide_mission_info_map(db)
            guide_mission_info = get(guide_mission_dict, req.platform)
            if not guide_mission_info:
                return get_response(code=ResponseCode.RES_NOT_FOUND_GUIDE_MISSION_DATA, uid=req.uid)
            
            if (guide_misison_data['c'] > 0) and (guide_misison_data['r']):
                current_info = get(guide_mission_info, str(guide_misison_data['id']))
                if not current_info:
                    return get_response(code=ResponseCode.RES_NOT_FOUND_GUIDE_MISSION_INFO_DATA, uid=req.uid)
                if get(current_info, 'order', None) == None:
                    return get_response(code=ResponseCode.RES_NOT_FOUND_GUIDE_MISSION_INFO_DATA, uid=req.uid)
                
                
                guide_mission_order_dict = await CacheController.guide_mission_info_map_by_order(db)
                guide_mission_order_info = get(guide_mission_order_dict, req.platform)
                if not guide_mission_order_info:
                    return get_response(code=ResponseCode.RES_NOT_FOUND_GUIDE_MISSION_DATA, uid=req.uid)

                next_info = get(guide_mission_order_info, str(current_info['order'] + 1), None)
                if next_info:
                    if get(next_info, 'order', None) == None:
                        return get_response(code=ResponseCode.RES_NOT_FOUND_GUIDE_MISSION_INFO_DATA, uid=req.uid)
                    guide_misison_data['id'] = next_info['id']
                    guide_misison_data['c'] = 0
                    guide_misison_data['d'] = False
                    guide_misison_data['r'] = False
                    need_update_user = True
            
            # if (guide_misison_data['id'] == 10027):
            #     guide_misison_data['id'] = 10003
            #     need_update_user = True
            
            # elif (guide_misison_data['c'] > 0):
            #     current_info = get(guide_mission_info, str(guide_misison_data['id']))
            #     if not current_info:
            #         return get_response(code=ResponseCode.RES_NOT_FOUND_GUIDE_MISSION_INFO_DATA, uid=req.uid)
            #     if get(current_info, 'order', None) == None:
            #         return get_response(code=ResponseCode.RES_NOT_FOUND_GUIDE_MISSION_INFO_DATA, uid=req.uid)
                
            #     count = get(current_info, 'count', 0)
                
            #     if count >= guide_misison_data['c']:
            #         guide_misison_data['d'] = True
            #         need_update_user = True
                
            
            if (guide_misison_data['id'] == 30012) and (guide_misison_data['c'] == 0) and (guide_misison_data['d']):
                guide_misison_data['c'] = 1
                need_update_user = True
    
    
    if (not stage_data) or (not user_data):
        pass
    else:
        stage_tile_dict = await CacheController.stage_tile_info_map_by_seq(db)
        stage_tile_info = get(stage_tile_dict, req.platform)
        if not stage_tile_info:
            return get_response(code=ResponseCode.RES_NOT_FOUND_STAGE_TILE_DATA, uid=req.uid)

        
        tile_obj = get(stage_tile_info, str(user_data['BestStageTileKey']), None)
        current_data = None
        if tile_obj != None:
            for stage in stage_data:
                if stage['ID'] == tile_obj['id']:
                    current_data = stage
                    break
            
            if current_data:
                if current_data['Star'] > 0:
                    next_obj = get(stage_tile_info, str(user_data['BestStageTileKey'] + 1), None)
                    if next_obj:
                        user_data['BestStageTileKey'] = user_data['BestStageTileKey'] + 1
                        need_update_user = True

                    
        tile_obj = get(stage_tile_info, str(user_data['BestStageHardTileKey']), None)
        current_data = None

        if tile_obj != None:
            for stage in stage_data:
                if stage['ID'] == tile_obj['id']:
                    current_data = stage
                    break
            
            if current_data:
                if current_data['hStar'] > 0:
                    next_obj = get(stage_tile_info, str(user_data['BestStageHardTileKey'] + 1), None)
                    if next_obj:
                        user_data['BestStageHardTileKey'] = user_data['BestStageHardTileKey'] + 1
                        need_update_user = True

    
    if need_update_user:
        crud_user_data.save(db, req.uid, user_category, json.dumps(user_data))
    
    __init_currency(db, req.uid)
    
    crud_postbox.check_special_post(db, req.uid, user_member_info.server)
    exists_posts = crud_postbox.is_exist_non_reward_post(db, req.uid)
    
    response = crud_user_currency.get_user_currency_data(db, req.uid)
    response['nickname'] = nickname
    response['existsPost'] = exists_posts

    if user_datas:
        response['UserData'] = user_datas
        
    return get_response(code=ResponseCode.RES_SUCCESS, data=response, uid=req.uid)



async def users_data_save(req:DataSaveReqParam, db:Session):

    user_member_info = await crud_user_members.get(db, req.uid)
    if not user_member_info:
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, uid=req.uid)
    
    if user_member_info.login_device_id:
       if user_member_info.login_device_id != req.d:
           return get_response(code=ResponseCode.RES_DUPLICATED_DEVICE, uid=req.uid)
       
     
    if crud_user_data.check_banned_user(db, req.uid):
        return get_response(code=ResponseCode.RES_ERR_ABUSE_DETECTION, uid=req.uid)
    
    user_category_data = None
    user_hero_data = None
    user_purchase_data = None
    payment_check = False
    
    user = {}
    other_data = []
    for data_row in req.data_list:
        if 'category' not in data_row:
            return get_response(code=ResponseCode.RES_INVALID_PARAMS, uid=req.uid)
        
        if data_row['category'] == 'User':
            user_category_data = data_row['data']
            if 'level' in user_category_data:
                if user_category_data['level'] and (user_member_info.level < int(user_category_data['level'])):
                    await crud_user_members.update_level(db, req.uid, int(user_category_data['level']))

        
        user_data = get(data_row, 'data')
        
        if user_data :
            before_data = crud_user_data.get(db, req.uid, data_row['category'])
            str_user_data = json.dumps(user_data)
            # 데이터 차이가 
            if before_data and (len(str_user_data) < len(before_data.data)) and ((len(before_data.data) - len(str_user_data)) >= 100):
                logger.warning("user_data " + str_user_data)
                logger.warning("user_data length " + str(len(str_user_data)))
                logger.warning("before_data " + before_data.data)
                logger.warning("before_data length " + str(len(before_data.data)))
                try:
                    crud_user_data.save_logs(db, req.uid, len(str_user_data), len(before_data.data), str(data_row['category']), str(str_user_data))
                except Exception as e:
                    logger.warning(e)

        if data_row:
            crud_user_data.save(db, req.uid, data_row['category'], json.dumps(data_row['data']))
            # if data_row['category'] in Constant.MYSQL_SIDE_DATA:
            #     crud_user_data.save(db, req.uid, data_row['category'], json.dumps(data_row['data']))
            # else:
            #     crud_user_data.save_by_mongo(req.uid, data_row['category'], data_row['data'])
    
    
    # 자동 벤처리 로직이 들어가야 하는데 여기서 product에 구분을 알아야 처리가 가능함
    # 이부분을 어떻게 처리할 지 고민해 봅시다. common으로 처리는 할 수 있을것 같음.        

    if crud_user_members.check_purchase(db, req.uid):
        payment_check = True
    
    ## TODO
    
    return get_response(code=ResponseCode.RES_SUCCESS, uid=req.uid)



async def users_nickname_save(req:NicknameSaveReqParam, db:Session):
    user_member_info = await crud_user_members.get(db, req.uid)
    
    if not user_member_info:
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, msg='Invalid User ID', uid=req.uid)

    has_nickname = crud_user_members.has_nickname(db, req.nickname)
    if has_nickname:
        return get_response(code=ResponseCode.RES_DUPLICATED_NICKNAME, uid=req.uid)
    
    await crud_user_members.update_nickname(db, req.uid, req.nickname)
    
    await rabbit_api.update_user_nickname(req.uid, req.nickname)
    
    return get_response(code=ResponseCode.RES_SUCCESS, uid=req.uid)



def users_battle_info(req:BaseReqParam, db:Session):
    if req.uid < 101:
        user_data = crud_user_data.get_battle_dummy_data(db, req.uid)
    else:
        user_data = crud_user_data.get_battle_data(db, req.uid)
    if not user_data or not user_data.data:
        ## 여기에 로그를 남기는 방법을 고민해 보자.
        pass
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=user_data, uid=req.uid)
    

def users_battle_infos(req:BattleInfosReqParam, db:Session):
    friends_uid = []
    dummys_uid = []
    
    for friend_id in req.uids:
        if friend_id < 101:
            dummys_uid.append(friend_id)
        else:
            friends_uid.append(friend_id)
    
    dummy_datas = crud_user_data.get_battle_dummy_datas(db, dummys_uid)
    user_datas = crud_user_data.get_battle_datas(db, friends_uid)
        
    result_data = []
    count = 0
    if dummy_datas:
        for data in dummy_datas:
            if (count >= Constant.FRIENDS_MAX_COUNT):
                break
            
            if not data.data:
                continue
            
            data.data = json.loads(data.data)
            result_data.append(data)
            count += 1

    if user_datas:
        for data in user_datas:
            if (count >= Constant.FRIENDS_MAX_COUNT):
                break
            
            if not data.data:
                continue
            
            data.data = json.loads(data.data)
            result_data.append(data)
            count += 1
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=result_data, uid=req.uid)
    


async def users_battle_save(req:BattleSaveReqParam, db:Session):
    user_member_info = await crud_user_members.get(db, req.uid)
    
    if not user_member_info:
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, msg='Invalid User ID', uid=req.uid)
    
    user_data = json.dumps(req.data)
    crud_user_data.save_battle_data(db, req.uid, req.battle_point, user_data)
    return get_response(code=ResponseCode.RES_SUCCESS, uid=req.uid)



async def users_coupon(req:CouponReqParam, db:Session):
    user_member_info = await crud_user_members.get(db, req.uid)
    
    if not user_member_info:
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, msg='Invalid User ID', uid=req.uid)
    
    return crud_coupon.check_coupon(db, req.uid, req.code)
    
    
    
async def user_refresh(req:BaseReqParam, db:Session, request:Request):
    if req.uid == 0:
        return get_response(code=ResponseCode.RES_SUCCESS, uid=req.uid)
    
    user_member_info = await crud_user_members.get(db, req.uid)
    
    if not user_member_info:
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, msg='Invalid User ID', uid=req.uid)
    
    await crud_user_members.update_refresh(db, req.uid)   

    
    base_uid_info = crud_user_server.base_uid(db, req.uid)
    if base_uid_info:
        req.uid = base_uid_info.uid

    
    try:
        crud_retention.set_uv(db, req.uid, req.platform, req.device_id, user_member_info.social_id, request.headers.get('origin_ip') if request.headers.get('origin_ip') else request.client.host)
    except Exception as e:
        logger.warning(e)
    
    return get_response(code=ResponseCode.RES_SUCCESS, uid=req.uid)
        
    


async def user_delete(req:BaseReqParam, db:Session, request:Request):
    if req.uid == 0:
        return get_response(code=ResponseCode.RES_SUCCESS, uid=req.uid)
    
    user_member_info = await crud_user_members.get(db, req.uid)
    
    if not user_member_info:
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, msg='Invalid User ID', uid=req.uid)
    
    base_uid_info = crud_user_server.base_uid(db, req.uid)
    if base_uid_info:
        server_infos = crud_user_server.get_all(db, base_uid_info.uid)
        if server_infos and (len(server_infos) > 0):
            crud_user_server.insert_all(db, server_infos)
            
            uids:list[int] = []
            for info in server_infos:
                uids.append(info.server_uid)
                
            user_platforms = crud_user_platforms.get_by_uids(db, uids)
            
            if user_platforms and (len(user_platforms) > 0):
                crud_user_platforms.insert_all(db, user_platforms)
                crud_user_platforms.remove_uids(db, uids)
                
            user_devices = crud_user_devices.get_by_uids(db, uids)
            if user_devices and (len(user_devices) > 0):
                crud_user_devices.insert_all(db, user_devices)
                crud_user_devices.remove_uids(db, uids)
            
            crud_user_server.remove_uids(db, uids)
            await rabbit_api.delete_user(req.uid)
        
    return get_response(code=ResponseCode.RES_SUCCESS, uid=req.uid)
        
    

async def user_review(req:ReviewReqParam, db:Session, request:Request):
    res = crud_user_members.get_review(db, req.uid)
    if res:
        return get_response(code=ResponseCode.RES_ALREADY_USER_REVIEWED, uid=req.uid)
    else:
        crud_user_members.insert_rewiew(db, req.uid, req.language, req.purchased, req.legend_count, req.art_star, req.fun_star, req.balance_star, request.headers.get('origin_ip') if request.headers.get('origin_ip') else request.client.host)
    return get_response(code=ResponseCode.RES_SUCCESS, uid=req.uid)
        
    
