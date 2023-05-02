from sqlalchemy import Column, String, Integer, BigInteger
from sqlalchemy.orm import relationship
from app.db.session import Base

class DummyDataBattle(Base):
    __tablename__ = "dummy_data_battle"
    
    uid = Column(Integer, primary_key=True, nullable=False)
    battle_point = Column(Integer, nullable=False, default=0)
    data = Column(String, default=None)
