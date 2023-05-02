from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.db.session import Base

class Config(Base):
    __tablename__ = "config"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)
    filter = Column(String, nullable=False)
    type = Column(String, nullable=False)
