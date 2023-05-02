import time
from loguru import logger
from enum import Enum
from pydantic import BaseModel
from typing import Optional

class BaseResParam(BaseModel):
    code:int=200
    msg:Optional[str]=''
    data:Optional[dict]=None
    ts:Optional[int]=0
    uid:Optional[int]=0


class ResponseCode(Enum):
    RES_SUCCESS = 200,
    RES_BAD_REQUEST = 400,
    RES_UNAUTHORIZED = 401,
    RES_AUTHORIZED_HEADER_NULL = 402,
    RES_HEADER_NULL = 403,
    RES_INVALID_AUTHORIZED_TOKEN = 404,
    RES_AUTHORIZED_EXPIRED = 405,
    RES_BODY_DECODE_FAIL = 406,
    RES_BATTLE_DATA_IS_NULL = 407,
    RES_AUTH_ID_IS_NULL = 408,
    RES_INTERNAL_SERVER_ERROR = 500,
    RES_DUPLICATED_NICKNAME = 10000,
    RES_INVALID_NICKNAME = 10001,
    RES_INVALID_PASSWORD = 10005,
    RES_INVALID_PARAMS = 20000,
    RES_INVALID_EXTRA_PARAMS = 20001,




    # 재화 관련 코드 추가.
    RES_INVALID_CURRENCY_TYPE = 20002,
    # 지원되지 않는 재화 타입입니다.
    RES_REWARD_TYPE_NOT_SUPPORT = 20003,
    # 재화가 충분하지 않음
    RES_CURRENCY_NOT_ENOUGH = 20004,
    # 재화량 변동없음
    RES_CURRENCY_NO_CHANGE = 20005,
    # 재화타입을 찾을수 없음
    RES_NOT_FOUND_CURRENCY_TYPE = 20006,
    # 사용자 데이터에서 확인이 불가능함.
    RES_NOT_FOUND_USER_DATA = 20007,
    # 사용자 데이터에서 스테이지 정보 확인이 불가능함.
    RES_NOT_FOUND_USER_STAGE_DATA = 20008,
    # 사용자 데이터에서 퀘스트 정보 확인이 불가능함.
    RES_NOT_FOUND_USER_QUEST_DATA = 20009,
    # 사용자 데이터에서 가이드 미션 정보 확인이 불가능함.
    RES_NOT_FOUND_USER_GUIDE_MISSION_DATA = 20010,
    # 사용자 데이터에서 캐릭터 정보 확인이 불가능함.
    RES_NOT_FOUND_USER_CHARACTER_DATA = 20011,
    # 사용자 데이터에서 캐릭터의 레벨 정보 확인이 불가능함.
    RES_NOT_FOUND_USER_CHARACTER_LEVEL_DATA = 20012,
    # 사용자 데이터에서 캐릭터의 경험치 정보를 찾을 수 없음.
    RES_NOT_FOUND_USER_CHARACTER_EXP_DATA = 20013,
    # 사용자 데이터에서 무기 정보 확인이 불가능함.
    RES_NOT_FOUND_USER_WEAPON_DATA = 20014,
    # 사용자 데이터에서 무기의 레벨 정보 확인이 불가능함.
    RES_NOT_FOUND_USER_WEAPON_ID_DATA = 20015,
    # 사용자 데이터에서 무기의 레벨 정보 확인이 불가능함.
    RES_NOT_FOUND_USER_HOMESHOP_DATA = 20016,
    
    
    
    



    
    RES_CURRENCY_NOT_FOUND_USE_TYPE = 20100,
    RES_CURRENCY_NOT_FOUND_GET_TYPE = 20101,
    RES_CURRENCY_NOT_FOUND_GETS_TYPE = 20102,
    RES_CURRENCY_NOT_FOUND_GAGHA_TYPE = 20103,
    RES_CURRENCY_NOT_FOUND_UPGRADE_TYPE = 20104,
    RES_CURRENCY_NOT_FOUND_SELL_TYPE = 20105,
    RES_CURRENCY_NOT_FOUND_SELLS_TYPE = 20106,
    RES_CURRENCY_NOT_FOUND_END_TYPE = 20107,
    RES_CURRENCY_NOT_FOUND_START_TYPE = 20108,

    
    
    # 퀘스트 정보를 찾을 수 없음
    RES_NOT_FOUND_QUEST_DATA = 21000,
    # 퀘스트 정보를 찾을 수 없음
    RES_NOT_FOUND_QUEST_INFO_DATA = 21001,
    # 이미 수령한 퀘스트 정보임.
    RES_ALREADY_REWARDED_QUEST = 21002,
    # 퀘스트에서 해당 id의 정보를 불러올 수 없음.
    RES_NOT_FOUND_QUEST_ID_DATA = 21003,
    
    
    
    # 가이드 미션 정보를 찾을 수 없음
    RES_NOT_FOUND_GUIDE_MISSION_DATA = 22000,
    # 가이드 미션 세부 정보를 찾을 수 없음
    RES_NOT_FOUND_GUIDE_MISSION_INFO_DATA = 22001,
    # 이미 수령한 가이드미션 정보.
    RES_ALREADY_REWARDED_GUIDE_MISSION = 22002,
    # 가이드 미션값이 현재 저장된 값과 다름
    RES_GUIDE_MISSION_ID_MISMATCH = 22003,
    
    
    
    # 챕터 정보를 찾을 수 없음
    RES_NOT_FOUND_CHAPTER_DATA = 23000,
    # 챕터 정보를 찾을 수 없음
    RES_NOT_FOUND_CHAPTER_INFO_DATA = 23001,
    # 이미 수령한 챕터 정보.
    RES_ALREADY_REWARDED_CHAPTER = 23002,
    # 데이터가 없는 상태에서 1 챕터값이 아닌 경우에 대한 에러처리
    RES_INVALID_CHAPTER = 23003,
    # 클라에서 올라온 데이터가 현재 state 값보다 작거나 같은 경우
    RES_STATE_INVALID_CHAPTER = 23004,
    #스테이지 정보를 찾을 수 없음
    RES_NOT_FOUND_STAGE_INFO_DATA = 23100,
    # 스테이지 세부 정보를 찾을 수 없음
    RES_NOT_FOUND_STAGE_DATA = 23101,
    #스테이지 타일 정보를 찾을수 없음
    RES_NOT_FOUND_STAGE_TILE_DATA = 23102,
    #스테이지 타일의 세부 정보를 찾을 수 없음.
    RES_NOT_FOUND_STAGE_TILE_INFO_DATA = 23103,
    #스테이지 타일의 typetype을 찾을 수 없음.
    RES_NOT_FOUND_STAGE_TILE_TYPE_DATA = 23104,
    # 이미 상자를 열어버린 상태임
    RES_ALREADY_OPEN_CHEST_BOX = 23105,
    # 별의 갯수값이 3을 넘었음
    RES_STAGE_STAR_INVALID_VALUE = 23106,
        
    
    
    # 레벨업 정보를 찾을 수 없음.
    RES_NOT_FOUND_LEVEL_UP_DATA = 24000,
    # 레벨업 정보를 찾을 수 없음.
    RES_NOT_FOUND_LEVEL_UP_INFO_DATA = 24001,
    # 레벨업 정보를 찾을 수 없음.
    RES_NOT_FOUND_LEVEL_UP_REWARD_DATA = 24002,
    # 이미 수령한 레벨업 정보
    RES_ALREADY_REWARDED_LEVEL_UP = 24003,
    # 최대 에너지 소유량이 없음
    RES_NOT_FOUND_MAX_ENERGY_VALUE = 24004,
    # 최대 에너지 소유량이 없음
    RES_ENERGY_VALUE_IS_MAX = 24005,
    # 레벨업 정보를 찾을 수 없음.
    RES_NOT_FOUND_LEVEL_MAX_BREAD_DATA = 24006,
    # 레벨업 정보를 찾을 수 없음.
    RES_NOT_FOUND_USER_BREAD_DATA = 24007,
    
    
    RES_NOT_FOUND_CHARACTER_INFO_DATA = 24050,
    RES_NOT_ENOUGH_CHARACTER_PIECE = 24051,
    # 캐릭터 레벨업 정보를 찾을 수 없음.
    RES_NOT_FOUND_CHARACTER_LEVEL_UP_DATA = 24100,
    # 캐릭터 레벨업 정보를 찾을 수 없음.
    RES_NOT_FOUND_CHARACTER_LEVEL_UP_INFO_DATA = 24101,
    # 캐릭터 레벨업 정보를 찾을 수 없음.
    RES_NOT_FOUND_CHARACTER_LEVEL_MISMATCH = 24102,
    # 캐릭터 레벨업 정보를 찾을 수 없음.
    RES_NOT_FOUND_CHARACTER_ENHANCE_DATA = 24110,
    # 캐릭터 레벨업 정보를 찾을 수 없음.
    RES_NOT_FOUND_CHARACTER_ENHANCE_INFO_DATA = 24111,
    # 캐릭터 레벨업 정보를 찾을 수 없음.
    RES_NOT_FOUND_CHARACTER_ENHANCE_MISMATCH = 24112,
    
    
    # 무기 레벨업 정보를 찾을 수 없음.
    RES_NOT_FOUND_WEAPON_LEVEL_UP_DATA = 24200,
    # 무기 레벨업 정보를 찾을 수 없음.
    RES_NOT_FOUND_WEAPON_LEVEL_UP_INFO_DATA = 24201,
    # 무기 레벨업 정보를 찾을 수 없음.
    RES_NOT_FOUND_WEAPON_LEVEL_MISMATCH = 24202,
    # 무기 레벨업 정보를 찾을 수 없음.
    RES_NOT_FOUND_WEAPON_DATA = 24300,
    # 무기 레벨업 정보를 찾을 수 없음.
    RES_NOT_FOUND_WEAPON_INFO_DATA = 24301,
    # 무기 레벨업 정보를 찾을 수 없음.
    RES_NOT_FOUND_WEAPON_ID_LENGTH_MISMATCH = 24302,
    # 무기 레벨업 정보를 찾을 수 없음.
    RES_NOT_FOUND_WEAPON_SELL_DATA = 24303,
    # 무기 레벨업 정보를 찾을 수 없음.
    RES_NOT_WEAPON_MAX_LEVEL = 24304,
    
    
    
    # 의뢰소 정보를 찾을 수 없음.
    RES_NOT_FOUND_REQUEST_DATA = 25000,
    # 이미 수령한 의뢰 정보
    RES_ALREADY_REWARDED_REQUEST = 25001,
    
    # 샵 정보를 찾을 수 없음.
    RES_NOT_FOUND_HOMESHOP_DATA = 26000,
    # 샵 세부 정보를 찾을 수 없음.
    RES_NOT_FOUND_HOMESHOP_CONTENT_DATA = 26001,
    # 이미 받은 상품임.
    RES_ALREADY_REWARDED_HOMESHOP = 26002,
    # 샵 정보를 찾을 수 없음.
    RES_NOT_FOUND_HOMESHOP_RANDOM_DATA = 26003,
    
    RES_NOT_FOUND_PVPSHOP_DATA = 26100,
    RES_ALREADY_REWARDED_PVPSHOP = 26101,
    RES_INVALUD_PVP_GAME_END = 26102,
    
    RES_NOT_FOUND_SHOP_DATA = 26200,
    RES_NOT_FOUND_SHOP_INFO_DATA = 26201,
    RES_ALREADY_REWARDED_SHOP = 26202,
    RES_INVALID_DAILY_BUY = 26203,
    RES_ALREADY_REWARDED_DAILY_BUY = 26204,
    RES_INVALID_WEEKLY_BUY = 26205,
    RES_ALREADY_REWARDED_WEEKLY_BUY = 26206,
    RES_INVALID_MONTHLY_BUY = 26207,
    RES_ALREADY_REWARDED_MONTHLY_BUY = 26208,
    RES_INVALID_SPECIAL_BUY = 26209,
    RES_ALREADY_REWARDED_SPECIAL_BUY = 26210,
    

    # 갱신 정보를 찾을 수 없음.
    RES_NOT_FOUND_COUNT_REFRESH_DATA = 27000,
    # 최종 소모 비용이 음수가 나왔음
    RES_NOT_FOUND_COUNT_REFRESH_SPEND_MINUS = 27001,
    # 빌딩 정보를 찾을 수 없음.
    RES_NOT_FOUND_BUILDING_DATA = 28000,
    RES_ALREADY_REWARDED_BUILDING = 28001,
    
    RES_NOT_FOUNG_GAME_START_COST = 28300,
    RES_USE_LIMIT_COUNT_SWEEP = 28301,
    RES_INVALID_GAME_START_PARAM = 28302,
    RES_USE_LIMIT_COUNT_SWEEP_IS_ZERO = 28303,
    
    #던전관련 정보
    RES_NOT_FOUND_DEFENSE_DUNGEON_DATA = 28500,
    RES_NOT_FOUND_DEFENSE_DUNGEON_INFO_DATA = 28501,
    
    RES_NOT_FOUND_STONE_DUNGEON_DATA = 28502,
    RES_NOT_FOUND_STONE_DUNGEON_INFO_DATA = 28503,
    
    RES_NOT_FOUND_MINE_DUNGEON_DATA = 28504,
    RES_NOT_FOUND_MINE_DUNGEON_INFO_DATA = 28505,
    
    
    # 상자 정보를 찾을 수 없음.
    RES_NOT_FOUND_CHEST_INFO_DATA = 29000,
    # 일반 상자 정보를 찾을 수 없음
    RES_NOT_FOUND_CHEST_DATA = 29001,
    # 일반 상자 정보를 찾을 수 없음
    RES_NOT_FOUND_CHEST_REWARD_DATA = 29002,
    # 어려움 난이도 상차 정보를 찾을 수 없음.
    RES_NOT_FOUND_HARD_CHEST_DATA = 29003,
    # 어려움 난이도 상차 정보를 찾을 수 없음.
    RES_NOT_FOUND_HARD_CHEST_REWARD_DATA = 29004,
    # max_count 값만큼을 전부 사용함.
    RES_CHEST_MAX_COUNT_IS_FULL = 29003,

    # 가차 비용 정보를 찾을 수 없음.
    RES_NOT_FOUND_GACHA_COST_DATA = 29100,
    # 가챠 타입을 찾을 수 없음.
    RES_NOT_FOUND_GACHA_COST_TYPE = 29101,
    
    # 캐릭터 가차 관련 정보를 찾을 수 없음.
    RES_NOT_FOUND_CHARACTER_PLATFORM_GACHA_DATA = 29200,
    # 캐릭터 가차 관련 정보를 찾을 수 없음.
    RES_NOT_FOUND_CHARACTER_GACHA_GRADE_PROB_DATA = 29201,
    # 캐릭터 가차 관련 정보를 찾을 수 없음.
    RES_NOT_FOUND_CHARACTER_GACHA_PROB_DATA = 29202,
    # 캐릭터 가차 관련 정보를 찾을 수 없음.
    RES_NOT_FOUND_CHARACTER_GACHA_RESULT = 29203,
    
    # 무기 가차 관련 정보를 찾을 수 없음.
    RES_NOT_FOUND_WEAPON_PLATFORM_GACHA_DATA = 29300,
    # 무기 가차 관련 정보를 찾을 수 없음.
    RES_NOT_FOUND_WEAPON_GACHA_GRADE_PROB_DATA = 29301,
    # 무기 가차 관련 정보를 찾을 수 없음.
    RES_NOT_FOUND_WEAPON_GACHA_PROB_DATA = 29302,
    # 무기 가차 관련 정보를 찾을 수 없음.
    RES_NOT_FOUND_WEAPON_GACHA_RESULT = 29303,
    
    
    # 빵이 이미 충분함.
    RES_ALREADY_ENOUGH_ENERGY = 29500,
    # 게임 config에서 값을 가지고 올 수 없음.
    RES_NOT_FOUND_GAME_CONFIG_DATA = 29501,
    # 게임 config에서 특정 위치의 값을 가지고 올 수 없음.
    RES_NOT_FOUND_GAME_CONFIG_VALUE = 29502,
    # DAILY RESET IS ALREADY FINISHED
    RES_ALREADY_DAILY_RESET_FINISHED = 29503,


    RES_STATE_INVALID_EXPEDITION = 29700,
    RES_NOT_FOUND_EXPEDITION_INFO_DATA = 29701,
    RES_NOT_FOUND_EXPEDITION_DATA = 29702,
    RES_NOT_FOUND_EXPEDITION_SHOP_DATA = 29703,
    RES_NOT_FOUND_EXPEDITION_INVALID_ID_DATA = 29704,
    RES_CAN_NOT_BUY_SHOP_ITEM = 29705,
    RES_EXPEDITION_INVALID_TYPE = 29706,
    RES_ALREADY_OPEN_EXPEDITION = 29707,
    RES_INVALID_EXPEDITION_TYPE = 29708,
    RES_NOT_FOUND_EXPEDITION_BATTLE_DATA = 29709,
    RES_NOT_FOUND_EXPEDITION_DIFFICULTY_DATA = 29710,
    RES_NOT_FOUND_EXPEDITION_CURRENT_DATA = 29711,
    
    
    
    
    
    
    RES_ALREADY_REWARDED = 30000,
    RES_INVALID_POST_ID = 30001,
    RES_EXPIRED_POST_ID = 30002,
    RES_ERR_WRITE_TERM = 40000,
    RES_ERR_ALREADY_DO_LIKE = 40001,
    RES_ERR_ALREADY_JOINED_CLAN =       50001,
    RES_ERR_DUPLICATED_CLAN_NAME =      50002,
    RES_ERR_CLAN_MEMBER_EXCEED =        50003,
    RES_ERR_REQUEST_ALREADY_SENDED =    50004,
    RES_ERR_CANNOT_LEAVE_CLAN =         50005,
    RES_ERR_CLAN_REQUEST_EXCEED =       50006,

    ## 쿠폰용 에러 메시지-코드
    RES_ERR_COUPON_NOT_EXIST = 60000,
    RES_ERR_COUPON_EXPIRED = 60001,
    RES_ERR_COUPON_ALREADY_REWARDED = 60002,
    RES_ERR_COUPON_NOT_AVAILABLE = 60003,
    RES_ALREADY_USER_REVIEWED = 60004,

    RES_DUPLICATED_DEVICE = 70000,
    RES_ERR_ABUSE_DETECTION = 90000,

    ## friends & NICKNAME
    RES_ALREADY_INVITE_FRIEND = 80000,         ## 대상 친구 요청에 내가 이미 있음.
    RES_ALREADY_INVITE_LIST =   80001,         ## 내요청 목록에 요청 상대가 이미 존재함
    RES_INVITE_FRIENDS_EXCEED = 80002,         ## 상대 요청 목록이 가득참.
    RES_TARGET_FRIENDS_EXCEED = 80003,         ## 요청 상대 친구 목록이 가득참.
    RES_MY_FRIENDS_EXCEED =     80004,         ## 내 친구 목록이 가득참.
    RES_INVALID_FRIEND =        80005,         ## 유효한 친구가 아님 (내친구 목록의 유가 아님)저
    RES_INVALID_GIFT_SEND =     80006,         ## 선물 보낼수 없음 (횟수 초과)
    RES_INVALID_MY_INFO =       80007,         ## 내 정보로 요청 불가
    RES_INVALID_REMAINING_TIME = 80008,        ## 친구 삭제등으로 (24시간기준) 재요청 기간이 존재함.
    RES_SEND_GIFT_COUNT_FULL = 80009,        ## 친구 선물보내기 횟수 만료(FRIENDS_MAX_GIFT_COUNT)

    ## RAID
    RES_INVALID_RAID_INFO =     90000,         ## 레이드 정보가 존재 하지 않음. 유효하지 않는 레이드.
    RES_RAID_HAS_ENDED =        90001,         ## 레이드 (성공/실패) 종료되었습니다.
    RES_INVALID_RAID_REWARD =   90002,         ## 레이드 보상 정보가 유효하지 않음.
    RES_ERR_RAID_ALREADY_REWARDED = 90003,     ## 이미 레이드 보상 받음.
    RES_ERR_RAID_PERMIT = 90004,               ## 공개에서 비공개로 변경할수 없음.
    RES_RAID_HAS_PERMIT = 90005,              ## 이미 공개상태임.
    
    def hasValue(self, code):
        for rspCode in ResponseCode:
            if code == rspCode:
                return True
        
        return False

def get_response(code:ResponseCode, msg:str='', data=None, uid=0):
    res = BaseResParam()
    res.code = code.value[0]
    if not msg:
        res.msg = code.name
    else:
        res.msg = msg
    
    if data:
        res.data = data
    
    if code != ResponseCode.RES_SUCCESS:
        logger.warning(code)
    res.uid = uid
    res.ts = int(time.time())
    
    return res