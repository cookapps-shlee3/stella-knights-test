import json
from typing import Optional
from fastapi import APIRouter, Depends, Request
from loguru import logger
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.params.ReqParam import PaymentReqParam, PaymentNotiReqParam
from app.auth.auth_bearer import JWTBearer
from app.params.ResParam import ResponseCode, get_response
from app.apis import payment_apis


payment_router = APIRouter()


@payment_router.post("/payment")
async def payment(payReq:PaymentReqParam, req:Request, db:Session = Depends(get_db)):
    
    payReq.platform = payReq.platform if payReq.platform else payReq.p
    payReq.device_id = payReq.device_id if payReq.device_id else payReq.d
    
        
    if (not payReq.product_id) or (not payReq.order_id) or (payReq.currency_price == None) or (not payReq.currency_code) or (not payReq.receipt):
        return get_response(code=ResponseCode.RES_INVALID_PARAMS, uid=payReq.uid)
    
    data = await payment_apis.payment(payReq, db)
    
    return get_response(code=ResponseCode.RES_SUCCESS, data=data, uid=payReq.uid)



@payment_router.post("/noti")
async def noti(notiReq:PaymentNotiReqParam, req:Request, db:Session = Depends(get_db)):
    
    # payment값을 일차로 추출한다.
    # signed_payload = str(req.query_params.get('signedPayload'))
    signed_payload = notiReq.signedPayload
    
    if not signed_payload:
        logger.error("ios refund payload is null")
        return    
    
    payment_apis.noti(signed_payload, db)
    
    return 
    