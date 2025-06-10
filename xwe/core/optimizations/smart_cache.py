"""
智能缓存系统 - 简化版
"""
import time
import threading
from typing import Any, Optional, Dict
from collections import OrderedDict

class SmartCache:
    def __init__(self, max_size: int = 1000, ttl: float = 300.0):
        self.max_size = max_size
        self.ttl = ttl
        self._cache = OrderedDict()
        self._lock = threading.RLock()
        self.hit_count = 0
        self.miss_count = 0
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._cache:
                self.miss_count += 1
                return None
            
            entry = self._cache[key]
            timestamp, value = entry['timestamp'], entry['value']
            
            # 检查是否过期
            if time.time() - timestamp > self.ttl:
                del self._cache[key]
                self.miss_count += 1
                return None
            
            # 移动到末尾（LRU）
            self._cache.move_to_end(key)
            self.hit_count += 1
            return value
    
    def set(self, key: str, value: Any):
        with self._lock:
            # 如果达到最大大小，删除最旧的
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._cache.popitem(last=False)
            
            self._cache[key] = {
                'value': value,
                'timestamp': time.time()
            }
    
    @property
    def hit_rate(self) -> float:
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0
    
    def get_stats(self):
        return {
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': self.hit_rate,
            'cache_size': len(self._cache),
            'max_size': self.max_size
        }
    
    def clear(self):
        with self._lock:
            self._cache.clear()

# 全局缓存实例
_global_cache = SmartCache()

def get_global_cache():
    return _global_cache
