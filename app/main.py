# -*- coding: utf-8 -*-
import time
import traceback
from loguru import logger
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from app.routers import app_router
from starlette.exceptions import HTTPException
from app.middleware.middleware import ApplicationJsonMiddleware, LimitUploadSize
from app.config.settings import settings
from app.redis.redisCache import redis
from fastapi.responses import HTMLResponse


async def logging_dependency(request: Request):
    
    logger.debug(f"{request.method} {request.url}")
    logger.debug("Params:")
    for name, value in request.path_params.items():
        logger.debug(f"\t{name}: {value}")
    logger.debug("Headers:")
    for name, value in request.headers.items():
        logger.debug(f"\t{name}: {value}")
    logger.debug("Body:")
    body = await request.body()
    logger.debug(f"\t{body}")


async def response_exception(request, exc):
    return HTMLResponse(status_code = exc.status_code, content = f'{exc.status_code} ERROR')

exceptions = {
    404: response_exception,
}

## 여기에서 분기를 태워서 docs를 볼수 없도록 변경해야 함.
if settings.ENVIRONMENT == 'prod':
    app = FastAPI(docs_url=None, redoc_url=None, exception_handlers=exceptions)    
elif (settings.ENVIRONMENT == 'dev') or (settings.ENVIRONMENT == 'stage') or (settings.ENVIRONMENT == 'local'):
    print('-----local-0----------')
    app = FastAPI(openapi_prefix="/unknown-knight-idle", root_path="/unknown-knight-idle", exception_handlers=exceptions)
else:
    app = FastAPI(exception_handlers=exceptions)


app.include_router(app_router.router)
app.add_middleware(ApplicationJsonMiddleware)
app.add_middleware(LimitUploadSize, max_upload_size=50_000_000) # ~20MB


@app.get("/", response_class=PlainTextResponse)
async def main():
    return 'HI I AM HEALTHY 😄'
@app.post("/", response_class=PlainTextResponse)
async def main():
    return 'HI I AM HEALTHY 😄'

@app.exception_handler(HTTPException)
async def exception_hander(request:Request, exc:HTTPException):
    # print('********************************************************************************************************************************')
    # print('HTTPException Happen ' +  exc.__str__)
    traceback.print_exc()
    # print('********************************************************************************************************************************')
    return JSONResponse(status_code=200, content={
        'code':400,
        'msg': 'HTTPException',
        'data':None
    })

@app.exception_handler(AttributeError)
async def exception_hander(request:Request, exc:AttributeError):
    # print('********************************************************************************************************************************')
    print('AttributeError Happen ' + exc.__str__)
    # traceback.print_exc()
    # print('********************************************************************************************************************************')
    return JSONResponse(status_code=200, content={
        'code':400,
        'msg': 'AttributeError',
        'data':None
    })
    
@app.exception_handler(KeyError)
async def exception_hander(request:Request, exc:KeyError):
    # print('********************************************************************************************************************************')
    print('KeyError Happen ' + exc.__str__)
    # traceback.print_exc()
    # print('********************************************************************************************************************************')
    return JSONResponse(status_code=200, content={
        'code':400,
        'msg': 'KeyError',
        'data':None
    })


@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend(), prefix='fastapi-cache')
    await redis.init_redis(host=settings.REDIS_HOST+':'+str(settings.REDIS_PORT),password=None)
    
@app.on_event("shutdown")
async def shutdown():
    await redis.close()    
