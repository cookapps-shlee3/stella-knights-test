import os
import math
import json
import random
import time
from datetime import datetime
from loguru import logger
from functools import reduce
from sqlalchemy.orm import Session
from app.util.util import get
from app.config.settings import Constant
from app.crud.cache import crud_user_currency


# 목표는 명확하게 타입에 따리를 별도록 할 수 있어야 함.
# 기본적으로 공통 처리는 default function으로 처리 할 수 있도록 연결 하고
# 나머지는 자체적으로 처리할 수 있는 핸들러가 필요하다.
# 추가로 ref할 수 있는 userdata를 manager할 수 있는 클래스와 연동을 할 수 있어야 할 것으로 생각됨.

class CurrencyManager():
    
    # 여기서 필요한 데이터 들에 대한 선언을 수행하도록 한다.
    # 셋팅에 있는 currency에 대한 데이터 처리를 할 수 있도록 한다.
    # 쪽에 있는 데이터는 소비를 할수도 있고 없을 수도 있을것 같은데 어떻게 처리 할 것인가?
    # None으로 퉁칠까?
    
    extre_currency:dict = {
        'KNIGHT_PIECE':{''},
        'RUNE':{''},
    }
    
    
    rewards:dict = None
    change:list = None
    rune_random_list:list = None
    character_random_piece_list:list = None
    
    def __init__(self) -> None:
        self.change = []
        self.rewards = {}
        self.rune_random_list = []
        self.character_random_piece_list = []
    
    
    @staticmethod
    def get_currency_type() -> list:
        return [
            'JEWEL',
            'COIN',
            'EXPITEM',
            'SOUL',
            'BREAD',
            'KTICKET',
            'ETICKET',
            'DUNGEON_KEY1',
            'DUNGEON_KEY2',
            'DUNGEON_KEY3',
            'STONE',
            'POWDER',
            'MEDAL',
            'PTICKET',
            'RUNEPIECE',
            'EXP',
            'BUILDING_SUPPLIES',
            'RANDOM_KNIGHT',
            'RANDOM_WEAPON',
            'RANDOM_RUNE',
            'MILEAGE',
            'RUNE_UPGRADE_STONE',
            'COMPASS',
            'EXPEDITION_TOKEN',
            'BUFF_COIN',
            'RANDOM_KNIGHT_PIECE',
            'RANDOM_WEAPON_PIECE',
            'RANDOM_RUNE_PIECE',
            'GRIND_STONE',
            'LV_POTION_50',
            ]
        
    

    ###############################################################################################################################################
    # Random Rune
    ###############################################################################################################################################

    def __generate_random_item(self, type:str, key:int, amount:int, rate:float):
        return {"reward_type":type, "reward_key":key, "reward_amount":amount, "reward_prob":int(rate * 10000)}


    def get_random_rune(self):
        total_prob = 0
        for random_rune in self.rune_random_list:
            total_prob += random_rune['reward_prob']
            
        rand_prob = random.randint(0, 9999)
        
        for random_rune in self.rune_random_list:
            if (rand_prob - random_rune['reward_prob']) <= 0:
                return random_rune
            else:
                rand_prob = rand_prob - random_rune['reward_prob']
    
        return None
    
    def get_random_rune_by_data(self, rune_data:list):
        total_prob = 0
        for random_rune in rune_data:
            total_prob += random_rune['ODD']
            
        rand_prob = random.randint(0, 9999)
        
        for random_rune in rune_data:
            if (rand_prob - random_rune['ODD']) <= 0:
                return random_rune
            else:
                rand_prob = rand_prob - random_rune['ODD']
    
        return None
    

    def add_rune(self, type:str, key:int, amount:int, rune_datas:list):
        max_uid = 0
        if rune_datas:
            max_uid = reduce(lambda x, y : x if int(x['UID']) > int(y['UID']) else y, rune_datas)
            max_uid = max_uid['UID']
        
        max_uid = max_uid + 1
        rune_datas.append({"UID": max_uid, "ID": key, "Enhance": 0, "Count": 0, "rate": 0.0, "equipCharacterID": 0})
        
        self.add_dict(type, key, amount)
        
        return rune_datas
    
    def add_rune_def_uid(self, type:str, key:int, amount:int, uid:int, rune_datas):
        
        rune_datas.append({"UID": uid, "ID": key, "Enhance": 0, "Count": 0, "rate": 0.0, "equipCharacterID": 0})
        
        self.add_dict(type, key, amount)
        
        return rune_datas

    ###############################################################################################################################################
    # WEAPON
    ###############################################################################################################################################    
    
    def add_weapon(self, type:str, key:int, amount:int, weapon_datas:list):
        
        if weapon_datas:
            max_uid = reduce(lambda x, y : x if int(x['UID']) > int(y['UID']) else y, weapon_datas)
            max_uid = max_uid['UID']
        else:
            max_uid = 0
        
        weapon_datas.append({"ID": key, "UID": max_uid+1, "Level": 1, "Reinforce": 0})
        
        self.add_dict(type, key, amount)
        
        return weapon_datas

    def add_weapon_def_uid(self, type:str, key:int, amount:int, uid:int, weapon_datas):
        
        weapon_datas.append({"ID": key, "UID": uid, "Level": 1, "Reinforce": 0})
        
        self.add_dict(type, key, amount)
        
        return weapon_datas

    ###############################################################################################################################################
    # Random Characer Piece
    ###############################################################################################################################################    
    
    def add_character(self, type:str, key:int, amount:int, default_piece:int, character_datas:list):
        find_character = None

        if character_datas:
            for character_data in character_datas:
                character_id = get(character_data, 'ID', None)
                if character_id == key:
                    find_character = character_data
                    break
        
        if find_character:
            if find_character['Level'] == 0:
                find_character['Level'] = 1
                self.add_dict(type, key, 1)
            else:
                character_piece = get(find_character, 'Piece', None)
                if character_piece:
                    find_character['Piece'] = find_character['Piece'] + default_piece
                    self.add_dict('KNIGHT_PIECE', key, default_piece)
                else:
                    find_character['Piece'] = amount
                    self.add_dict('KNIGHT_PIECE', key, default_piece)

    
    def add_character_piece(self, type:str, key:int, amount:int, character_datas:list):

        find_character = None
        
        for character_data in character_datas:
            character_id = get(character_data, 'ID', None)
            if (character_id != None) and (character_id == key):
                find_character = character_data
                break
        
        if find_character != None:
            character_piece = get(find_character, 'Piece', None)
            if character_piece:
                find_character['Piece'] = find_character['Piece'] + amount
            else:
                find_character['Piece'] = amount
                
            self.add_dict(type, key, amount)

        return character_datas


    def get_random_character_piece(self):
        total_prob = 0
        for character_piece in self.character_random_piece_list:
            total_prob += character_piece['reward_prob']
            
        rand_prob = random.randint(0, 9999)
        
        for character_piece in self.character_random_piece_list:
            if (rand_prob - character_piece['reward_prob']) <= 0:
                return character_piece
            else:
                rand_prob = rand_prob - character_piece['reward_prob']
    
        return None
        

    def __get_random_character(self, character_random_list:list):
        total_prob = 0
        for random_rune in character_random_list:
            total_prob += random_rune['reward_prob']
            
        rand_prob = random.randint(0, total_prob-1)
        
        for random_rune in character_random_list:
            if (rand_prob - random_rune['reward_prob']) <= 0:
                return random_rune
            else:
                rand_prob = rand_prob - random_rune['reward_prob']
                
        return None
    
    def get_amount(self, db:Session, uid:int, type:str):
        if type in CurrencyManager.get_currency_type():
            result = crud_user_currency.get(db, uid, type)
            if result:
                return result.amount
        else:
            return 0
    
    
    def star_reward(self, db:Session, uid:int, min:int, max:int, stage_info:dict):
        default_str = 'star_reward_'
        for star in range(min+1, max+1):
            type = get(stage_info, default_str+'type_'+str(star), None)
            count = get(stage_info, default_str+'count_'+str(star), None)
            self.add_dict(type, 0, count)
    
    
    def use_currency(self, db:Session, uid:int, type:str, amount:int):
        if type in self.get_currency_type():
            return self.__use_currency(db, uid, type, amount)
        pass
    
    
    def get_currency_rewards(self, db:Session, uid:int):
        for reward_type in self.rewards:
            if reward_type in CurrencyManager.get_currency_type():
                self.__get_currency(db, uid, reward_type, self.rewards[reward_type])


    def __get_currency(self, db:Session, uid:int, type:str, amount:int):
        if type not in CurrencyManager.get_currency_type():
            return None
        user_currency = crud_user_currency.update_get_user_currency(db, uid, type, amount)
        return user_currency


    def __use_currency(self, db:Session, uid:int, type:str, amount:int):
        user_currency = crud_user_currency.get(db, uid, type)
        if not user_currency:
            user_currency = crud_user_currency.insert(db, uid, type, amount)
            return None
        else:
            if (user_currency.amount - amount) < 0:
                return None
        crud_user_currency.update_use_user_currency(db, uid, type, amount)
        # 추가로 로그를 남길수 있는 방법을 생각해 보자.
        self.sub_dict(type, 0, amount)
        
        return user_currency
    
    # 특수 목적으로 만든 함수
    def use_currencys(self, db:Session, uid:int, use_list:list):
        types = []
        type_dict = {}
        for type in use_list:
            types.append(type['type'])
            type_dict[type['type']] = type['value']
            
        user_currencys = crud_user_currency.gets(db, uid, types)
        
        if user_currencys:
            for currency in user_currencys:
                current_amount = type_dict[currency.type]
                if (current_amount - (currency.amount)) < 0:
                    return False
                
            for use_currency in use_list:
                crud_user_currency.update_use_user_currency(db, uid, use_currency['type'], use_currency['value'])

        else:
            return False
        
        return True
    
    
    def get_user_currency_data(self, db:Session, uid:int):
        user_currencys = crud_user_currency.get_user_currency_all(db, uid)
        result = []
        for user_currency in user_currencys:
            result.append(user_currency.getdict())
        data = {'currency':result}
        return data
    
    
    #추가로 처리해야 할 것들이 여기에 있음....타입이 아닌 경우에는 어떻게 처리할 것인지 고민
    def add_dict(self, type:str, key:int, amount:int):
        if not amount: return
        if type in CurrencyManager.get_currency_type():
            if not get(self.rewards, type, None):
                self.rewards[type] = amount
            else:
                self.rewards[type] = self.rewards[type] + amount
                
        self.change.append({'reward_type':type, 'reward_key':key, 'reward_amount':amount})


    def add_random_rune(self, type:str, key:int, amount:int, rate:float=0):
        if type == 'RUNE':
            self.rune_random_list.append(self.__generate_random_item(type, key, amount, rate))
    
    def add_random_character_piece(self, type:str, key:int, amount:int, rate:float=0):
        if type == 'KNIGHT_PIECE':
            self.character_random_piece_list.append(self.__generate_random_item(type, key, amount, rate))

    def sub_dict(self, type:str, key:int, amount:int):
        self.change.append({'reward_type':type, 'reward_key':key, 'reward_amount':(-amount)})

    def get_change(self):
        return self.change
    
    def get_rewards(self):
        return self.rewards
    
    def get_random_rune_list(self):
        return self.rune_random_list
    
    def get_random_character_piece_list(self):
        return self.character_random_piece_list
            
    # def __change_dict(change:list):
        # result = []
        # if change:
        #     for reward in change:
        #         result.append({'reward_type':reward['type'], 'reward_key':reward['key'], 'reward_amount':reward['amount']})
                
        # return result

    ###############################################################################################################################################
    # Random Rune
    ###############################################################################################################################################
    
    pass