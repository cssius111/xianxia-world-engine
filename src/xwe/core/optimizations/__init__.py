# xwe/core/optimizations/__init__.py
"""优化模块"""

# 使用相对导入
from .smart_cache import CacheableFunction, SmartCache
from .expression_jit import ExpressionBenchmark, ExpressionJITCompiler

# 可选的异步事件系统
try:
    from .async_event_system import AsyncEvent, AsyncEventSystem, EventBus
except ImportError:
    AsyncEventSystem = None
    AsyncEvent = None
    EventBus = None

# 导出列表
__all__ = [
    "ExpressionJITCompiler",
    "ExpressionBenchmark",
    "SmartCache",
    "CacheableFunction",
    "AsyncEventSystem",
    "AsyncEvent",
    "EventBus",
]
