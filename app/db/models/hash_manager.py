from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base

class HashManager(Base):
    __tablename__ = "hash_manager"
    
    version = Column(Integer, primary_key=True, nullable=False, default=0)
    hash_key = Column(String, primary_key=True, nullable=False, default='')
    created = Column(DateTime, nullable=False)
