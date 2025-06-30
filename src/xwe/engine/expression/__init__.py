# engine/expression/__init__.py
"""
XWE表达式解析器模块

提供安全、高效的数学表达式解析和求值功能。

主要组件:
- ExpressionParser: 表达式解析器主类
- ExpressionError: 异常基类
- 各种具体异常类型

使用示例:
    >>> from xwe.engine.expression import ExpressionParser
    >>> parser = ExpressionParser()
    >>> result = parser.evaluate("2 + 3 * 4")
    >>> print(result)  # 14.0
"""

from .exceptions import (
    EvaluationError,
    ExpressionError,
    FunctionError,
    ParseError,
    TokenizationError,
    ValidationError,
)
from .parser import ExpressionParser

__all__ = [
    "ExpressionParser",
    "ExpressionError",
    "TokenizationError",
    "ParseError",
    "EvaluationError",
    "ValidationError",
    "FunctionError",
]

__version__ = "2.0.0"
