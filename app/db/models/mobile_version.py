from sqlalchemy import Column, String, Integer
from app.db.session import Base

class MobileLanguageVersion(Base):
    __tablename__ = "mobile_language_version"
    
    platform = Column(String, primary_key=True, nullable=False)
    app_version = Column(Integer, nullable=False, default=0)
    spec_version = Column(Integer, nullable=False, default=0)
    

class MobileSpecVersion(Base):
    __tablename__ = "mobile_spec_version"
    
    platform = Column(String, primary_key=True, nullable=False)
    app_version = Column(Integer, nullable=False, default=0)
    spec_version = Column(Integer, nullable=False, default=0)
    
    
class MobileVersion(Base):
    __tablename__ = "mobile_version"
    
    device = Column(String, primary_key=True, nullable=False)
    max_version = Column(Integer, nullable=False, default=0)
    min_version = Column(Integer, nullable=False, default=0)
    force_update = Column(Integer, nullable=False, default=0)
    
    
class MobileSystemLanguageVersion(Base):
    __tablename__ = "mobile_system_language_version"
    
    platform = Column(String, primary_key=True, nullable=False)
    app_version = Column(Integer, nullable=False, default=0)
    spec_version = Column(Integer, nullable=False, default=0)
    
class MobileScenarioLanguageVersion(Base):
    __tablename__ = "mobile_scenario_language_version"
    
    platform = Column(String, primary_key=True, nullable=False)
    app_version = Column(Integer, nullable=False, default=0)
    spec_version = Column(Integer, nullable=False, default=0)

    
    
class MobileSpecDetailVersion(Base):
    __tablename__ = "mobile_spec_detail_version"
    
    platform = Column(String, primary_key=True, nullable=False)
    spec = Column(String, primary_key=True, nullable=False)
    upload = Column(Integer, nullable=False, default=0)
    publish = Column(Integer, nullable=False, default=0)
    enable = Column(Integer, nullable=False, default=1)
    app_version = Column(Integer, nullable=False, default=0)
    limit_version = Column(Integer, nullable=False, default=0)
    