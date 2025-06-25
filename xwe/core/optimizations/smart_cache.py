"""简易智能缓存装饰器"""
from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Dict, Tuple


class CacheableFunction:
    """包装可缓存的函数"""

    def __init__(self, func: Callable[..., Any]) -> None:
        self.func = func
        self.cache: Dict[Tuple[Tuple[Any, ...], Tuple[Tuple[str, Any], ...]], Any] = {}
        wraps(func)(self)  # type: ignore

    def __call__(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover - simple wrapper
        key = (args, tuple(sorted(kwargs.items())))
        if key not in self.cache:
            self.cache[key] = self.func(*args, **kwargs)
        return self.cache[key]

    def clear_cache(self) -> None:
        self.cache.clear()


class SmartCache:
    """管理多个可缓存函数的简易缓存器"""

    def __init__(self) -> None:
        self._functions: list[CacheableFunction] = []

    def cache(self, func: Callable[..., Any]) -> CacheableFunction:
        wrapped = CacheableFunction(func)
        self._functions.append(wrapped)
        return wrapped

    def clear_all(self) -> None:
        for fn in self._functions:
            fn.clear_cache()
