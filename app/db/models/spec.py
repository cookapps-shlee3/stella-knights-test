from sqlalchemy import Column, Float, String, Integer, BigInteger, DateTime
from app.db.session import Base

class SpecChest(Base):
    __tablename__ = "spec_chest"
    
    seq = Column(Integer, primary_key=True, nullable=False)
    raid_type = Column(String, nullable=False, default='')
    set_id = Column(Integer, nullable=False)
    
    
class SpecPostbox(Base):
    __tablename__ = "spec_postbox"
    
    country = Column(String, primary_key=True, nullable=False)
    code = Column(Integer, primary_key=True, nullable=False)
    category = Column(String, nullable=False, default='')
    desc = Column(String, nullable=False)
    
    
class SpecRaid(Base):
    __tablename__ = "spec_raid"
    
    id = Column(Integer, primary_key=True, nullable=False)
    maxHp = Column(BigInteger, nullable=False)
    weight = Column(Float, nullable=False)
