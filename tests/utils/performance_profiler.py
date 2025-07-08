"""性能分析工具

提供基本的 CPU 使用率统计函数，供测试模块使用。
"""

import time
from contextlib import contextmanager
from typing import Any, Callable, Dict

import psutil


@contextmanager
def cpu_usage_tracker() -> None:
    """上下文管理器：追踪代码块的 CPU 使用时间。"""
    process = psutil.Process()
    start_times = process.cpu_times()
    start_time = time.time()
    try:
        yield
    finally:
        end_times = process.cpu_times()
        end_time = time.time()
        user_time = end_times.user - start_times.user
        system_time = end_times.system - start_times.system
        duration = end_time - start_time
        print(
            f"CPU user: {user_time:.4f}s, system: {system_time:.4f}s, duration: {duration:.4f}s"
        )


def profile_cpu(func: Callable, *args: Any, **kwargs: Any) -> Dict[str, float]:
    """执行函数并返回 CPU 使用时间和持续时间。"""
    process = psutil.Process()
    start_times = process.cpu_times()
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    end_times = process.cpu_times()

    return {
        "result": result,
        "user_time": end_times.user - start_times.user,
        "system_time": end_times.system - start_times.system,
        "duration": end_time - start_time,
    }


__all__ = ["cpu_usage_tracker", "profile_cpu"]


def _busy_work() -> int:
    """Simple workload used in tests."""
    return sum(i * i for i in range(1000))


def test_profile_cpu() -> None:
    """profile_cpu 应该返回统计信息并保持结果正确。"""
    stats = profile_cpu(_busy_work)
    assert stats["result"] == _busy_work()
    assert stats["duration"] >= 0


def test_cpu_usage_tracker() -> None:
    """cpu_usage_tracker 上下文应正常运行。"""
    with cpu_usage_tracker():
        _busy_work()
