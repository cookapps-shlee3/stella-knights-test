import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config.settings import conf

logging.basicConfig()
logging.getLogger('sqlalchemy.pool').setLevel(logging.DEBUG)


# SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

SQLALCHEMY_DATABASE_URL = conf().DATABASE_URL
print('---------------DB_URL_DEV_TEST-------------- : ', SQLALCHEMY_DATABASE_URL)
ENVIRONMENT = os.environ.get('PRODUCTION')

# if ENVIRONMENT == 'prod':
#     engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_recycle=(3600 * 7), pool_size=10, max_overflow=20, echo=False, echo_pool=True, pool_pre_ping=True)
# else:
#     engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_recycle=(3600 * 7), pool_size=3, max_overflow=5, echo=False, echo_pool=True, pool_pre_ping=True)
    # engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_recycle=(3600 * 7), pool_size=5, max_overflow=10, pool_pre_ping=True)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
                    #    pool_recycle=(3600 * 7), pool_size=3, max_overflow=5, echo=False, echo_pool=True, pool_pre_ping=True)

# @event.listens_for(engine, "connect")ㄹ
# def connect(dbapi_connection, connection_record):
#     connection_record.info['pid'] = os.getpid()

# @event.listens_for(engine, "checkout")
# def checkout(dbapi_connection, connection_record, connection_proxy):
#     pid = os.getpid()
#     if connection_record.info['pid'] != pid:
#         connection_record.connection = connection_proxy.connection = None
#         raise exc.DisconnectionError(
#                 "Connection record belongs to pid %s, "
#                 "attempting to check out in pid %s" %
#                 (connection_record.info['pid'], pid)
#         )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()