import time
from typing import Optional
from sqlalchemy import VARCHAR, Column, Float, String, Integer, BigInteger, DateTime, JSON
from app.db.session import Base
from bson import ObjectId
from pydantic import BaseConfig, BaseModel, Field

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class UserDataMongo(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    category: Optional[str]
    data: Optional[dict]
    class Config(BaseConfig):
        allow_population_by_field_name=True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: int}

    
class UserMembers(Base):
    
    __tablename__ = "user_members"
    
    uid = Column(BigInteger, primary_key=True)
    server = Column(Integer, default=1)
    level = Column(Integer, default=1)
    nickname = Column(VARCHAR, default='')
    is_nickname = Column(Integer, default=0)
    login_device_id = Column(VARCHAR, default=None)
    social_id = Column(VARCHAR, default=None)
    is_terms_agree = Column(Integer, default=0)
    updated = Column(DateTime)
    created = Column(DateTime)
    
    def setClassFromDict(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])
    

class FriendInfoBase:
    
    uid:int
    level:int
    server:int
    nickname:str
    updated:int
    
    def __init__(self, user:UserMembers) -> None:
        self.uid =  user.uid
        self.level = user.level
        self.server = user.server
        self.nickname = user.nickname
        self.updated = int(time.mktime(user.updated.timetuple()))
    
    

    
# class UserAccount(Base):
#     __tablename__ = "user_account"
    
#     auth_id = Column(String)
#     auth_pw = Column(String, default='')
#     uid = Column(Integer)
#     created = Column(DateTime)
    
    
class UserBanned(Base):
    __tablename__ = "user_banned"
    
    uid = Column(Integer, primary_key=True)
    created = Column(DateTime)
    expired = Column(DateTime, default=None)
    msg = Column(String(1000), default=None)
    tag = Column(String, default=None)
    
    
class UserBannedDevice(Base):
    __tablename__ = "user_banned_device"
    
    device_id = Column(VARCHAR, primary_key=True)
    created = Column(DateTime)
    tag = Column(String, default=None)
    
    
class UserCouponReward(Base):
    __tablename__ = "user_coupon_rewards"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer)
    pub = Column(String, default='')
    code = Column(String)
    created = Column(DateTime)


class UserData(Base):
    __tablename__ = "user_data"
    
    uid = Column(Integer, primary_key=True)
    category = Column(String, primary_key=True)
    data = Column(String, default=None)
    ts = Column(Integer, default=None)
    updated = Column(DateTime, default=None)
    
    
    
    
class UserData_1(Base):
    __tablename__ = "user_data_1"
    
    uid = Column(Integer, primary_key=True)
    category = Column(String, primary_key=True)
    data = Column(String, default=None)
    ts = Column(Integer, default=None)
    updated = Column(DateTime, default=None)
    
class UserData_2(Base):
    __tablename__ = "user_data_2"
    
    uid = Column(Integer, primary_key=True)
    category = Column(String, primary_key=True)
    data = Column(String, default=None)
    ts = Column(Integer, default=None)
    updated = Column(DateTime, default=None)
    
class UserData_3(Base):
    __tablename__ = "user_data_3"
    
    uid = Column(Integer, primary_key=True)
    category = Column(String, primary_key=True)
    data = Column(String, default=None)
    ts = Column(Integer, default=None)
    updated = Column(DateTime, default=None)
    
class UserData_4(Base):
    __tablename__ = "user_data_4"
    
    uid = Column(Integer, primary_key=True)
    category = Column(String, primary_key=True)
    data = Column(String, default=None)
    ts = Column(Integer, default=None)
    updated = Column(DateTime, default=None)
    
class UserData_5(Base):
    __tablename__ = "user_data_5"
    
    uid = Column(Integer, primary_key=True)
    category = Column(String, primary_key=True)
    data = Column(String, default=None)
    ts = Column(Integer, default=None)
    updated = Column(DateTime, default=None)
    
class UserData_6(Base):
    __tablename__ = "user_data_6"
    
    uid = Column(Integer, primary_key=True)
    category = Column(String, primary_key=True)
    data = Column(String, default=None)
    ts = Column(Integer, default=None)
    updated = Column(DateTime, default=None)
    
class UserData_7(Base):
    __tablename__ = "user_data_7"
    
    uid = Column(Integer, primary_key=True)
    category = Column(String, primary_key=True)
    data = Column(String, default=None)
    ts = Column(Integer, default=None)
    updated = Column(DateTime, default=None)
    
class UserData_8(Base):
    __tablename__ = "user_data_8"
    
    uid = Column(Integer, primary_key=True)
    category = Column(String, primary_key=True)
    data = Column(String, default=None)
    ts = Column(Integer, default=None)
    updated = Column(DateTime, default=None)
    
class UserData_9(Base):
    __tablename__ = "user_data_9"
    
    uid = Column(Integer, primary_key=True)
    category = Column(String, primary_key=True)
    data = Column(String, default=None)
    ts = Column(Integer, default=None)
    updated = Column(DateTime, default=None)
    
    
class UserData_0(Base):
    __tablename__ = "user_data_0"
    
    uid = Column(Integer, primary_key=True)
    category = Column(String, primary_key=True)
    data = Column(String, default=None)
    ts = Column(Integer, default=None)
    updated = Column(DateTime, default=None)
    
    
    
    
    
    

    
class UserDataBattle(Base):
    __tablename__ = "user_data_battle"
    
    uid = Column(Integer, primary_key=True)
    battle_point = Column(BigInteger, default=0)
    data = Column(String, default=None)
    
    
class UserDevices(Base):
    __tablename__ = "user_devices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, default=0)
    device_id = Column(String, default=None)
    platform = Column(String, default=None)
    updated = Column(DateTime)
    created = Column(DateTime)
    
    
class UserDevicesBackup(Base):
    __tablename__ = "user_devices_backup"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, default=0)
    device_id = Column(String, default=None)
    platform = Column(String, default=None)
    updated = Column(DateTime)
    created = Column(DateTime)
    
    
    
class UserFriends(Base):
    __tablename__ = "user_friends"
    
    def __init__(self, uid, friend_uid) -> None:
        super().__init__()
        self.uid = uid
        self.friend_uid = friend_uid
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer)
    friend_uid = Column(Integer)
    point = Column(Integer, default=0)
    gift_send = Column(Integer, default=0)
    date_key = Column(Integer, default=0)
    raid_open = Column(Integer, default=0)
    raid_expire = Column(Integer, default=0)
   
    
class UserFriendsInvite(Base):
    __tablename__ = "user_friends_invite"
    
    def __init__(self, uid, friend_uid) -> None:
        super().__init__()
        self.uid = uid
        self.friend_uid = friend_uid
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer)
    friend_uid = Column(Integer)


class UserFriendsRemove(Base):
    __tablename__ = "user_friends_remove"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer)
    friend_uid = Column(Integer)
    date_key = Column(Integer)
    created = Column(DateTime)


class UserPayment(Base):
    __tablename__ = "user_payment"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer)
    order_id = Column(String, default='')
    product_id = Column(String, default='')
    complete = Column(Integer, default=0)
    price = Column(Float, default=None)
    currency_price = Column(Float, default=0)
    currency_code = Column(String, default=None)
    platform = Column(String, default='')
    receipt = Column(String, default=None)
    target_uid = Column(Integer)
    social_id = Column(String, default=None)
    wdate_key = Column(Integer)
    wdate = Column(DateTime)
    hour = Column(Integer)


class UserPlatforms(Base):
    __tablename__ = "user_platforms"
    
    auth_platform = Column(String)
    auth_id = Column(String)
    uid = Column(Integer, primary_key=True)
    created = Column(DateTime)
    
    
class UserPlatformsBackup(Base):
    __tablename__ = "user_platforms_backup"
    
    auth_platform = Column(String)
    auth_id = Column(String)
    uid = Column(Integer, primary_key=True)
    created = Column(DateTime)



class UserPostbox(Base):
    __tablename__ = "user_postbox"
    
    post_id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer)
    sender_uid = Column(Integer)
    title_code = Column(Integer)
    desc_code = Column(Integer)
    tab = Column(Integer, default=1)
    product_id = Column(String, default='')
    product_key = Column(Integer, default=0)
    reward_type = Column(String, default='')
    reward_id = Column(Integer, default=0)
    reward_count = Column(Integer, default=0)
    special_reward_id = Column(Integer, default=0)
    is_rewarded = Column(Integer, default=0)
    start_time = Column(Integer)
    expire_time = Column(Integer)
    created = Column(DateTime)


class UserRaidResult(Base):
    __tablename__ = "user_raid_result"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer)
    friend_uid = Column(Integer, default=0)
    friend_nickname = Column(String, default=None)
    raid_state = Column(Integer, default=0)
    raid_index = Column(Integer, default=0)
    raid_lv = Column(Integer, default=1)
    boss_hp = Column(BigInteger, default=0)
    join_count = Column(Integer, default=0)
    raid_start = Column(Integer, default=0)
    raid_end = Column(Integer, default=0)
    result = Column(String, default=None)


class UserSendGift(Base):
    __tablename__ = "user_send_gift"
    
    uid = Column(BigInteger, primary_key=True, default=0)
    send_count = Column(Integer, default=0)
    date_key = Column(Integer, default=0)
    created = Column(DateTime)


class UserServer(Base):
    __tablename__ = "user_server"
    
    uid = Column(Integer, primary_key=True)
    is_base = Column(Integer, default=0)
    server_uid = Column(Integer)
    server = Column(Integer, primary_key=True)
    created = Column(DateTime)



class UserServerBackup(Base):
    __tablename__ = "user_server_backup"
    
    uid = Column(Integer, primary_key=True)
    is_base = Column(Integer, default=0)
    server_uid = Column(Integer)
    server = Column(Integer, primary_key=True)
    created = Column(DateTime)
    

class UserReview(Base):
    __tablename__ = "user_rewiew"
    
    uid = Column(Integer, primary_key=True)
    language = Column(String, default=None)
    purchased = Column(Integer, default=0)
    legend_count = Column(Integer)
    art_star = Column(Float)
    fun_star = Column(Float)
    balance_star = Column(Float)
    ip = Column(String, default=None)
    created = Column(DateTime)