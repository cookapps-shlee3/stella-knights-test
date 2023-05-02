from sqlalchemy import BigInteger, Column, String, Integer, DateTime
from app.db.session import Base

class RetentionUV(Base):
    __tablename__ = "retention_uv"
    
    rdate_key = Column(Integer, nullable=False, primary_key=True)
    hour = Column(Integer, nullable=False)
    uid = Column(Integer, nullable=False, primary_key=True)
    social_id = Column(String, nullable=False, default='')
    platform = Column(String, nullable=False, default='')
    device_id = Column(String, nullable=False, default=None)
    ip = Column(String, nullable=False)
    rdate = Column(DateTime, nullable=False)
    
    
    
class RetentionTag(Base):
    __tablename__ = "retention_tag"
    
    seq = Column(BigInteger, primary_key=True, autoincrement=True)
    alias = Column(String, default='', nullable=False)
    retention_tag = Column(String, default='', nullable=False)
    uid = Column(Integer, nullable=False)
    rdate_key = Column(Integer, nullable=False)
    rdate = Column(DateTime, nullable=False)
    hour = Column(Integer, nullable=False)