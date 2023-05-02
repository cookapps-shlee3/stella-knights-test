# -*- coding: utf-8 -*-
import time
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models.user import UserPayment
from app.db.models.user import UserPostbox


def set_data(db:Session, uid:int, platform:str, order_id:str, product_id:str, currency_price, currency_code:str, receipt:str='', target_uid:int = 0, social_id:str= ''):
    data = UserPayment()
    data.uid = uid
    data.order_id = order_id
    data.product_id = product_id
    data.complete = 0
    data.price = 0
    data.currency_code = currency_code
    data.currency_price = currency_price
    data.platform = platform
    data.receipt = receipt
    data.target_uid = target_uid
    data.social_id = social_id
    data.wdate = datetime.now()
    data.wdate_key = int(datetime.now().strftime('%Y%m%d'))
    data.hour = datetime.now().hour
    
    db.add(data)
    db.commit()
    db.refresh(data)
    
    return data.id
    

def is_exist_order_id(db:Session, order_id:str):
    count = db.query(UserPayment).filter(UserPayment.order_id == order_id).count()
    
    return True if count > 1 else False

def get_payment_row(db:Session, id):
    return db.query(UserPayment).filter(UserPayment.id == id).first()


def set_payment_complete(db:Session, id, complete:int=0):
    db.query(UserPayment).filter(UserPayment.id == id).update({UserPayment.complete : complete})
    db.commit()

def update_payment_complete(db:Session, order_id:str, complete=0):
    db.query(UserPayment).filter(UserPayment.order_id == order_id).update({UserPayment.complete : complete})
    db.commit()
    
def update_payment_complete_by_id(db:Session, id:int, complete=0):
    db.query(UserPayment).filter(UserPayment.id == id).update({UserPayment.complete : complete})
    db.commit()


## TODO : KIMKJ onestore 관련 항목과 구글 관련 항목은 lib 붙이고 나서 추가 구현을 하도록 한다.











def send_purchase_reward(db:Session, uid:int, product_id:str, product_key:str):
    if product_id:
        post = UserPostbox()
        post.uid = uid
        post.sender_uid = 0
        post.title_code = 110002
        post.desc_code = 120002
        post.tab = 1
        post.reward_type = 'NONE'
        post.product_id = product_id
        post.product_key = product_key
        post.reward_id = 0
        post.reward_count = 1
        post.start_time = int(time.time())
        post.expire_time = int(time.time() + (86400 * 365 * 100))
        post.created = datetime.now()
        
        db.add(post)
        db.commit()
        db.refresh(post)
        