from functools import reduce
import time
import json
import random
import random
from loguru import logger
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.config.settings import Constant
from app.crud import crud_user_members, crud_user_banned, crud_user_data
from app.db.models.user import UserMembers
from app.redis.redisCache import RedisCache
from app.cache import CacheController
from app.util.util import get


async def get_daily_ranking_key(service:RedisCache, key:str, date_key:int):
    redis_key = Constant.PROJECT_NAME + '_ranking_daily_' + key + '_' + str(date_key)
    await service.set_redis_hash(Constant.REDIS_RANKING_KEYS, redis_key, 1)
    return redis_key



async def get_daily_ranking_profile_key(service:RedisCache, key:str, date_key:int):
    redis_key = Constant.PROJECT_NAME + '_ranking_profile_daily_' + key + '_' + str(date_key)
    await service.set_redis_hash(Constant.REDIS_RANKING_KEYS, redis_key, 1)
    return redis_key



def get_last_date_key():
    yesterday = datetime.now() + timedelta(days=1)
    return yesterday.strftime('%Y%m%d')



async def set_daily_ranking_list(db:Session, service:RedisCache, uid:int, key:str, score:float, data:dict, update:int, day:int=None, listing:bool=True):
    if not day:
        date_key = day
    else:
        date_key = int(datetime.now().strftime('%Y%m%d'))
        
    
    ranking_key = await get_daily_ranking_key(service, key, date_key)
    ranking_profile_key = await get_daily_ranking_profile_key(service, key, date_key)
    
    user_member_info = await crud_user_members.get(db, uid)
    
    if not user_member_info:
        return False
    
    if update == 1:
        await set_ranking_profile(service, ranking_profile_key, uid, user_member_info.nickname, data)
        black_list = await get_block_list(service)
        
        if (uid not in black_list):
            rank_score = score
            my_score = await service.get_rank_score(ranking_key, uid)
            if my_score == None: my_score = 0
            if not my_score:
                if int(my_score) < int(rank_score):
                    await service.set_rank_add(ranking_key, rank_score, uid)
                else:
                    score = int(my_score)
            else:
                await service.set_rank_add(ranking_key, rank_score, uid)

            await service.set_expire(ranking_key, Constant.REDIS_DAILY_RANKING_EXPIRED_SEC)
            await service.set_expire(ranking_profile_key, Constant.REDIS_DAILY_RANKING_EXPIRED_SEC)
    
    
    return await get_daily_ranking_list(service, date_key, uid, user_member_info, ranking_key, ranking_profile_key, score, listing)
    
    
    


async def get_last_daily_ranking_list(db:Session, service:RedisCache, uid:int, key:str):
    yesterday_date_key = get_last_date_key()
    ranking_key = await get_daily_ranking_key(key, yesterday_date_key)
    ranking_profile_key = await get_daily_ranking_profile_key(key, yesterday_date_key)
    
    user_member_info = await crud_user_members.get(db, uid)
    if not user_member_info:
        return False
    
    return await get_last_daily_ranking_result(service, yesterday_date_key, uid, user_member_info, ranking_key, ranking_profile_key)



async def get_last_daily_ranking_result(service:RedisCache, date_number:int, uid:int, user_member_info:UserMembers, ranking_key:str, ranking_profile_key:str='', my_score:int=-1):
    my_rank = await service.get_rank(ranking_key, uid)
    if my_rank == None:
        my_rank = -1
    else:
        my_rank += 1        
    
    total_ranker_count = await service.get_count(ranking_key)
    rank_data = await service.get_rank_range(ranking_key, 0, Constant.REDIS_WEEKLY_RANKING_TOP_CNT, withscores=True)
    uid_list = []
    

    if rank_data and (len(rank_data) > 0) :
        for data in rank_data:
            uid_list.append(int(data[0]))
            
    
    if not uid_list:
        return {
            'myInfo' : {
                'nickname' : user_member_info.nickname,
                'rank' : my_rank,
                'score' : 0
            },
            'dateNumber' : int(date_number),
            'totalUserCount' : total_ranker_count,
            'rankings' : []
        }
    else:
        my_rank_index = my_rank - 1
        
        if (my_score < 0) and (my_rank_index >= 0):
            my_score = 0
            score_list = await service.get_rank_range(ranking_key, my_rank_index, my_rank_index, withscores=True)
            if score_list:
                for score in score_list:
                    if int(score[0]) == uid:
                        my_score = int(score[1])

        
        rankings = []
        user_list = await service.get_multi_hash(ranking_profile_key, *uid_list)
        
        rank = 0
        prev_rank = -1
        prev_score = -1
        same_score_cnt = 1
        idx = 1
        
        ## TODO : KIMKJ 여기에 클랜 정보를 가지고 올 수 잇는 로직이 추가되어야 함. (정확하게는 맵타입)
        
        for rank_uid in rank_data:
            if not user_list[idx-1]: continue
            
            rank_user_info = json.loads(user_list[idx-1])
            if not rank_user_info: continue
            
            user_score = int(rank_uid[1])
            
            if user_score != prev_score:
                prev_score = user_score
                rank += same_score_cnt
                prev_rank = rank
                same_score_cnt = 1
            else:
                same_score_cnt += 1
                
            if ('uid' in rank_user_info ) and (rank_user_info['uid'] == uid):
                my_rank = prev_rank
        
            idx += 1
        
        return {
            'myInfo' : {
                'nickname' : user_member_info.nickname,
                'rank' : my_rank,
                'score' : my_score
            },
            'dateNumber' : int(date_number),
            'totalUserCount' : total_ranker_count,
            'rankings' : rankings
        }
        


async def get_daily_ranking_list(service:RedisCache, date_number:int, uid:int, user_member_info:UserMembers, ranking_key:str, ranking_profile_key:str, my_score:int=-1, listing:bool=True):
    my_rank = await service.get_rank(ranking_key, uid)
    if my_rank == None:
        my_rank = -1
    else:
        my_rank += 1
    
    total_ranker_count = await service.get_count(ranking_key)
    rank_data = await service.get_rank_range(ranking_key, 0, Constant.REDIS_WEEKLY_RANKING_TOP_CNT, withscores=True)
    uid_list = []

    if rank_data and (len(rank_data) > 0) :
        for data in rank_data:
            uid_list.append(int(data[0]))
            
    
    if not uid_list:
        return {
            'myInfo' : {
                'nickname' : user_member_info.nickname,
                'rank' : my_rank,
                'score' : 0
            },
            'dateNumber' : int(date_number),
            'totalUserCount' : total_ranker_count,
            'rankings' : []
        }
    else:
        my_rank_index = my_rank - 1
        
        if (my_score < 0) and (my_rank_index >= 0):
            my_score = 0
            score_list = await service.get_rank_range(ranking_key, my_rank_index, my_rank_index, withscores=True)
            if score_list:
                for score in score_list:
                    if int(score[0]) == uid:
                        my_score = int(score[1])

        
        rankings = []
        user_list = await service.get_multi_hash(ranking_profile_key, *uid_list)
        
        rank = 0
        prev_rank = -1
        prev_score = -1
        same_score_cnt = 1
        idx = 1
        
        for rank_uid in rank_data:
            if not user_list[idx-1]: continue
            
            rank_user_info = json.loads(user_list[idx-1])
            if not rank_user_info: continue
            
            user_score = int(rank_uid[1])
            
            if user_score != prev_score:
                prev_score = user_score
                rank += same_score_cnt
                prev_rank = rank
                same_score_cnt = 1
            else:
                same_score_cnt += 1
                
            
            rankings.append({
                'rank' : prev_rank,
                'nickname' : rank_user_info['nickname'] if 'nickname' in rank_user_info and rank_user_info['nickname'] else 'unknown',
                'clan' : None,
                'score' : user_score,
                'data' : rank_user_info['data'] if 'data' in rank_user_info and rank_user_info['data'] else []
            })
            
                
            if ('uid' in rank_user_info ) and (rank_user_info['uid'] == uid):
                my_rank = prev_rank
        
            idx += 1
        
        if listing == 0:
            return {
                'myInfo' : {
                    'nickname' : user_member_info.nickname,
                    'rank' : my_rank,
                    'score' : my_score
                },
                'dateNumber' : int(date_number),
                'totalUserCount' : total_ranker_count,
                'rankings' : []
            }
        
        return {
            'myInfo' : {
                'nickname' : user_member_info.nickname,
                'rank' : my_rank,
                'score' : my_score
            },
            'dateNumber' : int(date_number),
            'totalUserCount' : total_ranker_count,
            'rankings' : rankings
        }



####################################################################################################################################################################
## custom weekly
####################################################################################################################################################################
async def get_weekly_ranking_position_list_key(service:RedisCache, key:str, week:int):
    redis_key = Constant.PROJECT_NAME + '_ranking_position_' + key + '_' + str(week)
    await service.set_redis_hash(Constant.REDIS_RANKING_KEYS, redis_key, 1)
    return redis_key


async def get_weekly_ranking_position(service:RedisCache, key:str, week:int, multiple:bool):
    if multiple:
        redis_key = Constant.PROJECT_NAME + '_ranking_multiple_position_' + key + '_' + str(week)
    else:
        redis_key = Constant.PROJECT_NAME + '_ranking_position_' + key + '_' + str(week)
        
    await service.set_redis_hash(Constant.REDIS_RANKING_KEYS, redis_key, 1)
    return redis_key


def has_key_word(service:RedisCache, key:str):
    searches = {'Forest':4, 'FrozenValley':3}
    for search in searches.keys:
        if key.find(search) >= 0:
            return search
    return None


def get_custom_week_number(day:int):
    now = datetime.now()
    delta = timedelta(days=-day)
    delta_time = now + delta
    return delta_time.isocalendar()[1]

def get_custom_prev_week_number(day:int):
    now = datetime.now()
    delta = timedelta(days=-(day + 7))
    delta_time = now + delta
    return delta_time.isocalendar()[1]


def get_custom_weekly_ranking_position_key(service:RedisCache, key:str, week:int):
    redis_key = Constant.PROJECT_NAME + '_ranking_position_' + key + "_" + str(week)
    service.set_hash(Constant.REDIS_RANKING_KEYS, redis_key, 1)
    return redis_key


def get_custom_history_key(key:str, week:int):
    return Constant.PROJECT_NAME+'_'+key+'_List_'+str(week)



async def set_custom_weekly_ranking_list(db:Session, service:RedisCache, uid:int, key:str, score:int, day:int, data:dict, update:int, week:int=0, multiple:bool=True):
    
    if week:
        current_week = week
    else:
        current_week = get_custom_week_number(day)
        
    prev_week = get_custom_prev_week_number(day)
    
    redis_key = Constant.PROJECT_NAME+'_ranking_'+key
    
    
    position_key = await get_weekly_ranking_position_list_key(service, key, current_week)
    history_key = get_custom_history_key(key, current_week)
    user_custom_ranking_key = await get_ranking_history(service, history_key, uid)
            
    if user_custom_ranking_key == None:
        #전주 작업을 먼저 잔행한다.
        prev_history_key = get_custom_history_key(key, prev_week)
        user_prev_ranking_key = await get_ranking_history(service, prev_history_key, uid)
        
        if user_prev_ranking_key == None:
            my_prev_rank = 0
        else:
            my_prev_rank = await service.get_rank(user_prev_ranking_key, uid)
            if my_prev_rank == None:
                my_prev_rank = 0
            else:
                my_prev_rank += 1
        
        if multiple:
            current_position_list = await service.get_value(redis_key)
            if current_position_list == None:
                current_position_list = []
                #initialize array
                for i in range(0, 1000):
                    current_position_list.append(0)
            else:
                current_position_list = json.loads(current_position_list)
                        
            for i in range(current_position_list[my_prev_rank], 10000):
                user_custom_ranking_key = redis_key+'_'+str(i)+'_'+str(my_prev_rank)+'_'+str(current_week)
                total_ranker_count = await service.get_count(user_custom_ranking_key)
                if total_ranker_count < Constant.RANKING_SECTION_MAX:
                    await set_ranking_history(service, history_key, uid, user_custom_ranking_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)
                    await service.set_rank_add(user_custom_ranking_key, 0, uid)
                    await service.set_expire(user_custom_ranking_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)
                    current_position_list[my_prev_rank] = i
                    await service.set_value(position_key, json.dumps(current_position_list, ensure_ascii = False))
                    await service.set_expire(position_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)

                    break
        else:
            current_position_list = service.get_value(redis_key)
            if current_position_list == None:
                current_position_list = []
                current_position_list[0] = 0
            else:
                current_position_list = json.loads(current_position_list)
                    
            for i in range(current_position_list[0], 10000):
                user_custom_ranking_key = redis_key+'_'+str(i)+'_'+str(0)+'_'+str(current_week)
                total_ranker_count = await service.get_count(user_custom_ranking_key)
                if total_ranker_count < Constant.RANKING_SECTION_MAX:
                    await set_ranking_history(service, history_key, uid, user_custom_ranking_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)
                    await service.set_rank_add(user_custom_ranking_key, int(Constant.RANKING_MARGIN_NUMBER - int(time.time())), uid)
                    await service.set_expire(user_custom_ranking_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)
                    current_position_list[0] = i
                    await service.set_value(position_key, json.dumps(current_position_list, ensure_ascii = False))
                    await service.set_expire(position_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)
                    break
    
    # set maximum number size
    # 랭킹에서 timestamp를 이용한 순위 결정 여부를 key값으로 결정하도록 수정함.
    # has_ts = True if key.find('_TS_') >= 0 else False
    
    has_ts = True
    
    ranking_key = user_custom_ranking_key
    ranking_profile_key = user_custom_ranking_key.replace('_ranking_', '_ranking_profile_')
    
    user_member_info = await crud_user_members.get(db, uid)
    if not user_member_info:
    
        return False
    
    if update == 1:
        await set_ranking_profile(service, ranking_profile_key, uid, user_member_info.nickname, data)
        is_block = is_block_list(db, service, uid)
        # need time stamp => value is small
        if (score < 100000000) and not is_block:
            rank_score = int(score * Constant.RANKING_MARGIN_NUMBER)
            rank_score = rank_score + int(Constant.RANKING_MARGIN_NUMBER - int(time.time()))
            
            my_score = await service.get_rank_score(ranking_key, uid)
            if my_score:
                if int(my_score) < int(rank_score):
                    await service.set_rank_add(ranking_key, rank_score, uid)
                else:
                    score = int(my_score)/Constant.RANKING_MARGIN_NUMBER
            else:
                await service.set_rank_add(ranking_key, rank_score, uid)

            await service.set_expire(ranking_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)
            await service.set_expire(ranking_profile_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)

            
            
    return await get_ranking_custom_list(db, service, current_week, uid, user_member_info, ranking_key, ranking_profile_key, score)



async def get_ranking_custom_list(db:Session, service:RedisCache, week_number:int, uid:int, user_member_info:UserMembers, ranking_key:str, ranking_profile_key:str, my_score:int=-1):
    my_rank = await service.get_rank(ranking_key, uid)
    if my_rank == None:
        my_rank = -1
    else:
        my_rank += 1
    
    # set maximum number size
    has_ts = True
    
    total_ranker_cnt = await service.get_count(ranking_key)
    
    if (ranking_key.find('PVP') >= 0) and (total_ranker_cnt < 10):
        await set_pvp_dummy_rank_data(db, service, ranking_key, ranking_profile_key, 1000)
        
    rank_data = await service.get_rank_range(ranking_key, 0, Constant.REDIS_WEEKLY_RANKING_TOP_CNT, withscores=True)
    
    uid_list = []

    if rank_data and (len(rank_data) > 0) :
        for data in rank_data:
            uid_list.append(int(data[0]))
            
    
    if not uid_list:
        return {
            'myInfo' : {
                'nickname' : user_member_info.nickname,
                'rank' : my_rank,
                'score' : 0
            },
            'dateNumber' : int(week_number),
            'totalUserCount' : total_ranker_cnt,
            'rankings' : []
        }
    else:
        my_rank_index = my_rank - 1
        
        if ranking_key.find('PVP') >= 0:
            if my_score <= 0 and my_rank_index >= 0:
                my_score = 0
                score_list = await service.get_rank_range(ranking_key, my_rank_index, my_rank_index, withscores=True)
                if score_list:
                    for score in score_list:
                        if int(score[0]) == uid:
                            my_score = int(score[1])/Constant.RANKING_MARGIN_NUMBER

            else:
                my_score = Constant.RANKING_PVP_DEFAULT_VALUE
        else:
            if (my_score < 0) and (my_rank_index >= 0):
                my_score = 1000
                score_list = await service.get_rank_range(ranking_key, my_rank_index, my_rank_index, withscores=True)
                if score_list:
                    for score in score_list:
                        if int(score[0]) == uid:
                            if has_ts:
                                my_score = int(score[1])/Constant.RANKING_MARGIN_NUMBER
                            else:
                                my_score = int(score[1])
        
    rankings = []
    user_list = await service.get_multi_hash(ranking_profile_key, *uid_list)
    # user_list = await service._redis.hmget(ranking_profile_key, *uid_list)
    # 11777, 11859, 11859, 11869, 11874, 11880
    
    same_score_cnt = 1
    idx = 1
    
    ## TODO : KIMKJ 여기에 클랜 정보를 가지고 올 수 잇는 로직이 추가되어야 함. (정확하게는 맵타입)
    
    for rank_uid in rank_data:
        if len(user_list) < idx:break

        if not user_list[idx-1]: continue
        
        rank_user_info = json.loads(user_list[idx-1])
        if not rank_user_info: continue
        if ranking_key.find('PVP') >= 0:
            user_score = int(rank_uid[1]/Constant.RANKING_MARGIN_NUMBER)
        else:
            if has_ts:
                user_score = int(rank_uid[1]/Constant.RANKING_MARGIN_NUMBER)
            else:
                user_score = int(rank_uid[1])
            
        rank = same_score_cnt
        same_score_cnt += 1

        rankings.append({
            'rank' : rank,
            'uid' : rank_uid[0],
            'nickname' : rank_user_info['nickname'] if 'nickname' in rank_user_info and rank_user_info['nickname'] else 'unknown',
            'clan' : None,
            'score' : int(user_score),
            'data' : rank_user_info['data'] if 'data' in rank_user_info and rank_user_info['data'] else []
        })
        
        if ('uid' in rank_user_info ) and (rank_user_info['uid'] == uid):
            my_rank = rank

        idx += 1
    
    return {
        'myInfo' : {
            'nickname' : user_member_info.nickname,
            'rank' : my_rank,
            'score' : int(my_score)
        },
        'dateNumber' : int(week_number),
        'totalUserCount' : total_ranker_cnt,
        'rankings' : rankings
    }
    


async def get_last_custom_weekly_rakning_list(db:Session, service:RedisCache, uid:int, key:str, day:int):
    last_week = get_custom_prev_week_number(day)
    history_key = get_custom_history_key(key, last_week)
    user_custom_ranking_key = await get_ranking_history(service, history_key, uid)
    if user_custom_ranking_key == None:
        user_member_info = await crud_user_members.get(db, uid)
        if not user_member_info:
            return False
        
        return {
                'myInfo' : {
                    'nickname' : user_member_info.nickname,
                    'rank' : -1,
                    'score' : 0
                },
                'dateNumber' : int(last_week),
                'totalUserCount' : 0,
                'rankings' : []
        }
    
    ranking_key = user_custom_ranking_key
    ranking_profile_key = user_custom_ranking_key.replace('_ranking_', '_ranking_profile_')
    user_member_info = await crud_user_members.get(db, uid)
    if not user_member_info:
        return False
    
    
    return await get_last_custom_ranking_result(service, last_week, uid, user_member_info, ranking_key, ranking_profile_key)



async def get_last_custom_ranking_result(service:RedisCache, week_number:int, uid:int, user_member_info:UserMembers, ranking_key:str, ranking_profile_key:str='', my_score:int=-1):

    # has_ts = True if ranking_key.find('_TS_') >= 0 else False
    has_ts = True
    
    my_rank = await service.get_rank(ranking_key, uid)
    if my_rank == None:
        my_rank = -1
    else:
        my_rank += 1
        
    total_ranker_cnt = await service.get_count(ranking_key)
    
    rank_data = await service.get_rank_range(ranking_key, 0, Constant.REDIS_WEEKLY_RANKING_TOP_CNT, withscores=True)
    
    uid_list = []

    if rank_data and (len(rank_data) > 0) :
        for data in rank_data:
            uid_list.append(int(data[0]))
            
    
    if not uid_list:
        return {
            'myInfo' : {
                'nickname' : user_member_info.nickname,
                'rank' : my_rank,
                'score' : 0
            },
            'dateNumber' : int(week_number),
            'totalUserCount' : total_ranker_cnt,
            'rankings' : []
        }
    else:
        my_rank_index = my_rank - 1
        
        if ranking_key.find('PVP') >= 0:
            if my_score <= 0 and my_rank_index >= 0:
                my_score = 0
                score_list = await service.get_rank_range(ranking_key, my_rank_index, my_rank_index, withscores=True)
                if score_list:
                    for score in score_list:
                        if int(score[0]) == uid:
                            if has_ts:
                                my_score = int(score[1]/Constant.RANKING_MARGIN_NUMBER)
                            else:
                                my_score = score[1]
        else:
            if (my_score < 0) and (my_rank_index >= 0):
                my_score = 0
                score_list = await service.get_rank_range(ranking_key, my_rank_index, my_rank_index, withscores=True)
                if score_list:
                    for score in score_list:
                        if int(score[0]) == uid:
                            if has_ts:
                                my_score = int(score[1]/Constant.RANKING_MARGIN_NUMBER)
                            else:
                                my_score = score[1]
        
    rankings = []
    user_list = await service.get_multi_hash(ranking_profile_key, *uid_list)
    
    same_score_cnt = 1
    idx = 1
    
    ## TODO : KIMKJ 여기에 클랜 정보를 가지고 올 수 잇는 로직이 추가되어야 함. (정확하게는 맵타입)
    
    for rank_uid in rank_data:
        if not user_list[idx-1]: continue
        
        rank_user_info = json.loads(user_list[idx-1])
        if not rank_user_info: continue
        
        user_score = int(rank_uid[1]/Constant.RANKING_MARGIN_NUMBER)
        rank = same_score_cnt
        same_score_cnt += 1

        # rankings.append({
        #     'rank' : rank,
        #     'uid' : rank_uid[0],
        #     'nickname' : rank_user_info['nickname'] if 'nickname' in rank_user_info and rank_user_info['nickname'] else 'unknown',
        #     'clan' : None,
        #     'score' : user_score,
        #     'data' : rank_user_info['data'] if 'data' in rank_user_info and rank_user_info['data'] else []
        # })
        
        if ('uid' in rank_user_info ) and (rank_user_info['uid'] == uid):
            my_rank = rank

        idx += 1
    
    return {
        'myInfo' : {
            'nickname' : user_member_info.nickname,
            'rank' : my_rank,
            'score' : my_score
        },
        'dateNumber' : int(week_number),
        'totalUserCount' : total_ranker_cnt,
        'rankings' : rankings
    }


####################################################################################################################################################################
## weekly
####################################################################################################################################################################



def get_week_number():
    return datetime.now().isocalendar()[1]


def get_last_week_number():
    now = datetime.now()
    delta = timedelta(weeks=-1)
    delta_time = now + delta
    return delta_time.isocalendar()[1]


async def get_weekly_ranking_key(service:RedisCache, key:str, week:int):
    redis_key = Constant.PROJECT_NAME + '_ranking_' + key + '_' + str(week)
    await service.set_redis_hash(Constant.REDIS_RANKING_KEYS, redis_key, 1)
    return redis_key


async def get_weekly_ranking_profile_key(service:RedisCache, key:str, week:int):
    redis_key = Constant.PROJECT_NAME + '_ranking_profile_' + key + '_' + str(week)
    await service.set_redis_hash(Constant.REDIS_RANKING_KEYS, redis_key, 1)
    return redis_key



async def set_weekly_ranking_list(db:Session, service:RedisCache, uid:int, key:str, score:int, data:dict, update:int, week:int=None):
    if not week:
        current_week = get_week_number()
    else:
        current_week = week
    
    # set maximum number size
    # 랭킹에서 timestamp를 이용한 순위 결정 여부를 key값으로 결정하도록 수정함.
    has_ts = True if key.find('_TS_') >= 0 else False
    
    
    ranking_key = await get_weekly_ranking_key(service, key, current_week)
    ranking_profile_key = await get_weekly_ranking_profile_key(service, key, current_week)
    
    user_member_info = await crud_user_members.get(db, uid)
    if not user_member_info:
        return False
    
    if update == 1:
        # search = has_key_word(service, key)
        # if search:
        #     history_list_key = await get_weekly_ranking_position_list_key(service, search, current_week)
        #     await service.set_expire(history_list_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)
        #     await set_ranking_history(service, history_list_key, uid, ranking_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)
        
        await set_ranking_profile(service, ranking_profile_key, uid, user_member_info.nickname, data)
        is_block = is_block_list(db, service, uid)
        # need time stamp => value is small
        if has_ts:
            if (score < 100000000) and not is_block:
                rank_score = score * Constant.RANKING_MARGIN_NUMBER
                rank_score = rank_score + (Constant.RANKING_MARGIN_NUMBER - int(time.time()))
                
                my_score = await service.get_rank_score(ranking_key, uid)
                if my_score:
                    if int(my_score) < int(rank_score):
                        await service.set_rank_add(ranking_key, rank_score, uid)
                    else:
                        score = int(my_score)/Constant.RANKING_MARGIN_NUMBER
                else:
                    await service.set_rank_add(ranking_key, rank_score, uid)

                await service.set_expire(ranking_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)
                await service.set_expire(ranking_profile_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)
        else: 
            if not is_block:
                rank_score = score
                my_score = await service.get_rank_score(ranking_key, uid)
                if my_score:
                    if my_score < rank_score:
                        await service.set_rank_add(ranking_key, rank_score, uid)
                    else:
                        score = my_score
                else:
                    await service.set_rank_add(ranking_key, rank_score, uid)

                await service.set_expire(ranking_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)
                await service.set_expire(ranking_profile_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)
            
            
    return await get_ranking_list(db, service, current_week, uid, user_member_info, ranking_key, ranking_profile_key, score)



async def get_last_weekly_rakning_list(db:Session, service:RedisCache, uid:int, key:str):
    last_week = get_last_week_number()
    ranking_key = await get_weekly_ranking_key(service, key, last_week)
    ranking_profile_key = await get_weekly_ranking_profile_key(service, key, last_week)
    
    user_member_info = await crud_user_members.get(db, uid)
    if not user_member_info:
        return False
    
    return await get_last_ranking_result(service, last_week, uid, user_member_info, ranking_key, ranking_profile_key)


async def get_weekly_section_ranking_recommand(service:RedisCache, key:str, week:int=None, multiple:bool=False, section:int=0):
    
    if not week:
        current_week = get_week_number()
    else:
        current_week = week
    
    arr_rankings = []
    
    ranking_position_key = get_weekly_ranking_position(service, key, current_week, multiple)
    redis_key = Constant.PROJECT_NAME + '_ranking_' + key
        
    if multiple:
        current_position_list = await service.get_value(ranking_position_key)
        
        if not current_position_list:
            current_position_list = []
        else:
            current_position_list = json.loads(current_position_list)

        for i  in range(0, section):
            if len(current_position_list) <= i:
                current_position_list.append(0)
        
        for i in range(int(current_position_list[section]), 10000):
            ranking_key = redis_key + '_' + str(i) + '_' + str(section) + '_' + str(current_week)
            total_ranker_cnt = await service.get_count(ranking_key)
            if total_ranker_cnt < Constant.RANKING_SECTION_MAX :
                current_position_list[section] = i
                await service.set_value(ranking_position_key, json.dumps(current_position_list, ensure_ascii = False))
                await service.set_expire(ranking_position_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)
                
                if current_position_list[section] == 0:
                    arr_rankings.append(total_ranker_cnt)
                else:
                    for j in range(0, current_position_list[section]):
                        arr_rankings.append(Constant.RANKING_SECTION_MAX)
                    arr_rankings.append(total_ranker_cnt)
                break
        
    else:
        
        current_position = await service.get_value(ranking_position_key)
        if not current_position:
            current_position = 0
            
        for i in range(current_position, 10000):
            ranking_key = redis_key + '_' + str(i) + '_' + str(current_week)
            total_ranker_cnt = await service.get_count(ranking_key)
            if total_ranker_cnt < Constant.RANKING_SECTION_MAX:
                if current_position < i:
                    current_position = i
                    await service.set_value(ranking_position_key, current_position)
                    await service.set_expire(ranking_position_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)
                
                if current_position == 0:
                    arr_rankings.append(total_ranker_cnt)
                else:
                    for j in range(0, (current_position-1)):
                        arr_rankings.append(Constant.RANKING_SECTION_MAX)
                    arr_rankings.append(total_ranker_cnt)
            break
    
    return arr_rankings




####################################################################################################################################################################
## half
####################################################################################################################################################################


async def get_half_number(db:Session):
    
    pvp_round = await CacheController.get_current_pvp_round_info(db)
    
    if pvp_round:
        return pvp_round
    
    return None
        
    
    # today = int(datetime.now().strftime('%d'))
    # if today < 15:
    #     now_date_key = int(datetime.now().strftime('%Y%m01'))
    # else:
    #     now_date_key = int(datetime.now().strftime('%Y%m15'))
    # return now_date_key


async def get_last_half_number(db:Session):
    pvp_round = await CacheController.get_current_pvp_round_info(db)
    
    if pvp_round:
        return pvp_round['id'] - 1
    
    return None
    


async def get_half_ranking_key(service:RedisCache, key:str, week:int):
    redis_key = Constant.PROJECT_NAME + '_ranking_' + key + '_' + str(week)
    await service.set_redis_hash(Constant.REDIS_RANKING_KEYS, redis_key, 1)
    return redis_key



async def get_half_ranking_profile_key(service:RedisCache, key:str, week:int):
    redis_key = Constant.PROJECT_NAME + '_ranking_profile_' + key + '_' + str(week)
    await service.set_redis_hash(Constant.REDIS_RANKING_KEYS, redis_key, 1)
    return redis_key



async def set_half_ranking_list(db:Session, service:RedisCache, uid:int, key:str, score:int, data:dict, update:int, week:int=None):
    if not week:
        current_half = await get_half_number(db)
        current_half = current_half['id']
    else:
        current_half = week
    
    # set maximum number size
    # 랭킹에서 timestamp를 이용한 순위 결정 여부를 key값으로 결정하도록 수정함.
    has_ts = True if key.find('_TS_') >= 0 else False
    
    
    ranking_key = await get_half_ranking_key(service, key, current_half)
    ranking_profile_key = await get_half_ranking_profile_key(service, key, current_half)
    
    user_member_info = await crud_user_members.get(db, uid)
    if not user_member_info:
        return False
    
    if update == 1:
        if data:
            await set_ranking_profile(service, ranking_profile_key, uid, user_member_info.nickname, data)
        else:
            await set_ranking_profile(service, ranking_profile_key, uid, user_member_info.nickname, {})
        
        is_block = is_block_list(db, service, uid)
        # need time stamp => value is small
        if has_ts:
            if (score < 100000000) and not is_block:
                rank_score = score * Constant.RANKING_MARGIN_NUMBER
                rank_score = rank_score + (Constant.RANKING_MARGIN_NUMBER - int(time.time()))
                
                my_score = await service.get_rank_score(ranking_key, uid)
                if my_score:
                    if int(my_score) < int(rank_score):
                        await service.set_rank_add(ranking_key, rank_score, uid)
                    else:
                        score = int(my_score)/Constant.RANKING_MARGIN_NUMBER
                else:
                    await service.set_rank_add(ranking_key, rank_score, uid)

                await service.set_expire(ranking_key, Constant.REDIS_HALF_RANKING_EXPIRED_SEC)
                await service.set_expire(ranking_profile_key, Constant.REDIS_HALF_RANKING_EXPIRED_SEC)
        else: 
            if not is_block:
                if (ranking_key.find('PVP') >= 0):
                    rank_score = score * Constant.RANKING_MARGIN_NUMBER
                    rank_score = rank_score + (Constant.RANKING_MARGIN_NUMBER - int(time.time()))
                    my_score = await service.get_rank_score(ranking_key, uid)
                else:
                    rank_score = score
                    my_score = await service.get_rank_score(ranking_key, uid)
                if my_score:
                    if my_score < rank_score:
                        await service.set_rank_add(ranking_key, rank_score, uid)
                    else:
                        score = my_score
                else:
                    await service.set_rank_add(ranking_key, rank_score, uid)

                await service.set_expire(ranking_key, Constant.REDIS_HALF_RANKING_EXPIRED_SEC)
                await service.set_expire(ranking_profile_key, Constant.REDIS_HALF_RANKING_EXPIRED_SEC)
            
            
    return await get_ranking_list(db, service, current_half, uid, user_member_info, ranking_key, ranking_profile_key, score)



async def get_last_half_rakning_list(db:Session, service:RedisCache, uid:int, key:str):
    last_week = await get_last_half_number(db)
    ranking_key = await get_half_ranking_key(service, key, last_week)
    ranking_profile_key = await get_half_ranking_profile_key(service, key, last_week)
    
    user_member_info = await crud_user_members.get(db, uid)
    if not user_member_info:
        return False
    
    return await get_last_ranking_result(service, last_week, uid, user_member_info, ranking_key, ranking_profile_key)



async def get_half_pvp_user(db:Session, service:RedisCache, uid:int, key:str):
    half = await get_half_number(db)
    week = half['id']
    ranking_key = await get_weekly_ranking_key(service, key, week)
    ranking_profile_key = await get_weekly_ranking_profile_key(service, key, week)
    
    my_rank = await service.get_rank(ranking_key, uid)
   
    if my_rank == None:
        my_rank = -1
    else:
        my_rank += 1
    
    total_ranker_cnt = await service.get_count(ranking_key)
    if total_ranker_cnt == 0:
        await set_pvp_dummy_rank_data(db, service, ranking_key, ranking_profile_key, 1000)
        total_ranker_cnt = await service.get_count(ranking_key)

    debug_type = 0
    match_uid = []
    
    if my_rank == 1:
        rank_data = await service.get_rank_range(ranking_key, 0, 10, withscores=True)
        uid_list = []

        if rank_data and (len(rank_data) > 0) :
            for data in rank_data:
                uid_list.append(int(data[0]))
        
        for i in range(0, 6):
            rand = random.randint(0, len(uid_list)-1)
            match_uid.append(uid_list[rand])
            uid_list.remove(uid_list[rand])
        
        ## 양방향 스코어 셋이라 내가 선택될 수 있음.
        if uid in match_uid:
            match_uid.remove(uid)
        debug_type = 1
    elif my_rank > 1 and my_rank <= 20:
        rank_data_t = await service.get_rank_range(ranking_key, 0, my_rank - 2, withscores=True)
        rank_data_u = await service.get_rank_range(ranking_key, my_rank, 20, withscores=True)
        rank_data = rank_data_t + rank_data_u
        uid_list = []
        if rank_data and (len(rank_data) > 0) :
            for data in rank_data:
                uid_list.append(int(data[0]))
        
        for i in range(0, 6):
            rand = random.randint(0, len(uid_list)-1)
            match_uid.append(uid_list[rand])
            uid_list.remove(uid_list[rand])
        
        ## 양방향 스코어 셋이라 내가 선택될 수 있음.
        if uid in match_uid:
            match_uid.remove(uid)
        
        debug_type = 2
    elif my_rank > 20:
        value_under = my_rank - int(my_rank * 30 / 100)
        default_under = my_rank - int(my_rank * 10 / 100)
        default_top = my_rank + int(my_rank * 10 / 100)
        value_top = my_rank + int(my_rank * 30 / 100)
        
        rank_data = await service.get_rank_range(ranking_key, value_under, default_under, withscores=True)
        uid_index = int(rank_data[random.randint(0, len(rank_data) - 1)][0])
        match_uid.append(uid_index)
        
        rank_data_u = await service.get_rank_range(ranking_key, default_under, (my_rank - 2), withscores=True)
        rank_data_t = await service.get_rank_range(ranking_key, my_rank, default_top, withscores=True)
        rank_data = rank_data_u + rank_data_t
        checker = False
        while(checker == False):
            uid_index = int(rank_data[random.randint(0, len(rank_data) - 1)][0])
            if uid_index not in match_uid: checker = True
        
        match_uid.append(uid_index)
        
        start = 0 if (total_ranker_cnt - 50) <= 0 else total_ranker_cnt - 100
        
        if my_rank > start:
            rank_data = await service.get_rank_range(ranking_key, start, total_ranker_cnt, withscores=True)
            checker = False
            while(checker == False):
                uid_index = int(rank_data[random.randint(0, len(rank_data) - 1)][0])
                if uid_index not in match_uid: checker = True
            match_uid.append(uid_index)
            
            checker = False
            while(checker == False):
                uid_index = int(rank_data[random.randint(0, len(rank_data) - 1)][0])
                if uid_index not in match_uid: checker = True
            match_uid.append(uid_index)
            
            checker = False
            while(checker == False):
                uid_index = int(rank_data[random.randint(0, len(rank_data) - 1)][0])
                if uid_index not in match_uid: checker = True
            match_uid.append(uid_index)
            
            checker = False
            while(checker == False):
                uid_index = int(rank_data[random.randint(0, len(rank_data) - 1)][0])
                if uid_index not in match_uid: checker = True
            match_uid.append(uid_index)
            
        else:
            rank_data = await service.get_rank_range(ranking_key, my_rank, value_top, withscores=True)
            checker = False
            while(checker == False):
                uid_index = int(rank_data[random.randint(0, len(rank_data) - 1)][0])
                if uid_index not in match_uid: checker = True
            match_uid.append(uid_index)
            
            checker = False
            while(checker == False):
                uid_index = int(rank_data[random.randint(0, len(rank_data) - 1)][0])
                if uid_index not in match_uid: checker = True
            match_uid.append(uid_index)
            
            checker = False
            while(checker == False):
                uid_index = int(rank_data[random.randint(0, len(rank_data) - 1)][0])
                if uid_index not in match_uid: checker = True
            match_uid.append(uid_index)
            
            checker = False
            while(checker == False):
                uid_index = int(rank_data[random.randint(0, len(rank_data) - 1)][0])
                if uid_index not in match_uid: checker = True
            match_uid.append(uid_index)
        ## 양방향 스코어 셋이라 내가 선택될 수 있음.
        if uid in match_uid:
            match_uid.remove(uid)
        
        debug_type = 3
    else:
        start = 0 if (total_ranker_cnt - 100) <= 0 else total_ranker_cnt - 100
        rank_data = await service.get_rank_range(ranking_key, start, total_ranker_cnt, withscores=True)
        uid_list = []
        if rank_data and (len(rank_data) > 0) :
            for data in rank_data:
                uid_list.append(int(data[0]))
        
        for i in range(0, 6):
            rand = random.randint(0, len(uid_list)-1)
            match_uid.append(uid_list[rand])
            uid_list.remove(uid_list[rand])
        
        ## 양방향 스코어 셋이라 내가 선택될 수 있음.
        if uid in match_uid:
            match_uid.remove(uid)

        debug_type = 4

        
    match_user_info = []
    for uid in match_uid:
        rank = await service.get_rank(ranking_key, uid)
        if rank == None:
            rank = -1
        else:
            rank += 1
            
        profile_json = await service.get_hash(ranking_profile_key, uid)
        profile = None
        if profile_json:
            profile = json.loads(await service.get_hash(ranking_profile_key, uid))
        else:
            user_battle_data = crud_user_data.get_battle_data(db, uid)
            user_member_info = await crud_user_members.get(db, uid)
            user_data = json.loads(user_battle_data.data)
            await set_ranking_profile(service, ranking_profile_key, uid, user_member_info.nickname, user_data)
            profile = value = {'uid' : uid,'nickname' : user_member_info.nickname, 'data' : user_data}
        
        match_user_info.append({
            'rank' : rank,
            'uid' : uid,
            'nickname' : profile['nickname'] if 'nickname' in profile and profile['nickname'] else 'unknown',
            'score' : int(await service.get_rank_score(ranking_key, uid) / Constant.RANKING_MARGIN_NUMBER),
            'data' : profile['data'] if 'data' in profile and profile['data'] else []
        })
        
    # revenge_info = await get_revenge_list(service, uid)
    
    return {
        'myRank' : my_rank,
        'match1' : match_user_info[0],
        'match2' : match_user_info[1],
        'match3' : match_user_info[2],
        'match4' : match_user_info[3],
        'match5' : match_user_info[4],
        # 'revenge_list' : revenge_info,
        'debugType' : debug_type
    }

    

async def set_half_pvp_score_ranking_list(db:Session, service:RedisCache, uid:int, key:str, score:int, data:dict, target_uid:int, is_win:int, is_revenge:bool):
    half = await get_half_number(db)
    week = half['id']
    ranking_key = await get_half_ranking_key(service, key, week)
    ranking_profile_key = await get_half_ranking_profile_key(service, key, week)
    
    user_member_info = await crud_user_members.get(db, uid)
    
    if not user_member_info:
        return False
    
    if data:
        await set_ranking_profile(service, ranking_profile_key, uid, user_member_info.nickname, data)
    else:
        await set_ranking_profile(service, ranking_profile_key, uid, user_member_info.nickname, {})
        
    is_block = is_block_list(db, service, uid)
    my_score = 0
    my_score_before = 0
    after_rank = 0
    before_rank = 0
    
    target_score = 0
    target_score_before = 0
    target_score_after = 0
    target_rank_before = 0
    target_rank_after = 0
    
    if (score < 100000000) and not is_block:
        before_rank = await service.get_rank(ranking_key, uid)
        if before_rank == None:
            before_rank = -1
        else:
            before_rank += 1
            
        ## 타겟 정보
        target_rank_before = await service.get_rank(ranking_key, target_uid)
        if target_rank_before == None:
            target_rank_before = -1
        else:
            target_rank_before += 1
            
        my_score = await service.get_rank_score(ranking_key, uid)
        if not my_score: my_score = 0
        
        target_score = await service.get_rank_score(ranking_key, target_uid)
        if not target_score: target_score = 0
        
        if is_win == 1:
            score_weight = 1 - (1 / (pow(10, (((target_score / Constant.RANKING_MARGIN_NUMBER)-(my_score / Constant.RANKING_MARGIN_NUMBER))/600)) + 1))
            score = int(round((my_score/Constant.RANKING_MARGIN_NUMBER) + 20 * score_weight) - (my_score / Constant.RANKING_MARGIN_NUMBER))
            score = int(score/4) if is_revenge else score
            if score <= 0: score = 1
            target_score_before = 0 if ((target_score/Constant.RANKING_MARGIN_NUMBER) - score < 0) else (target_score / Constant.RANKING_MARGIN_NUMBER) - score
            my_score_before = int((my_score/Constant.RANKING_MARGIN_NUMBER) + score)
            
            # __get_currency(db, uid, 'MEDAL', 10, None)
        else:
            score_weight = 1 - (1 / (pow(10, (((my_score / Constant.RANKING_MARGIN_NUMBER)-( target_score / Constant.RANKING_MARGIN_NUMBER))/600)) + 1))
            score = int(round((target_score/Constant.RANKING_MARGIN_NUMBER) + 20 * score_weight) - (target_score / Constant.RANKING_MARGIN_NUMBER))
            score = int(score/4) if is_revenge else score
            if score <= 0 : score =1
            target_score_before = int((target_score / Constant.RANKING_MARGIN_NUMBER) + score)
            my_score_before = 0 if (my_score/Constant.RANKING_MARGIN_NUMBER) - score < 0 else (my_score/Constant.RANKING_MARGIN_NUMBER) - score
            
        if target_uid < 101:
            dummy_info = crud_user_data.get_battle_dummy_data(db, target_uid)
            await service.set_rank_add(ranking_key, dummy_info.battle_point * Constant.RANKING_MARGIN_NUMBER, target_uid)
        else:
            target_score_before = target_score_before * Constant.RANKING_MARGIN_NUMBER
            target_score_before = target_score_before + (Constant.RANKING_MARGIN_NUMBER - int(time.time()))
            await service.set_rank_add(ranking_key, target_score_before, target_uid)
        
        my_score_before = my_score_before * Constant.RANKING_MARGIN_NUMBER
        my_score_before = my_score_before + (Constant.RANKING_MARGIN_NUMBER - int(time.time()))
        await service.set_rank_add(ranking_key, my_score_before, uid)
        
        after_rank = await service.get_rank(ranking_key, uid)
        if after_rank == None:
            after_rank = -1
        else:
            after_rank += 1
            
        target_rank_after = await service.get_rank(ranking_key, target_uid)
        if target_rank_after == None:
            target_rank_after = -1
        else:
            target_rank_after += 1
        
    pvp_info = {
        'is_win' : is_win,
        'after_rank' : after_rank,
        'before_rank' : before_rank,
        'after_score' : int( my_score_before/ Constant.RANKING_MARGIN_NUMBER),
        'before_score' : int( my_score/ Constant.RANKING_MARGIN_NUMBER)
    }
    
    pvp_target_info = {
        'is_win' : 1 if is_win == 0 else 0,
        'after_rank' : target_rank_after,
        'before_rank' : target_rank_before,
        'after_score' : int(target_score_before/ Constant.RANKING_MARGIN_NUMBER),
        'before_score' : int(target_score / Constant.RANKING_MARGIN_NUMBER)
    }        
    
    
    if is_win == 1:
        # 상대방에게 나를 알린다.
        await add_revenge_list(service, db, uid, target_uid, data, target_rank_after, int(target_score_before/ Constant.RANKING_MARGIN_NUMBER))
    
    await check_revenge(service, db, uid, target_uid, is_win)
    
    return {
        'pvp_info' : pvp_info,
        'pvp_target_info' : pvp_target_info
    }




####################################################################################################################################################################
## season
####################################################################################################################################################################

async def get_season_ranking_key(service:RedisCache, key:str):
    redis_key = Constant.PROJECT_NAME + '_ranking_' + key
    await service.set_redis_hash(Constant.REDIS_RANKING_KEYS, redis_key, 1)
    return redis_key


async def get_season_ranking_profile_key(service:RedisCache, key:str):
    redis_key = Constant.PROJECT_NAME + '_ranking_profile_' + key
    await service.set_redis_hash(Constant.REDIS_RANKING_KEYS, redis_key, 1)
    return redis_key


async def set_season_ranking_list(db:Session, service:RedisCache, uid:int, key:str, score:int, data:dict, update:int):
    ranking_key = get_season_ranking_key(service, key)
    ranking_profile_key = get_season_ranking_profile_key(service, key)
    
    user_member_info = await crud_user_members.get(db, uid)
    if not user_member_info:
        return False

    if update == 1:
        if data:
            await set_ranking_profile(service, key, uid, user_member_info.nickname, data)
        else:
            await set_ranking_profile(service, key, uid, user_member_info.nickname, {})
        
        
        is_block = is_block_list(db, service, uid)
        if (score < 100000000) and not is_block:
            rank_score = score * Constant.RANKING_MARGIN_NUMBER
            my_score = await service.get_rank_score(ranking_key, uid)
            if my_score:
                if int(my_score) < int(rank_score):
                    await service.set_rank_add(ranking_key, rank_score, uid)
                else:
                    score = int(my_score)/Constant.RANKING_MARGIN_NUMBER
            else:
                await service.set_rank_add(ranking_key, rank_score, uid)
            
    return await get_ranking_list(db, service, 0, uid, user_member_info, ranking_key, ranking_profile_key, score)


####################################################################################################################################################################
## common
####################################################################################################################################################################

async def get_ranking_list(db:Session, service:RedisCache, week_number:int, uid:int, user_member_info:UserMembers, ranking_key:str, ranking_profile_key:str, my_score:int=-1):
    my_rank = await service.get_rank(ranking_key, uid)
    if my_rank == None:
        my_rank = -1
    else:
        my_rank += 1
    
    # set maximum number size
    has_ts = True if ranking_key.find('_TS_') >= 0 else False
    
    total_ranker_cnt = await service.get_count(ranking_key)
    
    if (ranking_key.find('PVP') >= 0) and (total_ranker_cnt < 10):
        await set_pvp_dummy_rank_data(db, service, ranking_key, ranking_profile_key, 1000)
        
    rank_data = await service.get_rank_range(ranking_key, 0, Constant.REDIS_WEEKLY_RANKING_TOP_CNT, withscores=True)
    
    uid_list = []

    if rank_data and (len(rank_data) > 0) :
        for data in rank_data:
            uid_list.append(int(data[0]))
            
    
    if not uid_list:
        return {
            'myInfo' : {
                'nickname' : user_member_info.nickname,
                'rank' : my_rank,
                'score' : 0
            },
            'dateNumber' : int(week_number),
            'totalUserCount' : total_ranker_cnt,
            'rankings' : []
        }
    else:
        my_rank_index = my_rank - 1
        
        if ranking_key.find('PVP') >= 0:
            if my_score <= 0 and my_rank_index >= 0:
                my_score = 0
                score_list = await service.get_rank_range(ranking_key, my_rank_index, my_rank_index, withscores=True)
                if score_list:
                    for score in score_list:
                        if int(score[0]) == uid:
                            my_score = int(score[1])/Constant.RANKING_MARGIN_NUMBER

            else:
                my_score = Constant.RANKING_PVP_DEFAULT_VALUE
        else:
            if (my_score < 0) and (my_rank_index >= 0):
                my_score = 1000
                score_list = await service.get_rank_range(ranking_key, my_rank_index, my_rank_index, withscores=True)
                if score_list:
                    for score in score_list:
                        if int(score[0]) == uid:
                            if has_ts:
                                my_score = int(score[1])/Constant.RANKING_MARGIN_NUMBER
                            else:
                                my_score = int(score[1])
        
    rankings = []
    user_list = await service.get_multi_hash(ranking_profile_key, *uid_list)
    # user_list = await service._redis.hmget(ranking_profile_key, *uid_list)
    # 11777, 11859, 11859, 11869, 11874, 11880
    
    same_score_cnt = 1
    idx = 1
    
    ## TODO : KIMKJ 여기에 클랜 정보를 가지고 올 수 잇는 로직이 추가되어야 함. (정확하게는 맵타입)
    
    for rank_uid in rank_data:
        if len(user_list) < idx:break

        if not user_list[idx-1]: continue
        
        rank_user_info = json.loads(user_list[idx-1])
        if not rank_user_info: continue
        if ranking_key.find('PVP') >= 0:
            user_score = int(rank_uid[1]/Constant.RANKING_MARGIN_NUMBER)
        else:
            if has_ts:
                user_score = int(rank_uid[1]/Constant.RANKING_MARGIN_NUMBER)
            else:
                user_score = int(rank_uid[1])
            
        rank = same_score_cnt
        same_score_cnt += 1

        rankings.append({
            'rank' : rank,
            'uid' : rank_uid[0],
            'nickname' : rank_user_info['nickname'] if 'nickname' in rank_user_info and rank_user_info['nickname'] else 'unknown',
            'clan' : None,
            'score' : int(user_score),
            'data' : rank_user_info['data'] if 'data' in rank_user_info and rank_user_info['data'] else []
        })
        
        if ('uid' in rank_user_info ) and (rank_user_info['uid'] == uid):
            my_rank = rank

        idx += 1
    
    return {
        'myInfo' : {
            'nickname' : user_member_info.nickname,
            'rank' : my_rank,
            'score' : int(my_score)
        },
        'dateNumber' : int(week_number),
        'totalUserCount' : total_ranker_cnt,
        'rankings' : rankings
    }
    
    
async def get_ranking_info(db:Session, service:RedisCache, uid:int, key:str, week:int=None):
    
    if not week:
        current_week = get_week_number()
    else:
        current_week = week
    
    ranking_key = await get_weekly_ranking_key(service, key, current_week)
    
    # set maximum number size
    # 랭킹에서 timestamp를 이용한 순위 결정 여부를 key값으로 결정하도록 수정함.
    has_ts = True if key.find('_TS_') >= 0 else False
    
    user_member_info = await crud_user_members.get(db, uid)
    if not user_member_info:
        return False
    
    
    my_rank = await service.get_rank(ranking_key, uid)
    if my_rank == None:
        my_rank = -1
    else:
        my_rank += 1
    
    
    # set maximum number size
    has_ts = True if ranking_key.find('_TS_') >= 0 else False
    
    total_ranker_cnt = await service.get_count(ranking_key)

    my_rank_index = my_rank - 1
    
    my_score = 1000
    
    if (my_rank_index >= 0):
        score_list = await service.get_rank_range(ranking_key, my_rank_index, my_rank_index, withscores=True)
        if score_list:
            for score in score_list:
                if int(score[0]) == uid:
                    if ranking_key.find('PVP') >= 0:
                        my_score = int(score[1])/Constant.RANKING_MARGIN_NUMBER
                    else:
                        if has_ts:
                            my_score = int(score[1])/Constant.RANKING_MARGIN_NUMBER
                        else:
                            my_score = int(score[1])
    
    
    return {
        'myInfo' : {
            'nickname' : user_member_info.nickname,
            'rank' : my_rank,
            'score' : int(my_score)
        },
        'dateNumber' : int(current_week),
        'totalUserCount' : total_ranker_cnt,
    }
    



async def get_last_ranking_result(service:RedisCache, week_number:int, uid:int, user_member_info:UserMembers, ranking_key:str, ranking_profile_key:str='', my_score:int=-1):
    # search = has_key_word(service, ranking_key)
    
    # 랭킹에서 timestamp를 이용한 순위 결정 여부를 key값으로 결정하도록 수정함.
    # has_ts = True if ranking_key.find('_TS_') >= 0 else False
    has_ts = True
    
    # if search:
    #     history_list_key = Constant.PROJECT_NAME + '_ranking_' + search + '_List_' + str(week_number)
    #     temp_ranking_key = await get_ranking_history(service, history_list_key, uid)
    #     if temp_ranking_key:
    #         ranking_key = temp_ranking_key
    #         ranking_profile_key = ranking_key.replace('_ranking_', '_ranking_profile_')
    
    
    my_rank = await service.get_rank(ranking_key, uid)
    if my_rank == None:
        my_rank = -1
    else:
        my_rank += 1
        
    total_ranker_cnt = await service.get_count(ranking_key)
    
    rank_data = await service.get_rank_range(ranking_key, 0, Constant.REDIS_WEEKLY_RANKING_TOP_CNT, withscores=True)
    
    uid_list = []

    if rank_data and (len(rank_data) > 0) :
        for data in rank_data:
            uid_list.append(int(data[0]))
            
    
    if not uid_list:
        return {
            'myInfo' : {
                'nickname' : user_member_info.nickname,
                'rank' : my_rank,
                'score' : 0
            },
            'dateNumber' : int(week_number),
            'totalUserCount' : total_ranker_cnt,
            'rankings' : []
        }
    else:
        my_rank_index = my_rank - 1
        
        if ranking_key.find('PVP') >= 0:
            if my_score <= 0 and my_rank_index >= 0:
                my_score = 0
                score_list = await service.get_rank_range(ranking_key, my_rank_index, my_rank_index, withscores=True)
                if score_list:
                    for score in score_list:
                        if int(score[0]) == uid:
                            if has_ts:
                                my_score = int(int(score[1])/Constant.RANKING_MARGIN_NUMBER)
                            else:
                                my_score = score[1]
        else:
            if (my_score < 0) and (my_rank_index >= 0):
                my_score = 0
                score_list = await service.get_rank_range(ranking_key, my_rank_index, my_rank_index, withscores=True)
                if score_list:
                    for score in score_list:
                        if int(score[0]) == uid:
                            if has_ts:
                                my_score = int(int(score[1])/Constant.RANKING_MARGIN_NUMBER)
                            else:
                                my_score = score[1]
        
    rankings = []
    user_list = await service.get_multi_hash(ranking_profile_key, *uid_list)
    
    same_score_cnt = 1
    idx = 1
    
    ## TODO : KIMKJ 여기에 클랜 정보를 가지고 올 수 잇는 로직이 추가되어야 함. (정확하게는 맵타입)
    
    for rank_uid in rank_data:
        if not user_list[idx-1]: continue
        
        rank_user_info = json.loads(user_list[idx-1])
        if not rank_user_info: continue
        
        user_score = int(rank_uid[1]/Constant.RANKING_MARGIN_NUMBER)
        rank = same_score_cnt
        same_score_cnt += 1

        # rankings.append({
        #     'rank' : rank,
        #     'uid' : rank_uid[0],
        #     'nickname' : rank_user_info['nickname'] if 'nickname' in rank_user_info and rank_user_info['nickname'] else 'unknown',
        #     'clan' : None,
        #     'score' : user_score,
        #     'data' : rank_user_info['data'] if 'data' in rank_user_info and rank_user_info['data'] else []
        # })
        
        if ('uid' in rank_user_info ) and (rank_user_info['uid'] == uid):
            my_rank = rank

        idx += 1
    
    return {
        'myInfo' : {
            'nickname' : user_member_info.nickname,
            'rank' : my_rank,
            'score' : my_score
        },
        'dateNumber' : int(week_number),
        'totalUserCount' : total_ranker_cnt,
        'rankings' : rankings
    }


async def set_ranking_profile(service:RedisCache, key:str, uid:int, nickname:str, data:dict):
    value = {
        'uid' : uid,
        'nickname' : nickname,
        'data' : data
    }
    
    await service.set_redis_hash(key, uid, json.dumps(value))




async def set_ranking_history(service:RedisCache, key:str, uid:int, data:str, expire:int):
    await service.set_redis_hash(key, uid, data, expire)




async def get_ranking_history(service:RedisCache, key:str, uid:int):
    return await service.get_redis_hash(key, uid)




async def get_ranking_profile(service:RedisCache, key:str, uid:int):
    pass




async def get_ranker_clan_info(service:RedisCache, uid_list:list):
    ## TODO : KIMKJ 클랜쪽은 아직...
    pass



def is_block_list(db:Session, service:RedisCache, uid:int):
    user_banned = crud_user_banned.get(db, uid)
    return True if user_banned else False




async def get_block_list(service:RedisCache):
    block_list = await service.get_value(Constant.REDIS_RANKING_BLACKLIST)
    if not block_list:
        return []
    
    return json.loads(block_list)




async def set_block_list(service:RedisCache, uid:int):
    block_list = await service.get_value(Constant.REDIS_RANKING_BLACKLIST)
    
    if not block_list:
        block_list = [uid]
    else:
        block_list = list(json.loads(block_list))
        if uid not in block_list:
            block_list.append(uid)
        else:
            return block_list
    
    await service.set_value(Constant.REDIS_RANKING_BLACKLIST, json.dumps(block_list))
    
    return block_list


async def get_revenge_key(service:RedisCache, key:str):
    redis_key = Constant.PROJECT_NAME + '_revenge_' + key
    await service.set_redis_hash(Constant.REDIS_RANKING_KEYS, redis_key, 1)
    return redis_key


async def get_revenge_list(service:RedisCache, db:Session, uid:int):
    
    half = await get_half_number(db)
    key = await get_revenge_key(service, str(half['id']))
    
    revenge_list = await service.get_hash(key, uid)
    
    if not revenge_list:
        revenge_list = []
    else:
        revenge_list = list(json.loads(revenge_list))
        
    return revenge_list



# add my info to target
async def add_revenge_list(service:RedisCache, db:Session,  uid:int, target_uid:int, data:dict, rank:int, score:int):
    
    half = await get_half_number(db)
    key = await get_revenge_key(service, str(half['id']))
    
    revenge_list = await service.get_hash(key, target_uid)

    need_write = True
    
    if not revenge_list:
        revenge_list = []
        revenge_list.append({"UID":uid, "data":data, 'rank':rank, 'battlePoint':score, 'playState':0})
    else:
        find_target = False
        revenge_list = list(json.loads(revenge_list))
        if revenge_list:
            for revenge in revenge_list:
                if revenge['UID'] == uid:
                    find_target = True
                    break
            if not find_target:
                if len(revenge_list) >= 30:
                    revenge_list.pop(0)
                revenge_list.append({"UID":uid, "data":data, 'rank':rank, 'battlePoint':score, 'playState':0})
            else:
                need_write = False
        else:
            revenge_list.append({"UID":uid, "data":data, 'rank':rank, 'battlePoint':score, 'playState':0})
            
    if need_write:
        await service.set_hash(key, target_uid, json.dumps(revenge_list))
        await service.set_expire(key, Constant.REDIS_HALF_RANKING_EXPIRED_SEC)
    
    return revenge_list


async def check_revenge(service:RedisCache, db:Session, uid:int, target_uid:int, is_win:int):
    
    half = await get_half_number(db)
    key = await get_revenge_key(service, str(half['id']))
    
    revenge_list = await service.get_hash(key, uid)
    
    if revenge_list:
        revenge_list = list(json.loads(revenge_list))
        if revenge_list:
            find_target = False
            for revenge in revenge_list:
                if revenge['UID'] == target_uid:
                    revenge['playState'] = 1 if is_win == 1 else 2
                    find_target = True
                    break
            if find_target:
                await service.set_hash(key, uid, json.dumps(revenge_list))
                await service.set_expire(key, Constant.REDIS_HALF_RANKING_EXPIRED_SEC)
    

####################################################################################################################################################################
## common
####################################################################################################################################################################

## TODO : KIMKJ daily_dummy 호출 시에 처리 하는데 아직은 안하므로 
async def set_daily_ranking_list_dummy(service:RedisCache, uid:int, key:str, score:int, data:dict, date_key:str):
    pass




## TODO : KIMKJ weekly_dummy 호출 시에 처리 하는데 아직은 안하므로 
async def set_weekly_ranking_list_dummy(service:RedisCache, uid:int, key:str, score:int, data:dict, current_week:int):
    pass

  
    
async def get_pvp_user(db:Session, service:RedisCache, uid:int, key:str):
    week = get_week_number()
    ranking_key = await get_weekly_ranking_key(service, key, week)
    ranking_profile_key = await get_weekly_ranking_profile_key(service, key, week)
    
    my_rank = await service.get_rank(ranking_key, uid)
   
    if my_rank == None:
        my_rank = -1
    else:
        my_rank += 1
    
    total_ranker_cnt = await service.get_count(ranking_key)
    if total_ranker_cnt == 0:
        await set_pvp_dummy_rank_data(db, service, ranking_key, ranking_profile_key, 1000)
        total_ranker_cnt = await service.get_count(ranking_key)
        
    debug_type = 0
    match_uid = []
    
    if my_rank == 1:
        rank_data = await service.get_rank_range(ranking_key, 0, 10, withscores=True)
        uid_list = []

        if rank_data and (len(rank_data) > 0) :
            for data in rank_data:
                uid_list.append(int(data[0]))
        
        for i in range(0, 6):
            rand = random.randint(0, len(uid_list)-1)
            match_uid.append(uid_list[rand])
            uid_list.remove(uid_list[rand])
        
        ## 양방향 스코어 셋이라 내가 선택될 수 있음.
        if uid in match_uid:
            match_uid.remove(uid)
        debug_type = 1
    elif my_rank > 1 and my_rank <= 20:
        rank_data_t = await service.get_rank_range(ranking_key, 0, my_rank - 2, withscores=True)
        rank_data_u = await service.get_rank_range(ranking_key, my_rank, 20, withscores=True)
        rank_data = rank_data_t + rank_data_u
        uid_list = []
        if rank_data and (len(rank_data) > 0) :
            for data in rank_data:
                uid_list.append(int(data[0]))
        
        for i in range(0, 6):
            rand = random.randint(0, len(uid_list)-1)
            match_uid.append(uid_list[rand])
            uid_list.remove(uid_list[rand])
        
        ## 양방향 스코어 셋이라 내가 선택될 수 있음.
        if uid in match_uid:
            match_uid.remove(uid)
        
        debug_type = 2
    elif my_rank > 20:
        value_under = my_rank - int(my_rank * 30 / 100)
        default_under = my_rank - int(my_rank * 10 / 100)
        default_top = my_rank + int(my_rank * 10 / 100)
        value_top = my_rank + int(my_rank * 30 / 100)
        
        rank_data = await service.get_rank_range(ranking_key, value_under, default_under, withscores=True)
        uid_index = int(rank_data[random.randint(0, len(rank_data) - 1)][0])
        match_uid.append(uid_index)        
        
        rank_data_u = await service.get_rank_range(ranking_key, value_under, default_under, withscores=True)
        rank_data_t = await service.get_rank_range(ranking_key, value_under, default_under, withscores=True)
        rank_data = rank_data_u + rank_data_t
        checker = False
        while(checker == False):
            uid_index = int(rank_data[random.randint(0, len(rank_data) - 1)][0])
            if uid_index not in match_uid: checker = True
        
        match_uid.append(uid_index)
        
        start = 0 if (total_ranker_cnt - 50) <= 0 else total_ranker_cnt - 100
        
        if my_rank > start:
            rank_data = await service.get_rank_range(ranking_key, start, total_ranker_cnt, withscores=True)
            checker = False
            while(checker == False):
                uid_index = int(rank_data[random.randint(0, len(rank_data) - 1)][0])
                if uid_index not in match_uid: checker = True
            match_uid.append(uid_index)
            
            checker = False
            while(checker == False):
                uid_index = int(rank_data[random.randint(0, len(rank_data) - 1)][0])
                if uid_index not in match_uid: checker = True
            match_uid.append(uid_index)
        else:
            rank_data = await service.get_rank_range(ranking_key, my_rank, value_top, withscores=True)
            checker = False
            while(checker == False):
                uid_index = int(rank_data[random.randint(0, len(rank_data) - 1)][0])
                if uid_index not in match_uid: checker = True
            match_uid.append(uid_index)
            
            checker = False
            while(checker == False):
                uid_index = int(rank_data[random.randint(0, len(rank_data) - 1)][0])
                if uid_index not in match_uid: checker = True
            match_uid.append(uid_index)
        ## 양방향 스코어 셋이라 내가 선택될 수 있음.
        if uid in match_uid:
            match_uid.remove(uid)
        
        debug_type = 3
    else:
        start = 0 if (total_ranker_cnt - 100) <= 0 else total_ranker_cnt - 100
        rank_data = await service.get_rank_range(ranking_key, start, total_ranker_cnt, withscores=True)
        uid_list = []
        if rank_data and (len(rank_data) > 0) :
            for data in rank_data:
                uid_list.append(int(data[0]))
        
        for i in range(0, 6):
            rand = random.randint(0, len(uid_list)-1)
            match_uid.append(uid_list[rand])
            uid_list.remove(uid_list[rand])
        
        ## 양방향 스코어 셋이라 내가 선택될 수 있음.
        if uid in match_uid:
            match_uid.remove(uid)

        debug_type = 4

        
    match_user_info = []
    for uid in match_uid:
        rank = await service.get_rank(ranking_key, uid)
        if rank == None:
            rank = -1
        else:
            rank += 1
        profile = json.loads(await service.get_hash(ranking_profile_key, uid))
        
        match_user_info.append({
            'rank' : rank,
            'uid' : uid,
            'nickname' : profile['nickname'] if 'nickname' in profile and profile['nickname'] else 'unknown',
            'score' : int(await service.get_rank_score(ranking_key, uid) / Constant.RANKING_MARGIN_NUMBER),
            'data' : profile['data'] if 'data' in profile and profile['data'] else []
        })
        
    # revenge_info = await get_revenge_list(service, uid)
    
    return {
        'myRank' : my_rank,
        'match1' : match_user_info[0],
        'match2' : match_user_info[1],
        'match3' : match_user_info[2],
        'match4' : match_user_info[3],
        'match5' : match_user_info[4],
        # 'revenge_list' : revenge_info,
        'debugType' : debug_type
    }


    

async def set_pvp_score_ranking_list(db:Session, service:RedisCache, uid:int, key:str, score:int, data:dict, target_uid:int, is_win:int):
    week = get_week_number()
    ranking_key = await get_weekly_ranking_key(service, key, week)
    ranking_profile_key = await get_weekly_ranking_profile_key(service, key, week)
    
    user_member_info = await crud_user_members.get(db, uid)
    
    if not user_member_info:
        return False
    
    if data:
        await set_ranking_profile(service, ranking_profile_key, uid, user_member_info.nickname, data)
    else:
        await set_ranking_profile(service, ranking_profile_key, uid, user_member_info.nickname, {})
    
    is_block = is_block_list(db, service, uid)
    my_score = 0
    my_score_before = 0
    after_rank = 0
    before_rank = 0
    
    target_score = 0
    target_score_before = 0
    target_score_after = 0
    target_rank_before = 0
    target_rank_after = 0
    
    if (score < 100000000) and not is_block:
        before_rank = await service.get_rank(ranking_key, uid)
        if before_rank == None:
            before_rank = -1
        else:
            before_rank += 1
            
        ## 타겟 정보
        target_rank_before = await service.get_rank(ranking_key, target_uid)
        if target_rank_before == None:
            target_rank_before = -1
        else:
            target_rank_before += 1
            
        my_score = await service.get_rank_score(ranking_key, uid)
        if not my_score: my_score = 0
        
        target_score = await service.get_rank_score(ranking_key, target_uid)
        if not target_score: target_score = 0
        
        if is_win == 1:
            score_weight = 1 - (1 / (pow(10, (((target_score / Constant.RANKING_MARGIN_NUMBER)-(my_score / Constant.RANKING_MARGIN_NUMBER))/600)) + 1))
            score = int(round((my_score/Constant.RANKING_MARGIN_NUMBER) + 20 * score_weight) - (my_score / Constant.RANKING_MARGIN_NUMBER))
            if score <= 0: score = 1
            target_score_before = 0 if ((target_score/Constant.RANKING_MARGIN_NUMBER) - score < 0) else (target_score / Constant.RANKING_MARGIN_NUMBER) - score
            my_score_before = int((my_score/Constant.RANKING_MARGIN_NUMBER) + score)
        else:
            score_weight = 1 - (1 / (pow(10, (((my_score / Constant.RANKING_MARGIN_NUMBER)-( target_score / Constant.RANKING_MARGIN_NUMBER))/600)) + 1))
            score = int(round((target_score/Constant.RANKING_MARGIN_NUMBER) + 20 * score_weight) - (target_score / Constant.RANKING_MARGIN_NUMBER))
            if score <= 0 : score =1
            target_score_before = int((target_score / Constant.RANKING_MARGIN_NUMBER) + score)
            my_score_before = 0 if (my_score/Constant.RANKING_MARGIN_NUMBER) - score < 0 else (my_score/Constant.RANKING_MARGIN_NUMBER) - score
            
        if target_uid < 101 and target_score_before <= 0:
            dummy_info = crud_user_data.get_battle_dummy_data(db, target_uid)
            await service.set_rank_add(ranking_key, dummy_info.battle_point * Constant.RANKING_MARGIN_NUMBER, target_uid)
        else:
            target_score_before = target_score_before * Constant.RANKING_MARGIN_NUMBER
            target_score_before = target_score_before + (Constant.RANKING_MARGIN_NUMBER - int(time.time()))
            await service.set_rank_add(ranking_key, target_score_before, target_uid)
        
        my_score_before = my_score_before * Constant.RANKING_MARGIN_NUMBER
        my_score_before = my_score_before + (Constant.RANKING_MARGIN_NUMBER - int(time.time()))
        await service.set_rank_add(ranking_key, my_score_before, uid)
        
        after_rank = await service.get_rank(ranking_key, uid)
        if after_rank == None:
            after_rank = -1
        else:
            after_rank += 1
            
        target_rank_after = await service.get_rank(ranking_key, target_uid)
        if target_rank_after == None:
            target_rank_after = -1
        else:
            target_rank_after += 1
    
    pvp_info = {
        'is_win' : is_win,
        'after_rank' : after_rank,
        'before_rank' : before_rank,
        'after_score' : int( my_score/ Constant.RANKING_MARGIN_NUMBER),
        'before_score' : int(my_score_before / Constant.RANKING_MARGIN_NUMBER)
    }
    
    pvp_target_info = {
        'is_win' : 1 if is_win == 0 else 0,
        'after_rank' : target_rank_after,
        'before_rank' : target_rank_before,
        'after_score' : int(target_score/ Constant.RANKING_MARGIN_NUMBER),
        'before_score' : int(target_score_before / Constant.RANKING_MARGIN_NUMBER)
    }        
    
    
    
    
    return {
        'pvp_info' : pvp_info,
        'pvp_target_info' : pvp_target_info
    }
    
    


async def banned_expired(db:Session, service:RedisCache, uid:int):
    banned_list = await service.get_value(Constant.REDIS_RANKING_BLACKLIST)
    if banned_list:
        banned_list = list(json.loads(banned_list))
    
    if uid in banned_list:
        banned_list.remove(uid)
        await service.set_value(Constant.REDIS_RANKING_BLACKLIST, json.dumps(banned_list))
        
    crud_user_banned.remove(db, uid)


async def set_pvp_dummy_rank_data(db:Session, service:RedisCache, ranking_key:str, ranking_profile_key:str, score:int):
    dummy_list = crud_user_data.get_battle_dummy_data_all(db)
    count = 0
    random.shuffle(dummy_list)

    for dummy in dummy_list:
        await service.set_rank_add(ranking_key, dummy.battle_point * Constant.RANKING_MARGIN_NUMBER, dummy.uid)
        battle_data = json.loads(dummy.data)
        data = battle_data
        nickname = battle_data['nick'] if 'nick' in battle_data and battle_data['nick'] else 'unknown'
        await set_ranking_profile(service, ranking_profile_key, dummy.uid, nickname, data)
        count += 1
    
    return count


####################################################################################################################################################################
## monthly
####################################################################################################################################################################

async def get_month_number():
    pass


async def set_monthly_ranking_list(service:RedisCache, uid:int, key:str, score:int, data:dict, update:int, month:int=None):
    pass


async def get_monthly_ranking_key(service:RedisCache, key:str, month:int):
    pass


async def get_monthly_ranking_profile_key(service:RedisCache, key:str, month:int):
    pass


async def get_monthly_ranking_list(service:RedisCache, month_number:int, uid:int, user_info:dict, ranking_key:str, ranking_profile_key:str, my_score=-1):
    pass


####################################################################################################################################################################
## forever
####################################################################################################################################################################

async def set_forever_rakning_list(db:Session, service:RedisCache, uid:int, key:str, score:int, data:dict, update:int):
    ranking_key = get_forever_ranking_key(service, key)
    ranking_profile_key = get_forever_ranking_profile_key(service, key)
    
    has_ts = True if ranking_key.find('_TS_') >= 0 else False
    
    user_member_info = await crud_user_members.get(db, uid)
    if not user_member_info:
        return False
    
    if update == 1:
        await set_ranking_profile(service, key, uid, user_member_info.nickname, data)
        
        is_block = is_block_list(db, service, uid)
        if has_ts:
            if (score < 100000000) and not is_block:
                rank_score = score * Constant.RANKING_MARGIN_NUMBER
                my_score = await service.get_rank_score(ranking_key, uid)
                if my_score:
                    if int(my_score) < int(rank_score):
                        await service.set_rank_add(ranking_key, rank_score, uid)
                    else:
                        score = int(my_score)/Constant.RANKING_MARGIN_NUMBER
                else:
                    await service.set_rank_add(ranking_key, rank_score, uid)
        else:
            if not is_block:
                rank_score = score
                my_score = await service.get_rank_score(ranking_key, uid)
                if my_score:
                    if int(my_score) < int(rank_score):
                        await service.set_rank_add(ranking_key, rank_score, uid)
                    else:
                        score = int(my_score)
                else:
                    await service.set_rank_add(ranking_key, rank_score, uid)
            
    return await get_forever_ranking_list(db, service, uid, user_member_info, ranking_key, ranking_profile_key, score)


async def get_forever_ranking_key(service:RedisCache, key:str):
    redis_key = Constant.PROJECT_NAME + '_ranking_' + key
    await service.set_redis_hash(Constant.REDIS_RANKING_KEYS, redis_key, 1)
    return redis_key


async def get_forever_ranking_profile_key(service:RedisCache, key:str):
    redis_key = Constant.PROJECT_NAME + '_ranking_profile_' + key
    await service.set_redis_hash(Constant.REDIS_RANKING_KEYS, redis_key, 1)
    return redis_key


async def get_forever_ranking_list(db:Session, service:RedisCache, uid:int, user_member_info:UserMembers, ranking_key:str, ranking_profile_key:str, my_score:int=-1):
    my_rank = await service.get_rank(ranking_key, uid)
    if my_rank == None:
        my_rank = -1
    else:
        my_rank += 1
    
    # set maximum number size
    has_ts = True if ranking_key.find('_TS_') >= 0 else False
    
    total_ranker_cnt = await service.get_count(ranking_key)
    
    if (ranking_key.find('PVP') >= 0) and (total_ranker_cnt < 100):
        await set_pvp_dummy_rank_data(db, service, ranking_key, ranking_profile_key, 1000)
        
    rank_data = await service.get_rank_range(ranking_key, 0, Constant.REDIS_WEEKLY_RANKING_TOP_CNT, withscores=True)
    
    uid_list = []

    if rank_data and (len(rank_data) > 0) :
        for data in rank_data:
            uid_list.append(int(data[0]))
            
    
    if not uid_list:
        return {
            'myInfo' : {
                'nickname' : user_member_info.nickname,
                'rank' : my_rank,
                'score' : 0
            },
            'totalUserCount' : total_ranker_cnt,
            'rankings' : []
        }
    else:
        my_rank_index = my_rank - 1
        
        if ranking_key.find('PVP') >= 0:
            if my_score <= 0 and my_rank_index >= 0:
                my_score = 0
                score_list = await service.get_rank_range(ranking_key, my_rank_index, my_rank_index, withscores=True)
                if score_list:
                    for score in score_list:
                        if int(score[0]) == uid:
                            if has_ts:
                                my_score = int(score[1])/Constant.RANKING_MARGIN_NUMBER
                            else:
                                my_score = int(score[1])
            else:
                my_score = Constant.RANKING_PVP_DEFAULT_VALUE
        else:
            if (my_score < 0) and (my_rank_index >= 0):
                my_score = 0
                score_list = await service.get_rank_range(ranking_key, my_rank_index, my_rank_index, withscores=True)
                if score_list:
                    for score in score_list:
                        if int(score[0]) == uid:
                            if has_ts:
                                my_score = int(score[1])/Constant.RANKING_MARGIN_NUMBER
                            else:
                                my_score = int(score[1])
        
    rankings = []
    user_list = await service.get_multi_hash(ranking_profile_key, *uid_list)
    # user_list = await service._redis.hmget(ranking_profile_key, *uid_list)
    # 11777, 11859, 11859, 11869, 11874, 11880
    
    same_score_cnt = 1
    idx = 1
    
    ## TODO : KIMKJ 여기에 클랜 정보를 가지고 올 수 잇는 로직이 추가되어야 함. (정확하게는 맵타입)
    
    for rank_uid in rank_data:
        if len(user_list) < idx:break

        if not user_list[idx-1]: continue
        
        rank_user_info = json.loads(user_list[idx-1])
        if not rank_user_info: continue
        if has_ts:
            user_score = int(rank_uid[1]/Constant.RANKING_MARGIN_NUMBER)
        else:
            user_score = int(rank_uid[1])
            
        rank = same_score_cnt
        same_score_cnt += 1

        rankings.append({
            'rank' : rank,
            'uid' : rank_uid[0],
            'nickname' : rank_user_info['nickname'] if 'nickname' in rank_user_info and rank_user_info['nickname'] else 'unknown',
            'clan' : None,
            'score' : int(user_score),
            'data' : rank_user_info['data'] if 'data' in rank_user_info and rank_user_info['data'] else []
        })
        
        if ('uid' in rank_user_info ) and (rank_user_info['uid'] == uid):
            my_rank = rank

        idx += 1
    
    return {
        'myInfo' : {
            'nickname' : user_member_info.nickname,
            'rank' : my_rank,
            'score' : int(my_score)
        },
        'totalUserCount' : total_ranker_cnt,
        'rankings' : rankings
    }



####################################################################################################################################################################
## rate ranking
####################################################################################################################################################################

async def set_weekly_rate_ranking_list(db:Session, service:RedisCache, uid:int, key:str, score:int, data:dict, update:int, week:int=None):
    if not week:
        current_week = get_week_number()
    else:
        current_week = week
    
    # set maximum number size
    # 랭킹에서 timestamp를 이용한 순위 결정 여부를 key값으로 결정하도록 수정함.
    has_ts = True if key.find('_TS_') >= 0 else False
    
    
    ranking_key = await get_weekly_ranking_key(service, key, current_week)
    ranking_profile_key = await get_weekly_ranking_profile_key(service, key, current_week)
    
    user_member_info = await crud_user_members.get(db, uid)
    if not user_member_info:
        return False
    
    if update == 1:
        # search = has_key_word(service, key)
        # if search:
        #     history_list_key = await get_weekly_ranking_position_list_key(service, search, current_week)
        #     await service.set_expire(history_list_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)
        #     await set_ranking_history(service, history_list_key, uid, ranking_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)
        
        await set_ranking_profile(service, ranking_profile_key, uid, user_member_info.nickname, data)
        is_block = is_block_list(db, service, uid)
        # need time stamp => value is small
        if has_ts:
            if (score < 100000000) and not is_block:
                rank_score = score * Constant.RANKING_MARGIN_NUMBER
                rank_score = rank_score + (Constant.RANKING_MARGIN_NUMBER - int(time.time()))
                
                my_score = await service.get_rank_score(ranking_key, uid)
                if my_score:
                    if int(my_score) < int(rank_score):
                        await service.set_rank_add(ranking_key, rank_score, uid)
                    else:
                        score = int(my_score)/Constant.RANKING_MARGIN_NUMBER
                else:
                    await service.set_rank_add(ranking_key, rank_score, uid)

                await service.set_expire(ranking_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)
                await service.set_expire(ranking_profile_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)
        else: 
            if not is_block:
                rank_score = score
                my_score = await service.get_rank_score(ranking_key, uid)
                if my_score:
                    if my_score < rank_score:
                        await service.set_rank_add(ranking_key, rank_score, uid)
                    else:
                        score = my_score
                else:
                    await service.set_rank_add(ranking_key, rank_score, uid)

                await service.set_expire(ranking_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)
                await service.set_expire(ranking_profile_key, Constant.REDIS_WEEKLY_RANKING_EXPIRED_SEC)
            
            
    return await get_rate_ranking_list(db, service, current_week, uid, user_member_info, ranking_key, ranking_profile_key, score)


# 상위 1, 5, 10, 50, 80에 대해서 일차로 보여주도록 한다.
async def get_rate_ranking_list(db:Session, service:RedisCache, week_number:int, uid:int, user_member_info:UserMembers, ranking_key:str, ranking_profile_key:str, my_score:int=-1):
    my_rank = await service.get_rank(ranking_key, uid)
    if my_rank == None:
        my_rank = -1
    else:
        my_rank += 1
    
    # set maximum number size
    has_ts = True if ranking_key.find('_TS_') >= 0 else False
    
    total_ranker_cnt = await service.get_count(ranking_key)
    
    if (ranking_key.find('PVP') >= 0) and (total_ranker_cnt < 10):
        dummy_count = await set_pvp_dummy_rank_data(db, service, ranking_key, ranking_profile_key, 1000)
        total_ranker_cnt += dummy_count
        
    
    
    # 이 부분은 spec으로 가지고 오는 방법을 생각해 보자.
    default_rating = [0.01, 0.05, 0.1, 0.5, 0.8]
    rating = []
    
    for rate_value in default_rating:
        rank = int(rate_value*total_ranker_cnt)
        # 동일한 랭크에 대해서 range로 결과를 가지고 온다.
        rank_data = await service.get_rank_range(ranking_key, rank, rank, withscores=True)
        rating.append({'rating':rate_value, 'value':int(rate_value*total_ranker_cnt)})
        
    rank_data = await service.get_rank_range(ranking_key, 0, Constant.REDIS_WEEKLY_RANKING_TOP_CNT, withscores=True)
    
    uid_list = []

    if rank_data and (len(rank_data) > 0) :
        for data in rank_data:
            uid_list.append(int(data[0]))
            
    
    if not uid_list:
        return {
            'myInfo' : {
                'nickname' : user_member_info.nickname,
                'rank' : my_rank,
                'score' : 0
            },
            'dateNumber' : int(week_number),
            'totalUserCount' : total_ranker_cnt,
            'rankings' : []
        }
    else:
        my_rank_index = my_rank - 1
        
        if ranking_key.find('PVP') >= 0:
            if my_score <= 0 and my_rank_index >= 0:
                my_score = 0
                score_list = await service.get_rank_range(ranking_key, my_rank_index, my_rank_index, withscores=True)
                if score_list:
                    for score in score_list:
                        if int(score[0]) == uid:
                            my_score = int(score[1])/Constant.RANKING_MARGIN_NUMBER

            else:
                my_score = Constant.RANKING_PVP_DEFAULT_VALUE
        else:
            if (my_score < 0) and (my_rank_index >= 0):
                my_score = 1000
                score_list = await service.get_rank_range(ranking_key, my_rank_index, my_rank_index, withscores=True)
                if score_list:
                    for score in score_list:
                        if int(score[0]) == uid:
                            if has_ts:
                                my_score = int(score[1])/Constant.RANKING_MARGIN_NUMBER
                            else:
                                my_score = int(score[1])
        
    rankings = []
    user_list = await service.get_multi_hash(ranking_profile_key, *uid_list)
    # user_list = await service._redis.hmget(ranking_profile_key, *uid_list)
    # 11777, 11859, 11859, 11869, 11874, 11880
    
    same_score_cnt = 1
    idx = 1
    
    ## TODO : KIMKJ 여기에 클랜 정보를 가지고 올 수 잇는 로직이 추가되어야 함. (정확하게는 맵타입)
    
    for rank_uid in rank_data:
        if len(user_list) < idx:break

        if not user_list[idx-1]: continue
        
        rank_user_info = json.loads(user_list[idx-1])
        if not rank_user_info: continue
        if ranking_key.find('PVP') >= 0:
            user_score = int(rank_uid[1]/Constant.RANKING_MARGIN_NUMBER)
        else:
            if has_ts:
                user_score = int(rank_uid[1]/Constant.RANKING_MARGIN_NUMBER)
            else:
                user_score = int(rank_uid[1])
            
        rank = same_score_cnt
        same_score_cnt += 1

        rankings.append({
            'rank' : rank,
            'uid' : rank_uid[0],
            'nickname' : rank_user_info['nickname'] if 'nickname' in rank_user_info and rank_user_info['nickname'] else 'unknown',
            'clan' : None,
            'score' : int(user_score),
            'data' : rank_user_info['data'] if 'data' in rank_user_info and rank_user_info['data'] else []
        })
        
        if ('uid' in rank_user_info ) and (rank_user_info['uid'] == uid):
            my_rank = rank

        idx += 1
    
    return {
        'myInfo' : {
            'nickname' : user_member_info.nickname,
            'rank' : my_rank,
            'score' : int(my_score)
        },
        'dateNumber' : int(week_number),
        'totalUserCount' : total_ranker_cnt,
        'rankings' : rankings
    }
    
    
####################################################################################################################################################################
## dummy ranking
####################################################################################################################################################################

async def get_half_pvp_dummy_user(db:Session, service:RedisCache, uid:int, key:str):
    half = await get_half_number(db)
    week = half['id']
    ranking_key = await get_weekly_ranking_key(service, key, week)
    ranking_profile_key = await get_weekly_ranking_profile_key(service, key, week)
    
    dummy_list:list = await CacheController.pvp_dummy_info_map(db)
    
    total_ranker_cnt = await service.get_count(ranking_key)
    if total_ranker_cnt == 0:
        await set_pvp_dummy_rank_data(db, service, ranking_key, ranking_profile_key, 1000)
        total_ranker_cnt = await service.get_count(ranking_key)
    
    my_rank = await service.get_rank(ranking_key, uid)
   
    if my_rank == None:
        my_rank = -1
    else:
        my_rank += 1

    debug_type = 0
    match_user_info = []
    
    random.shuffle(dummy_list)
    
    for match_user in dummy_list:
        uid = get(match_user, 'uid', None)
        if not uid:
            continue
        
        #중요한건 랭킹에 데이터가 있어야 한다는 것이다.
        rank = await service.get_rank(ranking_key, uid)
        if rank == None:
            continue
        else:
            rank += 1

        user_data = json.loads(get(match_user, 'data', None))
        profile = {'uid' : uid,'nickname' : user_data['nick'], 'data' : user_data}
        score = int(await service.get_rank_score(ranking_key, uid) / Constant.RANKING_MARGIN_NUMBER)
            
        match_user_info.append({
            'rank' : rank,
            'uid' : uid,
            'nickname' : profile['nickname'] if 'nickname' in profile and profile['nickname'] else 'unknown',
            'score' : score,
            'data' : profile['data'] if 'data' in profile and profile['data'] else []
        })
        
        if len(match_user_info) > 5:
            break
     
     
    return {
        'myRank' : my_rank,
        'match1' : match_user_info[0],
        'match2' : match_user_info[1],
        'match3' : match_user_info[2],
        'match4' : match_user_info[3],
        'match5' : match_user_info[4],
        # 'revenge_list' : revenge_info,
        'debugType' : debug_type
    }
