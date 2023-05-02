import time
import typing
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from fastapi.encoders import jsonable_encoder
from loguru import logger
from sqlalchemy.orm import Session
from app.config.settings import Constant
from app.crud import crud_config, crud_mobile_version, crud_user_data
from app.crud.cache import crud_cache
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from app.config.settings import Constant
from app.util.util import object_as_dict
from app.util.util import get
import pandas as pd


def my_key_builder(func,namespace: typing.Optional[str] = "",db:Session = None,*args,**kwargs):
    prefix = FastAPICache.get_prefix()
    cache_key = f"{prefix}:{namespace}:{func.__module__}:{func.__name__}"
    return cache_key


# 전체 정보 캐싱 작업
@cache(namespace='cache_data', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def cache_data_map(db:Session):
    logger.warning("call cache_data_map = Refresh Cache Data")
    cache_data_info = {'android':None,'ios':None,'onestore':None, }
    for os_platform in Constant.OS_PLATFORMS:
        cache_data_list = crud_cache.get_cache_data_all(db, os_platform)
        if cache_data_list:
            cache_data_map_temp = {}
            for cache_data in cache_data_list:
                cache_data_map_temp[cache_data['sheet_key']] = json.loads(cache_data['value'])

                for cache_data_temp in cache_data_map_temp[cache_data['sheet_key']]:
                    if (cache_data_temp['id'] == 'int') or (cache_data_temp['id'] == '0') :
                        continue
                    for key in cache_data_temp.keys():
                        type_key = cache_data_map_temp[cache_data['sheet_key']][0][key]
                        if (type_key == 'int') or (type_key == '0') :
                            cache_data_temp[key] = int(cache_data_temp[key])
                        elif (type_key == 'float') or (type_key == 'double'):
                            cache_data_temp[key] = float(cache_data_temp[key].replace(',', ''))
                        elif (type_key == 'bool'):
                            cache_data_temp[key] = True if (cache_data_temp[key].lower() == 'true') else False

            cache_data_info[os_platform] = cache_data_map_temp

    return cache_data_info



@cache(namespace='quest_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def quest_info_map(db:Session):
    # logger.warning("call quest_info_map = Refresh Quest Info")
    quest_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            quest_list = get(platform_list, 'Quest', None)
            if quest_list:
                quest_map_temp = {}
                for quest in quest_list:
                    if quest['id'] == '0':
                        continue
                    quest_map_temp[str(quest['id'])] = quest
                
                quest_info[os_platform] = quest_map_temp

    return quest_info



@cache(namespace='guide_mission_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def guide_mission_info_map(db:Session):
    # logger.warning("call guide_mission_info = Refresh Guide Mission Info")
    guide_mission_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            guide_mission_list = get(platform_list, 'GuideMission', None)
            if guide_mission_list:
                guide_mission_map_temp = {}
                for guide_mission in guide_mission_list:
                    if guide_mission['id'] == '0':
                        continue
                    guide_mission_map_temp[str(guide_mission['id'])] = guide_mission
                
                guide_mission_info[os_platform] = guide_mission_map_temp

    return guide_mission_info




@cache(namespace='guide_mission_info_order', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def guide_mission_info_map_by_order(db:Session):
    # logger.warning("call guide_mission_info = Refresh Guide Mission Info")
    guide_mission_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            guide_mission_list = get(platform_list, 'GuideMission', None)
            if guide_mission_list:
                guide_mission_map_temp = {}
                for guide_mission in guide_mission_list:
                    if guide_mission['id'] == '0':
                        continue
                    guide_mission_map_temp[str(guide_mission['order'])] = guide_mission
                
                guide_mission_info[os_platform] = guide_mission_map_temp

    return guide_mission_info




@cache(namespace='chapter_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def chapter_info_map(db:Session):
    # logger.warning("call chapter_info = Refresh Chapter Info")
    chapter_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            chapter_info_list = get(platform_list, 'Chapter', None)
            if chapter_info_list:
                chapter_map_temp = {}
                for chapter in chapter_info_list:
                    if chapter['id'] == '0':
                        continue
                    chapter_map_temp[str(chapter['id'])] = chapter
                
                chapter_info[os_platform] = chapter_map_temp

    return chapter_info






@cache(namespace='homeshop_info_by_id', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def homeshop_info_by_id_map(db:Session):
    # logger.warning("call homeshop_info_map = Refresh Home Shop Info")
    homeshop_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            homeshop_info_list = get(platform_list, 'HomeShop', None)
            if homeshop_info_list:
                homeshop_map_temp = {}
                for homeshop in homeshop_info_list:
                    if homeshop['id'] == '0':
                        continue
                    homeshop_map_temp[str(homeshop['id'])] = homeshop
                
                homeshop_info[os_platform] = homeshop_map_temp

    return homeshop_info




@cache(namespace='shop_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def shop_info_map(db:Session):
    # logger.warning("call shop_info_map = Refresh Shop Info")
    shop_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            shop_info_list = get(platform_list, 'Shop', None)
            if shop_info_list:
                shop_map_temp = {}
                for shop in shop_info_list:
                    if shop['id'] == '0':
                        continue
                    
                    # pid 등록이 안되어 있는 상품은 무시한다.
                    if shop['pid'] == 'none':
                        continue
                    
                    if not get(shop_map_temp, shop['pid'], None):
                        shop_map_temp[shop['pid']] = []
                        shop_map_temp[shop['pid']].append(shop)
                    else:
                        shop_map_temp[shop['pid']].append(shop)
                
                shop_info[os_platform] = shop_map_temp

    return shop_info





@cache(namespace='homeshop_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def homeshop_info_map(db:Session):
    # logger.warning("call homeshop_info_map = Refresh Home Shop Info")
    homeshop_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            homeshop_info_list = get(platform_list, 'HomeShop', None)
            if homeshop_info_list:
                homeshop_map_temp = {}
                for homeshop in homeshop_info_list:
                    if homeshop['id'] == '0':
                        continue
                    if not get(homeshop_map_temp, str(homeshop['grade']), None):
                        homeshop_map_temp[str(homeshop['grade'])] = []
                        homeshop_map_temp[str(homeshop['grade'])].append(homeshop)
                    else:
                        homeshop_map_temp[str(homeshop['grade'])].append(homeshop)
                
                homeshop_info[os_platform] = homeshop_map_temp

    return homeshop_info





@cache(namespace='pvpshop_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def pvpshop_info_map(db:Session):
    # logger.warning("call pvpshop = Refresh PVP Shop Info")
    pvpshop_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            pvpshop_info_list = get(platform_list, 'PvpShop', None)
            if pvpshop_info_list:
                pvpshop_map_temp = {}
                for pvpshop in pvpshop_info_list:
                    if pvpshop['id'] == '0':
                        continue
                    pvpshop_map_temp[str(pvpshop['id'])] = pvpshop
                
                pvpshop_info[os_platform] = pvpshop_map_temp

    return pvpshop_info






@cache(namespace='chest_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def chest_info_map(db:Session):
    # logger.warning("call chest_info_map = Refresh Chest Info")
    chest_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            chest_info_list = get(platform_list, 'Chest', None)
            if chest_info_list:
                chest_map_temp = {}
                for chest in chest_info_list:
                    if chest['id'] == '0':
                        continue
                    if not get(chest_map_temp, str(chest['chest_id']), None):
                        chest_map_temp[str(chest['chest_id'])] = []
                        chest_map_temp[str(chest['chest_id'])].append(chest)
                    else:
                        chest_map_temp[str(chest['chest_id'])].append(chest)
                
                chest_info[os_platform] = chest_map_temp

    return chest_info



@cache(namespace='stage_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def stage_info_map(db:Session):
    # logger.warning("call stage_info_map = Refresh Stage Info")
    stage_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            stage_info_list = get(platform_list, 'Stage', None)
            if stage_info_list:
                stage_map_temp = {}
                for stage in stage_info_list:
                    if stage['id'] == '0':
                        continue
                    stage_map_temp[str(stage['id'])] = stage
                
                stage_info[os_platform] = stage_map_temp

    return stage_info



@cache(namespace='stage_tile_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def stage_tile_info_map(db:Session):
    # logger.warning("call stage_tile_info_map = Refresh Stage Tile Info")
    stage_tile_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            stage_tile_info_list = get(platform_list, 'StageTile', None)
            if stage_tile_info_list:
                stage_tile_map_temp = {}
                for stage_tile in stage_tile_info_list:
                    if stage_tile['id'] == '0':
                        continue
                    stage_tile_map_temp[str(stage_tile['id'])] = stage_tile
                
                stage_tile_info[os_platform] = stage_tile_map_temp

    return stage_tile_info





@cache(namespace='stage_tile_info_by_seq', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def stage_tile_info_map_by_seq(db:Session):
    # logger.warning("call stage_tile_info_map = Refresh Stage Tile Info By seq")
    stage_tile_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            stage_tile_info_list = get(platform_list, 'StageTile', None)
            if stage_tile_info_list:
                stage_tile_map_temp = {}
                for stage_tile in stage_tile_info_list:
                    if stage_tile['id'] == '0':
                        continue
                    if stage_tile['seq'] != '0':
                        stage_tile_map_temp[str(stage_tile['seq'])] = stage_tile
                
                stage_tile_info[os_platform] = stage_tile_map_temp

    return stage_tile_info




@cache(namespace='rune_upgrade_cost_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def rune_upgrade_cost_info_map(db:Session):
    # logger.warning("call rune_upgrade_cost_info_map = Refresh Rune Upgrade Cost Info")
    rune_upgrade_cost_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            rune_upgrade_cost_info_list = get(platform_list, 'RuneUpgradeCost', None)
            if rune_upgrade_cost_info_list:
                rune_upgrade_cost_map_temp = {}
                for rune_upgrade_cost in rune_upgrade_cost_info_list:
                    if rune_upgrade_cost['id'] == '0':
                        continue
                    rune_upgrade_cost_map_temp[str(rune_upgrade_cost['id'])] = rune_upgrade_cost
                
                rune_upgrade_cost_info[os_platform] = rune_upgrade_cost_map_temp

    return rune_upgrade_cost_info




@cache(namespace='rune_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def rune_info_map(db:Session):
    # logger.warning("call rune_info_map = Refresh Rune Upgrade Cost Info")
    rune_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            rune_info_list = get(platform_list, 'Rune', None)
            if rune_info_list:
                rune_map_temp = {}
                for rune in rune_info_list:
                    if rune['id'] == '0':
                        continue
                    rune_map_temp[str(rune['id'])] = rune
                
                rune_info[os_platform] = rune_map_temp

    return rune_info



@cache(namespace='rune_gacha_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def rune_gacha_info_map(db:Session):
    # logger.warning("call rune_info_map = Refresh Rune Info")
    rune_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            rune_info_list = get(platform_list, 'Rune', None)
            if rune_info_list:
                rune_map_temp = {}
                for rune in rune_info_list:
                    if rune['id'] == '0':
                        continue
                    if rune['odds'] == 0:
                        continue
                    if not get(rune_map_temp, str(rune['grade']), None):
                        rune_map_temp[str(rune['grade'])] = []
                        rune_map_temp[str(rune['grade'])].append(rune)
                    else:
                        rune_map_temp[str(rune['grade'])].append(rune)
                
                rune_info[os_platform] = rune_map_temp

    return rune_info


@cache(namespace='random_rune_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def random_rune_info_map(db:Session):
    # logger.warning("call rune_info_map = Refresh Rune Upgrade Cost Info")
    rune_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            rune_info_list = get(platform_list, 'Rune', None)
            if rune_info_list:
                rune_list_temp = []
                for rune in rune_info_list:
                    if rune['id'] == '0':
                        continue
                    if rune['odds'] == 0:
                        continue
                    rune_list_temp.append(rune)
                
                rune_info[os_platform] = rune_list_temp

    return rune_info



@cache(namespace='training_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def training_info_map(db:Session):
    # logger.warning("call training_info_map = Refresh training Upgrade Cost Info")
    training_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            training_info_list = get(platform_list, 'Train', None)
            if training_info_list:
                training_map_temp = {}
                for training in training_info_list:
                    if training['id'] == '0':
                        continue
                    training_map_temp[str(training['id'])] = training
                
                training_info[os_platform] = training_map_temp

    return training_info





@cache(namespace='home_contents_lv_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def home_contents_lv_info_map(db:Session):
    # logger.warning("call home_contents_lv_info_map = Refresh home_contents_lv Upgrade Cost Info")
    home_contents_lv_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            home_contents_lv_info_list = get(platform_list, 'HomeContentsLv', None)
            if home_contents_lv_info_list:
                home_contents_lv_map_temp = {}
                
                for home_contents_lv in home_contents_lv_info_list:
                    if home_contents_lv['id'] == '0':
                        continue
                    
                    if not get(home_contents_lv_map_temp, str(home_contents_lv['building_id']), None):
                        home_contents_lv_map_temp[str(home_contents_lv['building_id'])] = []
                        home_contents_lv_map_temp[str(home_contents_lv['building_id'])].append(home_contents_lv)
                    else:
                        home_contents_lv_map_temp[str(home_contents_lv['building_id'])].append(home_contents_lv)
                
                home_contents_lv_info[os_platform] = home_contents_lv_map_temp

    return home_contents_lv_info






@cache(namespace='game_config_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def game_config_info_map(db:Session):
    # logger.warning("call game_config_info_map = Refresh Battle Pass Info")
    game_config_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            game_config_info_list = get(platform_list, 'GameConfig', None)
            if game_config_info_list:
                game_config_map_temp = {}
                for game_config in game_config_info_list:
                    if game_config['id'] == '0':
                        continue
                    game_config_map_temp[str(game_config['id'])] = game_config
                
                game_config_info[os_platform] = game_config_map_temp

    return game_config_info





@cache(namespace='battle_pass_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def battle_pass_info_map(db:Session):
    # logger.warning("call battle_pass_info_map = Refresh Battle Pass Info")
    battle_pass_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            battle_pass_info_list = get(platform_list, 'BattlePass', None)
            if battle_pass_info_list:
                battle_pass_map_temp = {}
                for battle_pass in battle_pass_info_list:
                    if battle_pass['id'] == '0':
                        continue
                    battle_pass_map_temp[str(battle_pass['id'])] = battle_pass
                
                battle_pass_info[os_platform] = battle_pass_map_temp

    return battle_pass_info





@cache(namespace='pass_event_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def pass_event_info_map(db:Session):
    # logger.warning("call pass_event_info_map = Refresh Pass Event Info")
    pass_event_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            pass_event_info_list = get(platform_list, 'PassEvent', None)
            if pass_event_info_list:
                pass_event_list_temp = []
                for pass_event in pass_event_info_list:
                    if pass_event['id'] == '0':
                        continue
                    pass_event_list_temp.append(pass_event)
                
                pass_event_info[os_platform] = pass_event_list_temp

    return pass_event_info




async def get_current_pass_event_info(db:Session, platform:str):
    now = int(time.time())
    pass_event_map = await pass_event_info_map(db)
    pass_event_list = get(pass_event_map, platform, None)
    
    if not pass_event_list:
        return None
    
    for pass_event in pass_event_list:
        start_value = get(pass_event, 'start', 0)
        if start_value:
            start_value = datetime.strptime(start_value, '%Y/%m/%d %H:%M')
            start_value = int(time.mktime(start_value.timetuple()))
        end_value = get(pass_event, 'end', 0)
        if end_value:
            end_value = datetime.strptime(end_value, '%Y/%m/%d %H:%M')
            end_value = int(time.mktime(end_value.timetuple()))

        if ((now - start_value) >= 0) and ((end_value - now) >=0):
            return pass_event
        
        
    return None


@cache(namespace='pass_event_list_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def pass_event_info_map_list(db:Session):
    # logger.warning("call pass_event_info_map = Refresh Pass Event Info")
    pass_event_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            pass_event_info_list = get(platform_list, 'PassEvent', None)
            if pass_event_info_list:
                pass_event_list_temp = {}
                for pass_event in pass_event_info_list:
                    if pass_event['id'] == '0':
                        continue
                    if not get(pass_event_list_temp, str(pass_event['set_id']), None):
                        pass_event_list_temp[str(pass_event['set_id'])] = []
                        pass_event_list_temp[str(pass_event['set_id'])].append(pass_event)
                    else:
                        pass_event_list_temp[str(pass_event['set_id'])].append(pass_event)
                
                pass_event_info[os_platform] = pass_event_list_temp

    return pass_event_info



async def get_current_pass_event(db:Session, platform:str, id:int):
    now = int(time.time())
    pass_event_map = await pass_event_info_map_list(db)
    pass_event_list = get(pass_event_map, platform, None)
    
    if not pass_event_list:
        return None
    
    pass_event_list = get(pass_event_list, str(id), None)
    if not pass_event_list:
        return None
    
    for pass_event in pass_event_list:
        start_value = get(pass_event, 'start', 0)
        if start_value:
            start_value = datetime.strptime(start_value, '%Y/%m/%d %H:%M')
            start_value = int(time.mktime(start_value.timetuple()))
        end_value = get(pass_event, 'end', 0)
        if end_value:
            end_value = datetime.strptime(end_value, '%Y/%m/%d %H:%M')
            end_value = int(time.mktime(end_value.timetuple()))

        if ((now - start_value) >= 0) and ((end_value - now) >=0):
            return pass_event
        
        
    return None

@cache(namespace='pickup_event_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def pickup_event_info_map(db:Session):
    now = int(time.time())
    # logger.warning("call pickup_event_info_map = Refresh Pass Event Info")
    pickup_event_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            pickup_event_info_list = get(platform_list, 'Pickup', None)
            if pickup_event_info_list:
                pickup_event_map_temp = {}
                for pickup_event in pickup_event_info_list:
                    if pickup_event['id'] == '0':
                        continue
                    
                    start_value = pickup_event['start']
                    if start_value:
                        start_value = datetime.strptime(start_value, '%Y/%m/%d %H:%M')
                        start_value = int(time.mktime(start_value.timetuple()))
                    end_value = pickup_event['end']
                    if end_value:
                        end_value = datetime.strptime(end_value, '%Y/%m/%d %H:%M')
                        end_value = int(time.mktime(end_value.timetuple()))

                    if ((now - start_value) >= 0) and ((end_value - now) >=0):
                        pickup_event_map_temp[str(pickup_event['id'])] = pickup_event
            
                pickup_event_info[os_platform] = pickup_event_map_temp

    return pickup_event_info



        
    

@cache(namespace='pvp_round_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def pvp_round_info_list(db:Session):
    # logger.warning("call pvp_round_info_map = Refresh PVP Round Info")
    pvp_round_info_list = crud_cache.get_pvp_round_info(db)
    if pvp_round_info_list:
        pvp_round_list_temp = []
        for pvp_round in pvp_round_info_list:
            pvp_round_list_temp.append(object_as_dict(pvp_round))

    return pvp_round_list_temp
        

async def get_current_pvp_round_info(db:Session):
    now = int(time.time())
    pvp_round_list = await pvp_round_info_list(db)
    
    if not pvp_round_list:
        return None
    
    for pvp_round in pvp_round_list:
        start_value = get(pvp_round, 'start_date', 0)
        if start_value:
            start_value = int(time.mktime(start_value.timetuple()))
        end_value = get(pvp_round, 'end_date', 0)
        if end_value:
            end_value = int(time.mktime(end_value.timetuple()))
        
        if ((now - start_value) >= 0) and ((end_value - now) >= 0):
            return pvp_round

    # logger.warning('pvp round null happen = ' + str(now))
    return None




@cache(namespace='defense_reward_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def defense_reward_info_map(db:Session):
    # logger.warning("call dungeon_reward_info_map = Refresh Battle Pass Info")
    dungeon_reward_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            dungeon_reward_info_list = get(platform_list, 'DungeonReward', None)
            if dungeon_reward_info_list:
                dungeon_reward_map_temp = {}
                for dungeon_reward in dungeon_reward_info_list:
                    if dungeon_reward['id'] == '0':
                        continue
                    if dungeon_reward['dType'] != 'DEFENSE':
                        continue
                    if not get(dungeon_reward_map_temp, str(dungeon_reward['lv']), None):
                        dungeon_reward_map_temp[str(dungeon_reward['lv'])] = []
                        dungeon_reward_map_temp[str(dungeon_reward['lv'])].append(dungeon_reward)
                    else:
                        dungeon_reward_map_temp[str(dungeon_reward['lv'])].append(dungeon_reward)
                
                dungeon_reward_info[os_platform] = dungeon_reward_map_temp

    return dungeon_reward_info




@cache(namespace='stone_reward_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def stone_reward_info_map(db:Session):
    # logger.warning("call stone_reward_info_map = Refresh Battle Pass Info")
    stone_reward_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            stone_reward_info_list = get(platform_list, 'DungeonReward', None)
            if stone_reward_info_list:
                stone_reward_map_temp = {}
                for stone_reward in stone_reward_info_list:
                    if stone_reward['id'] == '0':
                        continue
                    if stone_reward['dType'] != 'STONE':
                        continue
                    if not get(stone_reward_map_temp, str(stone_reward['lv']), None):
                        stone_reward_map_temp[str(stone_reward['lv'])] = []
                        stone_reward_map_temp[str(stone_reward['lv'])].append(stone_reward)
                    else:
                        stone_reward_map_temp[str(stone_reward['lv'])].append(stone_reward)
                        
                stone_reward_info[os_platform] = stone_reward_map_temp

    return stone_reward_info






@cache(namespace='mine_reward_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def mine_reward_info_map(db:Session):
    # logger.warning("call mine_reward_info_map = Refresh Battle Pass Info")
    mine_reward_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            mine_reward_info_list = get(platform_list, 'DungeonReward', None)
            if mine_reward_info_list:
                mine_reward_map_temp = {}
                for mine_reward in mine_reward_info_list:
                    if mine_reward['id'] == '0':
                        continue
                    if mine_reward['dType'] != 'MINE':
                        continue
                    if not get(mine_reward_map_temp, str(mine_reward['lv']), None):
                        mine_reward_map_temp[str(mine_reward['lv'])] = []
                        mine_reward_map_temp[str(mine_reward['lv'])].append(mine_reward)
                    else:
                        mine_reward_map_temp[str(mine_reward['lv'])].append(mine_reward)
                        
                mine_reward_info[os_platform] = mine_reward_map_temp

    return mine_reward_info





@cache(namespace='character_grade_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def character_info_grade_list_map(db:Session):
    # logger.warning("call character_info_map = Refresh Character Info")
    character_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            character_info_list = get(platform_list, 'Character', None)
            if character_info_list:
                character_map_temp = {}
                for character in character_info_list:
                    if character['id'] == '0':
                        continue
                    if character['odds'] == 0:
                        continue
                    if not get(character_map_temp, str(character['grade_value']), None):
                        character_map_temp[str(character['grade_value'])] = []
                        character_map_temp[str(character['grade_value'])].append(character)
                    else:
                        character_map_temp[str(character['grade_value'])].append(character)
                
                character_info[os_platform] = character_map_temp

    return character_info


@cache(namespace='character_gacha_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def character_gacha_info_map(db:Session):
    # logger.warning("call character_info_map = Refresh Character Info")
    character_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            character_info_list = get(platform_list, 'Character', None)
            if character_info_list:
                character_map_temp = {}
                for character in character_info_list:
                    if character['id'] == '0':
                        continue
                    if character['seq'] == 0:
                        continue
                    if character['odds'] == 0:
                        continue
                    character_map_temp[str(character['id'])] = character
                
                character_info[os_platform] = character_map_temp

    return character_info


@cache(namespace='character_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def character_info_map(db:Session):
    # logger.warning("call character_info_map = Refresh Character Info")
    character_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            character_info_list = get(platform_list, 'Character', None)
            if character_info_list:
                character_map_temp = {}
                for character in character_info_list:
                    if character['id'] == '0':
                        continue
                    if character['seq'] == 0:
                        continue
                    character_map_temp[str(character['id'])] = character
                
                character_info[os_platform] = character_map_temp

    return character_info



@cache(namespace='weapon_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def weapon_info_map(db:Session):
    # logger.warning("call weapon_info_map = Refresh Weapon Info")
    weapon_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            weapon_info_list = get(platform_list, 'Weapon', None)
            if weapon_info_list:
                weapon_map_temp = {}
                for weapon in weapon_info_list:
                    if weapon['id'] == '0':
                        continue
                    if weapon['odds'] == 0:
                        continue
                    weapon_map_temp[str(weapon['id'])] = weapon
                
                weapon_info[os_platform] = weapon_map_temp

    return weapon_info



@cache(namespace='weapon_level_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def weapon_level_info_map(db:Session):
    # logger.warning("call weapon_level_info_map = Refresh Weapon Level Info")
    weapon_level_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            weapon_level_info_list = get(platform_list, 'WeaponLevelExp', None)
            if weapon_level_info_list:
                weapon_level_map_temp = {}
                for weapon_level in weapon_level_info_list:
                    if weapon_level['id'] == '0':
                        continue
                    weapon_level_map_temp[str(weapon_level['lv'])] = weapon_level
                
                weapon_level_info[os_platform] = weapon_level_map_temp

    return weapon_level_info




@cache(namespace='character_enhance_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def character_enhance_info_map(db:Session):
    # logger.warning("call character_enhance_map = Refresh Character Enhance Info")
    character_enhance_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            character_enhance_info_list = get(platform_list, 'CharacterEnhance', None)
            if character_enhance_info_list:
                character_enhance_map_temp = {}
                for character_enhance in character_enhance_info_list:
                    if character_enhance['id'] == '0':
                        continue
                    if not get(character_enhance_map_temp, str(character_enhance['grade']), None):
                        character_enhance_map_temp[str(character_enhance['grade'])] = {}
                        character_enhance_map_temp[str(character_enhance['grade'])][str(character_enhance['star'])] = character_enhance
                    else:
                        character_enhance_map_temp[str(character_enhance['grade'])][str(character_enhance['star'])] = character_enhance
                
                character_enhance_info[os_platform] = character_enhance_map_temp

    return character_enhance_info




@cache(namespace='character_level_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def character_level_info_map(db:Session):
    # logger.warning("call character_level_info_map = Refresh Character Level Info")
    character_level_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            character_level_info_list = get(platform_list, 'CharacterLevelExp', None)
            if character_level_info_list:
                character_level_map_temp = {}
                for character_level in character_level_info_list:
                    if character_level['id'] == '0':
                        continue
                    character_level_map_temp[str(character_level['lv'])] = character_level
                
                character_level_info[os_platform] = character_level_map_temp

    return character_level_info


@cache(namespace='weapon_gacha_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def weapon_gacha_info_map(db:Session):
    # logger.warning("call weapon_info_map = Refresh Weapon Info")
    weapon_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            weapon_info_list = get(platform_list, 'Weapon', None)
            if weapon_info_list:
                weapon_map_temp = {}
                for weapon in weapon_info_list:
                    if weapon['id'] == '0':
                        continue
                    if weapon['odds'] == 0:
                        continue
                    if not get(weapon_map_temp, str(weapon['grade_value']), None):
                        weapon_map_temp[str(weapon['grade_value'])] = []
                        weapon_map_temp[str(weapon['grade_value'])].append(weapon)
                    else:
                        weapon_map_temp[str(weapon['grade_value'])].append(weapon)
                
                weapon_info[os_platform] = weapon_map_temp

    return weapon_info




@cache(namespace='gacha_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def gacha_info_map(db:Session):
    # logger.warning("call gacha = Refresh Gacha Info")
    gacha_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            gacha_info_list = get(platform_list, 'Gacha', None)
            if gacha_info_list:
                gacha_map_temp = {}
                for gacha in gacha_info_list:
                    if gacha['id'] == '0':
                        continue
                    if gacha['rate'] == 0.0:
                        continue
                    if not get(gacha_map_temp, str(gacha['type'])):
                        gacha_map_temp[str(gacha['type'])] = []
                        gacha_map_temp[str(gacha['type'])].append(gacha)
                    else:
                        gacha_map_temp[str(gacha['type'])].append(gacha)
                
                gacha_info[os_platform] = gacha_map_temp

    return gacha_info





@cache(namespace='gacha_cost_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def gacha_cost_info_map(db:Session):
    # logger.warning("call gacha = Refresh Gacha Info")
    gacha_cost_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            gacha_cost_info_list = get(platform_list, 'GachaCost', None)
            if gacha_cost_info_list:
                gacha_cost_map_temp = {}
                for gacha_cost in gacha_cost_info_list:
                    if gacha_cost['id'] == '0':
                        continue
                    gacha_cost_map_temp[str(gacha_cost['id'])] = gacha_cost
                
                gacha_cost_info[os_platform] = gacha_cost_map_temp

    return gacha_cost_info




@cache(namespace='request_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def request_info_map(db:Session):
    # logger.warning("call request = Refresh Request Info")
    request_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            request_info_list = get(platform_list, 'Request', None)
            if request_info_list:
                request_map_temp = {}
                for request in request_info_list:
                    if request['id'] == '0':
                        continue
                    request_map_temp[str(request['id'])] = request
                
                request_info[os_platform] = request_map_temp

    return request_info




@cache(namespace='level_up_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def level_up_info_map(db:Session):
    # logger.warning("call level up = Refresh Level Up Info")
    level_up_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            level_up_info_list = get(platform_list, 'KnightsLevelExp', None)
            if level_up_info_list:
                level_up_map_temp = {}
                for level_up in level_up_info_list:
                    if level_up['id'] == '0':
                        continue
                    level_up_map_temp[str(level_up['id'])] = level_up
                
                level_up_info[os_platform] = level_up_map_temp

    return level_up_info




@cache(namespace='count_refresh_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def count_refresh_info_map(db:Session):
    # logger.warning("call count refresh = Refresh Count Refresh Info")
    count_refresh_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            count_refresh_info_list = get(platform_list, 'CountRefresh', None)
            if count_refresh_info_list:
                count_refresh_map_temp = {}
                for count_refresh in count_refresh_info_list:
                    if count_refresh['id'] == '0':
                        continue
                    count_refresh_map_temp[str(count_refresh['id'])] = count_refresh
                
                count_refresh_info[os_platform] = count_refresh_map_temp

    return count_refresh_info





@cache(namespace='building_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def building_info_map(db:Session):
    # logger.warning("call building = Refresh Building Info")
    building_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            building_info_list = get(platform_list, 'Building', None)
            if building_info_list:
                building_map_temp = {}
                for buinding in building_info_list:
                    if buinding['id'] == '0':
                        continue
                    building_map_temp[str(buinding['id'])] = buinding
                
                building_info[os_platform] = building_map_temp

    return building_info



@cache(namespace='expedition_battle_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def expedition_battle_info_map(db:Session):
    # logger.warning("call expedition battle = Refresh Expedition Battle")
    expedition_battle_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            expedition_battle_info_list = get(platform_list, 'ExpeditionBattle', None)
            if expedition_battle_info_list:
                expedition_battle_map_temp = {}
                for expedition_battle in expedition_battle_info_list:
                    if expedition_battle['id'] == '0':
                        continue
                    expedition_battle_map_temp[str(expedition_battle['id'])] = expedition_battle
                
                expedition_battle_info[os_platform] = expedition_battle_map_temp

    return expedition_battle_info





@cache(namespace='expedition_card_info_list', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def expedition_card_info_map(db:Session):
    # logger.warning("call expedition battle = Refresh Expedition Battle")
    expedition_card_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            expedition_card_info_list = get(platform_list, 'ExpeditionCard', None)
            if expedition_card_info_list:
                expedition_card_map_temp = {}
                for expedition_card in expedition_card_info_list:
                    if expedition_card['id'] == '0':
                        continue
                    expedition_card_map_temp[str(expedition_card['id'])] = expedition_card
                
                expedition_card_info[os_platform] = expedition_card_map_temp

    return expedition_card_info




@cache(namespace='expedition_card_info_map', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def expedition_card_info_list(db:Session):
    # logger.warning("call gacha = Refresh Gacha Info")
    expedition_card_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            expedition_card_info_list = get(platform_list, 'ExpeditionCard', None)
            if expedition_card_info_list:
                expedition_card_temp = {}
                for gacha in expedition_card_info_list:
                    if gacha['id'] == '0':
                        continue
                    if not get(expedition_card_temp, str(gacha['grade'])):
                        expedition_card_temp[str(gacha['grade'])] = []
                        expedition_card_temp[str(gacha['grade'])].append(gacha)
                    else:
                        expedition_card_temp[str(gacha['grade'])].append(gacha)
                
                expedition_card_info[os_platform] = expedition_card_temp

    return expedition_card_info



@cache(namespace='expedition_shop_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def expedition_shop_info_map(db:Session):
    # logger.warning("call expedition battle = Refresh Expedition Battle")
    expedition_shop_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            expedition_shop_info_list = get(platform_list, 'ExpeditionShop', None)
            if expedition_shop_info_list:
                expedition_shop_map_temp = {}
                for expedition_shop in expedition_shop_info_list:
                    if expedition_shop['id'] == '0':
                        continue
                    expedition_shop_map_temp[str(expedition_shop['id'])] = expedition_shop
                
                expedition_shop_info[os_platform] = expedition_shop_map_temp

    return expedition_shop_info



@cache(namespace='expedition_difficulty_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def expedition_difficulty_info_map(db:Session):
    # logger.warning("call expedition battle = Refresh Expedition Battle")
    expedition_difficulty_info = {'android':None,'ios':None,'onestore':None, }
    cache_info = await cache_data_map(db)
    for os_platform in Constant.OS_PLATFORMS:
        platform_list = get(cache_info, os_platform, None)
        if platform_list:
            expedition_difficulty_info_list = get(platform_list, 'ExpeditionDifficulty', None)
            if expedition_difficulty_info_list:
                expedition_difficulty_map_temp = {}
                for expedition_difficulty in expedition_difficulty_info_list:
                    if expedition_difficulty['id'] == '0':
                        continue
                    expedition_difficulty_map_temp[str(expedition_difficulty['id'])] = expedition_difficulty
                
                expedition_difficulty_info[os_platform] = expedition_difficulty_map_temp

    return expedition_difficulty_info
    
    
    
@cache(namespace='pvp_dummy_data_info', expire=Constant.CACHE_INFO_TTL, key_builder=my_key_builder)
async def pvp_dummy_info_map(db:Session):
    # logger.warning("call pvp dummy data = Refresh PVP Dummy Data")
    
    db_datas = crud_user_data.get_battle_dummy_data_all(db)
    dummy_datas = []
    for data in db_datas:
        dummy_datas.append(object_as_dict(data))
    
    
    return dummy_datas
    
    
    
    
    
    
    
    
    


@cache(namespace='mobile_version_info', expire=Constant.VERSION_INFO_CACHE_TTL, key_builder=my_key_builder)
async def get_mobile_version_info(db:Session):
    # logger.warning("call get_mobile_version_info = Refresh Mobild Version")
    version_info = {'android':None,'ios':None,'onestore':None, }
    for os_platform in Constant.OS_PLATFORMS:        
        version_value = crud_mobile_version.get_version_info(db, os_platform)
        if version_value:
            version_info[os_platform] = {'min_version':version_value.min_version,
                                        'max_version':version_value.max_version,
                                        'force_update':version_value.force_update,
                                        'device':version_value.device}
            logger.info(os_platform + ' ' + json.dumps(version_info[os_platform], ensure_ascii = False))
    return version_info



@cache(namespace='server_check_config_version', expire=Constant.VERSION_INFO_CACHE_TTL, key_builder=my_key_builder)
async def get_server_check_config_version(db:Session):
    # logger.warning("call get_server_check_config_version = Refresh Server Check Config Version")
    server_check_config_version:dict={'android':None,'ios':None,'onestore':None}
    for os_platform in Constant.OS_PLATFORMS:        
        server_check_config_version[os_platform] = crud_config.get_by_filter(db, 'server_check_'+os_platform)
        server_check_config_version[os_platform] = server_check_config_version[os_platform] if server_check_config_version[os_platform] else 0
        logger.info(os_platform + ' ' + json.dumps(server_check_config_version[os_platform], ensure_ascii = False))

    return server_check_config_version


@cache(namespace='publish_spec_version', expire=Constant.VERSION_INFO_CACHE_TTL, key_builder=my_key_builder)
async def get_publish_spec_version(db:Session):
    # logger.warning("call get_spec_version = Refresh Spec Version")
    spec_version:dict={'android':None,'ios':None,'onestore':None}
    for os_platform in Constant.OS_PLATFORMS:        
        spec_version[os_platform] = crud_config.get_by_filter(db, 'publish_spec_version_'+os_platform)
        spec_version[os_platform] = spec_version[os_platform] if spec_version[os_platform] else 0
        logger.info(os_platform + ' ' + json.dumps(spec_version[os_platform], ensure_ascii = False))
    
    return spec_version


@cache(namespace='app_limit_spec_version', expire=Constant.VERSION_INFO_CACHE_TTL, key_builder=my_key_builder)
async def get_app_limit_spec_version(db:Session):
    # logger.warning("call get_app_limit_spec_version = Refresh App Limit Spec Version")
    app_limit_spce_version:dict={'android':None,'ios':None,'onestore':None}
    for os_platform in Constant.OS_PLATFORMS:   
        app_limit_spce_version_value = crud_mobile_version.get_app_spec_version_limit(db, os_platform)
        if app_limit_spce_version_value:
            app_limit_spce_version[os_platform]  = {'platform':app_limit_spce_version_value.platform,
                                     'app_version':app_limit_spce_version_value.app_version,
                                     'spec_version':app_limit_spce_version_value.spec_version}
            logger.info(os_platform + ' ' + json.dumps(app_limit_spce_version[os_platform], ensure_ascii = False))
        
    return app_limit_spce_version


@cache(namespace='app_limit_lang_version', expire=Constant.VERSION_INFO_CACHE_TTL, key_builder=my_key_builder)
async def get_app_limit_lang_version(db:Session):
    # logger.warning("call get_app_limit_lang_version = Refresh App Limit Lang Version")
    app_limit_lang_version:dict={'android':None,'ios':None,'onestore':None}
    for os_platform in Constant.OS_PLATFORMS:
        app_limit_lang_version_value = crud_mobile_version.get_app_lang_version_limit(db, os_platform)
        if app_limit_lang_version_value:
            app_limit_lang_version[os_platform] = {'platform':app_limit_lang_version_value.platform,
                                     'app_version':app_limit_lang_version_value.app_version,
                                     'spec_version':app_limit_lang_version_value.spec_version}
            logger.info(os_platform + ' ' + json.dumps(app_limit_lang_version[os_platform], ensure_ascii = False))
    
    return app_limit_lang_version



@cache(namespace='app_limit_system_lang_version', expire=Constant.VERSION_INFO_CACHE_TTL, key_builder=my_key_builder)
async def get_app_limit_system_lang_version(db:Session):
    # logger.warning("call app_limit_system_lang_version = Refresh App Limit System Lang Version")
    app_limit_lang_version:dict={'android':None,'ios':None,'onestore':None}
    for os_platform in Constant.OS_PLATFORMS:
        app_limit_lang_version_value = crud_mobile_version.get_app_system_lang_version_limit(db, os_platform)
        if app_limit_lang_version_value:
            app_limit_lang_version[os_platform] = {'platform':app_limit_lang_version_value.platform,
                                     'app_version':app_limit_lang_version_value.app_version,
                                     'spec_version':app_limit_lang_version_value.spec_version}
            logger.info(os_platform + ' ' + json.dumps(app_limit_lang_version[os_platform], ensure_ascii = False))
    
    return app_limit_lang_version



@cache(namespace='app_limit_scenario_lang_version', expire=Constant.VERSION_INFO_CACHE_TTL, key_builder=my_key_builder)
async def get_app_limit_scenario_lang_version(db:Session):
    # logger.warning("call get_app_limit_scenario_lang_version = Refresh App Limit Scenario Lang Version")
    app_limit_lang_version:dict={'android':None,'ios':None,'onestore':None}
    for os_platform in Constant.OS_PLATFORMS:
        app_limit_lang_version_value = crud_mobile_version.get_app_scenario_lang_version_limit(db, os_platform)
        if app_limit_lang_version_value:
            app_limit_lang_version[os_platform] = {'platform':app_limit_lang_version_value.platform,
                                     'app_version':app_limit_lang_version_value.app_version,
                                     'spec_version':app_limit_lang_version_value.spec_version}
            logger.info(os_platform + ' ' + json.dumps(app_limit_lang_version[os_platform], ensure_ascii = False))
    
    return app_limit_lang_version





@cache(namespace='language_version', expire=Constant.VERSION_INFO_CACHE_TTL, key_builder=my_key_builder)
async def get_lang_version(db:Session):
    # logger.warning("call get_lang_version = Refresh Language Version")
    language_version:int = 0
    language_version = crud_config.get(db, 'publish_language_version')
    logger.info(json.dumps(language_version, ensure_ascii = False))
    return language_version



@cache(namespace='language_system_version', expire=Constant.VERSION_INFO_CACHE_TTL, key_builder=my_key_builder)
async def get_lang_system_version(db:Session):
    # logger.warning("call get_lang_system_version = Refresh Language Version")
    language_system_version:int = 0
    language_system_version = crud_config.get(db, 'publish_language_system_version')
    logger.info(json.dumps(language_system_version, ensure_ascii = False))
    return language_system_version



@cache(namespace='language_scenario_version', expire=Constant.VERSION_INFO_CACHE_TTL, key_builder=my_key_builder)
async def get_lang_scenario_version(db:Session):
    # logger.warning("call get_lang_scenario_version = Refresh Language Version")
    language_scenario_version:int = 0
    language_scenario_version = crud_config.get(db, 'publish_language_scenario_version')
    logger.info(json.dumps(language_scenario_version, ensure_ascii = False))
    return language_scenario_version


@cache(namespace='app_spec_detail_version', expire=Constant.VERSION_INFO_CACHE_TTL, key_builder=my_key_builder)
async def get_app_spec_detail_version(db:Session):
    # logger.warning("call app_spec_detail_version = Refresh App Spec Detail Version")
    app_spec_detail_version:dict={'android':None,'ios':None,'onestore':None}
    for os_platform in Constant.OS_PLATFORMS:
        app_spec_detail_version_value = crud_mobile_version.get_spec_detail_version_info(db, os_platform)
        if app_spec_detail_version_value:
            dictValue = []
            for item in app_spec_detail_version_value:
                dictValue.append(jsonable_encoder(item))
            app_spec_detail_version[os_platform] = dictValue
            logger.info(os_platform + ' ' + json.dumps(app_spec_detail_version[os_platform], ensure_ascii = False))
    
    return app_spec_detail_version


def read_parsheet(path):
    return pd.read_csv(path)

@cache(namespace='cparsheet', expire=Constant.SPEC_CACHE_INFO_TTL, key_builder=my_key_builder)
async def get_c_parsheet():
    return read_parsheet(f'./app/parsheet/CHARACTER.csv').to_dict('list')

@cache(namespace='wparsheet', expire=Constant.SPEC_CACHE_INFO_TTL, key_builder=my_key_builder)
async def get_w_parsheet():
    return read_parsheet(f'./app/parsheet/WEAPON.csv').to_dict('list')
