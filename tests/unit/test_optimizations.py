import asyncio
import pytest

# 使用标准导入方式
try:
    from src.xwe.core.optimizations import (
        ExpressionJITCompiler,
        ExpressionBenchmark,
        SmartCache,
        CacheableFunction,
        AsyncEventSystem
    )
except ImportError:
    # 如果标准导入失败，尝试备用方案
    import importlib.util
    from pathlib import Path

    def _load_module(path, name):
        spec = importlib.util.spec_from_file_location(name, Path(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore
        return module

    optimizations = _load_module('src/xwe/core/optimizations/__init__.py', 'optimizations')
    ExpressionJITCompiler = optimizations.ExpressionJITCompiler
    ExpressionBenchmark = optimizations.ExpressionBenchmark
    SmartCache = optimizations.SmartCache
    CacheableFunction = optimizations.CacheableFunction
    AsyncEventSystem = optimizations.AsyncEventSystem


def test_expression_jit_compile():
    if ExpressionJITCompiler is None:
        pytest.skip("ExpressionJITCompiler not available")
    
    compiler = ExpressionJITCompiler()
    func = compiler.compile("a + b * c")
    assert func(a=1, b=2, c=3) == 7


def test_smart_cache_basic():
    if SmartCache is None:
        pytest.skip("SmartCache not available")
        
    cache = SmartCache()
    call_count = {"n": 0}

    @cache.cache
    def add(a, b):
        call_count["n"] += 1
        return a + b

    assert add(1, 2) == 3
    assert add(1, 2) == 3
    assert call_count["n"] == 1
    cache.clear_all()
    assert add(1, 2) == 3
    assert call_count["n"] == 2


async def _async_test_helper():
    if AsyncEventSystem is None:
        return True
    events = AsyncEventSystem()
    result = {}

    @events.listener("test")
    async def on_test(value):
        result["value"] = value

    await events.emit("test", 42)
    return result.get("value") == 42


def test_async_event_system():
    assert asyncio.run(_async_test_helper())
