from typing import Any
# engine/expression/exceptions.py
"""
表达式解析器异常定义模块

定义了表达式解析和计算过程中可能出现的各种异常类型。
"""


class ExpressionError(Exception):
    """表达式错误基类"""

    def __init__(self, message: str, position: int = -1, expression: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.position = position
        self.expression = expression

    def __str__(self) -> Any:
        if self.position >= 0 and self.expression:
            # 显示错误位置
            lines = [
                f"表达式错误: {self.message}",
                f"表达式: {self.expression}",
                f"        {' ' * self.position}^"
            ]
            return "\n".join(lines)
        return f"表达式错误: {self.message}"


class TokenizationError(ExpressionError):
    """词法分析错误"""
    pass


class ParseError(ExpressionError):
    """语法分析错误"""
    pass


class EvaluationError(ExpressionError):
    """求值错误"""
    pass


class ValidationError(ExpressionError):
    """验证错误"""
    pass


class FunctionError(ExpressionError):
    """函数调用错误"""
    pass