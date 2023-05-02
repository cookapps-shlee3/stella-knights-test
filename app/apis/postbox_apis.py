# -*- coding: utf-8 -*-
from functools import reduce
import json
import time
from datetime import datetime
from sqlalchemy.orm import Session
from app.params.ResParam import get_response, ResponseCode
from app.params.ReqParam import PostListReqParam, PostRewardReqParam, PostRewardsReqParam
from app.config.settings import Constant
from app.crud import crud_user_members, crud_postbox
from app.util.util import get
from app.classes.CurrencyManager import CurrencyManager
from app.classes.UserDataManager import UserDataManager
from app.cache import CacheController



async def postbox_list(req:PostListReqParam, db:Session):
    now_date_key = int(datetime.now().strftime('%Y%m%d'))
    user_member_info = await crud_user_members.get(db, req.uid)
    
    if not user_member_info:
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, msg='Invalid User ID', uid=req.uid)
    
    if req.country == 'TC':
        req.country = 'TW'
    elif req.country == 'SC':
        req.country = 'CN'
    
    if req.country not in Constant.COUNTRY_CODE:
        req.country = 'EN'
        
    crud_postbox.check_special_post(db, req.uid, user_member_info.server)
    postbox_list = crud_postbox.get_list(db, req.uid, req.country)
    
    response = {
        'list' : postbox_list
    }
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=response, uid=req.uid)



async def postbox_reward(req:PostRewardReqParam, db:Session):
    rune_category = 'Rune'
    character_category = 'Character'
    weapon_category = 'Weapon'
    
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    character_enhance_dict = await CacheController.character_enhance_info_map(db)
    character_enhance_info = get(character_enhance_dict, req.platform)
    if not character_enhance_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_ENHANCE_DATA, uid=req.uid)
    
    character_info_dict = await CacheController.character_info_map(db)
    character_info = get(character_info_dict, req.platform)
    if not character_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_ENHANCE_DATA, uid=req.uid)
    
    user_member_info = await crud_user_members.get(db, req.uid)
    
    if not user_member_info:
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, msg='Invalid User ID', uid=req.uid)
    
    # result_code = crud_postbox.reward(db, req.uid, req.post_id)
    
    post = crud_postbox.get_reward(db, req.uid, req.post_id)
    
    if not post:
        return get_response(code=ResponseCode.RES_INVALID_POST_ID, msg='Invalid Post ID', uid=req.uid)
    
    if post.is_rewarded == 1:
        return get_response(code=ResponseCode.RES_ALREADY_REWARDED, msg='Already Rewarded', uid=req.uid)
    
    now = int(time.time())
    if post.expire_time < now:
        return get_response(code=ResponseCode.RES_EXPIRED_POST_ID, msg='Expired Post ID', uid=req.uid)
    
    if post.rewards:
        post_rewards = json.loads(post.rewards)
        if post_rewards:
            for post_reward in post_rewards:
                type = post_reward['reward_type']
                amount = int(post_reward['reward_amount'])
                key = int(post_reward['reward_key'])
                if type == 'RUNE':
                    rune_datas = userdataManager.get(db, req.uid, rune_category)
                    rune_datas = currencyManager.add_rune(type, key, amount, rune_datas)
                    userdataManager.set_update(rune_category)
                elif type == 'KNIGHT_PIECE':
                    character_datas = userdataManager.get(db, req.uid, character_category)
                    character_datas = currencyManager.add_character_piece(type, key, amount, character_datas)
                    userdataManager.set_update(character_category)
                elif type == 'KNIGHT':
                    character_datas = userdataManager.get(db, req.uid, character_category)
                    character_info_data = get(character_info, str(key), None)
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
                            character_datas = currencyManager.add_character(type, key, amount, default_character_piece, character_datas)
                            userdataManager.set_update(character_category)
                elif type == 'WEAPON':
                    weapon_datas = userdataManager.get(db, req.uid, weapon_category)
                    weapon_datas = currencyManager.add_weapon(type, key, amount, weapon_datas)
                    userdataManager.set_update(weapon_category)
                else:
                    currencyManager.add_dict(type, key, amount)

    
    result_code = crud_postbox.update_reward(db, req.uid, req.post_id)
    
    result_msg = ''
    
    if result_code == ResponseCode.RES_SUCCESS:
        result_msg = 'Update Success'
    elif result_code == ResponseCode.RES_INVALID_POST_ID:
        result_msg = 'Invalid Post ID'
    elif result_code == ResponseCode.RES_ALREADY_REWARDED:
        result_msg = 'Already Rewarded'
    elif result_code == ResponseCode.RES_EXPIRED_POST_ID:
        result_msg = 'Expired Post ID'
    elif result_code == ResponseCode.RES_INTERNAL_SERVER_ERROR:
        result_msg = 'Internal Server Error'
        
    if result_code != ResponseCode.RES_SUCCESS:
        return get_response(code=result_code, msg=result_msg, uid=req.uid)
    
    if currencyManager.get_rewards():
        currencyManager.get_currency_rewards(db, req.uid)
    
    data = currencyManager.get_user_currency_data(db, req.uid)
    data['UserData'] = userdataManager.generate_user_save(db, req.uid)
    data['change'] = currencyManager.get_change()
    data['post_id'] = req.post_id
    return get_response(code=ResponseCode.RES_SUCCESS, msg=result_msg, data=data, uid=req.uid)



async def postbox_rewards(req:PostRewardsReqParam, db:Session):
    rune_category = 'Rune'
    character_category = 'Character'
    weapon_category = 'Weapon'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    character_enhance_dict = await CacheController.character_enhance_info_map(db)
    character_enhance_info = get(character_enhance_dict, req.platform)
    if not character_enhance_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_ENHANCE_DATA, uid=req.uid)
    
    character_info_dict = await CacheController.chapter_info_map(db)
    character_info = get(character_info_dict, req.platform)
    if not character_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_ENHANCE_DATA, uid=req.uid)
    
    user_member_info = await crud_user_members.get(db, req.uid)
    
    if not user_member_info:
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, msg='Invalid User ID', uid=req.uid)
    
    if req.country not in Constant.COUNTRY_CODE:
        req.country = 'EN'
    
    
    posts = crud_postbox.get_rewards(db, req.uid, req.post_ids)
    now = int(time.time())
    result_reward:dict = {}
    if posts:
        for post in posts:
            if not post:
                continue
            if post.is_rewarded == 1:
                continue
            if post.expire_time < now:
                continue
            if post.rewards:
                post_rewards = json.loads(post.rewards)
                if post_rewards:
                    for post_reward in post_rewards:
                        type = post_reward['reward_type']
                        amount = int(post_reward['reward_amount'])
                        key = int(post_reward['reward_key'])
                        if type == 'RUNE':
                            rune_datas = userdataManager.get(db, req.uid, rune_category)
                            rune_datas = currencyManager.add_rune(type, key, amount, rune_datas)
                            userdataManager.set_update(rune_category)
                        elif type == 'KNIGHT_PIECE':
                            character_datas = userdataManager.get(db, req.uid, character_category)
                            character_datas = currencyManager.add_character_piece(type, key, amount, character_datas)
                            userdataManager.set_update(character_category)
                        elif type == 'KNIGHT':
                            character_datas = userdataManager.get(db, req.uid, character_category)
                            character_info_data = get(character_info, str(key), None)
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
                                    character_datas = currencyManager.add_character(type, key, amount, default_character_piece, character_datas)
                                    userdataManager.set_update(character_category)
                        elif type == 'WEAPON':
                            weapon_datas = userdataManager.get(db, req.uid, weapon_category)
                            weapon_datas = currencyManager.add_weapon(type, key, amount, weapon_datas)
                            userdataManager.set_update(weapon_category)
                        else:
                            currencyManager.add_dict(type, key, amount)

    
    result_code = crud_postbox.rewards(db, req.uid, req.post_ids)
    postbox_list = crud_postbox.get_list(db, req.uid, req.country)
    
    result_msg = ''
    if result_code != ResponseCode.RES_SUCCESS:
        result_msg = 'Update Success'
    elif result_code == ResponseCode.RES_INTERNAL_SERVER_ERROR:
        result_msg = 'Internal Server Error'

    if result_code != ResponseCode.RES_SUCCESS:
        return get_response(code=result_code, msg=result_msg, uid=req.uid)
    
    if currencyManager.get_rewards():
        currencyManager.get_currency_rewards(db, req.uid)
    
    data = currencyManager.get_user_currency_data(db, req.uid)
    data['UserData'] = userdataManager.generate_user_save(db, req.uid)
    data['change'] = currencyManager.get_change()
    data['list'] = postbox_list
    return get_response(code=ResponseCode.RES_SUCCESS, msg=result_msg, data=data, uid=req.uid)
