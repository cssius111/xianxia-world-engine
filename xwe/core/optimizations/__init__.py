# xwe/core/optimizations/__init__.py

from xwe.core.optimizations.expression_jit import (
    ExpressionBenchmark,
    ExpressionJITCompiler,
)
from xwe.core.optimizations.smart_cache import CacheableFunction, SmartCache

try:  # 兼容缺少异步事件系统实现的情况
    from xwe.core.optimizations.async_event_system import (
        AsyncEvent,
        AsyncEventSystem,
        EventBus,
    )
except Exception:  # pragma: no cover - allow missing module
    AsyncEventSystem = None
    AsyncEvent = None
    EventBus = None

__all__ = [
    "ExpressionJITCompiler",
    "ExpressionBenchmark",
    "SmartCache",
    "CacheableFunction",
    "AsyncEventSystem",
    "AsyncEvent",
    "EventBus",
]
