from datetime import datetime
import json
from app.config.settings import conf
import pika
from loguru import logger


async def send_new_user(uid:int, nickname:str, device_id:str, auth_id:str, platform:str, region:str):
    if conf().RABBITMQ_ENABLE:
        try:
            with pika.BlockingConnection(
                pika.URLParameters(conf().RABBITMQ_HOST)
            ) as connection:
                # connection.channel()
                channel = connection.channel()
                channel.basic_publish(exchange='user.created', routing_key='', body=json.dumps({
                    'uid': uid,
                    'device_id': device_id,
                    'auth_id' : auth_id,
                    'platform' : platform,
                    'nickname' : nickname,
                    'created': str(datetime.now()),
                    'region': region,
                    'pattern': 'user.created'
                }, default=str))
                # connection.close()
        except:
            logger.warning(f"")
        
    return uid


async def delete_user(uid:int):
    if conf().RABBITMQ_ENABLE:
        try:
            with pika.BlockingConnection(
                pika.URLParameters(conf().RABBITMQ_HOST)
            ) as connection:
                # connection.channel()
                channel = connection.channel()
                channel.basic_publish(exchange='user.deleted', routing_key='', body=json.dumps({
                    'uid': uid,
                    'pattern': 'user.deleted'
                }, default=str))
                # connection.close()
        except:
            logger.warning(f"")
        
    return uid



async def select_user_server(uid:int, server:int):
    if conf().RABBITMQ_ENABLE:
        try:
            with pika.BlockingConnection(
                pika.URLParameters(conf().RABBITMQ_HOST)
            ) as connection:
                # connection.channel()
                channel = connection.channel()
                channel.basic_publish(exchange='user.server_selected', routing_key='', body=json.dumps({
                    'uid': uid,
                    'server' : server,
                    'pattern': 'user.server_selected'
                }, default=str))
                # connection.close()
        except:
            logger.warning(f"")
        
    return uid



async def update_user_nickname(uid:int, nickname:str):
    if conf().RABBITMQ_ENABLE:
        try:
            with pika.BlockingConnection(
                pika.URLParameters(conf().RABBITMQ_HOST)
            ) as connection:
                # connection.channel()
                channel = connection.channel()
                channel.basic_publish(exchange='user.nickname_updated', routing_key='', body=json.dumps({
                    'uid': uid,
                    'nickname' : nickname,
                    'pattern': 'user.nickname_updated'
                }, default=str))
                # connection.close()
        except:
            logger.warning(f"")
        
    return uid



async def update_user_device(uid:int, device:str):
    if conf().RABBITMQ_ENABLE:
        try:
            with pika.BlockingConnection(
                pika.URLParameters(conf().RABBITMQ_HOST)
            ) as connection:
                # connection.channel()
                channel = connection.channel()
                channel.basic_publish(exchange='user.device_updated', routing_key='', body=json.dumps({
                    'uid': uid,
                    'device' : device,
                    'pattern': 'user.device_updated'
                }, default=str))
                # connection.close()
        except:
            logger.warning(f"")
        
    return uid