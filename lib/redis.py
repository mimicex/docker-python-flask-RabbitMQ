#!/usr/bin/env python3
import redis, json
from typing   import Any, Union
from decouple import config

class RedisClient:
    def __init__(self, host: str = '', port: int = 6379, password: str = '', db: int = 0):
        self.redis_client = redis.Redis(
            host=config('redisHost'),
            port=config('redisPort'),
            password=config('redisPwd'),
            db=db,
            decode_responses=True  # 自動將字節解碼為字符串
        )
    
    def set(self, key: str, value: Any, ex: int = None) -> bool:
        if not isinstance(value, (str, int, float, bool)):
            value = json.dumps(value)
        return self.redis_client.set(key, value, ex=ex)
    
    def get(self, key: str) -> Union[Any, None]:
        value = self.redis_client.get(key)
        if value is None:
            return None
        
        # 嘗試解析JSON
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    
    def delete(self, key: str) -> int:
        return self.redis_client.delete(key)
    
    def exists(self, key: str) -> bool:
        return bool(self.redis_client.exists(key))
    
    def ttl(self, key: str) -> int:
        return self.redis_client.ttl(key)