# xwe/core/optimizations/__init__.py

from .expression_jit import ExpressionJITCompiler, ExpressionBenchmark
from .smart_cache import SmartCache, CacheableFunction
from .async_event_system import AsyncEventSystem, AsyncEvent, EventBus

__all__ = [
    'ExpressionJITCompiler',
    'ExpressionBenchmark',
    'SmartCache',
    'CacheableFunction',
    'AsyncEventSystem',
    'AsyncEvent',
    'EventBus'
]
