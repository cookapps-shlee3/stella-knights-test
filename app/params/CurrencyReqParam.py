from .ReqParam import BaseReqParam
from typing import Optional


class CurrencyUpdateReqParam(BaseReqParam):
    data:Optional[list]=0


    
class CurrencyClearReqParam(BaseReqParam):
    level:int=0
    id:int=0
    extra_value:Optional[int]=0
    extra_value_2nd:Optional[int]=0
    # 가이드 미션 번호
    extra_value_3rd:Optional[int]=0
    
    
class CurrencySweepReqParam(BaseReqParam):
    level:int=0
    id:int=0
    extra_value:Optional[int]=0
    extra_value_2nd:Optional[int]=0
    
    
    
class CurrencyUserLevelReqParam(BaseReqParam):
    id:int=0
    
class CurrencyCharacterLevelReqParam(BaseReqParam):
    id:int=0
    extra_value:int = 0
    extra_value_2nd:int = 0
    
    
    
class CurrencyCharacterEnhanceReqParam(BaseReqParam):
    id:int=0
    
    
class CurrencyWeaponLevelReqParam(BaseReqParam):
    id:int=0
    extra_value:int = 0
    
    
    
class CurrencyWeaponSellReqParam(BaseReqParam):
    id:int=0
    
    
    
class CurrencyWeaponListSellReqParam(BaseReqParam):
    ids:list[int]=0

    
class CurrencyStartReqParam(BaseReqParam):
    type:str=''
    id:int=0
    extra_value:Optional[int]=0
    extra_value_2nd:Optional[int]=0
    
    
class CurrencyEndReqParam(BaseReqParam):
    level:int=0
    type:str=''
    id:int=0
    extra_value:Optional[int]=0
    extra_value_2nd:Optional[int]=0


class CurrencyClearListReqParam(BaseReqParam):
    ids:list[int]=None
    extra_value:Optional[int]=0
    extra_param:Optional[dict]=None
    
    
class CurrencyGetsReqParam(BaseReqParam):
    type:str=''
    ids:list[int]=None
    extra_value:Optional[int]=0
    extra_param:Optional[dict]=None
    

    
class GachaReqParam(BaseReqParam):
    id:int=0
    extra_value:Optional[int]=0
    extra_value_2nd:Optional[int]=0
    extra_param:Optional[dict]=None
    
    
class GachaRewardReqParam(BaseReqParam):
    type:str=0
    

    
class ExchangeItemReqParam(BaseReqParam):
    type:str=''
    extra_value:Optional[int]=0
    

    
class CurrencyHomeShopBuyReqParam(BaseReqParam):
    id:int=0
    extra_value:int=0


class CurrencyPvpShopBuyReqParam(BaseReqParam):
    index:int=0
    id:int=0


class CurrencyHomeShopRefreshReqParam(BaseReqParam):
    level:int=0
    
        
class CurrencyPvpShopRefreshReqParam(BaseReqParam):
    index:int=0

    
class CurrencyTrainingFinishReqParam(BaseReqParam):
    listuptype:int=0
    
    
class CurrencyBuildingBuyReqParam(BaseReqParam):
    id:int=0
    
    
class CurrencyBuildingUpgradeReqParam(BaseReqParam):
    building_id:str=''


class CurrencyEnergyRefreshReqParam(BaseReqParam):
    level:int=0
    
    
class CurrencyFreeReqParam(BaseReqParam):
    pid:str=''
    

class CurrencyPVPTicketRefreshReqParam(BaseReqParam):
    id:int=0    




############################################################################################################################################################
# Expidition
############################################################################################################################################################


#게임 종료시 호출 (추후 여기서 현재 캐릭터 정보들을 관리하는게 좋을듯...)
class ExpiditionEndReqParam(BaseReqParam):
    id:int=0
    characterData:Optional[dict]={}
    otherData:Optional[dict]={}
    
    
#소탕 호출시 (추후 여기서 현재 캐릭터 정보들을 관리하는게 좋을듯...)
class ExpiditionSweepReqParam(BaseReqParam):
    level:int=0
    type:str=''
    id:int=0
    data:Optional[dict]={}


# 카드가챠 호출시 (새로고침에도 적용예정)
# 카드에 대한 grade값을 받아서 처리하도록 수정이 필요함.
class CardGachaReqParam(BaseReqParam):
    # 이녀석을 grade로 사용하도록 하자.
    grade:int=4
    count:int=3
    position:Optional[list] = []
    
    
# 카드가챠 포기 (현재 뽑은 카드 목록을 받아서 환전해 주도록 한다.)
class CardGachaGiveupReqParam(BaseReqParam):
    ids:list=[]
    
    
# 카드가챠 포기 (현재 뽑은 카드 목록을 받아서 환전해 주도록 한다.)
class CardGachaSelectReqParam(BaseReqParam):
    ids:list=[]
    

# 원정대 상품 구매(추가로 랜덤 룬도 있음, 룬 로직이 포함되어야 함.)
# id는 인덱스로 잡고, extra_value는 상품에 대한 id로 결정하도록 하자
class ExpiditionShopBuyReqParam(BaseReqParam):
    index:int=0
    id:int=0
    
    
    
# 원정대 상품 갱신 (데이터에 정의된 시간값과 비교후 처리)    
# 리스트를 만들어서 어딘가에 저장을 해야 함.(시간 정보도 저장이 필요)
class ExpiditionShopRefreshReqParam(BaseReqParam):
    day:int=0
    
    
    
