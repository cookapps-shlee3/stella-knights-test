from sqlalchemy import Column, String, Integer, BigInteger, DateTime, null
from sqlalchemy.orm import relationship
from app.db.session import Base

class UserPostbox_1(Base):
    __tablename__ = "user_postbox_1"
    
    post_id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer)
    sender_uid = Column(Integer)
    title_code = Column(Integer)
    desc_code = Column(Integer)
    tab = Column(Integer, default=1)
    product_id = Column(String, default='')
    rewards = Column(String, default='')
    special_reward_id = Column(Integer, default=0)
    is_rewarded = Column(Integer, default=0)
    start_time = Column(Integer)
    expire_time = Column(Integer)
    created = Column(DateTime)
    
    
class UserPostbox_2(Base):
    __tablename__ = "user_postbox_2"
    
    post_id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer)
    sender_uid = Column(Integer)
    title_code = Column(Integer)
    desc_code = Column(Integer)
    tab = Column(Integer, default=1)
    product_id = Column(String, default='')
    rewards = Column(String, default='')
    special_reward_id = Column(Integer, default=0)
    is_rewarded = Column(Integer, default=0)
    start_time = Column(Integer)
    expire_time = Column(Integer)
    created = Column(DateTime)
    
    
class UserPostbox_3(Base):
    __tablename__ = "user_postbox_3"
    
    post_id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer)
    sender_uid = Column(Integer)
    title_code = Column(Integer)
    desc_code = Column(Integer)
    tab = Column(Integer, default=1)
    product_id = Column(String, default='')
    rewards = Column(String, default='')
    special_reward_id = Column(Integer, default=0)
    is_rewarded = Column(Integer, default=0)
    start_time = Column(Integer)
    expire_time = Column(Integer)
    created = Column(DateTime)
    
    
class UserPostbox_4(Base):
    __tablename__ = "user_postbox_4"
    
    post_id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer)
    sender_uid = Column(Integer)
    title_code = Column(Integer)
    desc_code = Column(Integer)
    tab = Column(Integer, default=1)
    product_id = Column(String, default='')
    rewards = Column(String, default='')
    special_reward_id = Column(Integer, default=0)
    is_rewarded = Column(Integer, default=0)
    start_time = Column(Integer)
    expire_time = Column(Integer)
    created = Column(DateTime)
    
    
class UserPostbox_5(Base):
    __tablename__ = "user_postbox_5"
    
    post_id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer)
    sender_uid = Column(Integer)
    title_code = Column(Integer)
    desc_code = Column(Integer)
    tab = Column(Integer, default=1)
    product_id = Column(String, default='')
    rewards = Column(String, default='')
    special_reward_id = Column(Integer, default=0)
    is_rewarded = Column(Integer, default=0)
    start_time = Column(Integer)
    expire_time = Column(Integer)
    created = Column(DateTime)
    
    

class UserPostbox_6(Base):
    __tablename__ = "user_postbox_6"
    
    post_id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer)
    sender_uid = Column(Integer)
    title_code = Column(Integer)
    desc_code = Column(Integer)
    tab = Column(Integer, default=1)
    product_id = Column(String, default='')
    rewards = Column(String, default='')
    special_reward_id = Column(Integer, default=0)
    is_rewarded = Column(Integer, default=0)
    start_time = Column(Integer)
    expire_time = Column(Integer)
    created = Column(DateTime)
    
    

class UserPostbox_7(Base):
    __tablename__ = "user_postbox_7"
    
    post_id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer)
    sender_uid = Column(Integer)
    title_code = Column(Integer)
    desc_code = Column(Integer)
    tab = Column(Integer, default=1)
    product_id = Column(String, default='')
    rewards = Column(String, default='')
    special_reward_id = Column(Integer, default=0)
    is_rewarded = Column(Integer, default=0)
    start_time = Column(Integer)
    expire_time = Column(Integer)
    created = Column(DateTime)
    
    

class UserPostbox_8(Base):
    __tablename__ = "user_postbox_8"
    
    post_id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer)
    sender_uid = Column(Integer)
    title_code = Column(Integer)
    desc_code = Column(Integer)
    tab = Column(Integer, default=1)
    product_id = Column(String, default='')
    rewards = Column(String, default='')
    special_reward_id = Column(Integer, default=0)
    is_rewarded = Column(Integer, default=0)
    start_time = Column(Integer)
    expire_time = Column(Integer)
    created = Column(DateTime)
    
    

class UserPostbox_9(Base):
    __tablename__ = "user_postbox_9"
    
    post_id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer)
    sender_uid = Column(Integer)
    title_code = Column(Integer)
    desc_code = Column(Integer)
    tab = Column(Integer, default=1)
    product_id = Column(String, default='')
    rewards = Column(String, default='')
    special_reward_id = Column(Integer, default=0)
    is_rewarded = Column(Integer, default=0)
    start_time = Column(Integer)
    expire_time = Column(Integer)
    created = Column(DateTime)
    
    
class UserPostbox_0(Base):
    __tablename__ = "user_postbox_0"
    
    post_id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer)
    sender_uid = Column(Integer)
    title_code = Column(Integer)
    desc_code = Column(Integer)
    tab = Column(Integer, default=1)
    product_id = Column(String, default='')
    rewards = Column(String, default='')
    special_reward_id = Column(Integer, default=0)
    is_rewarded = Column(Integer, default=0)
    start_time = Column(Integer)
    expire_time = Column(Integer)
    created = Column(DateTime)