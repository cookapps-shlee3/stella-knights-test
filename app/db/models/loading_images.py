from sqlalchemy import Column, String, Integer, DateTime
from app.db.session import Base

class LoadingImages(Base):
    __tablename__ = "loading_images"
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    url = Column(String, nullable=False)
    weight = Column(Integer, nullable=False, default='')
    enabled = Column(String, nullable=False)
    created = Column(DateTime, nullable=False)
