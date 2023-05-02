import json
import requests
from sqlalchemy.orm import Session
from app.crud import crud_payment
from app.config.settings import settings
from app.config.settings import Constant

def get_oauth_onestore():
    client_id = Constant.ONESTORE_BUNDLE_ID
    client_secret = Constant.ONESTORE_CLIENT_SECRET
    
    url = 'https://apis.onestore.co.kr/v6/oauth/token'
    header = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    str_param = 'client_id='+client_id+'&client_secret='+client_secret+'&grant_type=client_credentials'
    
    res = requests.post(url, params=str_param, headers=header)
    if res.status_code != 200:
        print("Status code is not 200")
        
    response = json.loads(res.text)
    return response['access_token']


def onestore_varify(db:Session, uid:int, id:int, product_id:str, purchase_token:str):
    complete = 0
    white_list = []
    if uid in white_list or (purchase_token.find('SANDBOX') == 0) or (crud_payment.is_exist_order_id(db, purchase_token)):
        complete = 3
        crud_payment.update_payment_complete(db, purchase_token, complete)
        return complete

    access_token = get_oauth_onestore()
    
    if access_token:
        if settings.ENVIRONMENT != 'prod':
            onestore_host = "https://sbpp.onestore.co.kr"
        else:
            onestore_host = "https://apis.onestore.co.kr"
            
        url = onestore_host+'/v6/apps/'+ Constant.ONESTORE_BUNDLE_ID +'/purchases/inapp/products/'+product_id+'/'+purchase_token
        header = {
            'Content-Type' : 'application/json',
            'Authorization' : 'Bearer '+ access_token
        }
        res = requests.get(url, headers=header)
        response = json.loads(res.text)
        if 'purchaseState' in response:
            if response['purchaseState'] == 0:
                complete = 1
                crud_payment.update_payment_complete_by_id(db, id, complete)
        else :
            complete = 0
    
    return complete

if __name__ == "__main__":
    get_oauth_onestore()