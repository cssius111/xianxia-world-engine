# xwe/core/optimizations/smart_cache.py

from typing import Any, Callable, Optional, Tuple, Dict
import time
from collections import defaultdict, OrderedDict
import pickle
import hashlib
import json

class SmartCache:
    """智能缓存系统"""
    
    def __init__(self, max_memory_mb: int = 100):
        self.cache = OrderedDict()
        self.access_patterns = defaultdict(lambda: {
            'count': 0,
            'last_access': 0,
            'computation_time': [],
            'memory_size': 0
        })
        self.max_memory = max_memory_mb * 1024 * 1024  # 转换为字节
        self.current_memory = 0
        
        # 机器学习预测器
        self.predictor = CachePredictor()
        
    def get_or_compute(self, 
                      key: str,
                      compute_func: Callable,
                      *args, **kwargs) -> Any:
        """获取缓存或计算"""
        
        # 检查缓存
        if key in self.cache:
            self._record_access(key, hit=True)
            # 移到最后（LRU）
            self.cache.move_to_end(key)
            return self.cache[key]['value']
            
        # 计算
        start_time = time.perf_counter()
        result = compute_func(*args, **kwargs)
        computation_time = time.perf_counter() - start_time
        
        # 决定是否缓存
        should_cache = self._should_cache(key, result, computation_time)
        
        if should_cache:
            self._add_to_cache(key, result, computation_time)
            
        self._record_access(key, hit=False, computation_time=computation_time)
        
        return result
        
    def _should_cache(self, key: str, value: Any, 
                     computation_time: float) -> bool:
        """决定是否应该缓存"""
        
        # 计算价值分数
        value_size = self._estimate_size(value)
        
        # 如果计算时间很短，不缓存
        if computation_time < 0.001:  # 1ms
            return False
            
        # 如果对象太大，不缓存
        if value_size > self.max_memory * 0.1:  # 超过10%的缓存空间
            return False
            
        # 使用机器学习预测未来访问概率
        access_probability = self.predictor.predict_access_probability(
            key,
            self.access_patterns[key],
            computation_time,
            value_size
        )
        
        # 计算缓存价值
        cache_value = (computation_time * access_probability) / (value_size / 1024 / 1024)  # MB
        
        # 动态阈值
        threshold = self._calculate_dynamic_threshold()
        
        return cache_value > threshold
        
    def _add_to_cache(self, key: str, value: Any, 
                     computation_time: float) -> None:
        """添加到缓存"""
        
        value_size = self._estimate_size(value)
        
        # 如果需要，先释放空间
        while self.current_memory + value_size > self.max_memory:
            if not self._evict_one():
                # 无法释放更多空间
                return
            
        # 添加到缓存
        self.cache[key] = {
            'value': value,
            'size': value_size,
            'computation_time': computation_time,
            'created_at': time.time(),
            'access_count': 0
        }
        
        self.current_memory += value_size
        
    def _evict_one(self) -> bool:
        """逐出一个缓存项"""
        
        if not self.cache:
            return False
            
        # 计算每个缓存项的价值
        eviction_scores = {}
        
        for key, cache_entry in self.cache.items():
            pattern = self.access_patterns[key]
            
            # LFU + LRU + 计算成本的混合策略
            age = time.time() - pattern['last_access']
            frequency = pattern['count']
            computation_cost = cache_entry['computation_time']
            size = cache_entry['size']
            
            # 价值越低越容易被逐出
            if age == 0:
                age = 0.1  # 避免除零
            score = (frequency * computation_cost) / (age * size)
            eviction_scores[key] = score
            
        # 逐出得分最低的
        victim_key = min(eviction_scores, key=eviction_scores.get)
        victim_size = self.cache[victim_key]['size']
        
        del self.cache[victim_key]
        self.current_memory -= victim_size
        
        return True
        
    def _record_access(self, key: str, hit: bool, 
                      computation_time: float = 0) -> None:
        """记录访问模式"""
        pattern = self.access_patterns[key]
        pattern['count'] += 1
        pattern['last_access'] = time.time()
        
        if computation_time > 0:
            pattern['computation_time'].append(computation_time)
            # 保持最近100次的计算时间
            if len(pattern['computation_time']) > 100:
                pattern['computation_time'] = pattern['computation_time'][-100:]
                
        if hit and key in self.cache:
            self.cache[key]['access_count'] += 1
            
    def _estimate_size(self, obj: Any) -> int:
        """估算对象大小"""
        try:
            # 尝试序列化来估算大小
            return len(pickle.dumps(obj))
        except:
            # 如果无法序列化，使用粗略估算
            if isinstance(obj, dict):
                return sum(self._estimate_size(k) + self._estimate_size(v) 
                          for k, v in obj.items())
            elif isinstance(obj, (list, tuple)):
                return sum(self._estimate_size(item) for item in obj)
            elif isinstance(obj, str):
                return len(obj.encode('utf-8'))
            elif isinstance(obj, (int, float)):
                return 8
            else:
                return 100  # 默认值
                
    def _calculate_dynamic_threshold(self) -> float:
        """计算动态阈值"""
        if not self.cache:
            return 0.1
            
        # 基于当前缓存利用率调整阈值
        utilization = self.current_memory / self.max_memory
        
        if utilization < 0.5:
            # 缓存空间充足，降低阈值
            return 0.05
        elif utilization < 0.8:
            # 缓存空间适中
            return 0.1
        else:
            # 缓存空间紧张，提高阈值
            return 0.2
            
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_hits = sum(1 for p in self.access_patterns.values() 
                        if p['count'] > 1 and p['last_access'] > 0)
        total_accesses = sum(p['count'] for p in self.access_patterns.values())
        
        hit_rate = total_hits / total_accesses if total_accesses > 0 else 0
        
        return {
            'cache_size': len(self.cache),
            'memory_usage_mb': self.current_memory / 1024 / 1024,
            'memory_utilization': self.current_memory / self.max_memory,
            'hit_rate': hit_rate,
            'total_accesses': total_accesses,
            'unique_keys': len(self.access_patterns)
        }
        
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.current_memory = 0
        
    def invalidate(self, key: str):
        """失效指定的缓存项"""
        if key in self.cache:
            self.current_memory -= self.cache[key]['size']
            del self.cache[key]
            
        
class CachePredictor:
    """缓存预测器"""
    
    def __init__(self):
        self.history_window = 1000
        self.access_history = []
        
    def predict_access_probability(self,
                                  key: str,
                                  pattern: Dict,
                                  computation_time: float,
                                  size: int) -> float:
        """预测未来访问概率"""
        
        # 简单的启发式预测
        # 实际应用中可以使用更复杂的ML模型
        
        # 基于历史访问频率
        if pattern['count'] == 0:
            base_probability = 0.1
        else:
            # 计算访问频率
            if pattern['last_access'] > 0:
                total_time = time.time() - (pattern['last_access'] - 
                                           pattern['count'] * 60)  # 假设平均间隔
            else:
                total_time = 3600  # 默认1小时
                
            frequency = pattern['count'] / max(total_time, 1)
            base_probability = min(frequency * 3600, 1.0)  # 转换为每小时
            
        # 基于计算成本的调整
        cost_factor = min(computation_time / 0.1, 2.0)  # 0.1秒作为基准
        
        # 基于大小的惩罚
        size_penalty = 1.0 / (1 + size / 1024 / 1024)  # MB
        
        # 时间衰减
        if pattern['last_access'] > 0:
            time_decay = 1.0 / (1 + (time.time() - pattern['last_access']) / 3600)
        else:
            time_decay = 0.5
            
        return base_probability * cost_factor * size_penalty * time_decay
        
    def update_history(self, key: str, accessed: bool):
        """更新访问历史"""
        self.access_history.append({
            'key': key,
            'accessed': accessed,
            'timestamp': time.time()
        })
        
        # 保持窗口大小
        if len(self.access_history) > self.history_window:
            self.access_history = self.access_history[-self.history_window:]


class CacheableFunction:
    """可缓存函数装饰器"""
    
    def __init__(self, cache: SmartCache, key_func: Optional[Callable] = None):
        self.cache = cache
        self.key_func = key_func or self._default_key_func
        
    def __call__(self, func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = self.key_func(func.__name__, *args, **kwargs)
            
            # 使用缓存
            return self.cache.get_or_compute(
                cache_key,
                func,
                *args,
                **kwargs
            )
            
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.cache_stats = lambda: self.cache.get_stats()
        wrapper.clear_cache = lambda: self.cache.clear()
        
        return wrapper
        
    def _default_key_func(self, func_name: str, *args, **kwargs) -> str:
        """默认的缓存键生成函数"""
        # 将参数转换为可哈希的形式
        key_parts = [func_name]
        
        # 处理位置参数
        for arg in args:
            if isinstance(arg, (str, int, float, bool, type(None))):
                key_parts.append(str(arg))
            elif isinstance(arg, (list, tuple)):
                key_parts.append(json.dumps(arg, sort_keys=True))
            elif isinstance(arg, dict):
                key_parts.append(json.dumps(arg, sort_keys=True))
            else:
                # 对于复杂对象，使用其哈希值
                key_parts.append(str(hash(str(arg))))
                
        # 处理关键字参数
        if kwargs:
            key_parts.append(json.dumps(kwargs, sort_keys=True))
            
        # 生成最终的键
        key_string = '|'.join(key_parts)
        
        # 如果键太长，使用哈希值
        if len(key_string) > 200:
            return hashlib.md5(key_string.encode()).hexdigest()
        else:
            return key_string
