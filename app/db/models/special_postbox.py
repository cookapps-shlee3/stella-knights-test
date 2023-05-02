from sqlalchemy import Column, String, Integer, BigInteger, DateTime, null
from sqlalchemy.orm import relationship
from app.db.session import Base

class SpecialPostbox(Base):
    __tablename__ = "special_postbox"
    
    special_post_id = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    server = Column(Integer)
    title_code = Column(Integer, nullable=False, default=0)
    desc_code = Column(Integer, nullable=False)
    rewards = Column(String, nullable=False, default='')
    start_time = Column(Integer, nullable=False)
    expire_time = Column(Integer, nullable=False)
    created = Column(DateTime, nullable=False)
