import os


class Settings:
    
    ENVIRONMENT = os.environ.get('PRODUCTION')
    
    PORT = 8001
    
    if ENVIRONMENT == 'prod':
        
        AES_KEY = 'BUnknown!@K3456M'
        
        DB_USERNAME : str = os.environ.get('DB_USERNAME_PROD')
        DB_PASSWORD = os.environ.get('DB_PASSWORD_PROD')
        DB_HOST : str = os.environ.get('DB_HOST_PROD')
        DB_PORT : str = os.environ.get('DB_PORT_PROD')
        DB_DATABASE : str = os.environ.get('DB_DATABASE_PROD')

        MONGO_URL = os.environ.get('MONGO_URL_PROD')
        MONGO_DATABASE= os.environ.get('MONGO_DATABASE_PROD')
        MONGO_COLLECTION = os.environ.get('MONGO_COLLECTION_PROD')

        REDIS_HOST : str = os.environ.get('REDIS_HOST_PROD')
        REDIS_PORT : str = os.environ.get('REDIS_PORT_PROD')
        REDIS_DATABASE : int = 0
        
        RABBITMQ_ENABLE : bool = True
        RABBITMQ_HOST : str = os.environ.get('RABBITMQ_PROD')
        
        # RABBITMQ_HOST = 'amqp://guest:guest@ec2-35-92-99-178.us-west-2.compute.amazonaws.com:5672'
        
        LOCATION : str = os.environ.get('LOCATION_CODE')

        USE_PRE_DEST:bool = False
        PRE_DEST_VERSION:int = 1024
        PRE_DEST:str = 'https://game.bm.py.cookapps.com/unknown-knight-idle/'
        PRE_LANG_DEST:str = 'https://ss-game.s3.ap-northeast-2.amazonaws.com/unknown-knight/dev/unknown-knight-{0}-{1}.json'
        PRE_SPEC_DEST:str = 'https://d19otl8pcfrvqp.cloudfront.net/unknown-knight/dev/unknown-knight-spec-{0}.json'
        PRE_LANG_VER:int = 482
        PRE_SPEC_VER:int = 2708
        
        
        CURRENT_DEST:str = 'https://unknown.bm.cookappsgames.com/'
        CURRENT_LANG_DEST:str = 'https://ss-game.s3.ap-northeast-2.amazonaws.com/unknown-knight/prod/unknown-knight-{0}-{1}.json'
        CURRENT_SPEC_DEST:str = 'https://d19otl8pcfrvqp.cloudfront.net/unknown-knight/prod/unknown-knight-spec-{0}.json'
        
    elif ENVIRONMENT == 'dev':
        
        AES_KEY = 'BUnknown!@K3456M'
        
        DB_USERNAME : str = "unknight_dev"
        DB_PASSWORD = "Unknown123$"
        DB_HOST : str = "playgrounds-dev-rds-cluster.cluster-czlr7v844fol.ap-northeast-2.rds.amazonaws.com"
        DB_PORT : str = "3306"
        DB_DATABASE : str = "unknown_knight_idle_dev"
        
        MONGO_URL = f"mongodb://burgermonster:BurgerMonster15$$@docdb-dev-bm.cluster-czlr7v844fol.ap-northeast-2.docdb.amazonaws.com:27017/?replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
        MONGO_DATABASE= 'log'
        MONGO_COLLECTION = 'log'
        # MONGO_URL = f"mongodb://burgermonster:BurgerMonster15$$@docdb-dev-bm.czlr7v844fol.ap-northeast-2.docdb.amazonaws.com:27017/?retryWrites=false"

        REDIS_HOST : str = "localhost"
        REDIS_PORT : int = 6379
        REDIS_DATABASE : int = 0
        
        RABBITMQ_ENABLE = False
        RABBITMQ_HOST = 'amqp://guest:guest@127.0.0.1:5672'
        
        LOCATION = 'GLOBAL'
        
        USE_PRE_DEST:bool = False
        PRE_DEST_VERSION:int = 1004
        PRE_DEST:str = 'https://game.bm.py.cookapps.com/unknown-knight-idle/'
        PRE_LANG_DEST:str = 'https://ss-game.s3.ap-northeast-2.amazonaws.com/unknown-knight/dev/unknown-knight-{0}-{1}.json'
        PRE_SPEC_DEST:str = 'https://d19otl8pcfrvqp.cloudfront.net/unknown-knight/dev/unknown-knight-spec-{0}.json'
        PRE_LANG_VER:int = 277
        PRE_SPEC_VER:int = 1931
        
        CURRENT_DEST:str = 'https://game.bm.py.cookapps.com/unknown-knight-idle/'
        CURRENT_LANG_DEST:str = 'https://ss-game.s3.ap-northeast-2.amazonaws.com/unknown-knight/dev/unknown-knight-{0}-{1}.json'
        CURRENT_SPEC_DEST:str = 'https://d19otl8pcfrvqp.cloudfront.net/unknown-knight/dev/unknown-knight-spec-{0}.json'
        
        
    elif ENVIRONMENT == 'stage':
        
        AES_KEY = 'BUnknown!@K3456M'
        
        DB_USERNAME : str = "user_stage"
        DB_PASSWORD = "StageUser123$"
        DB_HOST : str = "bm-staging-db-instance-1.czlr7v844fol.ap-northeast-2.rds.amazonaws.com"
        DB_PORT : str = "3306"
        DB_DATABASE : str = "unknown_knight_idle_stage"
        
        MONGO_URL = f"mongodb://burgermonster:BurgerMonster15$$@docdb-dev-bm.cluster-czlr7v844fol.ap-northeast-2.docdb.amazonaws.com:27017/?replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
        MONGO_DATABASE= 'afk-fortress-stage'
        MONGO_COLLECTION = 'user_save'
        # MONGO_URL = f"mongodb://burgermonster:BurgerMonster15$$@docdb-dev-bm.czlr7v844fol.ap-northeast-2.docdb.amazonaws.com:27017/?retryWrites=false"

        REDIS_HOST : str = "bm-py-test.vgui2q.ng.0001.apn2.cache.amazonaws.com"
        REDIS_PORT : int = 6379
        REDIS_DATABASE : int = 0
        
        RABBITMQ_ENABLE = True
        RABBITMQ_HOST = 'amqp://guest:guest@ec2-35-92-99-178.us-west-2.compute.amazonaws.com:5672'
        
        LOCATION = 'GLOBAL'
        
        USE_PRE_DEST:bool = True
        PRE_DEST_VERSION:int = 1023
        PRE_DEST:str = 'https://game.bm.py.cookapps.com/unknown-knight-idle/'
        PRE_LANG_DEST:str = 'https://ss-game.s3.ap-northeast-2.amazonaws.com/unknown-knight/dev/unknown-knight-{0}-{1}.json'
        PRE_SPEC_DEST:str = 'https://d19otl8pcfrvqp.cloudfront.net/unknown-knight/dev/unknown-knight-spec-{0}.json'
        PRE_LANG_VER:int = 482
        PRE_SPEC_VER:int = 2707

        CURRENT_DEST:str = 'https://game.bm.stage.cookapps.com/unknown-knight-idle/'
        CURRENT_LANG_DEST:str = 'https://ss-game.s3.ap-northeast-2.amazonaws.com/unknown-knight/stage/unknown-knight-{0}-{1}.json'
        CURRENT_SPEC_DEST:str = 'https://d19otl8pcfrvqp.cloudfront.net/unknown-knight/stage/unknown-knight-spec-{0}.json'

###########################################################################
    elif ENVIRONMENT == 'local':
        AES_KEY = 'BUnknown!@K3456M'
        
        DB_USERNAME : str = "root"
        DB_PASSWORD = "1q2w3e4r"
        DB_HOST : str = "172.22.0.2"
        DB_PORT : str = "3306"
        DB_DATABASE : str = "unknown_knight_idle_dev"
        
        MONGO_URL = f"mongodb://burgermonster:BurgerMonster15$$@docdb-dev-bm.cluster-czlr7v844fol.ap-northeast-2.docdb.amazonaws.com:27017/?replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
        MONGO_DATABASE= 'log'
        MONGO_COLLECTION = 'log'
        # MONGO_URL = f"mongodb://burgermonster:BurgerMonster15$$@docdb-dev-bm.czlr7v844fol.ap-northeast-2.docdb.amazonaws.com:27017/?retryWrites=false"

        REDIS_HOST : str = "localhost"
        REDIS_PORT : int = 6379
        REDIS_DATABASE : int = 0
        
        RABBITMQ_ENABLE = False
        RABBITMQ_HOST = 'amqp://guest:guest@127.0.0.1:5672'
        
        LOCATION = 'GLOBAL'
        
        USE_PRE_DEST:bool = False
        PRE_DEST_VERSION:int = 1004
        PRE_DEST:str = 'https://game.bm.py.cookapps.com/unknown-knight-idle/'
        PRE_LANG_DEST:str = 'https://ss-game.s3.ap-northeast-2.amazonaws.com/unknown-knight/dev/unknown-knight-{0}-{1}.json'
        PRE_SPEC_DEST:str = 'https://d19otl8pcfrvqp.cloudfront.net/unknown-knight/dev/unknown-knight-spec-{0}.json'
        PRE_LANG_VER:int = 277
        PRE_SPEC_VER:int = 1931
        
        CURRENT_DEST:str = 'https://game.bm.py.cookapps.com/unknown-knight-idle/'
        CURRENT_LANG_DEST:str = 'https://ss-game.s3.ap-northeast-2.amazonaws.com/unknown-knight/dev/unknown-knight-{0}-{1}.json'
        CURRENT_SPEC_DEST:str = 'https://d19otl8pcfrvqp.cloudfront.net/unknown-knight/dev/unknown-knight-spec-{0}.json'
 ###########################################################################


    else:
        
        AES_KEY = 'BUnknown!@K3456M'
        
        DB_USERNAME : str = "unknight_dev"
        DB_PASSWORD = "Unknown123$"
        DB_HOST : str = "playgrounds-dev-rds-cluster.cluster-czlr7v844fol.ap-northeast-2.rds.amazonaws.com"
        DB_PORT : str = "3306"
        DB_DATABASE : str = "unknown_knight_idle_dev"
        
        MONGO_URL = f"mongodb://mongodb:27017/?retryWrites=false"
        MONGO_DATABASE= 'afk-fortress'
        MONGO_COLLECTION = 'user_save'
        # MONGO_URL = f"mongodb://burgermonster:BurgerMonster15$$@docdb-dev-bm.cluster-czlr7v844fol.ap-northeast-2.docdb.amazonaws.com:27017/?replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"

        REDIS_HOST : str = "localhost"
        REDIS_PORT : int = 6379
        REDIS_DATABASE : int = 0
        
        RABBITMQ_ENABLE = True
        RABBITMQ_HOST = 'amqp://guest:guest@127.0.0.1:5672'
        
        LOCATION = 'GLOBAL'
        
        USE_PRE_DEST:bool = False
        PRE_DEST_VERSION:int = 1024
        PRE_DEST:str = 'https://game.bm.py.cookapps.com/unknown-knight-idle/'
        PRE_LANG_DEST:str = 'https://ss-game.s3.ap-northeast-2.amazonaws.com/unknown-knight/dev/unknown-knight-{0}-{1}.json'
        PRE_SPEC_DEST:str = 'https://d19otl8pcfrvqp.cloudfront.net/unknown-knight/dev/unknown-knight-spec-{0}.json'
        PRE_LANG_VER:int = 482
        PRE_SPEC_VER:int = 2708
        
        CURRENT_DEST:str = 'https://game.bm.py.cookapps.com/unknown-knight-idle/'
        CURRENT_LANG_DEST:str = 'https://ss-game.s3.ap-northeast-2.amazonaws.com/unknown-knight/dev/unknown-knight-{0}-{1}.json'
        CURRENT_SPEC_DEST:str = 'https://d19otl8pcfrvqp.cloudfront.net/unknown-knight/dev/unknown-knight-spec-{0}.json'
 
    DATABASE_URL = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}?charset=utf8"
    
        


   
    
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




settings = Settings()