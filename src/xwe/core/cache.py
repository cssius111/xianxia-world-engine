"""
简单的内存缓存实现
"""
from functools import lru_cache, wraps
from typing import Any, Dict, Optional
import time

class SimpleCache:
    """简单的TTL缓存"""
    
    def __init__(self, ttl: int = 300):
        self.ttl = ttl
        self._cache: Dict[str, tuple] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """设置缓存值"""
        self._cache[key] = (value, time.time())
    
    def clear(self):
        """清空缓存"""
        self._cache.clear()

# 全局缓存实例
_cache = SimpleCache()

def cached(ttl: int = 300):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 尝试从缓存获取
            result = _cache.get(cache_key)
            if result is not None:
                return result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            _cache.set(cache_key, result)
            return result
        
        return wrapper
    return decorator
