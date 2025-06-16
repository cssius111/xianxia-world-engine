# engine/expression/parser.py
"""
表达式解析器主模块

提供安全的数学表达式解析和求值功能。
"""

import re
import logging
import operator
from typing import Any, Callable, Dict, List, Optional, Union

from .tokenizer import Tokenizer, Token, TokenType
from .ast_nodes import (
    ASTNode, NumberNode, VariableNode,
    BinaryOpNode, UnaryOpNode, FunctionCallNode
)
from .functions import create_builtin_functions
from .exceptions import (
    ExpressionError, ParseError, EvaluationError,
    ValidationError, TokenizationError
)

# 配置日志
logger = logging.getLogger(__name__)


class ExpressionParser:
    """
    数学表达式解析器

    支持基本算术运算、变量、函数调用和优先级控制。
    通过词法分析和语法分析生成AST，然后进行求值。

    Examples:
        >>> parser = ExpressionParser()
        >>> parser.evaluate("2 + 3 * 4")
        14.0
        >>> parser.evaluate("x + y", {"x": 10, "y": 5})
        15.0
        >>> parser.evaluate("max(1, 2, 3)")
        3.0
    """

    # 运算符定义
    OPERATORS = {
        # 比较运算符（最低优先级）
        '<': {
            'precedence': 0,
            'associativity': 'left',
            'func': lambda a, b: float(a < b)
        },
        '>': {
            'precedence': 0,
            'associativity': 'left',
            'func': lambda a, b: float(a > b)
        },
        '<=': {
            'precedence': 0,
            'associativity': 'left',
            'func': lambda a, b: float(a <= b)
        },
        '>=': {
            'precedence': 0,
            'associativity': 'left',
            'func': lambda a, b: float(a >= b)
        },
        '==': {
            'precedence': 0,
            'associativity': 'left',
            'func': lambda a, b: float(a == b)
        },
        '!=': {
            'precedence': 0,
            'associativity': 'left',
            'func': lambda a, b: float(a != b)
        },
        # 算术运算符
        '+': {
            'precedence': 1,
            'associativity': 'left',
            'func': operator.add
        },
        '-': {
            'precedence': 1,
            'associativity': 'left',
            'func': operator.sub
        },
        '*': {
            'precedence': 2,
            'associativity': 'left',
            'func': operator.mul
        },
        '/': {
            'precedence': 2,
            'associativity': 'left',
            'func': operator.truediv
        },
        '^': {
            'precedence': 3,
            'associativity': 'right',
            'func': operator.pow
        },
    }

    def __init__(self, debug: bool = False):
        """
        初始化表达式解析器

        Args:
            debug: 是否启用调试模式
        """
        self.debug = debug
        self.BUILTIN_FUNCTIONS = create_builtin_functions()
        self._custom_functions: Dict[str, Dict[str, Any]] = {}

        # 解析状态
        self.tokens: List[Token] = []
        self.current = 0
        self.expression = ""

        if debug:
            logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)

    def register_function(self, name: str, func: Callable,
                          arg_count: int = -1, description: str = ""):
        """
        注册自定义函数

        Args:
            name: 函数名
            func: 函数实现
            arg_count: 参数数量，-1表示可变参数
            description: 函数描述

        Raises:
            ValueError: 函数名已存在或无效

        Example:
            >>> parser.register_function("double", lambda x: x * 2, 1)
            >>> parser.evaluate("double(5)")
            10.0
        """
        if not name or not name.isidentifier():
            raise ValueError(f"无效的函数名: {name}")

        if name in self.BUILTIN_FUNCTIONS:
            raise ValueError(f"不能覆盖内置函数: {name}")

        if name in self._custom_functions:
            raise ValueError(f"函数已存在: {name}")

        self._custom_functions[name] = {
            'func': func,
            'args': arg_count,
            'description': description
        }

        if self.debug:
            logger.debug(f"注册自定义函数: {name} (参数数: {arg_count})")

    def evaluate(self, expression: str, context: Optional[Dict[str, float]] = None) -> float:
        """
        计算表达式的值

        Args:
            expression: 数学表达式字符串
            context: 变量上下文，包含变量名到值的映射

        Returns:
            计算结果

        Raises:
            ExpressionError: 表达式错误
            TokenizationError: 词法分析错误
            ParseError: 语法分析错误
            EvaluationError: 求值错误

        Example:
            >>> parser = ExpressionParser()
            >>> parser.evaluate("2 + 3 * 4")
            14.0
            >>> parser.evaluate("damage * multiplier", {"damage": 100, "multiplier": 1.5})
            150.0
        """
        if not expression or not expression.strip():
            raise ExpressionError("表达式不能为空")

        self.expression = expression
        context = context or {}

        if self.debug:
            logger.debug(f"开始求值表达式: {expression}")
            logger.debug(f"变量上下文: {context}")

        try:
            # 词法分析
            tokenizer = Tokenizer(expression)
            self.tokens = tokenizer.tokenize()

            if self.debug:
                logger.debug(f"词法分析结果: {self.tokens}")

            # 语法分析
            self.current = 0
            ast = self._parse_expression()

            # 确保所有token都被消费
            if self.current < len(self.tokens) - 1:  # -1 是因为EOF
                token = self.tokens[self.current]
                raise ParseError(
                    f"意外的token: {token.value}",
                    position=token.position,
                    expression=expression
                )

            if self.debug:
                logger.debug(f"AST: {ast}")

            # 求值
            result = ast.evaluate(context, self)

            if self.debug:
                logger.debug(f"求值结果: {result}")

            return result

        except ExpressionError:
            # 已经是我们的异常，直接抛出
            raise
        except Exception as e:
            # 包装其他异常
            raise EvaluationError(f"表达式求值失败: {str(e)}")

    def validate(self, expression: str) -> bool:
        """
        验证表达式是否合法

        Args:
            expression: 表达式字符串

        Returns:
            是否合法

        Note:
            此方法会捕获所有异常并返回布尔值。
            如需详细错误信息，请使用 validate_with_error()
        """
        try:
            self.validate_with_error(expression)
            return True
        except ExpressionError:
            return False

    def validate_with_error(self, expression: str) -> None:
        """
        验证表达式并提供详细错误信息

        Args:
            expression: 表达式字符串

        Raises:
            ValidationError: 包含详细错误信息的验证异常
        """
        if not expression or not expression.strip():
            raise ValidationError("表达式不能为空")

        # 检查危险模式
        if self._contains_dangerous_patterns(expression):
            raise ValidationError("表达式包含不安全的内容")

        try:
            # 尝试解析
            tokenizer = Tokenizer(expression)
            tokens = tokenizer.tokenize()

            # 检查括号匹配
            paren_count = 0
            for token in tokens:
                if token.type == TokenType.LPAREN:
                    paren_count += 1
                elif token.type == TokenType.RPAREN:
                    paren_count -= 1
                    if paren_count < 0:
                        raise ValidationError(
                            "右括号多于左括号",
                            position=token.position,
                            expression=expression
                        )

            if paren_count > 0:
                raise ValidationError(
                    f"缺少 {paren_count} 个右括号",
                    expression=expression
                )

            # 检查连续运算符
            for i in range(len(tokens) - 1):  # 跳过EOF
                token = tokens[i]
                if token.type == TokenType.OPERATOR:
                    # 检查下一个token
                    next_token = tokens[i + 1]
                    if next_token.type == TokenType.OPERATOR:
                        # 特殊处理：不允许+/-后面跟+/-（如 "2 ++ 3"）
                        # 但允许其他运算符后跟+/-作为一元运算符（如 "2 * -3"）
                        if token.value in ['+', '-'] and next_token.value in ['+', '-']:
                            # ++ +- -+ -- 都不允许
                            raise ValidationError(
                                f"连续的运算符: {token.value}{next_token.value}",
                                position=token.position,
                                expression=expression
                            )
                        elif next_token.value in ['+', '-']:
                            # 其他运算符后可以跟+/-作为一元运算符
                            # 检查位置是否合法
                            if i == 0:  # 表达式开始
                                continue
                            prev_token = tokens[i - 1]
                            if prev_token.type in [TokenType.LPAREN, TokenType.COMMA] or \
                               (prev_token.type == TokenType.OPERATOR and prev_token.value not in ['+', '-']):
                                # 合法的一元运算符位置
                                continue
                        # 其他情况都是非法的连续运算符
                        raise ValidationError(
                            f"连续的运算符: {token.value}{next_token.value}",
                            position=token.position,
                            expression=expression
                        )

            # 检查函数调用
            for i, token in enumerate(tokens[:-1]):
                if token.type == TokenType.FUNCTION:
                    # 确保函数后面跟着左括号
                    if i + 1 >= len(tokens) - 1 or tokens[i + 1].type != TokenType.LPAREN:
                        raise ValidationError(
                            f"函数 '{token.value}' 后需要括号",
                            position=token.position,
                            expression=expression
                        )

            # 尝试构建AST（使用空上下文）
            self.tokens = tokens
            self.current = 0
            self.expression = expression
            self._parse_expression()

        except ExpressionError as e:
            # 转换为验证错误
            raise ValidationError(str(e), e.position if hasattr(e, 'position') else None, expression)
        except Exception as e:
            raise ValidationError(f"表达式格式错误: {str(e)}", expression=expression)

    def _contains_dangerous_patterns(self, expression: str) -> bool:
        """检查表达式是否包含危险模式"""
        dangerous_patterns = [
            r'__[a-zA-Z]+__',  # 双下划线方法
            r'import\s+',  # import语句
            r'exec\s*\(',  # exec函数
            r'eval\s*\(',  # eval函数
            r'compile\s*\(',  # compile函数
            r'open\s*\(',  # 文件操作
            r'os\.',  # os模块
            r'sys\.',  # sys模块
            r'globals\s*\(',  # globals函数
            r'locals\s*\(',  # locals函数
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, expression, re.IGNORECASE):
                return True
        return False

    # === 语法分析方法 ===

    def _parse_expression(self) -> ASTNode:
        """解析表达式（入口）"""
        return self._parse_binary_expression(self._parse_unary(), 0)

    def _parse_binary_expression(self, left: ASTNode, min_precedence: int) -> ASTNode:
        """
        解析二元表达式（运算符优先级算法）

        使用Pratt解析算法处理运算符优先级和结合性。
        """
        while True:
            token = self._peek()

            # 检查是否为运算符
            if token.type != TokenType.OPERATOR or token.value not in self.OPERATORS:
                break

            op_info = self.OPERATORS[token.value]
            if op_info['precedence'] < min_precedence:
                break

            # 消费运算符
            op_token = self._advance()

            # 根据结合性决定右侧最小优先级
            if op_info['associativity'] == 'right':
                next_min_prec = op_info['precedence']
            else:
                next_min_prec = op_info['precedence'] + 1

            # 检查是否为不允许的连续运算符
            # 不允许+/-后面直接跟+/-
            if op_token.value in ['+', '-']:
                peek_token = self._peek()
                if peek_token.type == TokenType.OPERATOR and peek_token.value in ['+', '-']:
                    raise ParseError(
                        f"连续的运算符: {op_token.value}{peek_token.value}",
                        position=op_token.position,
                        expression=self.expression
                    )

            # 解析右侧
            right = self._parse_binary_expression(self._parse_unary(), next_min_prec)

            # 创建二元运算节点
            left = BinaryOpNode(op_token.value, left, right)

        return left

    def _parse_unary(self) -> ASTNode:
        """解析一元表达式"""
        token = self._peek()

        # 处理一元运算符
        if token.type == TokenType.OPERATOR and token.value in ['+', '-']:
            self._advance()
            operand = self._parse_unary()
            return UnaryOpNode(token.value, operand)

        return self._parse_primary()

    def _parse_primary(self) -> ASTNode:
        """解析基本表达式"""
        token = self._advance()

        if token.type == TokenType.NUMBER:
            return NumberNode(token.value)

        elif token.type == TokenType.VARIABLE:
            return VariableNode(token.value)

        elif token.type == TokenType.FUNCTION:
            return self._parse_function_call(token.value)

        elif token.type == TokenType.LPAREN:
            # 括号表达式
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "期望右括号 ')'")
            return expr

        else:
            raise ParseError(
                f"意外的token: {token.value}",
                position=token.position,
                expression=self.expression
            )

    def _parse_function_call(self, func_name: str) -> FunctionCallNode:
        """解析函数调用"""
        self._consume(TokenType.LPAREN, f"函数 '{func_name}' 后需要左括号 '('")

        args: List[ASTNode] = []

        # 处理空参数列表
        if self._peek().type == TokenType.RPAREN:
            self._advance()
            return FunctionCallNode(func_name, args)

        # 解析参数列表
        while True:
            args.append(self._parse_expression())

            if self._peek().type == TokenType.COMMA:
                self._advance()
            elif self._peek().type == TokenType.RPAREN:
                break
            else:
                token = self._peek()
                raise ParseError(
                    f"函数参数之间需要逗号，但得到: {token.value}",
                    position=token.position,
                    expression=self.expression
                )

        self._consume(TokenType.RPAREN, "期望右括号 ')'")
        return FunctionCallNode(func_name, args)

    # === 辅助方法 ===

    def _peek(self) -> Token:
        """查看当前token但不消费"""
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return self.tokens[-1]  # EOF

    def _advance(self) -> Token:
        """消费并返回当前token"""
        token = self._peek()
        if token.type != TokenType.EOF:
            self.current += 1
        return token

    def _consume(self, expected_type: TokenType, error_message: str) -> None:
        """消费期望类型的token"""
        token = self._advance()
        if token.type != expected_type:
            raise ParseError(
                f"{error_message}，但得到: {token.value}",
                position=token.position,
                expression=self.expression
            )
