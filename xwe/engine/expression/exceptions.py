"""
表达式系统异常定义
"""

class ExpressionError(Exception):
    """表达式错误基类"""
    pass

class ParseError(ExpressionError):
    """解析错误"""
    pass

class EvaluationError(ExpressionError):
    """求值错误"""
    pass

class VariableNotFoundError(ExpressionError):
    """变量未找到错误"""
    pass

class TypeMismatchError(ExpressionError):
    """类型不匹配错误"""
    pass

class FunctionNotFoundError(ExpressionError):
    """函数未找到错误"""
    pass

class FunctionError(ExpressionError):
    """函数错误"""
    pass

class TokenizationError(ExpressionError):
    """词法分析错误"""
    pass

__all__ = [
    "ExpressionError",
    "ParseError",
    "EvaluationError",
    "VariableNotFoundError",
    "TypeMismatchError",
    "FunctionNotFoundError",
    "FunctionError",
    "TokenizationError"
]
