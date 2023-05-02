import json
from typing import Optional
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.params.ResParam import ResponseCode, get_response

notice_router = APIRouter(prefix='/notice')

@notice_router.get("", response_class=JSONResponse)
async def getAllnoticeByLanguage(req:Request, db:Session = Depends(get_db)):
    language = str(req.query_params.get('language', default='KR'))
    
    sql = f"SELECT id, title, content, image FROM notice WHERE language = '{language}' order by id desc"
    query = db.execute(sql)
    result = query.fetchall()
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=result, uid=req.uid)