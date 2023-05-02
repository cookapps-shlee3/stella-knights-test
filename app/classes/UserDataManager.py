# -*- coding: utf-8 -*-
import json
from loguru import logger
from functools import reduce
from sqlalchemy.orm import Session
from app.util.util import get
from app.crud import crud_user_data

class UserDataManager:
    
    user_datas = None
    user_data_update = None
   
    
    def __init__(self) -> None:
        self.user_datas = {}
        self.user_data_update = {}
        pass
    
    
    def get(self, db:Session, uid:int, category:str):
        data = get(self.user_datas, category, None)
        if data == None:
            data = crud_user_data.get(db, uid, category)
            self.user_datas[category] = json.loads(data.data)
            self.user_data_update[category] = False
        return self.user_datas[category]
        
    
    def set(self, category:str, target):
        self.user_datas[category] = target
        self.set_update(category)
        
        
    def change_user_data_value(self, db:Session, uid:int, category:str, key:str, value):
        data = get(self.user_datas, category, None)
        if data == None:
            data = crud_user_data.get(db, uid, category)
            self.user_datas[category] = json.loads(data.data)
            self.user_data_update[category] = False
            data = get(self.user_datas, category, None)
            
        data[key] = value
        
        self.user_data_update[category] = True
        
        return self.user_datas[category]
        
        
    def add_user_data_value(self, db:Session, uid:int, category:str, key:str, value):
        data = get(self.user_datas, category, None)
        if data == None:
            temp_data = crud_user_data.get(db, uid, category)
            self.user_datas[category] = json.loads(temp_data.data)
            self.user_data_update[category] = False
            data = get(self.user_datas, category, None)
        
        
        data_value = get(self.user_datas[category], key, None)
        self.user_datas[category][key] = (data_value or 0) + value
        
        self.user_data_update[category] = True
        
        return self.user_datas[category]
    
    
    def sub_user_data_value(self, db:Session, uid:int, category:str, key:str, value):
        data = get(self.user_datas, category, None)
        if data == None:
            data = crud_user_data.get(db, uid, category)
            self.user_datas[category] = data
            self.user_data_update[category] = False

        data_value = get(self.user_datas[category], key, None)
        self.user_datas[category][key] = (data_value or 0) - value
        
        self.user_data_update[category] = True
        
        return self.user_datas[category]
        
    def set_update(self, category:str):
        self.user_data_update[category] = True
        
        
    def generate_user_save(self, db:Session, uid:int):
        gen_user_datas = {}
        for user_data in UserDataManager.get_user_data_category():
            temp_data = get(self.user_datas, user_data, None)
            gen_user_datas[user_data] = temp_data
            if self.user_data_update.get(user_data):
                crud_user_data.save(db, uid, user_data, json.dumps(temp_data))
                self.user_data_update[user_data] = False

        return gen_user_datas
    
    
    @staticmethod
    def get_user_data_category():
        return [
            'User',
            'Time',
            'Purchase',
            'Quest',
            'Character',
            'Stage',
            'Request',
            'HomeShop',
            'Building',
            'Material',
            'Artifact',
            'Weapon',
            'PVP',
            'Pass',
            'Training',
            'Rune', 
            'Achievement',
            'Expedition',
            'Collection',
            'Training',
            'GameEvent',
            ]