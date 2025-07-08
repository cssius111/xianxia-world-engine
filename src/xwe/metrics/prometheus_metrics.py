"""
Prometheus 监控指标定义
提供 XianXia World Engine 的核心性能指标
"""

import logging
from typing import Dict, Optional, Any
from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry
from prometheus_flask_exporter import PrometheusMetrics
import time
from contextlib import contextmanager
from threading import RLock

logger = logging.getLogger(__name__)

# 指标前缀
METRIC_PREFIX = "xwe_"

# 独立的指标注册表，避免重复注册
REGISTRY = CollectorRegistry()

# NLP 请求处理时间（秒）
nlp_request_seconds = Histogram(
    f'{METRIC_PREFIX}nlp_request_seconds',
    'NLP request processing time in seconds',
    labelnames=['command_type', 'status'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=REGISTRY
)

# NLP Token 使用量
nlp_token_count = Histogram(
    f'{METRIC_PREFIX}nlp_token_count',
    'Number of tokens used per NLP request',
    labelnames=['model'],
    buckets=(10, 50, 100, 250, 500, 1000, 2500, 5000),
    registry=REGISTRY
)

# 缓存命中总数
nlp_cache_hit_total = Counter(
    f'{METRIC_PREFIX}nlp_cache_hit_total',
    'Total number of NLP cache hits',
    labelnames=['cache_type'],
    registry=REGISTRY
)

# 上下文压缩次数
context_compression_total = Counter(
    f'{METRIC_PREFIX}context_compression_total',
    'Total number of context compressions performed',
    registry=REGISTRY
)

# 当前记忆块数量
context_memory_blocks_gauge = Gauge(
    f'{METRIC_PREFIX}context_memory_blocks_gauge',
    'Current number of memory blocks in context',
    registry=REGISTRY
)

# 异步线程池大小
async_thread_pool_size = Gauge(
    f'{METRIC_PREFIX}async_thread_pool_size',
    'Current size of async thread pool',
    registry=REGISTRY
)

# 异步请求队列长度
async_request_queue_size = Gauge(
    f'{METRIC_PREFIX}async_request_queue_size',
    'Current length of async request queue',
    registry=REGISTRY
)

# NLP 错误计数
nlp_error_total = Counter(
    f'{METRIC_PREFIX}nlp_error_total',
    'Total number of NLP errors',
    labelnames=['error_type'],
    registry=REGISTRY
)

# 命令执行时间
command_execution_seconds = Histogram(
    f'{METRIC_PREFIX}command_execution_seconds',
    'Command execution time in seconds',
    labelnames=['command', 'handler'],
    registry=REGISTRY
)

# API 调用延迟
api_call_latency = Summary(
    f'{METRIC_PREFIX}api_call_latency_seconds',
    'External API call latency in seconds',
    labelnames=['api_name', 'endpoint'],
    registry=REGISTRY
)

# 游戏实例数量
game_instances_gauge = Gauge(
    f'{METRIC_PREFIX}game_instances_gauge',
    'Current number of active game instances',
    registry=REGISTRY
)

# 玩家在线数
players_online_gauge = Gauge(
    f'{METRIC_PREFIX}players_online_gauge',
    'Current number of online players',
    registry=REGISTRY
)

# 系统资源使用
system_cpu_usage = Gauge(
    f'{METRIC_PREFIX}system_cpu_usage_percent',
    'System CPU usage percentage',
    registry=REGISTRY
)

system_memory_usage = Gauge(
    f'{METRIC_PREFIX}system_memory_usage_mb',
    'System memory usage in MB',
    registry=REGISTRY
)


class MetricsCollector:
    """
    Prometheus 指标收集器
    提供线程安全的指标更新接口
    """
    
    def __init__(self):
        self._lock = RLock()
        self._enabled = True
        self._degraded = False
        
    def set_enabled(self, enabled: bool):
        """启用/禁用指标收集"""
        with self._lock:
            self._enabled = enabled
            logger.info(f"Prometheus metrics collection {'enabled' if enabled else 'disabled'}")
    
    def set_degraded(self, degraded: bool):
        """设置降级模式（减少指标收集）"""
        with self._lock:
            self._degraded = degraded
            if degraded:
                logger.warning("Prometheus metrics in degraded mode")
    
    @contextmanager
    def measure_time(self, histogram, labels: Dict[str, str]):
        """
        测量代码块执行时间的上下文管理器
        
        Args:
            histogram: Prometheus Histogram 对象
            labels: 标签字典
            
        Example:
            with metrics_collector.measure_time(nlp_request_seconds, {'command_type': 'explore', 'status': 'success'}):
                # 执行需要计时的代码
                process_nlp_request()
        """
        if not self._enabled:
            yield
            return
            
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            try:
                histogram.labels(**labels).observe(duration)
            except Exception as e:
                logger.error(f"Failed to record metric: {e}")
    
    def record_nlp_request(self, 
                          command_type: str,
                          duration: float,
                          success: bool,
                          token_count: int = 0,
                          model: str = "deepseek-chat",
                          use_cache: bool = False,
                          error_type: Optional[str] = None):
        """记录 NLP 请求指标"""
        if not self._enabled:
            return
            
        with self._lock:
            try:
                # 记录请求时间
                status = "success" if success else "failure"
                nlp_request_seconds.labels(
                    command_type=command_type,
                    status=status
                ).observe(duration)
                
                # 记录 token 使用量
                if token_count > 0:
                    nlp_token_count.labels(model=model).observe(token_count)
                
                # 记录缓存命中
                if use_cache:
                    cache_type = "nlp_cache"
                    nlp_cache_hit_total.labels(cache_type=cache_type).inc()
                
                # 记录错误
                if not success and error_type:
                    nlp_error_total.labels(error_type=error_type).inc()
                    
            except Exception as e:
                logger.error(f"Failed to record NLP metrics: {e}")
    
    def record_context_compression(self, 
                                 memory_blocks: int = 0,
                                 compression_ratio: float = 1.0):
        """记录上下文压缩指标"""
        if not self._enabled:
            return
            
        with self._lock:
            try:
                context_compression_total.inc()
                if memory_blocks >= 0:
                    context_memory_blocks_gauge.set(memory_blocks)
            except Exception as e:
                logger.error(f"Failed to record context compression metrics: {e}")
    
    def update_async_metrics(self,
                           thread_pool_size: int = 0,
                           queue_size: int = 0):
        """更新异步处理指标"""
        if not self._enabled or self._degraded:
            return
            
        with self._lock:
            try:
                if thread_pool_size >= 0:
                    async_thread_pool_size.set(thread_pool_size)
                if queue_size >= 0:
                    async_request_queue_size.set(queue_size)
            except Exception as e:
                logger.error(f"Failed to update async metrics: {e}")
    
    def record_command_execution(self,
                               command: str,
                               handler: str,
                               duration: float):
        """记录命令执行时间"""
        if not self._enabled:
            return
            
        with self._lock:
            try:
                command_execution_seconds.labels(
                    command=command,
                    handler=handler
                ).observe(duration)
            except Exception as e:
                logger.error(f"Failed to record command execution: {e}")
    
    def record_api_call(self,
                       api_name: str,
                       endpoint: str,
                       duration: float):
        """记录 API 调用延迟"""
        if not self._enabled:
            return
            
        with self._lock:
            try:
                api_call_latency.labels(
                    api_name=api_name,
                    endpoint=endpoint
                ).observe(duration)
            except Exception as e:
                logger.error(f"Failed to record API call: {e}")
    
    def update_game_metrics(self,
                          instances: int = 0,
                          players: int = 0):
        """更新游戏状态指标"""
        if not self._enabled:
            return
            
        with self._lock:
            try:
                if instances >= 0:
                    game_instances_gauge.set(instances)
                if players >= 0:
                    players_online_gauge.set(players)
            except Exception as e:
                logger.error(f"Failed to update game metrics: {e}")
    
    def update_system_metrics(self,
                            cpu_percent: float = 0.0,
                            memory_mb: float = 0.0):
        """更新系统资源指标"""
        if not self._enabled or self._degraded:
            return
            
        with self._lock:
            try:
                if cpu_percent >= 0:
                    system_cpu_usage.set(cpu_percent)
                if memory_mb >= 0:
                    system_memory_usage.set(memory_mb)
            except Exception as e:
                logger.error(f"Failed to update system metrics: {e}")


# 全局指标收集器实例
metrics_collector = MetricsCollector()


def init_prometheus_app_metrics(app, app_version='1.0.0', app_config=None):
    """
    初始化 Flask 应用的 Prometheus 指标
    
    Args:
        app: Flask 应用实例
        app_version: 应用版本
        app_config: 应用配置
        
    Returns:
        PrometheusMetrics 实例
    """
    # 配置默认值
    if app_config is None:
        app_config = {}
    
    # 从环境变量读取配置
    metrics_path = app_config.get('metrics_path', '/metrics')
    enable_default_metrics = app_config.get('enable_default_metrics', True)
    
    # 初始化 PrometheusMetrics
    metrics = PrometheusMetrics(
        app,
        group_by='endpoint',
        defaults_prefix=METRIC_PREFIX,
        registry=REGISTRY,
        excluded_paths=['/static', '/health', '/favicon.ico']
    )
    
    # 添加应用信息
    metrics.info('xwe_app_info', 'XianXia World Engine application info', 
                 version=app_version)
    
    # 禁用默认指标（如果配置要求）
    if not enable_default_metrics:
        metrics.do_not_track()
    
    # 设置自定义指标路径
    if metrics_path != '/metrics':
        # 需要手动处理路由
        pass
    
    logger.info(f"Prometheus metrics initialized at {metrics_path}")
    
    return metrics


def get_metrics_collector() -> MetricsCollector:
    """获取全局指标收集器实例"""
    return metrics_collector
