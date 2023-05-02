from sqlalchemy import Column, String, Integer, BigInteger, DateTime, JSON
from app.db.session import Base

class UserCurrency_1(Base):
    __tablename__ = "user_currency_1"
    
    uid = Column(Integer, primary_key=True)
    type = Column(String, primary_key=True)
    amount = Column(BigInteger, default=0)
    daily_get = Column(BigInteger, default=0)
    daily_use = Column(BigInteger, default=0)
    total_get = Column(BigInteger, default=0)
    total_use = Column(BigInteger, default=0)
    updated = Column(DateTime, default=None)
    created = Column(DateTime, default=None)
    
    def getdict(self):
        return {"type":self.type, "value":self.amount}
    
    
    
class UserCurrency_2(Base):
    __tablename__ = "user_currency_2"
    
    uid = Column(Integer, primary_key=True)
    type = Column(String, primary_key=True)
    amount = Column(BigInteger, default=0)
    daily_get = Column(BigInteger, default=0)
    daily_use = Column(BigInteger, default=0)
    total_get = Column(BigInteger, default=0)
    total_use = Column(BigInteger, default=0)
    updated = Column(DateTime, default=None)
    created = Column(DateTime, default=None)
    
    def getdict(self):
        return {"type":self.type, "value":self.amount}
    
    
    
class UserCurrency_3(Base):
    __tablename__ = "user_currency_3"
    
    uid = Column(Integer, primary_key=True)
    type = Column(String, primary_key=True)
    amount = Column(BigInteger, default=0)
    daily_get = Column(BigInteger, default=0)
    daily_use = Column(BigInteger, default=0)
    total_get = Column(BigInteger, default=0)
    total_use = Column(BigInteger, default=0)
    updated = Column(DateTime, default=None)
    created = Column(DateTime, default=None)
    
    def getdict(self):
        return {"type":self.type, "value":self.amount}
    
    
    
class UserCurrency_4(Base):
    __tablename__ = "user_currency_4"
    
    uid = Column(Integer, primary_key=True)
    type = Column(String, primary_key=True)
    amount = Column(BigInteger, default=0)
    daily_get = Column(BigInteger, default=0)
    daily_use = Column(BigInteger, default=0)
    total_get = Column(BigInteger, default=0)
    total_use = Column(BigInteger, default=0)
    updated = Column(DateTime, default=None)
    created = Column(DateTime, default=None)
    
    def getdict(self):
        return {"type":self.type, "value":self.amount}
    
    
    
class UserCurrency_5(Base):
    __tablename__ = "user_currency_5"
    
    uid = Column(Integer, primary_key=True)
    type = Column(String, primary_key=True)
    amount = Column(BigInteger, default=0)
    daily_get = Column(BigInteger, default=0)
    daily_use = Column(BigInteger, default=0)
    total_get = Column(BigInteger, default=0)
    total_use = Column(BigInteger, default=0)
    updated = Column(DateTime, default=None)
    created = Column(DateTime, default=None)
    
    def getdict(self):
        return {"type":self.type, "value":self.amount}
    
    
    
class UserCurrency_6(Base):
    __tablename__ = "user_currency_6"
    
    uid = Column(Integer, primary_key=True)
    type = Column(String, primary_key=True)
    amount = Column(BigInteger, default=0)
    daily_get = Column(BigInteger, default=0)
    daily_use = Column(BigInteger, default=0)
    total_get = Column(BigInteger, default=0)
    total_use = Column(BigInteger, default=0)
    updated = Column(DateTime, default=None)
    created = Column(DateTime, default=None)
    
    def getdict(self):
        return {"type":self.type, "value":self.amount}
    
    
    
class UserCurrency_7(Base):
    __tablename__ = "user_currency_7"
    
    uid = Column(Integer, primary_key=True)
    type = Column(String, primary_key=True)
    amount = Column(BigInteger, default=0)
    daily_get = Column(BigInteger, default=0)
    daily_use = Column(BigInteger, default=0)
    total_get = Column(BigInteger, default=0)
    total_use = Column(BigInteger, default=0)
    updated = Column(DateTime, default=None)
    created = Column(DateTime, default=None)
    
    def getdict(self):
        return {"type":self.type, "value":self.amount}
    
    
    
class UserCurrency_8(Base):
    __tablename__ = "user_currency_8"
    
    uid = Column(Integer, primary_key=True)
    type = Column(String, primary_key=True)
    amount = Column(BigInteger, default=0)
    daily_get = Column(BigInteger, default=0)
    daily_use = Column(BigInteger, default=0)
    total_get = Column(BigInteger, default=0)
    total_use = Column(BigInteger, default=0)
    updated = Column(DateTime, default=None)
    created = Column(DateTime, default=None)
    
    def getdict(self):
        return {"type":self.type, "value":self.amount}
    
    
    
class UserCurrency_9(Base):
    __tablename__ = "user_currency_9"
    
    uid = Column(Integer, primary_key=True)
    type = Column(String, primary_key=True)
    amount = Column(BigInteger, default=0)
    daily_get = Column(BigInteger, default=0)
    daily_use = Column(BigInteger, default=0)
    total_get = Column(BigInteger, default=0)
    total_use = Column(BigInteger, default=0)
    updated = Column(DateTime, default=None)
    created = Column(DateTime, default=None)
    
    def getdict(self):
        return {"type":self.type, "value":self.amount}
    
    
    
class UserCurrency_0(Base):
    __tablename__ = "user_currency_0"
    
    uid = Column(Integer, primary_key=True)
    type = Column(String, primary_key=True)
    amount = Column(BigInteger, default=0)
    daily_get = Column(BigInteger, default=0)
    daily_use = Column(BigInteger, default=0)
    total_get = Column(BigInteger, default=0)
    total_use = Column(BigInteger, default=0)
    updated = Column(DateTime, default=None)
    created = Column(DateTime, default=None)
    
    def getdict(self):
        return {"type":self.type, "value":self.amount}
    