import os
from loguru import logger
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .auth_handler import parse




class JWTBearer(HTTPBearer):
    
    pass_url = ['/users/refresh', '/users/lobby']
    ENVIRONMENT = os.environ.get('PRODUCTION')
    
    def __init__(self, auto_error:bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
        
    async def __call__(self, request:Request):
        
        if self.ENVIRONMENT == 'local':
            return {}
        
        # logger.warning('request.url.path' + request.url.path)
        for url in self.pass_url:
            if request.url.path.find(url) >= 0:
                return {}
            
        # if request.url.path in self.pass_url:
        #     return {}
        credentials:HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        payload = None
        if credentials:
            if not credentials.scheme == 'Bearer':
                raise HTTPException(status_code=403, detail="Invalid authentication scheme")
            payload = self.varify_jwt(credentials.credentials)
            if not payload:
                raise HTTPException(status_code=403, detail="Invalid Token or expired token")
            return payload
        else :
            raise HTTPException(status_code=403, detail="Invalid authorization code")
    
    def varify_jwt(self, token:str) ->dict:
        try:
            payload = parse(token)
        except:
            payload = None
        
        
        return payload
    