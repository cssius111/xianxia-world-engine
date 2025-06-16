# xwe/core/optimizations/__init__.py

from xwe.core.expression_jit import ExpressionJITCompiler, ExpressionBenchmark
from xwe.core.smart_cache import SmartCache, CacheableFunction

try:  # 兼容缺少异步事件系统实现的情况
    from xwe.core.optimizations.async_event_system import AsyncEventSystem, AsyncEvent, EventBus
except Exception:  # pragma: no cover - allow missing module
    AsyncEventSystem = None
    AsyncEvent = None
    EventBus = None

__all__ = [
    'ExpressionJITCompiler',
    'ExpressionBenchmark',
    'SmartCache',
    'CacheableFunction',
    'AsyncEventSystem',
    'AsyncEvent',
    'EventBus'
]
