# -*- coding: utf-8 -*-
import json
import time
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models.pub_coupons import PubCoupons
from app.db.models.user import UserCouponReward, UserPostbox
from app.params.ResParam import get_response, ResponseCode

## 추가로 response에 대한 처리 과정이 필요함.
def check_coupon(db:Session, uid:int, code:str):
    pub_coupon = db.query(PubCoupons).filter(PubCoupons.code == code).first()
    
    if not pub_coupon:
        return get_response(code=ResponseCode.RES_ERR_COUPON_NOT_EXIST, msg='COUPON_NOT_EXIST', uid=uid)
    
    if (int(pub_coupon.expired.timestamp()) < int(time.time())) or (pub_coupon.enabled != 1):
        return get_response(code=ResponseCode.RES_ERR_COUPON_EXPIRED, uid=uid)
    
    if (pub_coupon.type == 'UNIQUE') and (pub_coupon.used == 1):
        return get_response(code=ResponseCode.RES_ERR_COUPON_ALREADY_REWARDED, uid=uid)
    
    user_coupon = db.query(UserCouponReward).filter(UserCouponReward.uid == uid, UserCouponReward.pub == pub_coupon.pub).first()
    if not user_coupon:
        return get_response(code=ResponseCode.RES_ERR_COUPON_NOT_AVAILABLE, uid=uid)
    
    
    db.query(PubCoupons).filter(PubCoupons.code == code).update({PubCoupons.used:1})
    data = UserCouponReward()
    data.uid = uid
    data.pub = pub_coupon.pub
    data.code = code
    data.created = datetime.now()
    db.add(data)
    db.commit()
    
    rewards = json.loads(pub_coupon.rewards)
    
    if pub_coupon.pub.find('23') == -1:
        title_code = 110011
        desc_code = 120018
    else:
        title_code = 110004
        desc_code = 120002
    
    post_data = []
    for reward in rewards:
        data = UserPostbox()
        data.uid = uid
        data.sender_uid = 0
        data.title_code = title_code
        data.desc_code = desc_code
        data.tab = 1
        data.reward_type = reward['reward_type']
        data.reward_id = reward['reward_id']
        data.reward_count = reward['reward_count']
        data.start_time = int(time.time())
        data.expire_time = int(time.time()) + (86400 * 365)
        data.created = datetime.now()
        
        post_data.append(data)
    
    db.add_all(post_data)
    db.commit()
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=rewards, uid=uid)


