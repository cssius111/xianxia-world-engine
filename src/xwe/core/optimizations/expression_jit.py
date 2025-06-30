"""表达式 JIT 编译器和基准测试工具"""
from __future__ import annotations

import time
from typing import Any, Callable, Dict


class ExpressionJITCompiler:
    """简单的表达式 JIT 编译器"""

    def __init__(self) -> None:
        self._cache: Dict[str, Any] = {}

    def compile(self, expression: str) -> Callable[..., Any]:
        """将表达式编译成可调用对象"""
        if expression not in self._cache:
            self._cache[expression] = compile(expression, "<expr>", "eval")

        code = self._cache[expression]

        def func(**variables: Any) -> Any:
            return eval(code, {"__builtins__": {}}, variables)

        return func


class ExpressionBenchmark:
    """用于测试表达式执行效率的简单基准工具"""

    def __init__(self, compiler: ExpressionJITCompiler) -> None:
        self.compiler = compiler

    def run(self, expression: str, iterations: int = 1000, **variables: Any) -> float:
        """执行基准测试并返回耗时"""
        func = self.compiler.compile(expression)
        start = time.perf_counter()
        for _ in range(iterations):
            func(**variables)
        end = time.perf_counter()
        return end - start
