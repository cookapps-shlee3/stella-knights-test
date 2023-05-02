# -*- coding: utf-8 -*-
import base64
import json
import os
import logging
from loguru import logger
from datetime import datetime
from sqlalchemy.orm import Session
from app.params.ResParam import get_response, ResponseCode
from app.params.ReqParam import PaymentReqParam
from app.crud import crud_payment, crud_user_server
from app.purchase.onestore import onestore_varify
from app.purchase.googleplay import InAppPyValidationError, GooglePlayVerifier
from app.purchase.appstore import AppStoreValidator
from app.purchase import errors
from app.util.util import get
from app.config.settings import Constant
from app.cache import CacheController
from app.crud import crud_user_data, crud_postbox, crud_user_members
from app.classes.CurrencyManager import CurrencyManager
from app.classes.UserDataManager import UserDataManager


async def payment(req:PaymentReqParam, db:Session):
    rune_category = 'Rune'
    character_category = 'Character'
    weapon_category = 'Weapon'
    time_category = 'Time'
    pass_category = 'Pass'
    purchase_category = 'Purchase'
    
    currencyManager = CurrencyManager()
    userdataManager = UserDataManager()
    
    
    if req.currency_price.find(",") > 0:
        req.currency_price = req.currency_price.replace(",", ".")
    
    user_member_info = await crud_user_members.get(db, req.uid, False)
    
    base_uid = crud_user_server.base_uid(db, req.uid)
    if base_uid:
        iid = crud_payment.set_data(db, base_uid.uid, req.platform, req.order_id, req.product_id, float(req.currency_price), req.currency_code, req.receipt, req.uid, user_member_info.social_id)
    else:
        iid = crud_payment.set_data(db, req.uid, req.platform, req.order_id, req.product_id, float(req.currency_price), req.currency_code, req.receipt, req.uid, user_member_info.social_id)
    
    if (not req.order_id) or (not req.receipt):
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, uid=req.uid)
        
    purchase_datas = userdataManager.get(db, req.uid, purchase_category)
    
    if not purchase_datas:
        purchase_datas = []
    dt_now = datetime.now()
    purchase_datas.append({'id':req.product_id, 'time':dt_now.strftime('%Y-%m-%d %H:%M:%S')})
    
    userdataManager.set(purchase_category, purchase_datas)
    
    is_complete = 0
    
    time_datas = None
    # 여기서 메일함에 넣어주는 로직을 만들어야 한다.
    shop_info_dict = await CacheController.shop_info_map(db)
    shop_info_values = get(shop_info_dict, req.p, None)
    
    
    character_enhance_dict = await CacheController.character_enhance_info_map(db)
    character_enhance_info = get(character_enhance_dict, req.platform)
    if not character_enhance_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_ENHANCE_DATA, uid=req.uid)
    
    character_info_dict = await CacheController.character_info_map(db)
    character_info = get(character_info_dict, req.platform)
    if not character_info:
        return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_ENHANCE_DATA, uid=req.uid)
    
    if shop_info_values:
        #여기서 메일을 쏘자
        shop_info_list = get(shop_info_values, req.product_id, None)
        m_point = 0
        # TODO 주석풀기
        if shop_info_list:
            for shop_info in shop_info_list:
                m_point += get(shop_info, 'm_point', 0)
                
        
        time_datas = userdataManager.get(db, req.uid, time_category)
        
        jewel_records = time_datas['jewelRecords']
        
        is_double = False
        data = {}
        
        if shop_info_list:
            payment_id = shop_info_list[0]['id']
            is_first:bool = True
            reward_list = []
            if not jewel_records:
                jewel_records = []
            if (shop_info_list[0]['id'] not in jewel_records) and (shop_info_list[0]['first_double']):
                is_double = True
            
            if is_double:
                jewel_records.append(shop_info_list[0]['id'])
                time_datas['jewelRecords'] = jewel_records
                userdataManager.set_update(time_category)
                
            for shop_info in shop_info_list:
                is_send = get(shop_info, 'is_send', False)
                _term = get(shop_info, 'term', None)
                _type = get(shop_info, 'reward_type', None)
                _key = get(shop_info, 'reward_key', None)
                _amount = get(shop_info, 'reward_amount', None)

                # if _term == 'SPECIAL':
                #     if req.product_id == 'uk_special_begiiner_legend_knight':
                #         tristan_pack = get(time_datas, 'tristanPack', None)
                #         special_buy_limit_count = get(shop_info, 'limit_count', 0)
                #         special_purchases = get(time_datas, 'specialPurchases', None)
                        
                #         if special_purchases == None:
                #             special_purchases = []
                #             time_datas['specialPurchases'] = special_purchases
                #             userdataManager.set_update(time_category)
                        
                        
                #         legend_pack_data = None
                #         legend_pack_index = 0
                        
                #         for idx in range(0, len(new_legended_pack_list)):
                #             if tristan_pack[idx]['key'] == req.key:
                #                 legend_pack_data = tristan_pack[idx]
                #                 legend_pack_index = idx
                #                 break
                            
                #         if special_buy_limit_count > 0:
                #             if (special_purchases.count(payment_id) < special_buy_limit_count) and legend_pack_data and is_first:
                #                 special_purchases.append(payment_id)
                #                 time_datas['specialPurchases'] = special_purchases
                #                 if (legend_pack_data['pCount'] + 1) == special_buy_limit_count:
                #                     is_first = False
                #                     del tristan_pack[legend_pack_index]
                #                 else:
                #                     is_first = False
                #                     legend_pack_data['pCount'] = legend_pack_data['pCount'] + 1

                #                 userdataManager.set_update(time_category)
                #             else:
                #                 pass

                #             userdataManager.set_update(time_category)

                #         if (_type != None) and (_key != None) and (_amount != None):
                #             if is_send:
                #                 if (_type == 'RUNE') or (_type == 'KNIGHT_PIECE') or (_type == 'KNIGHT') or (_type == 'WEAPON'):
                #                     _amount = (_amount *2) if is_double else _amount
                #                     reward_list.append({'reward_type':_type,'reward_key':req.key, 'reward_amount':_amount})
                #                 else:
                #                     if not is_double:
                #                         reward_list.append({'reward_type':_type,'reward_key':_key, 'reward_amount':_amount})
                #                     else:
                #                         reward_list.append({'reward_type':_type,'reward_key':_key, 'reward_amount':_amount})
                #                         reward_list.append({'reward_type':_type,'reward_key':_key, 'reward_amount':_amount})
                #             else:
                #                 _amount = (_amount *2) if is_double else _amount
                #                 if _type == 'RUNE':
                #                     rune_datas = userdataManager.get(db, req.uid, rune_category)
                #                     rune_datas = currencyManager.add_rune(_type, req.key, _amount, rune_datas)
                #                     userdataManager.set_update(rune_category)
                #                 elif _type == 'KNIGHT_PIECE':
                #                     character_datas = userdataManager.get(db, req.uid, character_category)
                #                     character_datas = currencyManager.add_character_piece(_type, req.key, _amount, character_datas)
                #                     userdataManager.set_update(character_category)
                #                 elif _type == 'KNIGHT':
                #                     character_datas = userdataManager.get(db, req.uid, character_category)
                #                     character_info_data = get(character_info, str(req.key), None)
                #                     if character_info_data:
                #                         character_grade = get(character_info_data, 'grade_value', None)
                #                         if character_grade:
                #                             character_enhance = get(character_enhance_info, str(character_grade), None)
                #                             if character_enhance == None:
                #                                 return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)
                #                             character_enhance = get(character_enhance, str(character_grade), None)
                #                             if character_enhance == None:
                #                                 return get_response(code=ResponseCode.RES_NOT_FOUND_CHARACTER_INFO_DATA, uid=req.uid)
                #                             default_character_piece = get(character_enhance, 'piece', None)
                #                             character_datas = currencyManager.add_character(_type, req.key, _amount, default_character_piece, character_datas)
                #                             userdataManager.set_update(character_category)
                #                 elif _type == 'WEAPON':
                #                     weapon_datas = userdataManager.get(db, req.uid, weapon_category)
                #                     weapon_datas = currencyManager.add_weapon(_type, req.key, _amount, weapon_datas)
                #                     userdataManager.set_update(weapon_category)
                #                 else:
                #                     currencyManager.add_dict(_type, _key, _amount)
                        
                if _term == 'DAILY':
                    daily_buy_limit_count = get(shop_info, 'limit_count', 0)
                    daily_purchases = get(time_datas, 'dailyPurchases', None)
    
                    if daily_purchases == None:
                        daily_purchases = []
                        userdataManager.set_update(time_category)
                    
                    if daily_buy_limit_count > 0:
                        if (daily_purchases.count(payment_id) < daily_buy_limit_count) and is_first:
                            is_first = False
                            daily_purchases.append(payment_id)
                            time_datas['dailyPurchases'] = daily_purchases
                            userdataManager.set_update(time_category)
                        if (_type != None) and (_key != None) and (_amount != None) and (not is_first):
                            if is_send:
                                if not is_double:
                                    reward_list.append({'reward_type':_type,'reward_key':_key, 'reward_amount':_amount})
                                else:
                                    reward_list.append({'reward_type':_type,'reward_key':_key, 'reward_amount':_amount})
                                    reward_list.append({'reward_type':_type,'reward_key':_key, 'reward_amount':_amount})
                            else:
                                _amount = (_amount *2) if is_double else _amount
                                if _type == 'RUNE':
                                    rune_datas = userdataManager.get(db, req.uid, rune_category)
                                    rune_datas = currencyManager.add_rune(_type, _key, _amount, rune_datas)
                                    userdataManager.set_update(rune_category)
                                elif _type == 'KNIGHT_PIECE':
                                    character_datas = userdataManager.get(db, req.uid, character_category)
                                    character_datas = currencyManager.add_character_piece(_type, _key, _amount, character_datas)
                                    userdataManager.set_update(character_category)
                                elif _type == 'KNIGHT':
                                    character_datas = userdataManager.get(db, req.uid, character_category)
                                    character_info_data = get(character_info, str(_key), None)
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
                                            character_datas = currencyManager.add_character(_type, _key, _amount, default_character_piece, character_datas)
                                            userdataManager.set_update(character_category)
                                elif _type == 'WEAPON':
                                    weapon_datas = userdataManager.get(db, req.uid, weapon_category)
                                    weapon_datas = currencyManager.add_weapon(_type, _key, _amount, weapon_datas)
                                    userdataManager.set_update(weapon_category)
                                else:
                                    currencyManager.add_dict(_type, _key, _amount)

                elif _term == 'WEEKLY':
                    weekly_buy_limit_count = get(shop_info, 'limit_count', 0)
                    weekly_purchases = get(time_datas, 'weeklyPurchases', None)
    
                    if weekly_purchases == None:
                        weekly_purchases = []
                        userdataManager.set_update(time_category)
                   
                    if weekly_buy_limit_count > 0:
                        if (weekly_purchases.count(payment_id) < weekly_buy_limit_count) and is_first:
                            is_first = False
                            weekly_purchases.append(payment_id)
                            time_datas['weeklyPurchases'] = weekly_purchases
                            userdataManager.set_update(time_category)
                        if (_type != None) and (_key != None) and (_amount != None) and (not is_first):
                            if is_send:
                                if not is_double:
                                    reward_list.append({'reward_type':_type,'reward_key':_key, 'reward_amount':_amount})
                                else:
                                    reward_list.append({'reward_type':_type,'reward_key':_key, 'reward_amount':_amount})
                                    reward_list.append({'reward_type':_type,'reward_key':_key, 'reward_amount':_amount})
                            else:
                                _amount = (_amount *2) if is_double else _amount
                                if _type == 'RUNE':
                                    rune_datas = userdataManager.get(db, req.uid, rune_category)
                                    rune_datas = currencyManager.add_rune(_type, _key, _amount, rune_datas)
                                    userdataManager.set_update(rune_category)
                                elif _type == 'KNIGHT_PIECE':
                                    character_datas = userdataManager.get(db, req.uid, character_category)
                                    character_datas = currencyManager.add_character_piece(_type, _key, _amount, character_datas)
                                    userdataManager.set_update(character_category)
                                elif _type == 'KNIGHT':
                                    character_datas = userdataManager.get(db, req.uid, character_category)
                                    character_info_data = get(character_info, str(_key), None)
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
                                            character_datas = currencyManager.add_character(_type, _key, _amount, default_character_piece, character_datas)
                                            userdataManager.set_update(character_category)
                                elif _type == 'WEAPON':
                                    weapon_datas = userdataManager.get(db, req.uid, weapon_category)
                                    weapon_datas = currencyManager.add_weapon(_type, _key, _amount, weapon_datas)
                                    userdataManager.set_update(weapon_category)
                                else:
                                    currencyManager.add_dict(_type, _key, _amount)
                        
                elif _term == 'MONTHLY':
                    monthly_buy_limit_count = get(shop_info, 'limit_count', 0)
                    monthly_purchases = get(time_datas, 'monthlyPurchases', None)
    
                    if monthly_purchases == None:
                        monthly_purchases = []
                        userdataManager.set_update(time_category)
                    
                    if monthly_buy_limit_count > 0:
                        if (monthly_purchases.count(payment_id) < monthly_buy_limit_count) and is_first:
                            is_first = False
                            monthly_purchases.append(payment_id)
                            time_datas['monthlyPurchases'] = monthly_purchases
                            userdataManager.set_update(time_category)
                        if (_type != None) and (_key != None) and (_amount != None) and (not is_first):
                            if is_send:
                                if not is_double:
                                    reward_list.append({'reward_type':_type,'reward_key':_key, 'reward_amount':_amount})
                                else:
                                    reward_list.append({'reward_type':_type,'reward_key':_key, 'reward_amount':_amount})
                                    reward_list.append({'reward_type':_type,'reward_key':_key, 'reward_amount':_amount})
                            else:
                                _amount = (_amount *2) if is_double else _amount
                                if _type == 'RUNE':
                                    rune_datas = userdataManager.get(db, req.uid, rune_category)
                                    rune_datas = currencyManager.add_rune(_type, _key, _amount, rune_datas)
                                    userdataManager.set_update(rune_category)
                                elif _type == 'KNIGHT_PIECE':
                                    character_datas = userdataManager.get(db, req.uid, character_category)
                                    character_datas = currencyManager.add_character_piece(_type, _key, _amount, character_datas)
                                    userdataManager.set_update(character_category)
                                elif _type == 'KNIGHT':
                                    character_datas = userdataManager.get(db, req.uid, character_category)
                                    character_info_data = get(character_info, str(_key), None)
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
                                            character_datas = currencyManager.add_character(_type, _key, _amount, default_character_piece, character_datas)
                                            userdataManager.set_update(character_category)
                                elif _type == 'WEAPON':
                                    weapon_datas = userdataManager.get(db, req.uid, weapon_category)
                                    weapon_datas = currencyManager.add_weapon(_type, _key, _amount, weapon_datas)
                                    userdataManager.set_update(weapon_category)
                                else:
                                    currencyManager.add_dict(_type, _key, _amount)

                elif _term == 'TIME':
                    time_buy_limit_count = get(shop_info, 'limit_count', 0)
                    is_tristan:bool = False
                    new_legended_pack_list = None
                    if req.product_id == 'uk_time_deal_knight_pack':
                        new_legended_pack_list = get(time_datas, 'newLegendPackList', None)
                    else:
                        new_legended_pack_list = get(time_datas, 'timePackList', None)
                    
                    # if is_tristan:
                    #     if is_first:
                    #         if (new_legended_pack_list['pCount'] + 1) == time_buy_limit_count:
                    #             is_first = False
                    #             time_datas['tristanPack'] = None
                    #         else:
                    #             new_legended_pack_list['pCount'] = new_legended_pack_list['pCount'] + 1
                                
                    #         userdataManager.set_update(time_category)

                    # else:       
                    
                    legend_pack_data = None
                    legend_pack_index = 0
                
                    for idx in range(0, len(new_legended_pack_list)):
                        if req.product_id == 'uk_time_deal_knight_pack':
                            if new_legended_pack_list[idx]['key'] == req.key:
                                legend_pack_data = new_legended_pack_list[idx]
                                legend_pack_index = idx
                                break
                        else:
                            if new_legended_pack_list[idx]['pid'] == payment_id:
                                legend_pack_data = new_legended_pack_list[idx]
                                legend_pack_index = idx
                                break
                    
                    #카운트는 한번만 선물은 여러번...ㅠ,.ㅠ
                    if legend_pack_data and is_first:
                        if (legend_pack_data['pCount'] + 1) == time_buy_limit_count:
                            is_first = False
                            del new_legended_pack_list[legend_pack_index]
                        else:
                            is_first = False
                            legend_pack_data['pCount'] = legend_pack_data['pCount'] + 1
                    
                        userdataManager.set_update(time_category)

                    if (_type != None) and (_key != None) and (_amount != None):
                        if is_send:
                            if (_type == 'RUNE') or (_type == 'KNIGHT_PIECE') or (_type == 'KNIGHT'):
                                _amount = (_amount *2) if is_double else _amount
                                reward_list.append({'reward_type':_type,'reward_key':req.key, 'reward_amount':_amount})
                            elif (_type == 'WEAPON'):
                                reward_list.append({'reward_type':_type,'reward_key':_key, 'reward_amount':_amount})
                            else:
                                if not is_double:
                                    reward_list.append({'reward_type':_type,'reward_key':_key, 'reward_amount':_amount})
                                else:
                                    reward_list.append({'reward_type':_type,'reward_key':_key, 'reward_amount':_amount})
                                    reward_list.append({'reward_type':_type,'reward_key':_key, 'reward_amount':_amount})
                        else:
                            _amount = (_amount *2) if is_double else _amount
                            if _type == 'RUNE':
                                rune_datas = userdataManager.get(db, req.uid, rune_category)
                                key = _key if is_tristan else req.key
                                rune_datas = currencyManager.add_rune(_type, key, _amount, rune_datas)
                                userdataManager.set_update(rune_category)
                            elif _type == 'KNIGHT_PIECE':
                                character_datas = userdataManager.get(db, req.uid, character_category)
                                key = _key if is_tristan else req.key
                                character_datas = currencyManager.add_character_piece(_type, key, _amount, character_datas)
                                userdataManager.set_update(character_category)
                            elif _type == 'KNIGHT':
                                character_datas = userdataManager.get(db, req.uid, character_category)
                                key = req.key
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
                                        character_datas = currencyManager.add_character(_type, key, _amount, default_character_piece, character_datas)
                                        userdataManager.set_update(character_category)
                            elif _type == 'WEAPON':
                                weapon_datas = userdataManager.get(db, req.uid, weapon_category)
                                # key = _key if is_tristan else req.key
                                weapon_datas = currencyManager.add_weapon(_type, _key, _amount, weapon_datas)
                                userdataManager.set_update(weapon_category)
                            else:
                                currencyManager.add_dict(_type, _key, _amount)
                else:
                    if req.product_id == 'uk_battle_pass':
                        pass_datas = userdataManager.get(db, req.uid, pass_category)
                        for pass_data in pass_datas:
                            if pass_data['id'] == 2010:
                                pass_data['vip'] = True
                                userdataManager.set_update(pass_category)
                                break
                    elif (req.product_id == 'uk_attendance') or (req.product_id == 'uk_attendance_half_sale') :
                        time_datas = userdataManager.get(db, req.uid, time_category)
                        time_datas['IsSpecialAtt'] = True
                        userdataManager.set_update(time_category)
                    elif req.product_id == 'uk_expedition_pass':
                        current_pass_event = await CacheController.get_current_pass_event(db, req.p, 2001)
                        
                        if current_pass_event:
                            pass_datas = userdataManager.get(db, req.uid, pass_category)
                            for pass_data in pass_datas:
                                if pass_data['id'] == current_pass_event['id']:
                                    pass_data['vip'] = True
                                    userdataManager.set_update(pass_category)
                                    break
                    else:
                        if (_type != None) and (_key != None) and (_amount != None):
                            if is_send:
                                if not is_double:
                                    reward_list.append({'reward_type':_type,'reward_key':_key, 'reward_amount':_amount})
                                else:
                                    reward_list.append({'reward_type':_type,'reward_key':_key, 'reward_amount':_amount})
                                    reward_list.append({'reward_type':_type,'reward_key':_key, 'reward_amount':_amount})
                            else:
                                _amount = (_amount *2) if is_double else _amount
                                currencyManager.add_dict(_type, _key, _amount)
                
                
            if is_send and m_point:    
                reward_list.append({'reward_type':'MILEAGE','reward_key':0, 'reward_amount':m_point})
            else:
                currencyManager.add_dict('MILEAGE', 0, m_point)

            if reward_list:
                crud_postbox.send_payment_mail(db, req.uid, reward_list, req.product_id)
    
    ENVIRONMENT = os.environ.get('PRODUCTION')
    
    if ENVIRONMENT != 'prod':
        if req.receipt == 'EDITOR':
            if currencyManager.get_rewards():
                currencyManager.get_currency_rewards(db, req.uid)
            data = currencyManager.get_user_currency_data(db, req.uid)
            data['UserData'] = userdataManager.generate_user_save(db, req.uid)
            data['resultCode'] = Constant.RESULT_VALID_RECEIPT
            if currencyManager.get_change():
                data['change'] = currencyManager.get_change()
            
            return data
    
    
    if iid:
        if req.platform == 'android':
            
            logger.info('purchase receipt = ' + req.receipt)
                
            current_dir = os.path.dirname(os.path.realpath(__file__))
            credential_path = current_dir + '/../' + os.path.join("credentials", 'google_service_account.json')
            with open(credential_path) as json_file:
                api_credentials = json.load(json_file)        
            
            # 이 부분에 대한 처리를 어떻게 할지 실제로 데이터를 받아서 처리해보도록 한다.
            # req.receipt = req.receipt.replace('"{','{')
            # req.receipt = req.receipt.replace('}"','}')
            req.receipt = req.receipt.replace('\\\\\\','\\')
            receipt = json.loads(req.receipt)
            verifier = GooglePlayVerifier(Constant.ANDROID_BUNDLE_ID, api_credentials)
            
            response = {'valid': False, 'transactions': [], 'orderId' : '', 'resultCode':5}
            
            payload = get(receipt, 'Payload')
            if not payload:
                response['resultCode'] = Constant.RESULT_INVALID_RECEIPT
                return response
            
            payload = payload.replace('"{','{')
            payload = payload.replace('}"','}')
            
            logger.info('purchase payload = ' + payload)
            
            payload = json.loads(payload)
            
            json_data = get(payload, 'json')
            
            if not json_data:
                response['resultCode'] = Constant.RESULT_INVALID_RECEIPT
                return response
            
            purchase_token = get(json_data, 'purchaseToken')
            product_sku = get(json_data, 'productId')
            package_name = get(json_data, 'packageName')
            if purchase_token and product_sku and package_name:
                try:
                    result = verifier.verify(purchase_token,product_sku,is_subscription=False)
                    purchase_state = int(result.get("purchaseState", 1))
                    # 여기서 반환되는 값들에 대해서 지정하고 돌려줄 수 있도록 수정함.
                    if not result:
                        response['orderId'] = str(result.get("orderId"))

                    if purchase_state == 0:
                        response['valid'] = True
                        response['transactions'].append((result['orderId'], product_sku))
                        response['resultCode'] = Constant.RESULT_VALID_RECEIPT
                        purchase_type = result.get("purchaseType", None)
                        
                        if purchase_type!= None and purchase_type == 0:
                            response['resultCode'] = Constant.RESULT_VALID_SANDBOX
                            
                        is_complete = 1

                    else:
                        response['resultCode'] = Constant.RESULT_INVALID_RECEIPT
                        
                    if crud_payment.is_exist_order_id(db, result.get('orderId')):
                        response['resultCode'] = Constant.RESULT_DUPLICATE
                    
                except errors.GoogleError as exc:
                    logging.error('Purchase validation failed {}'.format(exc))
            else:
                response['resultCode'] = Constant.RESULT_INVALID_RECEIPT
            
            crud_payment.set_payment_complete(db, iid, response['resultCode'])   
            if currencyManager.get_rewards():
                currencyManager.get_currency_rewards(db, req.uid)
            data = currencyManager.get_user_currency_data(db, req.uid)
            data['UserData'] = userdataManager.generate_user_save(db, req.uid)
            if currencyManager.get_change():
                data['change'] = currencyManager.get_change()
            data['resultCode'] = response['resultCode']

            return data
            
        elif req.platform == 'ios':
            bundle_id = Constant.IOS_BUNDLE_ID
            receipt = json.loads(req.receipt)
            auto_retry_wrong_env_request=True # if True, automatically query sandbox endpoint if
                                            # validation fails on production endpoint
            validator = AppStoreValidator(bundle_id, auto_retry_wrong_env_request=auto_retry_wrong_env_request)

            try:
                response = {'valid': False, 'orderId' : ''}
                exclude_old_transactions=False # if True, include only the latest renewal transaction
                ios_payload = get(receipt, 'Payload')
                if not ios_payload:
                    return None
                
                validation_result = validator.validate(ios_payload, None, exclude_old_transactions=exclude_old_transactions)
                
                if int(validation_result.get('status', 1)) == 0:
                    receipt_data = validation_result.get('receipt')
                    
                    response['resultCode'] = Constant.RESULT_VALID_RECEIPT
                    
                    if validation_result.get('environment', '') == 'Sandbox':
                        response['resultCode'] = Constant.RESULT_VALID_SANDBOX
                    
                    if str(receipt_data.get('bundle_id', '')) != Constant.IOS_BUNDLE_ID:
                        response['resultCode'] = Constant.RESULT_INVALID_RECEIPT
                        
                    arr_in_app = receipt_data.get('in_app')
                    
                    order_id = ''
                    for item in arr_in_app:
                        order_id = response['orderId'] = item['transaction_id']
                        
                    if order_id and crud_payment.is_exist_order_id(db, order_id):
                        response['resultCode'] = Constant.RESULT_DUPLICATE
                        
                    if response['resultCode'] == Constant.RESULT_VALID_RECEIPT:
                        response['valid'] = True
                
                
            except InAppPyValidationError as ex:
                # handle validation error
                response_from_apple = ex.raw_response  # contains actual response from AppStore service.
                response['resultCode'] = Constant.RESULT_INVALID_RECEIPT
            
            crud_payment.set_payment_complete(db, iid, response['resultCode'])   
            if currencyManager.get_rewards():
                currencyManager.get_currency_rewards(db, req.uid)
            data = currencyManager.get_user_currency_data(db, req.uid)
            data['UserData'] = userdataManager.generate_user_save(db, req.uid)
            if currencyManager.get_change():
                data['change'] = currencyManager.get_change()
            data['resultCode'] = response['resultCode']
            
            return data

        elif req.platform == 'onestore':
            response = {'valid': False, 'orderId' : ''}
            is_complete = onestore_varify(db, req.uid, iid, req.product_id, req.receipt)
            if is_complete:
                response['resultCode'] = Constant.RESULT_VALID_RECEIPT
                response['valid'] = True
            else:
                response['resultCode'] = Constant.RESULT_INVALID_RECEIPT
                
            if currencyManager.get_rewards():
                currencyManager.get_currency_rewards(db, req.uid)
            data = currencyManager.get_user_currency_data(db, req.uid)
            data['UserData'] = userdataManager.generate_user_save(db, req.uid)
            if currencyManager.get_change():
                data['change'] = currencyManager.get_change()
            data['resultCode'] = response['resultCode']
            
            return data
            
            


def noti(signed_payload:str, db:Session):
    
    arr_signed_payload = signed_payload.split('.')
    
    if len(arr_signed_payload) != 3:
        logger.error("signedPayload count is not 3")
        return
    
    payload = arr_signed_payload[1]
    
    # python에서는 신기하게 패딩처리를 해줘야 하네.....젠장할....
    payload += "=" * ((4 - len(payload) % 4) % 4)
        
    if not payload:
        logger.error("payload string is null")
        return
    
    payload = json.loads(base64.b64decode(payload))
    
    if not payload:
        logger.error("decode payload string is null")
        return
    
    
    notification_type = get(payload, 'notificationType')
    
    if notification_type and (notification_type == 'REFUND'):
        signed_transaction_info = str(payload['data']['signedTransactionInfo'])
        
        if not signed_transaction_info:
            logger.error("signed transaction info is null")
            return
        
        arr_signed_transaction_info = signed_transaction_info.split('.')
        
        if len(arr_signed_transaction_info) != 3 and (not arr_signed_transaction_info[1]):
            logger.error("signed transaction info array is invalid")
            return
        
        transaction_info = arr_signed_transaction_info[1]
        transaction_info += "=" * ((4 - len(transaction_info) % 4) % 4)
        
        transaction_info = json.loads(base64.b64decode(transaction_info))
        
        if not transaction_info:
            logger.error("transaction info is null")
            return
        
        transaction_id = get(transaction_info, 'transactionId')
        if transaction_id:
            if crud_payment.is_exist_order_id(get(transaction_info)):
                crud_payment.update_payment_complete(db, transaction_id, 2)
    else:
        return
    
    