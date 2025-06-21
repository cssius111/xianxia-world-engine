"""表达式解析器 (简化版)"""

from typing import Any

class ExpressionParser:
    """简易表达式解析器"""

    def evaluate(self, expression: str) -> Any:
        """评估一个数学表达式"""
        try:
            return eval(expression, {"__builtins__": {}})
        except Exception as exc:
            raise ValueError(str(exc))
