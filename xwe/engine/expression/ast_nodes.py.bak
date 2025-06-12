# engine/expression/ast_nodes.py
"""
抽象语法树（AST）节点定义

定义了表达式解析后生成的各种AST节点类型。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .parser import ExpressionParser


class ASTNode(ABC):
    """
    抽象语法树节点基类

    所有AST节点都必须实现evaluate方法用于求值。
    """

    @abstractmethod
    def evaluate(self, context: Dict[str, float], parser: 'ExpressionParser') -> float:
        """
        对节点进行求值

        Args:
            context: 变量上下文
            parser: 解析器实例（用于访问函数定义等）

        Returns:
            求值结果
        """
        pass

    @abstractmethod
    def __repr__(self) -> str:
        """返回节点的字符串表示"""
        pass


class NumberNode(ASTNode):
    """数字字面量节点"""

    def __init__(self, value: float):
        self.value = value

    def evaluate(self, context: Dict[str, float], parser: 'ExpressionParser') -> float:
        """直接返回数字值"""
        return self.value

    def __repr__(self) -> str:
        return f"Number({self.value})"


class VariableNode(ASTNode):
    """变量引用节点"""

    def __init__(self, name: str):
        self.name = name

    def evaluate(self, context: Dict[str, float], parser: 'ExpressionParser') -> float:
        """从上下文中查找变量值"""
        from .exceptions import EvaluationError

        if self.name in context:
            value = context[self.name]
            # 确保返回浮点数
            try:
                return float(value)
            except (TypeError, ValueError) as e:
                raise EvaluationError(f"变量 '{self.name}' 的值无法转换为数字: {value}")
        else:
            # 提供更详细的错误信息
            available_vars = list(context.keys())
            if available_vars:
                raise EvaluationError(
                    f"未定义的变量: '{self.name}'。可用变量: {', '.join(available_vars)}"
                )
            else:
                raise EvaluationError(f"未定义的变量: '{self.name}'（上下文为空）")

    def __repr__(self) -> str:
        return f"Variable({self.name})"


class BinaryOpNode(ASTNode):
    """二元运算节点"""

    def __init__(self, operator: str, left: ASTNode, right: ASTNode):
        self.operator = operator
        self.left = left
        self.right = right

    def evaluate(self, context: Dict[str, float], parser: 'ExpressionParser') -> float:
        """计算二元运算结果"""
        from .exceptions import EvaluationError

        left_val = self.left.evaluate(context, parser)
        right_val = self.right.evaluate(context, parser)

        # 特殊处理除零
        if self.operator == '/' and right_val == 0:
            raise EvaluationError("除零错误")

        # 从解析器获取运算符函数
        if self.operator in parser.OPERATORS:
            op_func = parser.OPERATORS[self.operator]['func']
            return op_func(left_val, right_val)
        else:
            raise EvaluationError(f"未知的运算符: {self.operator}")

    def __repr__(self) -> str:
        return f"BinaryOp({self.left} {self.operator} {self.right})"


class UnaryOpNode(ASTNode):
    """一元运算节点"""

    def __init__(self, operator: str, operand: ASTNode):
        self.operator = operator
        self.operand = operand

    def evaluate(self, context: Dict[str, float], parser: 'ExpressionParser') -> float:
        """计算一元运算结果"""
        from .exceptions import EvaluationError

        val = self.operand.evaluate(context, parser)

        if self.operator == '-':
            return -val
        elif self.operator == '+':
            return val
        else:
            raise EvaluationError(f"未知的一元运算符: {self.operator}")

    def __repr__(self) -> str:
        return f"UnaryOp({self.operator}{self.operand})"


class FunctionCallNode(ASTNode):
    """函数调用节点"""

    def __init__(self, name: str, args: List[ASTNode]):
        self.name = name
        self.args = args

    def evaluate(self, context: Dict[str, float], parser: 'ExpressionParser') -> float:
        """计算函数调用结果"""
        from .exceptions import FunctionError

        # 查找函数定义
        if self.name in parser.BUILTIN_FUNCTIONS:
            func_info = parser.BUILTIN_FUNCTIONS[self.name]
        elif self.name in parser._custom_functions:
            func_info = parser._custom_functions[self.name]
        else:
            # 列出可用函数
            available_funcs = list(parser.BUILTIN_FUNCTIONS.keys()) + \
                              list(parser._custom_functions.keys())
            raise FunctionError(
                f"未定义的函数: '{self.name}'。可用函数: {', '.join(available_funcs)}"
            )

        # 求值参数
        try:
            arg_values = [arg.evaluate(context, parser) for arg in self.args]
        except Exception as e:
            raise FunctionError(f"函数 '{self.name}' 参数求值失败: {str(e)}")

        # 检查参数数量
        expected_args = func_info['args']
        if expected_args != -1 and len(arg_values) != expected_args:
            raise FunctionError(
                f"函数 '{self.name}' 期望 {expected_args} 个参数，"
                f"但提供了 {len(arg_values)} 个"
            )

        # 调用函数
        try:
            return func_info['func'](*arg_values)
        except Exception as e:
            raise FunctionError(f"函数 '{self.name}' 执行失败: {str(e)}")

    def __repr__(self) -> str:
        args_str = ", ".join(repr(arg) for arg in self.args)
        return f"Function({self.name}({args_str}))"