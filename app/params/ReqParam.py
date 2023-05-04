from pydantic.main import BaseModel
from typing import Optional

class BaseReqParam(BaseModel):
    p:str = 'android'
    d:str = ''
    h:Optional[str] = ''
    v:int = 1003
    version:int = 0
    uid:Optional[int] = 0
    platform:Optional[str]=''
    device_id:Optional[str]=''
    
class AuthReqParam(BaseReqParam):
    auth_id:str=''
    auth_pw:str=''
    auth_platform:str=''
    
    
class ServerReqParam(BaseReqParam):
    server:int = 0
    
    
class DataSaveReqParam(BaseReqParam):
    platform:str=''
    device_id:str=''
    data_list:list=None
    

class NicknameSaveReqParam(BaseReqParam):
    nickname:str=''
    


class BattleInfosReqParam(BaseReqParam):
    uids:list=None

class BattleSaveReqParam(BaseReqParam):
    battle_point:int = 0
    data:dict=None



class CouponReqParam(BaseReqParam):
    code:str=''
    
class ConfigReqParam(BaseReqParam):
    filter:str=''
    
    
    
    
class FriendReqParam(BaseReqParam):
    target_uid:int=0
    
class FriendNickReqParam(BaseReqParam):
    nickname:str=''
    
    
    
class PostListReqParam(BaseReqParam):
    country:str='EN'
    
class PostRewardReqParam(BaseReqParam):
    post_id:int=0
    
class PostRewardsReqParam(BaseReqParam):
    country:Optional[str]='EN'
    post_ids:Optional[list]=None





class PvpSearchReqParam(BaseReqParam):
    key:str=''
    
class PvpScoreReqParam(PvpSearchReqParam):
    score:int=0
    target_uid:int=0
    is_win:int=0
    data:Optional[dict]=''

class WeeklyReqParam(BaseReqParam):
    key:str=''
    score:Optional[int]=0
    week:Optional[int]=0
    update:int=0
    data:Optional[dict]=''
    

class CustomWeeklyReqParam(BaseReqParam):
    key:str=''
    score:Optional[int]=0
    week:Optional[int]=0
    update:int=0
    day:int=0
    multiple:Optional[bool]=True
    data:Optional[dict]=''
    

class WeeklyInfoReqParam(BaseReqParam):
    key:Optional[str]=''
    week:Optional[int]=0

    
class CustomWeekReqParam(BaseReqParam):
    day:int=0
    
class WeeklySectionReqParam(BaseReqParam):
    key:str=''
    week:int=0
    multiple:bool=False
    section:int=0

class DailyReqParam(BaseReqParam):
    key:str=''
    score:Optional[int]=0
    update:Optional[int]=0
    data:Optional[dict]=''
    day:Optional[int]=0
    listing:Optional[int]=0
    


class PvpHalfSearchReqParam(BaseReqParam):
    key:str=''
    
class PvpHalfScoreReqParam(PvpHalfSearchReqParam):
    score:int=0
    target_uid:int=0
    is_win:int=0
    data:Optional[dict]=''
    is_revenge:Optional[bool]=False

class HalfReqParam(BaseReqParam):
    key:Optional[str]=''
    score:Optional[int]=0
    half:Optional[int]=0
    update:int=0
    data:Optional[dict]=''
    

class HalfInfoReqParam(BaseReqParam):
    key:Optional[str]=''
    half:Optional[int]=0


    
class BattleData(BaseModel):
    mode:Optional[int] = None
    oRank:Optional[int] = -1
    mTrophy:Optional[int] = -1
    crown:Optional[int] = -1
    oNick:Optional[str] = 'ERR'
    mDeck:Optional[str] = 'ERR'
    oDeck:Optional[str] = 'ERR'
    status:Optional[str] = None
    isAI:Optional[bool] = False
    isFriendly:Optional[bool] = False
    win:Optional[bool] = False
    
class BattleLogReqParam(BaseReqParam):
    data:BattleData = None


class PaymentReqParam(BaseReqParam):
    product_id:Optional[str] = ''
    order_id:Optional[str] = ''
    currency_price:Optional[str] = ''
    currency_code:Optional[str] = ''
    receipt:Optional[str]
    product_key:Optional[str] = ''
    is_send:Optional[bool]=False
    key:Optional[int]=0
    


class PaymentNotiReqParam(BaseModel):
    signedPayload:str = ''


class ForeverReqParam(BaseReqParam):
    key:str=''
    score:Optional[int]=0
    update:Optional[int]=0
    data:Optional[dict]=''



class ReviewReqParam(BaseReqParam):
    language:str=''
    purchased:int=0
    legend_count:int=0
    art_star:float=0
    fun_star:float=0
    balance_star:float=0