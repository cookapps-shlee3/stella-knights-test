from sqlalchemy import Column, DateTime, String, Integer
from app.db.session import Base

class PubCoupons(Base):
    __tablename__ = "pub_coupons"
    
    id = Column(Integer, primary_key=True, nullable=False)
    pub = Column(String, nullable=False)
    code = Column(String, nullable=False)
    type = Column(String, nullable=False)
    rewards = Column(String, nullable=False)
    issuer = Column(String)
    memo = Column(String)
    used = Column(Integer, nullable=False)
    enabled = Column(Integer, nullable=False)
    expired = Column(DateTime, nullable=False)
    created = Column(DateTime, nullable=False)
    