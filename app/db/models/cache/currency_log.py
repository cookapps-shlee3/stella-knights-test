from sqlalchemy import Column, String, Integer, BigInteger, DateTime, JSON
from app.db.session import Base

class UserCurrencyLog_1(Base):
    __tablename__ = "user_currency_log_1"
    
    uid = Column(Integer, primary_key=True)
    type = Column(String, primary_key=True)
    amount = Column(Integer, default=0)
    daily_get = Column(Integer, default=0)
    daily_use = Column(Integer, default=0)
    total_get = Column(BigInteger, default=0)
    total_use = Column(BigInteger, default=0)
    date_key = Column(String, default=None)
    created = Column(DateTime, default=None)
    
    def getdict(self):
        return {"type":self.type, "value":self.amount}
    
    
    
class UserCurrencyLog_2(Base):
    __tablename__ = "user_currency_log_2"
    
    uid = Column(Integer, primary_key=True)
    type = Column(String, primary_key=True)
    amount = Column(Integer, default=0)
    daily_get = Column(Integer, default=0)
    daily_use = Column(Integer, default=0)
    total_get = Column(BigInteger, default=0)
    total_use = Column(BigInteger, default=0)
    date_key = Column(String, default=None)
    created = Column(DateTime, default=None)
    
    def getdict(self):
        return {"type":self.type, "value":self.amount}
    
    
    
class UserCurrencyLog_3(Base):
    __tablename__ = "user_currency_log_3"
    
    uid = Column(Integer, primary_key=True)
    type = Column(String, primary_key=True)
    amount = Column(Integer, default=0)
    daily_get = Column(Integer, default=0)
    daily_use = Column(Integer, default=0)
    total_get = Column(BigInteger, default=0)
    total_use = Column(BigInteger, default=0)
    date_key = Column(String, default=None)
    created = Column(DateTime, default=None)
    
    def getdict(self):
        return {"type":self.type, "value":self.amount}
    
    
    
class UserCurrencyLog_4(Base):
    __tablename__ = "user_currency_log_4"
    
    uid = Column(Integer, primary_key=True)
    type = Column(String, primary_key=True)
    amount = Column(Integer, default=0)
    daily_get = Column(Integer, default=0)
    daily_use = Column(Integer, default=0)
    total_get = Column(BigInteger, default=0)
    total_use = Column(BigInteger, default=0)
    date_key = Column(String, default=None)
    created = Column(DateTime, default=None)
    
    def getdict(self):
        return {"type":self.type, "value":self.amount}
    
    
    
class UserCurrencyLog_5(Base):
    __tablename__ = "user_currency_log_5"
    
    uid = Column(Integer, primary_key=True)
    type = Column(String, primary_key=True)
    amount = Column(Integer, default=0)
    daily_get = Column(Integer, default=0)
    daily_use = Column(Integer, default=0)
    total_get = Column(BigInteger, default=0)
    total_use = Column(BigInteger, default=0)
    date_key = Column(String, default=None)
    created = Column(DateTime, default=None)
    
    def getdict(self):
        return {"type":self.type, "value":self.amount}
    
    
    
class UserCurrencyLog_6(Base):
    __tablename__ = "user_currency_log_6"
    
    uid = Column(Integer, primary_key=True)
    type = Column(String, primary_key=True)
    amount = Column(Integer, default=0)
    daily_get = Column(Integer, default=0)
    daily_use = Column(Integer, default=0)
    total_get = Column(BigInteger, default=0)
    total_use = Column(BigInteger, default=0)
    date_key = Column(String, default=None)
    created = Column(DateTime, default=None)
    
    def getdict(self):
        return {"type":self.type, "value":self.amount}
    
    
    
class UserCurrencyLog_7(Base):
    __tablename__ = "user_currency_log_7"
    
    uid = Column(Integer, primary_key=True)
    type = Column(String, primary_key=True)
    amount = Column(Integer, default=0)
    daily_get = Column(Integer, default=0)
    daily_use = Column(Integer, default=0)
    total_get = Column(BigInteger, default=0)
    total_use = Column(BigInteger, default=0)
    date_key = Column(String, default=None)
    created = Column(DateTime, default=None)
    
    def getdict(self):
        return {"type":self.type, "value":self.amount}
    
    
    
class UserCurrencyLog_8(Base):
    __tablename__ = "user_currency_log_8"
    
    uid = Column(Integer, primary_key=True)
    type = Column(String, primary_key=True)
    amount = Column(Integer, default=0)
    daily_get = Column(Integer, default=0)
    daily_use = Column(Integer, default=0)
    total_get = Column(BigInteger, default=0)
    total_use = Column(BigInteger, default=0)
    date_key = Column(String, default=None)
    created = Column(DateTime, default=None)
    
    def getdict(self):
        return {"type":self.type, "value":self.amount}
    
    
    
class UserCurrencyLog_9(Base):
    __tablename__ = "user_currency_log_9"
    
    uid = Column(Integer, primary_key=True)
    type = Column(String, primary_key=True)
    amount = Column(Integer, default=0)
    daily_get = Column(Integer, default=0)
    daily_use = Column(Integer, default=0)
    total_get = Column(BigInteger, default=0)
    total_use = Column(BigInteger, default=0)
    date_key = Column(String, default=None)
    created = Column(DateTime, default=None)
    
    def getdict(self):
        return {"type":self.type, "value":self.amount}
    
    
    
class UserCurrencyLog_0(Base):
    __tablename__ = "user_currency_log_0"
    
    uid = Column(Integer, primary_key=True)
    type = Column(String, primary_key=True)
    amount = Column(Integer, default=0)
    daily_get = Column(Integer, default=0)
    daily_use = Column(Integer, default=0)
    total_get = Column(BigInteger, default=0)
    total_use = Column(BigInteger, default=0)
    date_key = Column(String, default=None)
    created = Column(DateTime, default=None)
    
    def getdict(self):
        return {"type":self.type, "value":self.amount}
    