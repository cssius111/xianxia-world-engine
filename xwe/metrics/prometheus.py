"""
Prometheus指标导出器
提供游戏性能监控和统计指标
"""

import time
import threading
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import json


class MetricType(Enum):
    """指标类型"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Metric:
    """指标定义"""
    name: str
    type: MetricType
    help: str
    labels: List[str] = field(default_factory=list)
    

class PrometheusMetrics:
    """Prometheus指标收集器"""
    
    # 标签基数限制
    MAX_LABEL_CARDINALITY = 1000  # 每个指标最多1000个标签组合
    
    def __init__(self) -> None:
        self._metrics: Dict[str, Metric] = {}
        self._values: Dict[str, float] = defaultdict(float)
        self._labels_values: Dict[str, Dict[tuple, float]] = defaultdict(lambda: defaultdict(float))
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.RLock()
        self._label_counts: Dict[str, int] = defaultdict(int)  # 跟踪标签基数
        
        # 注册核心指标
        self._register_core_metrics()
        
    def _register_core_metrics(self) -> None:
        """注册核心监控指标"""
        # HTTP请求指标
        self.register_histogram(
            "http_request_duration_seconds",
            "HTTP request latency in seconds",
            labels=["method", "path", "status"]
        )
        
        # 游戏事件指标（注意：不包含player_id避免基数爆炸）
        self.register_counter(
            "game_events_total",
            "Total number of game events",
            labels=["event_type", "category"]  # 只保留service级别标签
        )
        
        # 在线玩家数
        self.register_gauge(
            "active_players",
            "Number of active players"
        )
        
        # 系统性能指标
        self.register_gauge(
            "memory_usage_bytes",
            "Memory usage in bytes"
        )
        
        self.register_gauge(
            "cpu_usage_percent",
            "CPU usage percentage"
        )
        
        # API调用指标
        self.register_counter(
            "api_calls_total",
            "Total number of API calls",
            labels=["endpoint", "method"]
        )
        
        # 错误指标
        self.register_counter(
            "errors_total",
            "Total number of errors",
            labels=["error_type", "severity"]
        )
        
    def register_counter(self, name: str, help: str, labels: Optional[List[str]] = None) -> None:
        """注册计数器指标"""
        with self._lock:
            self._metrics[name] = Metric(
                name=name,
                type=MetricType.COUNTER,
                help=help,
                labels=labels or []
            )
            
    def register_gauge(self, name: str, help: str, labels: Optional[List[str]] = None) -> None:
        """注册仪表指标"""
        with self._lock:
            self._metrics[name] = Metric(
                name=name,
                type=MetricType.GAUGE,
                help=help,
                labels=labels or []
            )
            
    def register_histogram(self, name: str, help: str, labels: Optional[List[str]] = None) -> None:
        """注册直方图指标"""
        with self._lock:
            self._metrics[name] = Metric(
                name=name,
                type=MetricType.HISTOGRAM,
                help=help,
                labels=labels or []
            )
            
    def inc_counter(self, name: str, value: float = 1, labels: Optional[Dict[str, str]] = None) -> None:
        """增加计数器值"""
        with self._lock:
            if name not in self._metrics:
                raise ValueError(f"Metric {name} not registered")
                
            if self._metrics[name].type != MetricType.COUNTER:
                raise ValueError(f"Metric {name} is not a counter")
                
            if labels:
                label_values = tuple(labels.get(l, "") for l in self._metrics[name].labels)
                
                # 检查标签基数
                if label_values not in self._labels_values[name]:
                    if self._label_counts[name] >= self.MAX_LABEL_CARDINALITY:
                        # 超过基数限制，使用默认标签
                        label_values = tuple("overflow" for _ in self._metrics[name].labels)
                    else:
                        self._label_counts[name] += 1
                
                self._labels_values[name][label_values] += value
            else:
                self._values[name] += value
                
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """设置仪表值"""
        with self._lock:
            if name not in self._metrics:
                raise ValueError(f"Metric {name} not registered")
                
            if self._metrics[name].type != MetricType.GAUGE:
                raise ValueError(f"Metric {name} is not a gauge")
                
            if labels:
                label_values = tuple(labels.get(l, "") for l in self._metrics[name].labels)
                self._labels_values[name][label_values] = value
            else:
                self._values[name] = value
                
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """记录直方图观测值"""
        with self._lock:
            if name not in self._metrics:
                raise ValueError(f"Metric {name} not registered")
                
            if self._metrics[name].type != MetricType.HISTOGRAM:
                raise ValueError(f"Metric {name} is not a histogram")
                
            if labels:
                label_values = tuple(labels.get(l, "") for l in self._metrics[name].labels)
                key = f"{name}:{label_values}"
            else:
                key = name
                
            if key not in self._histograms:
                self._histograms[key] = []
            self._histograms[key].append(value)
            
    def time_histogram(self, name: str, labels: Optional[Dict[str, str]] = None) -> None:
        """计时器上下文管理器"""
        class Timer:
            def __init__(self, metrics, metric_name, metric_labels) -> None:
                self.metrics = metrics
                self.metric_name = metric_name
                self.metric_labels = metric_labels
                self.start_time = None
                
            def __enter__(self) -> Any:
                self.start_time = time.time()
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb) -> Any:
                duration = time.time() - self.start_time
                self.metrics.observe_histogram(self.metric_name, duration, self.metric_labels)
                
        return Timer(self, name, labels)
        
    def export_metrics(self) -> str:
        """导出Prometheus格式的指标"""
        lines = []
        
        with self._lock:
            for name, metric in self._metrics.items():
                # 添加HELP和TYPE
                lines.append(f"# HELP {name} {metric.help}")
                lines.append(f"# TYPE {name} {metric.type.value}")
                
                if metric.type in [MetricType.COUNTER, MetricType.GAUGE]:
                    # 导出简单值
                    if name in self._values:
                        lines.append(f"{name} {self._values[name]}")
                        
                    # 导出带标签的值
                    if name in self._labels_values:
                        for label_values, value in self._labels_values[name].items():
                            labels_str = self._format_labels(metric.labels, label_values)
                            lines.append(f"{name}{{{labels_str}}} {value}")
                            
                elif metric.type == MetricType.HISTOGRAM:
                    # 导出直方图
                    for key, observations in self._histograms.items():
                        if key.startswith(name):
                            self._export_histogram(lines, name, observations, key)
                            
        return "\n".join(lines) + "\n"
        
    def _format_labels(self, label_names: List[str], label_values: tuple) -> str:
        """格式化标签"""
        parts = []
        for name, value in zip(label_names, label_values):
            # 转义值中的特殊字符
            escaped_value = value.replace('\\', '\\\\').replace('"', '\\"')
            parts.append(f'{name}="{escaped_value}"')
        return ",".join(parts)
        
    def _export_histogram(self, lines: List[str], name: str, observations: List[float], key: str) -> None:
        """导出直方图数据"""
        if not observations:
            return
            
        # 计算分位数
        sorted_obs = sorted(observations)
        count = len(sorted_obs)
        sum_value = sum(sorted_obs)
        
        # 提取标签
        labels_str = ""
        if ":" in key:
            _, label_part = key.split(":", 1)
            if label_part != "()":
                # 重构标签字符串
                metric = self._metrics[name]
                label_values = eval(label_part)  # 安全的，因为是我们自己生成的
                labels_str = self._format_labels(metric.labels, label_values)
                if labels_str:
                    labels_str = labels_str + ","
                    
        # 导出分桶
        buckets = [0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
        for bucket in buckets:
            le_count = sum(1 for v in sorted_obs if v <= bucket)
            lines.append(f'{name}_bucket{{{labels_str}le="{bucket}"}} {le_count}')

        # bucket
        if labels_str:
            bucket_labels = labels_str + 'le="+Inf"'
        else:
            bucket_labels = 'le="+Inf"'
        lines.append(f'{name}_bucket{{{bucket_labels}}} {count}')

        # sum
        lines.append(f'{name}_sum{{{labels_str[:-1] if labels_str else ""}}} {sum_value}')

        # count
        lines.append(f'{name}_count{{{labels_str[:-1] if labels_str else ""}}} {count}')

    def get_stats(self) -> Dict[str, Any]:
        """获取指标统计信息"""
        with self._lock:
            stats = {
                "metrics_count": len(self._metrics),
                "counters": {},
                "gauges": {},
                "histograms": {}
            }
            
            for name, metric in self._metrics.items():
                if metric.type == MetricType.COUNTER:
                    stats["counters"][name] = self._values.get(name, 0)
                elif metric.type == MetricType.GAUGE:
                    stats["gauges"][name] = self._values.get(name, 0)
                elif metric.type == MetricType.HISTOGRAM:
                    hist_data = []
                    for key, observations in self._histograms.items():
                        if key.startswith(name):
                            hist_data.extend(observations)
                    if hist_data:
                        stats["histograms"][name] = {
                            "count": len(hist_data),
                            "sum": sum(hist_data),
                            "avg": sum(hist_data) / len(hist_data) if hist_data else 0,
                            "min": min(hist_data) if hist_data else 0,
                            "max": max(hist_data) if hist_data else 0
                        }
                        
            return stats


# 全局指标注册表
metrics_registry = PrometheusMetrics()


# 便捷函数
def inc_counter(name: str, value: float = 1, labels: Optional[Dict[str, str]] = None) -> None:
    """增加计数器"""
    metrics_registry.inc_counter(name, value, labels)
    

def set_gauge(name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
    """设置仪表值"""
    metrics_registry.set_gauge(name, value, labels)
    

def observe_histogram(name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
    """记录直方图值"""
    metrics_registry.observe_histogram(name, value, labels)
    

def time_histogram(name: str, labels: Optional[Dict[str, str]] = None) -> Any:
    """计时器装饰器/上下文管理器"""
    return metrics_registry.time_histogram(name, labels)
