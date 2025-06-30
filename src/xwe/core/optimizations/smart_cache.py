"""简易智能缓存装饰器"""
from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Dict, Tuple, Optional
from collections import OrderedDict
import time
from config.game_config import config


class CacheableFunction:
    """包装可缓存的函数"""

    def __init__(self, func: Callable[..., Any], ttl: Optional[int], max_size: Optional[int]) -> None:
        self.func = func
        self.ttl = ttl
        self.max_size = max_size
        self.cache: "OrderedDict[Tuple[Tuple[Any, ...], Tuple[Tuple[str, Any], ...]], Tuple[Any, float]]" = OrderedDict()
        wraps(func)(self)  # type: ignore

    def __call__(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover - simple wrapper
        key = (args, tuple(sorted(kwargs.items())))
        now = time.time()
        if key in self.cache:
            value, ts = self.cache[key]
            if self.ttl is None or now - ts < self.ttl:
                self.cache.move_to_end(key)
                return value
            del self.cache[key]
        result = self.func(*args, **kwargs)
        self.cache[key] = (result, now)
        if self.max_size is not None and len(self.cache) > self.max_size:
            self.cache.popitem(last=False)
        return result

    def clear_cache(self) -> None:
        self.cache.clear()


class SmartCache:
    """管理多个可缓存函数的简易缓存器"""

    def __init__(self, ttl: Optional[int] = None, max_size: Optional[int] = None) -> None:
        self._functions: list[CacheableFunction] = []
        self.ttl = ttl if ttl is not None else config.smart_cache_ttl
        self.max_size = max_size if max_size is not None else config.smart_cache_size

    def cache(self, func: Callable[..., Any]) -> CacheableFunction:
        wrapped = CacheableFunction(func, self.ttl, self.max_size)
        self._functions.append(wrapped)
        return wrapped

    def clear_all(self) -> None:
        for fn in self._functions:
            fn.clear_cache()
