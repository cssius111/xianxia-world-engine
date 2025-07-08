"""
Metrics module for monitoring and observability
"""

# 尝试导入新的 Prometheus 指标模块
try:
    from .prometheus_metrics import (
        MetricsCollector,
        get_metrics_collector,
        init_prometheus_app_metrics,
        # 导出指标对象，便于直接访问
        nlp_request_seconds,
        nlp_token_count,
        nlp_cache_hit_total,
        context_compression_total,
        context_memory_blocks_gauge,
        async_thread_pool_size,
        async_request_queue_size,
        nlp_error_total,
        command_execution_seconds,
        api_call_latency,
        game_instances_gauge,
        players_online_gauge,
        system_cpu_usage,
        system_memory_usage,
    )
    PROMETHEUS_METRICS_AVAILABLE = True
except ImportError:
    PROMETHEUS_METRICS_AVAILABLE = False

# 保留原有的简单指标系统（向后兼容）
try:
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
except ImportError:
    # 如果旧模块不存在，创建空对象
    class PrometheusMetrics:
        pass
    
    metrics_registry = None
    
    def inc_counter(*args, **kwargs):
        pass
    
    def set_gauge(*args, **kwargs):
        pass
    
    def get_counter(*args, **kwargs):
        return 0
    
    def get_gauge(*args, **kwargs):
        return 0
    
    def register_counter(*args, **kwargs):
        pass
    
    def register_gauge(*args, **kwargs):
        pass

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
                
                # 如果新的 Prometheus 指标可用，也记录到新系统
                if PROMETHEUS_METRICS_AVAILABLE:
                    try:
                        collector = get_metrics_collector()
                        if collector:
                            collector.record_command_execution(
                                command=name,
                                handler=func.__name__,
                                duration=duration
                            )
                    except:
                        pass
        return wrapper
    return decorator

# 导出列表
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

# 如果新的 Prometheus 指标可用，添加到导出列表
if PROMETHEUS_METRICS_AVAILABLE:
    __all__.extend([
        "MetricsCollector",
        "get_metrics_collector",
        "init_prometheus_app_metrics",
        "nlp_request_seconds",
        "nlp_token_count",
        "nlp_cache_hit_total",
        "context_compression_total",
        "context_memory_blocks_gauge",
        "async_thread_pool_size",
        "async_request_queue_size",
        "nlp_error_total",
        "command_execution_seconds",
        "api_call_latency",
        "game_instances_gauge",
        "players_online_gauge",
        "system_cpu_usage",
        "system_memory_usage",
    ])
