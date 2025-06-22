"""
Metrics module for monitoring and observability
"""

from .prometheus import (
    PrometheusMetrics,
    inc_counter,
    set_gauge,
    get_counter,
    get_gauge,
    register_counter,
    register_gauge,
)

# 创建全局实例
metrics_registry = PrometheusMetrics()

# 时间直方图装饰器
import time
from functools import wraps

def time_histogram(name: str):
    """装饰器：记录函数执行时间"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                # 记录到gauge中
                set_gauge(f"{name}_duration_seconds", duration)
                inc_counter(f"{name}_total")
        return wrapper
    return decorator

__all__ = [
    "PrometheusMetrics", 
    "metrics_registry", 
    "inc_counter", 
    "set_gauge", 
    "time_histogram",
    "get_counter",
    "get_gauge",
    "register_counter",
    "register_gauge",
]
