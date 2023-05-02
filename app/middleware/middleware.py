import time
import json
import base64
from fastapi import HTTPException
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from loguru import logger
from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from starlette.responses import Response
from starlette import status
from app.db.connection import get_db
from app.util.util import get
from app.config.settings import settings
from datetime import datetime
from app.db.models.log import NetworkRecoder

excluded_path = [
    '/time',
    '/version',
    '/config',
    '/auth/server',
    '/auth/login/v2',
    '/users/refresh',
    '/users/nickname/save',
    '/users/lobby',
    '/users/data/save',
    '/currency/update',
]

class LimitUploadSize:

    def __init__(self, app: ASGIApp, max_upload_size: int) -> None:
        self.app = app
        self.max_upload_size = max_upload_size

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == 'http':
            if scope['method'] == 'POST':
                # scope 객체 구조가 바뀌는 브레이킹 체인지만 없다면..
                content_length = [data[1] for data in scope['headers'] if b'content-length' in data]

                if not content_length:
                    resp = Response(status_code=status.HTTP_411_LENGTH_REQUIRED)
                    await resp(scope, receive, send)
                    return

                if int(content_length[0]) > self.max_upload_size:
                    resp = Response(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
                    await resp(scope, receive, send)
                    return
                    
                await self.app(scope, receive, send)
                return

        await self.app(scope, receive, send)

class ApplicationJsonMiddleware:
    def __init__(
        self,
        app: ASGIApp
    ) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            responder = _ApplicationJsonResponder(
                self.app
            )
            await responder(scope, receive, send)
            return
        await self.app(scope, receive, send)


class _ApplicationJsonResponder:
    def __init__(
        self,
        app: ASGIApp
    ) -> None:
        self.app = app
        self.should_decode_from_json = False
        self.should_decode_from_AES_to_json = True
        self.should_send_json = True
        self.receive: Receive = unattached_receive
        self.send: Send = unattached_send
        self.initial_message: Message = {}
        self.start_message: Message = {}
        self.started = False
        self.time = 0
        self.path = ''
        self.strRequest = ''
        self.strResponse = ''
        self.uid = 0
        self.status = 0
        self.need_cipyer = False
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        headers = MutableHeaders(scope=scope)

        x = 'x-forwarded-for'.encode('utf-8')
        for header in headers.raw:
            if header[0] == x:
                if header[1].decode('utf-8').find(',') >= 0:
                    origin_ip, forward_ip = header[1].decode('utf-8').split(', ')
                    headers['origin_ip'] = origin_ip
                else:
                    origin_ip = header[1].decode('utf-8')
                    headers['origin_ip'] = origin_ip
                
        
        self.should_decode_from_json = (
            "application/json" in headers.get("Content-Type", "")
        )
        
        # Take an initial guess, although we eventually may not
        # be able to do the conversion.
        self.path = get(scope, 'path')
        self.receive = receive
        self.send = send
        self.time = int(time.time())
        # 여기서 시작 시간을 저장하도록 한다.

        if self.should_decode_from_json:
            headers["content-type"] = "application/json"
        await self.app(scope, self.receive_with_middleware, self.send_with_middleware)

    async def receive_with_middleware(self) -> Message:
        message = await self.receive()

        if (self.path == '/docs') or (self.path == '/openapi.json'):
            return message

        if not self.should_decode_from_AES_to_json:
            return message
        
        # 해당 요청이 왔을 경우에는 바로 반환하도록 수정함.
        if message["type"] == 'http.disconnect':
            return message
        
        assert message["type"] == "http.request"

        body = message["body"].decode('utf-8')
        more_body = message.get("more_body", False)


        while more_body:
            message = await self.receive()
            if message and message['body']:
                body = body + message['body'].decode('utf-8')
                
            more_body = message.get("more_body", False)
        
        if not body:
            return message
        
        
        obj = json.loads(body)
        k = get(obj, 'k')
        # 암호화 처리에 대한 부분을 여기서 진행하도록 한다.
        if k:
            # 암호화를 풀어서 스트링을 얻고 얻은 값을 obj에 넣어서 진행해 주도록 한다.
            decipyer = AES.new(settings.AES_KEY.encode("utf8"), AES.MODE_ECB)
            k = base64.b64decode(k)
            msg_dec = decipyer.decrypt(k)
            msg_dec = unpad(msg_dec, 16)
            obj = json.loads(msg_dec)
        else:
            if settings.ENVIRONMENT == 'prod':
                raise HTTPException(status_code=404)
            else:
                pass

            
        logger.warning(self.path + " = " + json.dumps(obj))
        version = get(obj, 'v')
        
        if (int(version) >= int(settings.PRE_DEST_VERSION)):
            self.need_cipyer = True
        
        if settings.ENVIRONMENT != 'prod':
            self.uid = get(obj, 'uid')
            if not self.uid:
                self.uid = 0
            message["body"] = bytes(json.dumps(obj), 'utf-8')
            if self.path != '/payment':
                self.strRequest = json.dumps(obj)
            else:
                self.strRequest = ''
        else:
            self.uid = get(obj, 'uid')
            self.strRequest = json.dumps(obj)
            message["body"] = bytes(json.dumps(obj), 'utf-8')
        
        return message

    async def send_with_middleware(self, message: Message) -> None:
        
        if (self.path == '/docs') or (self.path == '/openapi.json') :
            await self.send(message)
            return

        if message["type"] == "http.response.start":
            headers = Headers(raw=message["headers"])
            if headers["content-type"] != "application/json":
                self.should_send_json = False
                await self.send(message)
                return
            self.start_message = message
        elif message["type"] == "http.response.body":
            body = get(message, 'body')
            if not self.should_send_json:
                await self.send(message)
                return

            if body and (body != b'null'):
                logger.info("body = " + str(body))
                obj = json.loads(body)
                self.status = obj['code']
                if not self.status:
                    self.status = 0
                self.strResponse = json.dumps(obj, ensure_ascii = False)

                if self.need_cipyer or (self.path == '/time'):
                    cipyer = AES.new(settings.AES_KEY.encode("utf8"), AES.MODE_ECB)
                    msg_enc = pad(body, 16)
                    msg_enc = cipyer.encrypt(msg_enc)
                    k = base64.b64encode(msg_enc)
                    
                    message['body'] = k
                    
                    headers = MutableHeaders(raw=self.start_message["headers"])
                    headers.update({'content-length':str(len(k))})
                    
            await self.send(self.start_message)

            if settings.ENVIRONMENT != 'prod':
                try:
                    recoder = NetworkRecoder()
                    recoder.uid = self.uid
                    recoder.url = self.path
                    recoder.req_origin = self.strRequest
                    recoder.status = self.status
                    recoder.res_data = self.strResponse
                    recoder.res_final = None
                    recoder.latency = self.time - int(time.time())
                    recoder.created = datetime.now()
                    db = get_db().__next__()
                    db.connection()
                    db.add(recoder)
                    db.commit()
                finally:
                    db.close()

            await self.send(message)
        
        return 


async def unattached_receive() -> Message:
    raise RuntimeError("receive awaitable not set")  # pragma: no cover


async def unattached_send(message: Message) -> None:
    raise RuntimeError("send awaitable not set")  # pragma: no cover
