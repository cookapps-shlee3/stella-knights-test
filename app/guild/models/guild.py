from enum import unique
from sqlalchemy import BigInteger, Column, DateTime, String, Integer, VARCHAR
from app.db.session import Base

class GuildHelp(Base):
    __tablename__ = "guild_help"
    
    guild_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    uid = Column(Integer, unique=True, nullable=False)
    message_type = Column(Integer, unique=True, nullable=False)
    sender_uid = Column(Integer, unique=True, nullable=False)
    create_at = Column(DateTime, nullable=False)

    
class GuildInfo(Base):
    __tablename__ = "guild_info"
    
    guild_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Integer, nullable=True)
    logo = Column(Integer, nullable=False)
    type = Column(Integer, nullable=False)
    minimum_level = Column(Integer, nullable=False)
    user_count = Column(Integer, nullable=False)
    guild_score =Column(Integer, nullable=False)
    comment = Column(String, nullable=True)
    updated_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False)
    

class GuildJoinStatus(Base):
    __tablename__ = "guild_join_status"
    
    guild_id = Column(Integer, primary_key=True,unique=True, nullable=False)
    uid = Column(Integer, unique=True, nullable=False)
    status = Column(Integer, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    
class GuildMember(Base):
    __tablename__ = "guild_member"
    
    guild_id = Column(Integer, primary_key=True, nullable=False)
    uid = Column(Integer, primary_key=True, nullable=False)
    assist_count = Column(Integer, nullable=False)
    user_level = Column(Integer, nullable=False)
    
    
class GuildMessage(Base):
    __tablename__ = "guild_message"
    
    guild_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    uid = Column(Integer, unique=True, nullable=False)
    message_type = Column(Integer, unique=True, nullable=False)
    nickname = Column(Integer, nullable=False)
    request_count = Column(Integer, nullable=False)
    receive_count = Column(Integer, nullable=False)
    request_timestamp = Column(BigInteger, nullable=False)
    created_timestamp = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    
class UserMembers(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = "user_members"
    
    uid = Column(BigInteger, primary_key=True)
    server = Column(Integer, default=1)
    level = Column(Integer, default=1)
    nickname = Column(VARCHAR, default='')
    is_nickname = Column(Integer, default=0)
    login_device_id = Column(VARCHAR, default=None)
    is_terms_agree = Column(Integer, default=0)
    updated = Column(DateTime)
    created = Column(DateTime)