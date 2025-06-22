"""
Prometheus 监控指标
"""

from typing import Dict, Any, Optional
import time

class Counter:
    """计数器指标"""
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.value = 0
    
    def inc(self, amount: int = 1):
        self.value += amount
    
    def get(self) -> int:
        return self.value

class Gauge:
    """仪表指标"""
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.value = 0.0
    
    def set(self, value: float):
        self.value = value
    
    def inc(self, amount: float = 1.0):
        self.value += amount
    
    def dec(self, amount: float = 1.0):
        self.value -= amount
    
    def get(self) -> float:
        return self.value

class PrometheusMetrics:
    """Prometheus 指标管理器"""
    
    def __init__(self):
        self.counters = {}
        self.gauges = {}
        self.histograms = {}
        self.summaries = {}
    
    def register_counter(self, name: str, description: str = "") -> Counter:
        """注册计数器"""
        if name not in self.counters:
            self.counters[name] = Counter(name, description)
        return self.counters[name]
    
    def register_gauge(self, name: str, description: str = "") -> Gauge:
        """注册仪表"""
        if name not in self.gauges:
            self.gauges[name] = Gauge(name, description)
        return self.gauges[name]
    
    def get_metrics(self) -> dict:
        """获取所有指标"""
        return {
            "counters": {k: v.get() for k, v in self.counters.items()},
            "gauges": {k: v.get() for k, v in self.gauges.items()}
        }

# 全局指标管理器
_metrics = PrometheusMetrics()

def register_counter(name: str, description: str = "") -> Counter:
    """注册计数器（便捷函数）"""
    return _metrics.register_counter(name, description)

def register_gauge(name: str, description: str = "") -> Gauge:
    """注册仪表（便捷函数）"""
    return _metrics.register_gauge(name, description)

def inc_counter(name: str, amount: int = 1):
    """增加计数器值"""
    counter = _metrics.counters.get(name)
    if not counter:
        counter = register_counter(name)
    counter.inc(amount)

def set_gauge(name: str, value: float):
    """设置仪表值"""
    gauge = _metrics.gauges.get(name)
    if not gauge:
        gauge = register_gauge(name)
    gauge.set(value)

def get_counter(name: str) -> int:
    """获取计数器值"""
    counter = _metrics.counters.get(name)
    return counter.get() if counter else 0

def get_gauge(name: str) -> float:
    """获取仪表值"""
    gauge = _metrics.gauges.get(name)
    return gauge.get() if gauge else 0.0

__all__ = [
    "Counter", 
    "Gauge", 
    "PrometheusMetrics",
    "register_counter", 
    "register_gauge",
    "inc_counter",
    "set_gauge",
    "get_counter",
    "get_gauge"
]
