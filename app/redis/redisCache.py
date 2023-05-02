from typing import Optional
from aioredis import Redis, create_redis_pool

class RedisCache:
    def __init__(self):
        self._redis:Optional[Redis] = None
        
    async def init_redis(self, host:str, password:str):
        self._redis = await create_redis_pool(f"redis://{host}/0?encoding=utf-8", password=password)
    
    
    async def close(self):
        self._redis.close()
        await self._redis.wait_closed()
    
    
    async def get_redis_hash(self, key:str, member:str):
        return await self._redis.hget(key, member)

    async def set_redis_hash(self, key:str, member:str, value:str, expire:int=0):
        await self._redis.hset(key, member, value)
        if expire > 0:
            await self._redis.expire(key, expire)
   
    async def set_expire(self, key:str, expire:int=0):
        if expire > 0:
            await self._redis.expire(key, expire)
    
    
    async def set_rank_add(self, ranking_key:str, rank_score:int, member:int):
        await self._redis.zadd(ranking_key, rank_score, member)
        
        
    async def get_count(self, ranking_key:str, min=float('-inf'), max=float('inf')):
        return await self._redis.zcount(ranking_key, min, max)
    
    
    async def get_rank_range(self, ranking_key:str, start:int, stop:int, withscores:bool=False):
        return await self._redis.zrevrange(ranking_key, start, stop, withscores)
    
    
    async def get_rank(self, ranking_key:str, member:int):
        return await self._redis.zrevrank(ranking_key, member)
        
        
    async def get_hash(self, hash_key:str, field:int):
        return await self._redis.hget(hash_key, field)
    

    async def set_hash(self, hash_key:str, field:int, value:str):
        return await self._redis.hset(hash_key, field, value)
    
    
    async def get_multi_hash(self, hash_key:str, field, *fields):
        return await self._redis.hmget(hash_key, field, *fields)
    
    
    async def get_rank_score(self, ranking_key:str, member:int):
        return await self._redis.zscore(ranking_key, member)
    
    
    async def get_value(self, key:str):
        return await self._redis.get(key)
    
    
    async def set_value(self, key:str, value):
        return await self._redis.set(key, value)

redis = RedisCache()