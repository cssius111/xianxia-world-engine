# xwe/core/optimizations/expression_jit.py

import ast
import types
from typing import Any, Callable, Dict, List
import time
import hashlib

class ExpressionJITCompiler:
    """表达式JIT编译器"""
    
    def __init__(self) -> None:
        self.compiled_functions = {}
        self.optimization_stats = {
            'compile_time': 0,
            'execution_speedup': []
        }
        
    def compile_expression(self, expr_id: str, expression: Dict[str, Any]) -> Callable:
        """将表达式编译为Python函数"""
        
        if expr_id in self.compiled_functions:
            return self.compiled_functions[expr_id]
            
        start_time = time.perf_counter()
        
        # 生成Python AST
        ast_node = self._expression_to_ast(expression)
        
        # 优化AST
        optimized_ast = self._optimize_ast(ast_node)
        
        # 生成函数
        func_ast = ast.FunctionDef(
            name=f'expr_{expr_id}',
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg='ctx', annotation=None)],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[]
            ),
            body=[ast.Return(value=optimized_ast)],
            decorator_list=[]
        )
        
        # 编译为字节码
        module = ast.Module(body=[func_ast], type_ignores=[])
        ast.fix_missing_locations(module)  # 修复位置信息
        code = compile(module, f'<expression_{expr_id}>', 'exec')
        
        # 执行得到函数
        namespace = {
            'min': min, 'max': max, 'abs': abs,
            'pow': pow, 'sqrt': __import__('math').sqrt
        }
        exec(code, namespace)
        
        compiled_func = namespace[f'expr_{expr_id}']
        self.compiled_functions[expr_id] = compiled_func
        
        compile_time = time.perf_counter() - start_time
        self.optimization_stats['compile_time'] += compile_time
        
        return compiled_func
        
    def _expression_to_ast(self, expr: Any) -> ast.AST:
        """将表达式转换为AST"""
        
        if isinstance(expr, dict):
            if 'constant' in expr:
                return ast.Constant(value=expr['constant'])
                
            elif 'attribute' in expr:
                # 将点号路径转换为属性访问
                parts = expr['attribute'].split('.')
                node = ast.Name(id='ctx', ctx=ast.Load())
                
                for part in parts:
                    node = ast.Subscript(
                        value=node,
                        slice=ast.Constant(value=part),
                        ctx=ast.Load()
                    )
                return node
                
            elif 'operation' in expr:
                op = expr['operation']
                operands = [self._expression_to_ast(operand) 
                           for operand in expr.get('operands', [])]
                
                # 二元运算
                if op in ['+', '-', '*', '/', '//', '%', '**']:
                    op_map = {
                        '+': ast.Add(), '-': ast.Sub(),
                        '*': ast.Mult(), '/': ast.Div(),
                        '//': ast.FloorDiv(), '%': ast.Mod(),
                        '**': ast.Pow()
                    }
                    
                    if len(operands) < 2:
                        raise ValueError(f"Operation {op} requires at least 2 operands")
                    
                    result = operands[0]
                    for operand in operands[1:]:
                        result = ast.BinOp(
                            left=result,
                            op=op_map[op],
                            right=operand
                        )
                    return result
                    
                # 函数调用
                elif op in ['min', 'max', 'abs', 'sqrt']:
                    return ast.Call(
                        func=ast.Name(id=op, ctx=ast.Load()),
                        args=operands,
                        keywords=[]
                    )
                    
        return ast.Constant(value=expr)
        
    def _optimize_ast(self, node: ast.AST) -> ast.AST:
        """优化AST"""
        optimizer = ASTOptimizer()
        return optimizer.visit(node)
        
    def get_stats(self) -> Dict[str, Any]:
        """获取优化统计信息"""
        return self.optimization_stats
        

class ASTOptimizer(ast.NodeTransformer):
    """AST优化器"""
    
    def visit_BinOp(self, node) -> Any:
        """优化二元运算"""
        self.generic_visit(node)
        
        # 常量折叠
        if (isinstance(node.left, ast.Constant) and 
            isinstance(node.right, ast.Constant)):
            
            left_val = node.left.value
            right_val = node.right.value
            
            if isinstance(node.op, ast.Add):
                return ast.Constant(value=left_val + right_val)
            elif isinstance(node.op, ast.Sub):
                return ast.Constant(value=left_val - right_val)
            elif isinstance(node.op, ast.Mult):
                return ast.Constant(value=left_val * right_val)
            elif isinstance(node.op, ast.Div) and right_val != 0:
                return ast.Constant(value=left_val / right_val)
            elif isinstance(node.op, ast.Mod) and right_val != 0:
                return ast.Constant(value=left_val % right_val)
            elif isinstance(node.op, ast.Pow):
                return ast.Constant(value=left_val ** right_val)
            
        # 代数简化
        # x * 1 => x
        if (isinstance(node.op, ast.Mult) and 
            isinstance(node.right, ast.Constant) and 
            node.right.value == 1):
            return node.left
            
        # x + 0 => x  
        if (isinstance(node.op, ast.Add) and 
            isinstance(node.right, ast.Constant) and 
            node.right.value == 0):
            return node.left
            
        # x * 0 => 0
        if (isinstance(node.op, ast.Mult) and 
            isinstance(node.right, ast.Constant) and 
            node.right.value == 0):
            return ast.Constant(value=0)
            
        # x ** 1 => x
        if (isinstance(node.op, ast.Pow) and 
            isinstance(node.right, ast.Constant) and 
            node.right.value == 1):
            return node.left
            
        # x ** 0 => 1
        if (isinstance(node.op, ast.Pow) and 
            isinstance(node.right, ast.Constant) and 
            node.right.value == 0):
            return ast.Constant(value=1)
            
        return node
        
    def visit_Call(self, node) -> Any:
        """优化函数调用"""
        self.generic_visit(node)
        
        # 常量函数调用折叠
        if isinstance(node.func, ast.Name) and all(isinstance(arg, ast.Constant) for arg in node.args):
            func_name = node.func.id
            arg_values = [arg.value for arg in node.args]
            
            try:
                if func_name == 'min':
                    return ast.Constant(value=min(*arg_values))
                elif func_name == 'max':
                    return ast.Constant(value=max(*arg_values))
                elif func_name == 'abs' and len(arg_values) == 1:
                    return ast.Constant(value=abs(arg_values[0]))
                elif func_name == 'sqrt' and len(arg_values) == 1:
                    import math
                    return ast.Constant(value=math.sqrt(arg_values[0]))
            except:
                pass
                
        return node


class ExpressionBenchmark:
    """表达式性能基准测试"""
    
    def __init__(self, jit_compiler: ExpressionJITCompiler) -> None:
        self.jit = jit_compiler
        self.results: Dict[str, Dict[str, Any]] = {}
        
    def benchmark_expression(self, expr_id: str, expression: Dict[str, Any], 
                           test_contexts: List[Dict], iterations: int = 10000) -> Dict:
        """基准测试单个表达式"""
        
        # 测试解释执行
        interpreter = SimpleExpressionInterpreter()
        
        start_time = time.perf_counter()
        for _ in range(iterations):
            for ctx in test_contexts:
                interpreter.evaluate(expression, ctx)
        interpret_time = time.perf_counter() - start_time
        
        # 测试JIT编译执行
        compiled_func = self.jit.compile_expression(expr_id, expression)
        
        start_time = time.perf_counter()
        for _ in range(iterations):
            for ctx in test_contexts:
                compiled_func(ctx)
        jit_time = time.perf_counter() - start_time
        
        speedup = interpret_time / jit_time if jit_time > 0 else 0
        
        result = {
            'expression_id': expr_id,
            'iterations': iterations * len(test_contexts),
            'interpret_time': interpret_time,
            'jit_time': jit_time,
            'speedup': speedup,
            'compile_time': self.jit.optimization_stats.get('compile_time', 0)
        }
        
        self.results[expr_id] = result
        return result
        
    def generate_report(self) -> str:
        """生成性能报告"""
        lines = ["表达式JIT性能报告", "=" * 40]
        
        for expr_id, result in self.results.items():
            lines.extend([
                f"\n表达式: {expr_id}",
                f"迭代次数: {result['iterations']}",
                f"解释执行时间: {result['interpret_time']:.4f}秒",
                f"JIT执行时间: {result['jit_time']:.4f}秒",
                f"加速比: {result['speedup']:.2f}x",
                f"编译时间: {result['compile_time']:.4f}秒"
            ])
            
        return "\n".join(lines)


class SimpleExpressionInterpreter:
    """简单的表达式解释器（用于对比）"""
    
    def evaluate(self, expression: Any, context: Dict[str, Any]) -> Any:
        if isinstance(expression, dict):
            if 'constant' in expression:
                return expression['constant']
            elif 'attribute' in expression:
                path = expression['attribute'].split('.')
                value = context
                for part in path:
                    value = value.get(part, 0) if isinstance(value, dict) else 0
                return value
            elif 'operation' in expression:
                op = expression['operation']
                operands = [self.evaluate(operand, context) 
                           for operand in expression.get('operands', [])]
                
                if op == '+':
                    return sum(operands)
                elif op == '-':
                    return operands[0] - sum(operands[1:]) if operands else 0
                elif op == '*':
                    result = 1
                    for v in operands:
                        result *= v
                    return result
                elif op == '/' and len(operands) >= 2 and operands[1] != 0:
                    return operands[0] / operands[1]
                elif op == 'max':
                    return max(operands) if operands else 0
                elif op == 'min':
                    return min(operands) if operands else 0
                    
        return expression
