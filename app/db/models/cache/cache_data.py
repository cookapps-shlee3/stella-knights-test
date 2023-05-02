import time
from typing import Optional
from sqlalchemy import VARCHAR, Column, Float, String, Integer, BigInteger, DateTime
from app.db.session import Base


class PvpRoundInfo(Base):
    
    __tablename__ = "platform_pvp_round_info"
    
    id = Column(Integer, primary_key=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    updated = Column(DateTime)
    
    def setClassFromDict(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])
            

class CacheData(Base):
    
    __tablename__ = "platform_cache_data"
    
    platform = Column(String, primary_key=True, nullable=False, default='')
    sheet_key = Column(String)
    value = Column(String)
    updated = Column(DateTime)
    
    def setClassFromDict(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])