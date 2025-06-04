# engine/expression/tokenizer.py
"""
词法分析器模块

将表达式字符串分解为词法单元（Token）序列。
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

from .exceptions import TokenizationError


class TokenType(Enum):
    """Token类型枚举"""
    NUMBER = auto()  # 数字
    VARIABLE = auto()  # 变量/标识符
    OPERATOR = auto()  # 运算符
    FUNCTION = auto()  # 函数名
    LPAREN = auto()  # 左括号
    RPAREN = auto()  # 右括号
    COMMA = auto()  # 逗号
    EOF = auto()  # 结束符


@dataclass
class Token:
    """
    词法单元

    Attributes:
        type: Token类型
        value: Token值
        position: 在原始表达式中的位置
    """
    type: TokenType
    value: any
    position: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, pos={self.position})"


class Tokenizer:
    """
    词法分析器

    将表达式字符串转换为Token序列。
    """

    # 正则表达式模式
    PATTERNS = {
        'NUMBER': r'\d+(\.\d+)?([eE][+-]?\d+)?',  # 支持科学计数法
        'IDENTIFIER': r'[a-zA-Z_]\w*',
        'COMPARISON_OPERATOR': r'(<=|>=|==|!=|<|>)',  # 比较运算符
        'OPERATOR': r'[+\-*/^]',
        'LPAREN': r'\(',
        'RPAREN': r'\)',
        'COMMA': r',',
        'WHITESPACE': r'\s+',
    }

    def __init__(self, expression: str):
        """
        初始化词法分析器

        Args:
            expression: 要分析的表达式字符串
        """
        self.expression = expression
        self.position = 0
        self.tokens: List[Token] = []

    def tokenize(self) -> List[Token]:
        """
        执行词法分析

        Returns:
            Token列表

        Raises:
            TokenizationError: 遇到非法字符时
        """
        self.position = 0
        self.tokens = []

        while self.position < len(self.expression):
            # 跳过空白
            if self._match_pattern('WHITESPACE'):
                continue

            # 匹配数字
            if self._match_number():
                continue

            # 先匹配比较运算符（因为它们可能包含单字符运算符）
            if self._match_comparison_operator():
                continue

            # 匹配标识符
            if self._match_identifier():
                continue

            # 匹配算术运算符
            if self._match_operator():
                continue

            # 匹配单字符标记
            elif self._match_single_char('(', TokenType.LPAREN):
                continue
            elif self._match_single_char(')', TokenType.RPAREN):
                continue
            elif self._match_single_char(',', TokenType.COMMA):
                continue
            else:
                # 非法字符
                char = self.expression[self.position]
                raise TokenizationError(
                    f"非法字符 '{char}'",
                    position=self.position,
                    expression=self.expression
                )

        # 添加EOF标记
        self.tokens.append(Token(TokenType.EOF, None, len(self.expression)))
        return self.tokens

    def _match_pattern(self, pattern_name: str) -> Optional[str]:
        """匹配指定的正则表达式模式"""
        pattern = self.PATTERNS[pattern_name]
        regex = re.compile(pattern)
        match = regex.match(self.expression, self.position)

        if match:
            matched_text = match.group(0)
            self.position = match.end()
            return matched_text
        return None

    def _match_number(self) -> bool:
        """匹配数字"""
        start_pos = self.position
        matched = self._match_pattern('NUMBER')

        if matched:
            try:
                value = float(matched)
                self.tokens.append(Token(TokenType.NUMBER, value, start_pos))
                return True
            except ValueError:
                raise TokenizationError(
                    f"无效的数字格式: {matched}",
                    position=start_pos,
                    expression=self.expression
                )
        return False

    def _match_identifier(self) -> bool:
        """匹配标识符（变量或函数名）"""
        start_pos = self.position
        matched = self._match_pattern('IDENTIFIER')

        if matched:
            # 向前查看是否跟着左括号（判断是否为函数）
            # 跳过空白
            temp_pos = self.position
            while temp_pos < len(self.expression) and self.expression[temp_pos].isspace():
                temp_pos += 1

            if temp_pos < len(self.expression) and self.expression[temp_pos] == '(':
                token_type = TokenType.FUNCTION
            else:
                token_type = TokenType.VARIABLE

            self.tokens.append(Token(token_type, matched, start_pos))
            return True
        return False

    def _match_comparison_operator(self) -> bool:
        """匹配比较运算符"""
        start_pos = self.position
        matched = self._match_pattern('COMPARISON_OPERATOR')
        
        if matched:
            # 比较运算符也用OPERATOR类型，这样可以统一处理
            self.tokens.append(Token(TokenType.OPERATOR, matched, start_pos))
            return True
        return False

    def _match_operator(self) -> bool:
        """匹配算术运算符"""
        start_pos = self.position
        matched = self._match_pattern('OPERATOR')

        if matched:
            self.tokens.append(Token(TokenType.OPERATOR, matched, start_pos))
            return True
        return False

    def _match_single_char(self, char: str, token_type: TokenType) -> bool:
        """匹配单个字符"""
        if self.position < len(self.expression) and self.expression[self.position] == char:
            self.tokens.append(Token(token_type, char, self.position))
            self.position += 1
            return True
        return False
