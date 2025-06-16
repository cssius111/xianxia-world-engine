#!/usr/bin/env python3
# @dev_only
"""
验证游戏平衡性修复和UI优化
"""
import os
import sys
import json

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def verify_combat_balance():
    """验证战斗系统平衡性修复"""
    print("🗡️  验证战斗系统平衡性...")
    
    # 读取战斗系统配置
    combat_path = os.path.join(project_root, "xwe/data/restructured/combat_system.json")
    with open(combat_path, 'r', encoding='utf-8') as f:
        combat_data = json.load(f)
    
    # 检查元素伤害倍率
    elements = combat_data["elemental_system"]["basic_elements"]
    for element, data in elements.items():
        damage_bonus = data["damage_bonus"]
        if damage_bonus == 1.2:
            print(f"  ✅ {element} 元素伤害倍率已调整为: {damage_bonus}")
        else:
            print(f"  ❌ {element} 元素伤害倍率异常: {damage_bonus}")
    
    # 检查暴击倍率
    crit_multiplier = combat_data["attack_resolution"]["hit_calculation"]["critical_hit"]["damage_multiplier"]
    if crit_multiplier == 1.5:
        print(f"  ✅ 暴击伤害倍率已调整为: {crit_multiplier}")
    else:
        print(f"  ❌ 暴击伤害倍率异常: {crit_multiplier}")
    
    # 检查组合技伤害
    combo = combat_data["special_mechanics"]["combo_system"]["special_combos"][0]
    combo_multiplier = combo["damage_multiplier"]
    if combo_multiplier == 2.5:
        print(f"  ✅ 五行毁灭伤害倍率已调整为: {combo_multiplier}")
    else:
        print(f"  ❌ 五行毁灭伤害倍率异常: {combo_multiplier}")


def verify_realm_balance():
    """验证境界系统平衡性修复"""
    print("\n⛰️  验证境界系统平衡性...")
    
    # 读取境界配置
    realm_path = os.path.join(project_root, "xwe/data/restructured/cultivation_realm.json")
    with open(realm_path, 'r', encoding='utf-8') as f:
        realm_data = json.load(f)
    
    expected_multipliers = {
        "qi_gathering": 1.0,
        "foundation_building": 2.0,
        "golden_core": 5.0,
        "nascent_soul": 15.0,
        "deity_transformation": 40.0,
        "void_refinement": 100.0,
        "body_integration": 250.0,
        "mahayana": 600.0,
        "tribulation_transcendence": 1500.0
    }
    
    for realm in realm_data["realms"]:
        realm_id = realm["id"]
        actual = realm["power_multiplier"]
        expected = expected_multipliers.get(realm_id)
        
        if expected and actual == expected:
            print(f"  ✅ {realm['name']} 力量倍率已调整为: {actual}")
        else:
            print(f"  ❌ {realm['name']} 力量倍率异常: {actual} (期望: {expected})")
    
    # 检查境界压制公式
    suppression_formula = realm_data["realm_suppression"]["formula"]
    if "min(0.5, tier_difference * 0.15)" in suppression_formula:
        print(f"  ✅ 境界压制公式已优化: {suppression_formula}")
    else:
        print(f"  ❌ 境界压制公式异常: {suppression_formula}")


def verify_attribute_system():
    """验证属性系统优化"""
    print("\n📊 验证属性系统优化...")
    
    # 读取属性配置
    attr_path = os.path.join(project_root, "xwe/data/restructured/attribute_model.json")
    with open(attr_path, 'r', encoding='utf-8') as f:
        attr_data = json.load(f)
    
    # 检查成长公式
    strength_formula = attr_data["primary_attributes"]["strength"]["growth_formula"]
    if "level / 200" in strength_formula:
        print(f"  ✅ 力量成长公式已优化: {strength_formula}")
    else:
        print(f"  ❌ 力量成长公式未优化: {strength_formula}")
    
    # 检查软硬上限
    soft_cap = attr_data["growth_modifiers"]["soft_cap"]["primary_attributes"]
    hard_cap = attr_data["growth_modifiers"]["hard_cap"]["primary_attributes"]
    
    if soft_cap == 100 and hard_cap == 999:
        print(f"  ✅ 属性上限已调整: 软上限={soft_cap}, 硬上限={hard_cap}")
    else:
        print(f"  ❌ 属性上限异常: 软上限={soft_cap}, 硬上限={hard_cap}")


def verify_spiritual_vein_system():
    """验证灵脉系统"""
    print("\n🌟 验证灵脉系统...")
    
    # 检查灵脉系统文件
    vein_path = os.path.join(project_root, "xwe/data/restructured/spiritual_vein_system.json")
    if os.path.exists(vein_path):
        with open(vein_path, 'r', encoding='utf-8') as f:
            vein_data = json.load(f)
        
        vein_types = vein_data["spiritual_vein_system"]["vein_types"]
        print(f"  ✅ 灵脉系统已创建，包含 {len(vein_types)} 种灵脉类型")
        
        for vein_id, vein_info in vein_types.items():
            print(f"    - {vein_info['name']}: 修炼倍率 {vein_info['multiplier']}x")
    else:
        print(f"  ❌ 灵脉系统文件未找到")


def test_enhanced_output():
    """测试增强输出系统"""
    print("\n🖼️  测试增强输出系统...")
    
    try:
        from xwe.features.enhanced_output import EnhancedGameOutput
        from xwe.features.html_output import HtmlGameLogger
        
        # 创建测试实例
        html_logger = HtmlGameLogger("test_output.html", refresh_interval=1)
        output = EnhancedGameOutput(html_logger)
        
        # 测试多行输出合并
        output.output("测试开始", "system")
        output.output("- 检查点 1", "system")
        output.output("- 检查点 2", "system")
        output.output("- 检查点 3", "system")
        
        # 测试战斗序列
        output.combat_sequence([
            "战斗测试",
            "攻击动作",
            "防御动作",
            "战斗结束"
        ])
        
        print("  ✅ 增强输出系统正常工作")
        print(f"  📄 测试输出文件: {os.path.abspath('test_output.html')}")
        
    except Exception as e:
        print(f"  ❌ 增强输出系统测试失败: {e}")


def main():
    """主测试函数"""
    print("=" * 50)
    print("🔍 修仙世界引擎修复验证")
    print("=" * 50)
    
    # 运行所有验证
    verify_combat_balance()
    verify_realm_balance()
    verify_attribute_system()
    verify_spiritual_vein_system()
    test_enhanced_output()
    
    print("\n" + "=" * 50)
    print("✅ 验证完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
