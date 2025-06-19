# tests/test_expression_parser.py
"""
表达式解析器单元测试

测试ExpressionParser的所有功能。
"""


# 添加项目路径

import unittest
import math
from unittest.mock import patch

from xwe.engine.expression import (
    ExpressionParser,
    ExpressionError,
    TokenizationError,
    ParseError,
    EvaluationError,
    ValidationError,
    FunctionError
)


class TestExpressionParser(unittest.TestCase):
    """ExpressionParser测试类"""

    def setUp(self):
        """每个测试前的设置"""
        self.parser = ExpressionParser()
        self.debug_parser = ExpressionParser(debug=True)

    # === 基本算术测试 ===

    def test_addition(self):
        """测试加法运算"""
        self.assertAlmostEqual(self.parser.evaluate("2 + 3"), 5.0)
        self.assertAlmostEqual(self.parser.evaluate("1.5 + 2.5"), 4.0)
        self.assertAlmostEqual(self.parser.evaluate("0 + 0"), 0.0)

    def test_subtraction(self):
        """测试减法运算"""
        self.assertAlmostEqual(self.parser.evaluate("10 - 3"), 7.0)
        self.assertAlmostEqual(self.parser.evaluate("5.5 - 2.3"), 3.2, places=1)
        self.assertAlmostEqual(self.parser.evaluate("0 - 5"), -5.0)

    def test_multiplication(self):
        """测试乘法运算"""
        self.assertAlmostEqual(self.parser.evaluate("4 * 5"), 20.0)
        self.assertAlmostEqual(self.parser.evaluate("2.5 * 4"), 10.0)
        self.assertAlmostEqual(self.parser.evaluate("0 * 100"), 0.0)

    def test_division(self):
        """测试除法运算"""
        self.assertAlmostEqual(self.parser.evaluate("10 / 2"), 5.0)
        self.assertAlmostEqual(self.parser.evaluate("7 / 2"), 3.5)
        self.assertAlmostEqual(self.parser.evaluate("1 / 3"), 1 / 3)

    def test_power(self):
        """测试幂运算"""
        self.assertAlmostEqual(self.parser.evaluate("2 ^ 3"), 8.0)
        self.assertAlmostEqual(self.parser.evaluate("4 ^ 0.5"), 2.0)
        self.assertAlmostEqual(self.parser.evaluate("10 ^ 0"), 1.0)

    # === 运算符优先级测试 ===

    def test_operator_precedence(self):
        """测试运算符优先级"""
        # 乘除优先于加减
        self.assertAlmostEqual(self.parser.evaluate("2 + 3 * 4"), 14.0)
        self.assertAlmostEqual(self.parser.evaluate("10 - 6 / 2"), 7.0)

        # 幂运算优先级最高
        self.assertAlmostEqual(self.parser.evaluate("2 * 3 ^ 2"), 18.0)
        self.assertAlmostEqual(self.parser.evaluate("2 ^ 3 * 2"), 16.0)

    def test_parentheses(self):
        """测试括号优先级"""
        self.assertAlmostEqual(self.parser.evaluate("(2 + 3) * 4"), 20.0)
        self.assertAlmostEqual(self.parser.evaluate("2 * (3 + 4)"), 14.0)
        self.assertAlmostEqual(self.parser.evaluate("((2 + 3) * (4 + 5))"), 45.0)

    # === 变量测试 ===

    def test_simple_variables(self):
        """测试简单变量"""
        context = {"x": 10, "y": 5}
        self.assertAlmostEqual(self.parser.evaluate("x", context), 10.0)
        self.assertAlmostEqual(self.parser.evaluate("x + y", context), 15.0)
        self.assertAlmostEqual(self.parser.evaluate("x * y", context), 50.0)

    def test_complex_variable_names(self):
        """测试复杂变量名"""
        context = {
            "base_damage": 100,
            "skill_mult_1": 1.5,
            "enemy_defense": 30
        }
        expr = "base_damage * skill_mult_1 - enemy_defense"
        self.assertAlmostEqual(self.parser.evaluate(expr, context), 120.0)

    def test_undefined_variable(self):
        """测试未定义变量"""
        with self.assertRaises(EvaluationError) as cm:
            self.parser.evaluate("undefined_var")
        self.assertIn("未定义的变量", str(cm.exception))

    # === 内置函数测试 ===

    def test_min_max_functions(self):
        """测试min/max函数"""
        self.assertAlmostEqual(self.parser.evaluate("min(1, 2, 3)"), 1.0)
        self.assertAlmostEqual(self.parser.evaluate("max(1, 2, 3)"), 3.0)
        self.assertAlmostEqual(self.parser.evaluate("min(5, 2, 8, 1, 9)"), 1.0)
        self.assertAlmostEqual(self.parser.evaluate("max(5, 2, 8, 1, 9)"), 9.0)

    def test_abs_function(self):
        """测试abs函数"""
        self.assertAlmostEqual(self.parser.evaluate("abs(-5)"), 5.0)
        self.assertAlmostEqual(self.parser.evaluate("abs(3.5)"), 3.5)
        self.assertAlmostEqual(self.parser.evaluate("abs(0)"), 0.0)

    def test_sqrt_function(self):
        """测试sqrt函数"""
        self.assertAlmostEqual(self.parser.evaluate("sqrt(16)"), 4.0)
        self.assertAlmostEqual(self.parser.evaluate("sqrt(2)"), math.sqrt(2))
        self.assertAlmostEqual(self.parser.evaluate("sqrt(0)"), 0.0)

    def test_ceil_floor_functions(self):
        """测试ceil/floor函数"""
        self.assertAlmostEqual(self.parser.evaluate("ceil(3.2)"), 4.0)
        self.assertAlmostEqual(self.parser.evaluate("floor(3.8)"), 3.0)
        self.assertAlmostEqual(self.parser.evaluate("ceil(-3.2)"), -3.0)
        self.assertAlmostEqual(self.parser.evaluate("floor(-3.8)"), -4.0)

    def test_rand_function(self):
        """测试rand函数"""
        # 测试返回值在范围内
        for _ in range(10):
            result = self.parser.evaluate("rand(1, 10)")
            self.assertGreaterEqual(result, 1)
            self.assertLessEqual(result, 10)

        # 测试参数顺序无关
        for _ in range(10):
            result = self.parser.evaluate("rand(10, 1)")
            self.assertGreaterEqual(result, 1)
            self.assertLessEqual(result, 10)

    def test_ifelse_function(self):
        """测试ifelse函数"""
        self.assertAlmostEqual(self.parser.evaluate("ifelse(1, 10, 20)"), 10.0)
        self.assertAlmostEqual(self.parser.evaluate("ifelse(0, 10, 20)"), 20.0)

        context = {"health": 30, "max_health": 100}
        expr = "ifelse(health < max_health * 0.5, 100, 50)"
        self.assertAlmostEqual(self.parser.evaluate(expr, context), 100.0)

    # === 复杂表达式测试 ===

    def test_nested_functions(self):
        """测试嵌套函数调用"""
        expr = "max(abs(-5), min(10, 3))"
        self.assertAlmostEqual(self.parser.evaluate(expr), 5.0)

        expr = "sqrt(max(16, min(25, 20)))"
        # min(25, 20) = 20, max(16, 20) = 20, sqrt(20) = 4.472...
        self.assertAlmostEqual(self.parser.evaluate(expr), math.sqrt(20))

    def test_game_damage_formula(self):
        """测试游戏伤害公式"""
        context = {
            "base_atk": 100,
            "skill_mult": 1.5,
            "crit": 1,
            "crit_dmg": 2.0,
            "enemy_def": 30
        }

        # 基础伤害公式
        formula = "base_atk * skill_mult - enemy_def"
        self.assertAlmostEqual(self.parser.evaluate(formula, context), 120.0)

        # 包含暴击的伤害公式
        formula = "base_atk * skill_mult * ifelse(crit, crit_dmg, 1) - enemy_def"
        self.assertAlmostEqual(self.parser.evaluate(formula, context), 270.0)

        # 保证最小伤害为1
        formula = "max(1, base_atk * skill_mult * ifelse(crit, crit_dmg, 1) - enemy_def)"
        self.assertAlmostEqual(self.parser.evaluate(formula, context), 270.0)

    # === 错误处理测试 ===

    def test_empty_expression(self):
        """测试空表达式"""
        with self.assertRaises(ExpressionError):
            self.parser.evaluate("")
        with self.assertRaises(ExpressionError):
            self.parser.evaluate("   ")

    def test_division_by_zero(self):
        """测试除零错误"""
        with self.assertRaises(EvaluationError) as cm:
            self.parser.evaluate("1 / 0")
        self.assertIn("除零", str(cm.exception))

    def test_syntax_errors(self):
        """测试语法错误"""
        invalid_expressions = [
            "2 ++ 3",
            "2 * * 3",
            "max(1 2)",
            "1 + + 2",
            "())",
            "((1 + 2)",
        ]

        for expr in invalid_expressions:
            with self.assertRaises(ExpressionError):
                self.parser.evaluate(expr)

    def test_function_errors(self):
        """测试函数调用错误"""
        # 未定义的函数
        with self.assertRaises(FunctionError) as cm:
            self.parser.evaluate("undefined_func(1)")
        self.assertIn("未定义的函数", str(cm.exception))

        # 参数数量错误
        with self.assertRaises(FunctionError) as cm:
            self.parser.evaluate("sqrt()")
        self.assertIn("期望 1 个参数", str(cm.exception))

        with self.assertRaises(FunctionError) as cm:
            self.parser.evaluate("sqrt(1, 2)")
        self.assertIn("期望 1 个参数", str(cm.exception))

    def test_tokenization_errors(self):
        """测试词法分析错误"""
        with self.assertRaises(TokenizationError) as cm:
            self.parser.evaluate("2 @ 3")
        self.assertIn("非法字符", str(cm.exception))

    # === 表达式验证测试 ===

    def test_validate_valid_expressions(self):
        """测试合法表达式验证"""
        valid_expressions = [
            "2 + 3",
            "x * y",
            "max(a, b, c)",
            "sqrt(x) + abs(y)",
            "(a + b) * (c - d)",
            "ifelse(x > 0, x, -x)"
        ]

        for expr in valid_expressions:
            self.assertTrue(self.parser.validate(expr),
                            f"Expression '{expr}' should be valid")

    def test_validate_invalid_expressions(self):
        """测试非法表达式验证"""
        invalid_expressions = [
            "2 ++ 3",
            "max(a b)",
            "1 / / 2",
            "__import__('os')",
            "eval('code')",
            "exec('code')",
            "",
            "   ",
        ]

        for expr in invalid_expressions:
            self.assertFalse(self.parser.validate(expr),
                             f"Expression '{expr}' should be invalid")

    def test_validate_with_error(self):
        """测试带错误信息的验证"""
        # 测试括号不匹配
        with self.assertRaises(ValidationError) as cm:
            self.parser.validate_with_error("((1 + 2)")
        self.assertIn("缺少", str(cm.exception))

        # 测试危险模式
        with self.assertRaises(ValidationError) as cm:
            self.parser.validate_with_error("__import__('os')")
        self.assertIn("不安全", str(cm.exception))

    # === 自定义函数测试 ===

    def test_register_custom_function(self):
        """测试注册自定义函数"""
        # 注册简单函数
        self.parser.register_function("double", lambda x: x * 2, 1)
        self.assertAlmostEqual(self.parser.evaluate("double(5)"), 10.0)

        # 注册可变参数函数
        self.parser.register_function("avg",
                                      lambda *args: sum(args) / len(args) if args else 0,
                                      -1)
        self.assertAlmostEqual(self.parser.evaluate("avg(1, 2, 3, 4, 5)"), 3.0)

    def test_register_function_errors(self):
        """测试注册函数错误"""
        # 无效函数名
        with self.assertRaises(ValueError):
            self.parser.register_function("", lambda x: x, 1)

        with self.assertRaises(ValueError):
            self.parser.register_function("123invalid", lambda x: x, 1)

        # 覆盖内置函数
        with self.assertRaises(ValueError):
            self.parser.register_function("max", lambda x: x, 1)

        # 注册重复的自定义函数
        self.parser.register_function("dup", lambda x: x * 2, 1)
        with self.assertRaises(ValueError):
            self.parser.register_function("dup", lambda x: x + 2, 1)

    # === 一元运算符测试 ===

    def test_unary_operators(self):
        """测试一元运算符"""
        self.assertAlmostEqual(self.parser.evaluate("-5"), -5.0)
        self.assertAlmostEqual(self.parser.evaluate("+5"), 5.0)
        self.assertAlmostEqual(self.parser.evaluate("-(-5)"), 5.0)
        self.assertAlmostEqual(self.parser.evaluate("-(2 + 3)"), -5.0)

        context = {"x": 10}
        self.assertAlmostEqual(self.parser.evaluate("-x", context), -10.0)

    # === 调试模式测试 ===

    def test_debug_mode(self):
        """测试调试模式"""
        # 在调试模式下应该有日志输出
        with patch('xwe.engine.expression.parser.logger') as mock_logger:
            debug_parser = ExpressionParser(debug=True)
            debug_parser.evaluate("2 + 3")

            # 验证有调试日志
            self.assertTrue(mock_logger.debug.called)

    # === 边界情况测试 ===

    def test_edge_cases(self):
        """测试边界情况"""
        # 多层括号
        self.assertAlmostEqual(self.parser.evaluate("(((2 + 3)))"), 5.0)

        # 大数值
        self.assertAlmostEqual(self.parser.evaluate("1e6 + 1"), 1000001.0)

        # 极小数值
        self.assertAlmostEqual(self.parser.evaluate("1e-6 + 1"), 1.000001)

        # 连续运算
        self.assertAlmostEqual(self.parser.evaluate("1 + 2 + 3 + 4 + 5"), 15.0)

    # === 性能测试 ===

    def test_performance(self):
        """测试性能基准"""
        import time

        # 准备测试数据
        complex_expr = "max(abs(x - y), min(x * 2, y * 3)) + sqrt(x ^ 2 + y ^ 2)"
        context = {"x": 3, "y": 4}

        # 预热
        for _ in range(100):
            self.parser.evaluate(complex_expr, context)

        # 计时
        iterations = 1000
        start = time.time()
        for _ in range(iterations):
            self.parser.evaluate(complex_expr, context)
        elapsed = time.time() - start

        avg_time = elapsed / iterations * 1000  # 毫秒

        # 确保性能在合理范围内
        self.assertLess(avg_time, 5.0,
                        f"平均求值时间过长: {avg_time:.3f}ms")

        print(f"\n性能测试: 平均求值时间 {avg_time:.3f}ms")


class TestExpressionErrorDisplay(unittest.TestCase):
    """测试错误显示功能"""

    def test_error_position_display(self):
        """测试错误位置显示"""
        parser = ExpressionParser()

        try:
            parser.evaluate("2 + @ 3")
        except ExpressionError as e:
            error_str = str(e)
            self.assertIn("@", error_str)
            self.assertIn("^", error_str)  # 错误位置指示器


if __name__ == "__main__":
    unittest.main(verbosity=2)