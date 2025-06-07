"""
公式解析-执行引擎 —— FormulaEngine
安全地解析和执行数学表达式
"""

import ast
import operator
import math
import random
from typing import Dict, Any, Union, Optional, Callable
import logging
from .data_manager_v3 import DM

logger = logging.getLogger(__name__)


class FormulaEngine:
    """
    公式解析和执行引擎
    支持安全的数学表达式计算，不使用eval()
    """
    
    # 支持的运算符
    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
        ast.Mod: operator.mod,
    }
    
    # 支持的比较运算符
    COMPARISONS = {
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
    }
    
    # 支持的内置函数
    FUNCTIONS = {
        'abs': abs,
        'min': min,
        'max': max,
        'round': round,
        'floor': math.floor,
        'ceil': math.ceil,
        'sqrt': math.sqrt,
        'pow': pow,
        'random': random.random,
        'randint': random.randint,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'log': math.log,
        'exp': math.exp,
    }
    
    def __init__(self):
        self._formula_cache = {}
        self._compiled_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # 加载公式库
        self._load_formula_library()
    
    def _load_formula_library(self):
        """加载公式库配置"""
        try:
            self.formula_library = DM.load("formula_library")
            self.formulas = {f["id"]: f for f in self.formula_library.get("formulas", [])}
            logger.info(f"Loaded {len(self.formulas)} formulas from library")
        except Exception as e:
            logger.error(f"Failed to load formula library: {e}")
            self.formulas = {}
    
    def execute(self, formula_id: str, context: Dict[str, Union[float, int]]) -> float:
        """
        执行预定义的公式
        
        Args:
            formula_id: 公式ID
            context: 变量上下文
            
        Returns:
            计算结果
        """
        if formula_id not in self.formulas:
            raise ValueError(f"Formula not found: {formula_id}")
        
        formula = self.formulas[formula_id]
        expression = formula["expression"]
        
        # 添加默认值
        full_context = self._prepare_context(formula, context)
        
        # 计算表达式
        result = self.evaluate(expression, full_context)
        
        # 应用约束
        if "constraints" in formula:
            result = self._apply_constraints(result, formula["constraints"])
        
        return float(result)
    
    def evaluate(self, expression: str, context: Dict[str, Any]) -> Union[float, int]:
        """
        安全地计算数学表达式
        
        Args:
            expression: 数学表达式字符串
            context: 变量上下文
            
        Returns:
            计算结果
        """
        # 生成缓存键
        cache_key = f"{expression}:{sorted(context.items())}"
        
        # 检查缓存
        if cache_key in self._formula_cache:
            self.cache_hits += 1
            return self._formula_cache[cache_key]
        
        self.cache_misses += 1
        
        try:
            # 解析表达式
            if expression not in self._compiled_cache:
                tree = ast.parse(expression, mode='eval')
                self._validate_ast(tree)
                self._compiled_cache[expression] = tree
            else:
                tree = self._compiled_cache[expression]
            
            # 计算结果
            result = self._eval_node(tree.body, context)
            
            # 缓存结果
            self._formula_cache[cache_key] = result
            
            # 限制缓存大小
            if len(self._formula_cache) > 10000:
                # 清除一半缓存
                keys = list(self._formula_cache.keys())[:5000]
                for key in keys:
                    del self._formula_cache[key]
            
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating expression '{expression}': {e}")
            raise
    
    def _validate_ast(self, tree: ast.AST):
        """验证AST树的安全性"""
        for node in ast.walk(tree):
            # 只允许特定的节点类型
            allowed_types = (
                ast.Module, ast.Expr, ast.Expression,
                ast.Load, ast.Name, ast.Constant, ast.Num, ast.Str,
                ast.BinOp, ast.UnaryOp, ast.Compare,
                ast.Call, ast.keyword,
                ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod,
                ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
                ast.USub, ast.UAdd,
                ast.IfExp,  # 支持三元表达式
            )
            
            if not isinstance(node, allowed_types):
                raise ValueError(f"Unsafe node type: {type(node).__name__}")
            
            # 检查函数调用
            if isinstance(node, ast.Call):
                if not isinstance(node.func, ast.Name):
                    raise ValueError("Only direct function calls allowed")
                if node.func.id not in self.FUNCTIONS:
                    raise ValueError(f"Unknown function: {node.func.id}")
    
    def _eval_node(self, node: ast.AST, context: Dict[str, Any]) -> Union[float, int, bool]:
        """递归计算AST节点"""
        if isinstance(node, ast.Constant):
            return node.value
        
        elif isinstance(node, ast.Num):  # 兼容旧版本
            return node.n
        
        elif isinstance(node, ast.Name):
            if node.id in context:
                return context[node.id]
            else:
                # 尝试从点分隔的路径获取值
                for key, value in context.items():
                    if isinstance(value, dict) and node.id in value:
                        return value[node.id]
                raise NameError(f"Variable not found: {node.id}")
        
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, context)
            right = self._eval_node(node.right, context)
            op_func = self.OPERATORS.get(type(node.op))
            if op_func:
                return op_func(left, right)
            else:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, context)
            op_func = self.OPERATORS.get(type(node.op))
            if op_func:
                return op_func(operand)
            else:
                raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
        
        elif isinstance(node, ast.Compare):
            left = self._eval_node(node.left, context)
            for op, comparator in zip(node.ops, node.comparators):
                right = self._eval_node(comparator, context)
                op_func = self.COMPARISONS.get(type(op))
                if op_func:
                    if not op_func(left, right):
                        return False
                    left = right
                else:
                    raise ValueError(f"Unsupported comparison: {type(op).__name__}")
            return True
        
        elif isinstance(node, ast.Call):
            func_name = node.func.id
            if func_name not in self.FUNCTIONS:
                raise ValueError(f"Unknown function: {func_name}")
            
            # 计算参数
            args = [self._eval_node(arg, context) for arg in node.args]
            
            # 调用函数
            return self.FUNCTIONS[func_name](*args)
        
        elif isinstance(node, ast.IfExp):
            # 三元表达式: a if condition else b
            condition = self._eval_node(node.test, context)
            if condition:
                return self._eval_node(node.body, context)
            else:
                return self._eval_node(node.orelse, context)
        
        else:
            raise ValueError(f"Unsupported node type: {type(node).__name__}")
    
    def _prepare_context(self, formula: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备计算上下文，添加默认值
        
        Args:
            formula: 公式定义
            context: 用户提供的上下文
            
        Returns:
            完整的上下文
        """
        full_context = context.copy()
        
        # 添加默认变量值
        if "default_values" in formula:
            for var, default in formula["default_values"].items():
                if var not in full_context:
                    full_context[var] = default
        
        # 添加常量
        if "constants" in formula:
            full_context.update(formula["constants"])
        
        return full_context
    
    def _apply_constraints(self, value: float, constraints: Dict[str, Any]) -> float:
        """
        应用约束条件
        
        Args:
            value: 原始值
            constraints: 约束条件
            
        Returns:
            约束后的值
        """
        if "min" in constraints:
            value = max(value, constraints["min"])
        
        if "max" in constraints:
            value = min(value, constraints["max"])
        
        if "round" in constraints:
            decimals = constraints["round"]
            value = round(value, decimals)
        
        return value
    
    def register_custom_function(self, name: str, func: Callable):
        """
        注册自定义函数
        
        Args:
            name: 函数名
            func: 函数对象
        """
        self.FUNCTIONS[name] = func
        logger.info(f"Registered custom function: {name}")
    
    def compile_expression(self, expression: str) -> ast.AST:
        """
        预编译表达式
        
        Args:
            expression: 表达式字符串
            
        Returns:
            编译后的AST
        """
        if expression not in self._compiled_cache:
            tree = ast.parse(expression, mode='eval')
            self._validate_ast(tree)
            self._compiled_cache[expression] = tree
        
        return self._compiled_cache[expression]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total if total > 0 else 0
        
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate,
            "cache_size": len(self._formula_cache),
            "compiled_size": len(self._compiled_cache)
        }


# 全局实例
formula_engine = FormulaEngine()

# 导出便捷函数
def calculate(formula_id: str, **kwargs) -> float:
    """计算公式的便捷函数"""
    return formula_engine.execute(formula_id, kwargs)

def evaluate_expression(expression: str, **kwargs) -> Union[float, int]:
    """计算表达式的便捷函数"""
    return formula_engine.evaluate(expression, kwargs)
