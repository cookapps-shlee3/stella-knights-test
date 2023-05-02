class Config:
  APP_ID:int = 1                            # 앱 고유번호
  DEFAULT_MAX_GUILD_USER_COUNT:int =  50     # 길드에 가입할 수 있는 기본 최대 길드원 수
  SHOW_GUILD_LIST_COUNT:int =  50            # 가입 팀 리스트에서 보여질 팀 수
  GUILD_LEADER_LEVEL:int =  9                # 길드 리더 유저 레벨
  GUILD_COLEADER_LEVEL:int =  8              # 길드 공동 리더 유저 레벨
  GUILD_NORMAL_LEVEL:int =  1                # 길드 일반 유저 레벨
  MAX_COLEADER_COUNT:int =  3                # 공동 리더 최대 수
  DEFAULT_REQUEST_LIFE_COUNT:int =  5        # 길드에서 라이프 요청시, 받을 수 있는 기본 라이프 수
  MAX_FREE_LIFE_COUNT:int =  10              # 요청으로 받을 수 있는 최대 라이프 수
  LIFE_MESSAGE_COOL_TIME:int =  14400        # 라이프 요청 메시지 보낼 수 있는 쿨타임 (초)


config = Config()