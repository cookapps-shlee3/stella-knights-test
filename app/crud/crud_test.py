import random
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from app.db.models.user import UserMembers, UserFriends


def _get_admin_nickname(country:str):
    nickname = 'Operator'
    if country == 'KR':
        nickname = '운영자'
    elif country == 'TW':
        nickname = '遊戲操作負責人'
    elif country == 'CN':
        nickname = '游戏操作负责人'
    elif country == 'JP':
        nickname = '運営者'
        
    return nickname
    


def get_list(db:Session, uid:int, country:str='EN'):
    # now = int(time.time())
    now = 1644796801
    sql = "SELECT t1.post_id, t1.sender_uid, t4.nickname as sender_nickname, t1.product_id, t1.product_key, t1.reward_type, "
    sql += "t1.reward_id, t2.desc as `title`, t3.desc as `desc`, t1.reward_id, t1.reward_count, t1.start_time, t1.expire_time "
    sql += "FROM user_postbox t1 LEFT JOIN user_members t4 ON t1.sender_uid = t4.uid "
    sql += "LEFT JOIN spec_postbox t2 ON t1.title_code = t2.code AND t2.category = 'TITLE' AND t2.country = '{}' "
    sql += "LEFT JOIN spec_postbox t3 ON t1.desc_code = t3.code AND t3.category = 'DESC' AND t3.country = '{}' "
    sql += "WHERE t1.uid = {} AND t1.is_rewarded = 0 AND t1.expire_time > {} AND t1.start_time <= {} ORDER BY t1.post_id DESC LIMIT 0, 30 "
    sql = sql.format(country, country, uid, now, now)
    a = db.execute(sql)
    result = a.fetchall()
        
    admin_nickname = _get_admin_nickname(country=country)
    
    value = []
    if result:
        for post in result:
            temp = dict(post)
            if not temp['sender_uid']:
                temp['sender_nickname'] = admin_nickname
            value.append(temp)
    
    return value


def rand_test(db:Session, uid:int):
    uid_list = [uid]
    user_member_info = db.query(UserMembers).filter(UserMembers.uid == uid).first()
    friends_list = db.query(UserFriends).filter(UserFriends.uid == uid).all()
    
    if friends_list and len(friends_list) > 0 :
        for friend in friends_list:
            uid_list.append(friend.friend_uid)
    
    my_level = user_member_info.level
    
    row_level = 1 if ((my_level - 10) < 0) else my_level - 10
    high_level = 200 if ((my_level + 10) > 200) else my_level + 10
    query = db.query(UserMembers).filter(UserMembers.uid.notin_(uid_list), UserMembers.server == user_member_info.server, UserMembers.level >= row_level, UserMembers.level <= high_level)
    row_count = int(query.count())
    random_list = query.offset(int(row_count*random.random())).limit(20).all()
    return random_list

def friends_list_invite(db:Session, uid:int):
    sql = "SELECT t2.uid, t2.level, t2.server, t2.nickname, UNIX_TIMESTAMP(t2.updated) as updated FROM user_friends_invite t1 LEFT JOIN user_members t2 "
    sql += "ON t1.friend_uid = t2.uid WHERE t1.uid = {}"
    sql = sql.format(uid)
    query = db.execute(sql)
    result = query.fetchall()
    value = []
    
    if result:
        for friend in result:
            value.append(dict(friend))
    
    return value