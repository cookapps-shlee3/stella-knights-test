from sqlalchemy import Column, String, Integer, DateTime

from sqlalchemy.orm import relationship
from app.db.session import Base
from sqlalchemy.dialects.mysql import MEDIUMTEXT

class HashManager(Base):
    __tablename__ = "hash_manager"
    
    version = Column(Integer, primary_key=True, nullable=False, default=0)
    hash_key = Column(MEDIUMTEXT, primary_key=True, nullable=False, default='')
    created = Column(DateTime, nullable=False)
