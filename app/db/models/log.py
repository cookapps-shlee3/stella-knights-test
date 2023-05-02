from sqlalchemy import Column, String, Integer, BigInteger, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base

class LogBanned(Base):
    __tablename__ = "log_banned"
    
    seq = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer)
    tag = Column(String, default='')
    desc = Column(String, default='')
    data = Column(String, default=None)


class LogBattle(Base):
    __tablename__ = "log_battle"
    
    seq = Column(BigInteger, primary_key=True, autoincrement=True)
    log_date = Column(Integer)
    uid = Column(BigInteger)
    version = Column(String, default='')
    status = Column(String, default='None')
    mode = Column(String)
    rank = Column(Integer)
    trophy = Column(Integer, default=0)
    crown = Column(Integer, default=0)
    o_nickname = Column(String)
    m_deck = Column(String)
    o_deck = Column(String)
    is_ai = Column(Integer)
    is_friendly = Column(Integer)
    win = Column(Integer)
    created = Column(DateTime)


class LogFixedVersion(Base):
    __tablename__ = "log_fixed_version"
    
    seq = Column(BigInteger, primary_key=True, autoincrement=True)
    app_version = Column(Integer, default=0)
    spec_version = Column(Integer, default=0)


class LogHackCheck(Base):
    __tablename__ = "log_hack_check"
    
    seq = Column(BigInteger, primary_key=True, autoincrement=True)
    uid = Column(Integer)
    is_banned = Column(Integer, default=0)
    commend = Column(String, default=None)
    created = Column(DateTime)


## 우선은 쿼리로만 작성할 것
class LogHash(Base):
    __tablename__ = "log_hash"
    
    version = Column(Integer, default=0, primary_key=True)
    hash_key = Column(String, default='', primary_key=True)
    device_id = Column(String, default='', primary_key=True)
    created = Column(DateTime)


class LogJackpot(Base):
    __tablename__ = "log_jackpot"
    
    seq = Column(BigInteger, primary_key=True, autoincrement=True)
    uid = Column(Integer)
    server = Column(Integer)
    tag = Column(String)
    before_value = Column(Integer)
    after_Value = Column(Integer)
    value = Column(Integer)
    before_code = Column(Integer)
    after_code = Column(Integer)
    created = Column(DateTime)


class LogLogin(Base):
    __tablename__ = "log_login"
    
    seq = Column(Integer, primary_key=True, autoincrement=True)
    log_date = Column(Integer)
    uid = Column(Integer)
    path = Column(String, default='')
    platform = Column(String)
    device_id = Column(String)
    auth_id = Column(String, default=None)
    auth_platform = Column(String, default=None)
    version = Column(String, default=None)
    status = Column(Integer, default=0)
    hash_key = Column(String, default='')
    created = Column(DateTime)


class LogUserAttr(Base):
    __tablename__ = "log_user_attr"
    
    uid = Column(Integer, primary_key=True)
    level = Column(Integer, default=0)
    coin = Column(Integer, default=0)
    jewel = Column(Integer, default=0)
    stone = Column(Integer, default=0)
    acc_get_jewel = Column(Integer, default=0)
    acc_use_jewel = Column(Integer, default=0)


class LogUserAttrHistory(Base):
    __tablename__ = "log_user_attr_history"
    
    seq = Column(BigInteger, primary_key=True, autoincrement=True)
    log_date = Column(Integer)
    log_hour = Column(Integer)
    uid = Column(Integer)
    level = Column(Integer, primary_key=True, default=0)
    coin = Column(Integer, default=0)
    jewel = Column(Integer, default=0)
    stone = Column(Integer, default=0)
    at_level = Column(Integer, default=0)
    at_coin = Column(Integer, default=0)
    at_jewel = Column(Integer, default=0)
    at_stone = Column(Integer, default=0)
    acc_get_jewel = Column(Integer, default=0)
    created = Column(DateTime)


class LogUserData(Base):
    __tablename__ = "log_user_data"
    
    uid = Column(BigInteger, primary_key=True)
    category = Column(String, primary_key=True)
    data = Column(String, default=None)
    after_length = Column(Integer, default=0)
    before_length = Column(Integer, default=0)
    
    
    
class NetworkRecoder(Base):
    __tablename__ = "network_records"
    
    uid = Column(BigInteger, primary_key=True)
    url = Column(String, )
    req_origin = Column(String, default=None)
    status = Column(BigInteger, )
    res_data = Column(Integer, default=None)
    res_final = Column(Integer, default=None)
    latency = Column(BigInteger)
    created = Column(DateTime)
    
    