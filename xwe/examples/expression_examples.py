# examples/expression_examples.py
"""
表达式解析器使用示例

展示ExpressionParser的各种使用场景。
"""

from engine.expression import ExpressionParser, ExpressionError


def basic_examples():
    """基础使用示例"""
    print("=== 基础算术运算 ===")
    parser = ExpressionParser()

    # 简单运算
    print(f"2 + 3 = {parser.evaluate('2 + 3')}")
    print(f"10 - 4 = {parser.evaluate('10 - 4')}")
    print(f"5 * 6 = {parser.evaluate('5 * 6')}")
    print(f"15 / 3 = {parser.evaluate('15 / 3')}")
    print(f"2 ^ 8 = {parser.evaluate('2 ^ 8')}")

    # 运算符优先级
    print(f"\n2 + 3 * 4 = {parser.evaluate('2 + 3 * 4')}")
    print(f"(2 + 3) * 4 = {parser.evaluate('(2 + 3) * 4')}")


def variable_examples():
    """变量使用示例"""
    print("\n=== 变量使用 ===")
    parser = ExpressionParser()

    # 角色属性计算
    character = {
        "level": 10,
        "strength": 50,
        "agility": 30,
        "intelligence": 25
    }

    # 物理攻击力 = 力量 * 2 + 等级 * 5
    phys_attack = parser.evaluate("strength * 2 + level * 5", character)
    print(f"物理攻击力: {phys_attack}")

    # 魔法攻击力 = 智力 * 3 + 等级 * 3
    magic_attack = parser.evaluate("intelligence * 3 + level * 3", character)
    print(f"魔法攻击力: {magic_attack}")

    # 闪避率 = 敏捷 / 200
    evasion = parser.evaluate("agility / 200", character)
    print(f"闪避率: {evasion:.2%}")


def function_examples():
    """内置函数使用示例"""
    print("\n=== 内置函数 ===")
    parser = ExpressionParser()

    # 数学函数
    print(f"min(10, 5, 8) = {parser.evaluate('min(10, 5, 8)')}")
    print(f"max(10, 5, 8) = {parser.evaluate('max(10, 5, 8)')}")
    print(f"abs(-15) = {parser.evaluate('abs(-15)')}")
    print(f"sqrt(64) = {parser.evaluate('sqrt(64)')}")
    print(f"ceil(3.2) = {parser.evaluate('ceil(3.2)')}")
    print(f"floor(3.8) = {parser.evaluate('floor(3.8)')}")

    # 随机函数
    print(f"\n随机伤害 (90-110):")
    for i in range(5):
        damage = parser.evaluate("rand(90, 110)")
        print(f"  第{i + 1}次: {damage:.1f}")

    # 条件函数
    context = {"health": 30, "max_health": 100}
    is_low_health = parser.evaluate(
        "ifelse(health < max_health * 0.3, 1, 0)",
        context
    )
    print(f"\n低血量状态: {'是' if is_low_health else '否'}")


def game_formula_examples():
    """游戏公式示例"""
    print("\n=== 游戏公式计算 ===")
    parser = ExpressionParser()

    # 战斗场景
    attacker = {
        "base_attack": 100,
        "weapon_damage": 50,
        "skill_multiplier": 1.5,
        "critical_rate": 0.3,
        "critical_damage": 2.0,
        "is_critical": 0  # 这次攻击是否暴击
    }

    defender = {
        "defense": 40,
        "armor": 20,
        "damage_reduction": 0.1
    }

    # 合并上下文
    combat_context = {**attacker, **defender}

    # 基础伤害计算
    base_damage_formula = "(base_attack + weapon_damage) * skill_multiplier"
    base_damage = parser.evaluate(base_damage_formula, combat_context)
    print(f"基础伤害: {base_damage}")

    # 考虑防御的伤害
    actual_damage_formula = """
        max(1, 
            (base_attack + weapon_damage) * skill_multiplier 
            - (defense + armor)
        ) * (1 - damage_reduction)
    """
    actual_damage = parser.evaluate(actual_damage_formula, combat_context)
    print(f"实际伤害: {actual_damage}")

    # 暴击伤害
    combat_context["is_critical"] = 1
    crit_damage_formula = """
        max(1, 
            (base_attack + weapon_damage) * skill_multiplier 
            * ifelse(is_critical, critical_damage, 1)
            - (defense + armor)
        ) * (1 - damage_reduction)
    """
    crit_damage = parser.evaluate(crit_damage_formula, combat_context)
    print(f"暴击伤害: {crit_damage}")


def custom_function_examples():
    """自定义函数示例"""
    print("\n=== 自定义函数 ===")
    parser = ExpressionParser()

    # 注册游戏专用函数

    # 1. 属性加成函数
    def attribute_bonus(base, bonus_percent):
        """计算属性加成后的值"""
        return base * (1 + bonus_percent / 100)

    parser.register_function("attr_bonus", attribute_bonus, 2,
                             "计算百分比加成后的属性值")

    # 2. 伤害减免函数
    def damage_mitigation(damage, defense, reduction_percent):
        """计算减免后的伤害"""
        mitigated = damage - defense
        mitigated = max(1, mitigated)  # 最小伤害为1
        return mitigated * (1 - reduction_percent / 100)

    parser.register_function("mitigate", damage_mitigation, 3,
                             "计算防御和减免后的伤害")

    # 使用自定义函数
    print("基础攻击力 100，装备加成 50%:")
    enhanced_attack = parser.evaluate("attr_bonus(100, 50)")
    print(f"  强化后攻击力: {enhanced_attack}")

    print("\n伤害 200，防御 50，减免 20%:")
    final_damage = parser.evaluate("mitigate(200, 50, 20)")
    print(f"  最终伤害: {final_damage}")


def error_handling_examples():
    """错误处理示例"""
    print("\n=== 错误处理 ===")
    parser = ExpressionParser()

    test_cases = [
        ("", "空表达式"),
        ("undefined_var", "未定义变量"),
        ("1 / 0", "除零错误"),
        ("2 ++ 3", "语法错误"),
        ("max()", "函数参数错误"),
        ("2 @ 3", "非法字符"),
    ]

    for expr, description in test_cases:
        try:
            result = parser.evaluate(expr)
            print(f"{description}: {result}")
        except ExpressionError as e:
            print(f"{description}: {type(e).__name__} - {e}")


def validation_examples():
    """表达式验证示例"""
    print("\n=== 表达式验证 ===")
    parser = ExpressionParser()

    expressions = [
        "2 + 3 * 4",
        "max(a, b, c)",
        "sqrt(x^2 + y^2)",
        "2 ++ 3",
        "__import__('os')",
        "",
    ]

    for expr in expressions:
        is_valid = parser.validate(expr)
        status = "✓ 合法" if is_valid else "✗ 非法"
        print(f"{status}: {expr}")

        # 获取详细错误信息
        if not is_valid and expr:
            try:
                parser.validate_with_error(expr)
            except ExpressionError as e:
                print(f"       错误: {e}")


def debug_mode_example():
    """调试模式示例"""
    print("\n=== 调试模式 ===")

    # 启用调试模式
    debug_parser = ExpressionParser(debug=True)

    context = {
        "base_damage": 100,
        "multiplier": 1.5,
        "bonus": 20
    }

    print("计算: base_damage * multiplier + bonus")
    result = debug_parser.evaluate("base_damage * multiplier + bonus", context)
    print(f"结果: {result}")


def main():
    """运行所有示例"""
    print("XWE 表达式解析器示例")
    print("=" * 50)

    basic_examples()
    variable_examples()
    function_examples()
    game_formula_examples()
    custom_function_examples()
    error_handling_examples()
    validation_examples()
    debug_mode_example()

    print("\n" + "=" * 50)
    print("示例运行完成！")


if __name__ == "__main__":
    main()