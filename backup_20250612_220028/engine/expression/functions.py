# engine/expression/functions.py
"""
内置函数定义模块

定义表达式解析器的内置函数。
"""

import math
import random
from typing import Any, Callable, Dict


def create_builtin_functions() -> Dict[str, Dict[str, Any]]:
    """
    创建内置函数字典

    Returns:
        函数名到函数信息的映射
    """
    return {
        # 数学函数
        'min': {
            'args': -1,  # 可变参数
            'func': lambda *args: min(args) if args else 0,
            'description': '返回最小值'
        },
        'max': {
            'args': -1,
            'func': lambda *args: max(args) if args else 0,
            'description': '返回最大值'
        },
        'abs': {
            'args': 1,
            'func': abs,
            'description': '返回绝对值'
        },
        'sqrt': {
            'args': 1,
            'func': lambda x: math.sqrt(x) if x >= 0 else float('nan'),
            'description': '返回平方根'
        },
        'ceil': {
            'args': 1,
            'func': math.ceil,
            'description': '向上取整'
        },
        'floor': {
            'args': 1,
            'func': math.floor,
            'description': '向下取整'
        },

        # 随机函数
        'rand': {
            'args': 2,
            'func': lambda a, b: random.uniform(min(a, b), max(a, b)),
            'description': '返回[a,b]范围内的随机数'
        },

        # 条件函数
        'ifelse': {
            'args': 3,
            'func': lambda cond, true_val, false_val: true_val if cond else false_val,
            'description': '条件判断，如果条件为真返回第二个参数，否则返回第三个参数'
        },

        # 扩展数学函数
        'pow': {
            'args': 2,
            'func': pow,
            'description': '幂运算'
        },
        'log': {
            'args': 1,
            'func': math.log,
            'description': '自然对数'
        },
        'log10': {
            'args': 1,
            'func': math.log10,
            'description': '以10为底的对数'
        },
        'sin': {
            'args': 1,
            'func': math.sin,
            'description': '正弦函数'
        },
        'cos': {
            'args': 1,
            'func': math.cos,
            'description': '余弦函数'
        },
        'tan': {
            'args': 1,
            'func': math.tan,
            'description': '正切函数'
        },

        # 实用函数
        'round': {
            'args': 2,
            'func': lambda x, n=0: round(x, int(n)),
            'description': '四舍五入到指定小数位'
        },
        'clamp': {
            'args': 3,
            'func': lambda x, min_val, max_val: max(min_val, min(x, max_val)),
            'description': '将值限制在指定范围内'
        },
    }