from dataclasses import dataclass
from os import path, environ

# conf().ENVIRONMENT == "dev":

base_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))


@dataclass
class Settings:
    ENVIRONMENT: str = environ.get("ENVIRONMENT", "local")
    PORT = 8001
    DEBUG: bool = False
    AES_KEY: str = environ.get("AES_KEY")
    DB_USERNAME : str = environ.get("DB_USERNAME")
    DB_PASSWORD : str = environ.get("DB_PASSWORD")
    DB_HOST : str = environ.get("DB_HOST")
    DB_PORT : str = environ.get("DB_PORT")
    DB_DATABASE : str = environ.get("DB_DATABASE")
    MONGO_URL: str = environ.get('MONGO_URL')
    MONGO_DATABASE: str = environ.get('MONGO_DATABASE')
    MONGO_COLLECTION: str = environ.get('MONGO_COLLECTION')
    REDIS_HOST : str = environ.get('REDIS_HOST')
    REDIS_PORT : str = environ.get('REDIS_PORT')
    REDIS_DATABASE : int = 0
    RABBITMQ_ENABLE : bool = False
    RABBITMQ_HOST : str = environ.get('RABBITMQ_HOST')
    LOCATION : str = environ.get('LOCATION')
    USE_PRE_DEST : bool = False
    PRE_DEST_VERSION : int = 1024
    PRE_DEST : str = environ.get('PRE_DEST')
    PRE_LANG_DEST : str = environ.get('PRE_LANG_DEST')
    PRE_SPEC_DEST : str = environ.get('PRE_SPEC_DEST')
    PRE_LANG_VER : int = 482
    PRE_SPEC_VER : int = 2708
    CURRENT_DEST : str = environ.get('CURRENT_DEST')
    CURRENT_LANG_DEST : str = environ.get('CURRENT_LANG_DEST')
    CURRENT_SPEC_DEST : str = environ.get('CURRENT_SPEC_DEST')
    DATABASE_URL = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}?charset=utf8"


@dataclass
class LocalConfig(Settings):
    DEBUG : bool = True
    RABBITMQ_ENABLEL: bool = True


@dataclass
class DevConfig(Settings):
    DEBUG : bool = True
    RABBITMQ_ENABLE: bool = False
    PRE_DEST_VERSION : int = 1004
    PRE_LANG_VER : int = 277
    PRE_SPEC_VER : int = 1931


@dataclass
class StageConfig(Settings):
    DEBUG : bool = True
    RABBITMQ_ENABLEL: bool = True
    USE_PRE_DEST : bool = True
    PRE_DEST_VERSION : int = 1023
    PRE_LANG_VER : int = 482
    PRE_SPEC_VER : int = 2707


@dataclass
class ProdConfig(Settings):
    RABBITMQ_ENABLE: bool = True


class Constant:
    PROJECT_NAME = 'unknown-knight-idle'
    
    AUTH_PLATFORM_GUEST = 'guest'
    AUTH_PLATFORM_GOOGLE = 'google'
    AUTH_PLATFORM_GAMECENTER = 'gamecenter'
    AUTH_PLATFORM_APPLE = 'apple'
    AUTH_PLATFORM_FACEBOOK = 'facebook'
    AUTH_PLATFORM_PG = 'pg'
    
    FRIENDS_MAX_COUNT = 20
    FRIENDS_MAX_GIFT_COUNT = 20
    
    CLIENT_STATUS_SKIP = 0
    CLIENT_STATUS_FORCE_UPDATE =  1
    CLIENT_STATUS_SELECT_UPDATE = 2
    CLIENT_STATUS_SERVER_CHECK = 3
    CLIENT_STATUS_ACCESS_DENIED = 5
    CLIENT_STATUS_INVALID_HASH = 6
    
    REDIS_RANKING_KEYS = PROJECT_NAME + '_ranking_keys'
    REDIS_RANKING_BLACKLIST = PROJECT_NAME + '_banned'
    REDIS_PVP_REVENGE_LIST = PROJECT_NAME + '_revenge'
    REDIS_DAILY_GROUP_KEY = PROJECT_NAME + '_ranking_DGR'
    REDIS_WEEKLY_RANKING_EXPIRED_SEC = (86400 * 14)
    REDIS_WEEKLY_RANKING_TOP_CNT = 99
    REDIS_DAILY_RANKING_EXPIRED_SEC = (86400 * 3)
    REDIS_DAILY_RANKING_TOP_CNT = 99
    REDIS_HALF_RANKING_EXPIRED_SEC = (86400 * 14 *  3)
    REDIS_HALF_RANKING_TOP_CNT = 99
    
    
    RANKING_MARGIN_NUMBER = 10000000000
    RANKING_SECTION_MAX = 100
    RANKING_PVP_DEFAULT_VALUE = 1000
    
    
    
    STAGE_MAX_STAR = 3
    
    COUNTRY_CODE = ['KR', 'EN', 'TW', 'CN', 'JP' ,'FR', 'DE', 'RU', 'ES', 'IT', 'PT', 'VN', 'ID', 'TH', 'TR']
    OS_PLATFORMS = ['ios', 'android', 'onestore']
    MYSQL_SIDE_DATA = ['User', 'Currency']
        
    INIT_BREAD_COUNT = 50
    INIT_PTICKET_COUNT = 5
    
    
    GAME_CONFIG_BREAD_PER_MIN = '20'
    GAME_CONFIG_PVP_WIN_PER_MEDAL = '21'
    GAME_CONFIG_PTICKET_PER_MIN = '22'
    GAME_CONFIG_NORMAL_PTICKET_MAX = '23'
    GAME_CONFIG_PASS_ENABLE_PTICKET_MAX = '24'
    
    GAME_CONFIG_GACHA_KNIGHT_HARD_PITY = '38'
    GAME_CONFIG_GACHA_WEAPON_HARD_PITY = '42'

    
    
    ONESTORE_BUNDLE_ID = 'com.cookapps.afkdungeon.onestore'
    ONESTORE_CLIENT_SECRET = '1FMe7oap+LeOwBUOXvndV4/51v/fmurdquh/rdCcmrw='
    ANDROID_BUNDLE_ID = 'com.cookapps.bm.unknownknight'
    IOS_BUNDLE_ID = 'com.cookapps.bm.unknownknight'
    
    VALUE_OF_1970 = 62135596800
    
    
    RESULT_VALID_RECEIPT = 1
    RESULT_VALID_REFUND = 2
    RESULT_INVALID_RECEIPT_CRON = 3      # Cron 영수증 검증 에서만 사용
    RESULT_VALID_SANDBOX = 4
    RESULT_INVALID_RECEIPT = 5
    RESULT_DUPLICATE = 6
    RESULT_BETA_PRODUCT = 7
    
    ## Cache Time
    
    VERSION_INFO_CACHE_TTL = 60
    SPEC_CACHE_INFO_TTL = 600
    CACHE_INFO_TTL = 300
    PVP_ROUND_CACHE_TTL = 600
    
    pass


def conf():
    config = dict(prod=ProdConfig, dev=DevConfig, local=LocalConfig)

    return config[environ.get("ENVIRONMENT", "local")]()
