"""内存分析工具

提供基本的内存使用统计函数，供测试模块使用。
"""

import time
from contextlib import contextmanager
from typing import Any, Callable, Dict

import psutil


@contextmanager
def memory_usage_tracker() -> None:
    """上下文管理器：追踪代码块的内存变化(MB)。"""
    process = psutil.Process()
    start_mem = process.memory_info().rss
    start_time = time.time()
    try:
        yield
    finally:
        end_mem = process.memory_info().rss
        end_time = time.time()
        delta_mb = (end_mem - start_mem) / 1024 / 1024
        duration = end_time - start_time
        print(f"Memory change: {delta_mb:.4f} MB, duration: {duration:.4f}s")


def profile_memory(func: Callable, *args: Any, **kwargs: Any) -> Dict[str, float]:
    """执行函数并返回内存变化（MB）和持续时间。"""
    process = psutil.Process()
    start_mem = process.memory_info().rss
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    end_mem = process.memory_info().rss

    return {
        "result": result,
        "memory_change_mb": (end_mem - start_mem) / 1024 / 1024,
        "duration": end_time - start_time,
    }


__all__ = ["memory_usage_tracker", "profile_memory"]


def _busy_work() -> int:
    """Simple workload used in tests."""
    return sum(i * i for i in range(1000))


def test_profile_memory() -> None:
    """profile_memory 应该返回统计信息并保持结果正确。"""
    stats = profile_memory(_busy_work)
    assert stats["result"] == _busy_work()
    assert stats["duration"] >= 0


def test_memory_usage_tracker() -> None:
    """memory_usage_tracker 上下文应正常运行。"""
    with memory_usage_tracker():
        _busy_work()
