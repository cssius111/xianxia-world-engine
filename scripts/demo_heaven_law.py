#!/usr/bin/env python3
"""
Heaven Law Engine Demo Script
演示天道法则引擎的各种功能
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.xwe.core.heaven_law_engine import HeavenLawEngine, ActionContext
from src.xwe.core.character import Character, CharacterType
from src.xwe.core.attributes import CharacterAttributes
from src.xwe.core.combat import CombatSystem


def create_test_character(name: str, realm: str, level: int = 1) -> Character:
    """创建测试角色"""
    character = Character(
        id=f"test_{name.lower()}",
        name=name,
        character_type=CharacterType.PLAYER
    )
    
    character.attributes = CharacterAttributes()
    character.attributes.realm_name = realm
    character.attributes.realm_level = level
    character.attributes.current_health = 1000
    character.attributes.max_health = 1000
    character.attributes.cultivation_level = level * 10
    
    # 添加状态效果列表
    character.status_effects = []
    
    return character


def demo_cross_realm_kill():
    """演示跨境界斩杀限制"""
    print("=" * 60)
    print("演示1: 跨境界斩杀限制")
    print("=" * 60)
    
    # 创建天道法则引擎
    heaven_law = HeavenLawEngine()
    
    # 场景1: 正常战斗（境界接近）
    print("\n场景1: 筑基期 vs 炼气期（允许）")
    attacker1 = create_test_character("张三", "筑基期")
    defender1 = create_test_character("李四", "炼气期")
    
    ctx1 = ActionContext()
    heaven_law.enforce(attacker1, defender1, ctx1)
    
    if ctx1.cancelled:
        print(f"❌ 攻击被阻止: {ctx1.reason}")
    else:
        print("✅ 攻击允许 - 境界差距在合理范围内")
    
    # 场景2: 跨境界攻击（触发天道惩罚）
    print("\n场景2: 金丹期 vs 炼气期（禁止）")
    attacker2 = create_test_character("王五", "金丹期")
    defender2 = create_test_character("赵六", "炼气期")
    
    ctx2 = ActionContext()
    heaven_law.enforce(attacker2, defender2, ctx2)
    
    if ctx2.cancelled:
        print(f"❌ 攻击被阻止: {ctx2.reason}")
        for event in ctx2.events:
            print(f"⚡ 触发事件: {event.name} (严重程度: {event.severity})")
            result = event.apply()
            print(f"   {result}")
            print(f"   {attacker2.name}剩余生命: {attacker2.attributes.current_health}/{attacker2.attributes.max_health}")
    
    # 场景3: 极大境界差距（严重天劫）
    print("\n场景3: 大乘期 vs 炼气期（严重惩罚）")
    attacker3 = create_test_character("陈七", "大乘期")
    defender3 = create_test_character("周八", "炼气期")
    attacker3.attributes.current_health = 10000
    attacker3.attributes.max_health = 10000
    
    ctx3 = ActionContext()
    heaven_law.enforce(attacker3, defender3, ctx3)
    
    if ctx3.cancelled:
        print(f"❌ 攻击被阻止: {ctx3.reason}")
        for event in ctx3.events:
            print(f"⚡ 触发事件: {event.name} (严重程度: {event.severity})")
            result = event.apply()
            print(f"   {result}")
            print(f"   {attacker3.name}剩余生命: {attacker3.attributes.current_health}/{attacker3.attributes.max_health}")
    
    # 场景4: 低境界攻击高境界（允许）
    print("\n场景4: 炼气期 vs 元婴期（勇气可嘉）")
    attacker4 = create_test_character("小明", "炼气期")
    defender4 = create_test_character("老怪", "元婴期")
    
    ctx4 = ActionContext()
    heaven_law.enforce(attacker4, defender4, ctx4)
    
    if ctx4.cancelled:
        print(f"❌ 攻击被阻止: {ctx4.reason}")
    else:
        print("✅ 攻击允许 - 以弱击强，勇气可嘉！")


def demo_forbidden_arts():
    """演示禁术使用"""
    print("\n" + "=" * 60)
    print("演示2: 禁术反噬")
    print("=" * 60)
    
    heaven_law = HeavenLawEngine()
    character = create_test_character("邪修", "金丹期")
    character.karma = 500  # 初始业力值
    
    print(f"\n{character.name}当前业力值: {character.karma}")
    
    # 使用普通技能
    print("\n使用普通技能「青云剑诀」:")
    ctx1 = ActionContext()
    heaven_law.check_forbidden_art(character, "青云剑诀", ctx1)
    print("✅ 正常使用，无反噬")
    
    # 使用禁术
    print("\n使用禁术「血魔大法」:")
    ctx2 = ActionContext()
    heaven_law.check_forbidden_art(character, "血魔大法", ctx2)
    
    if ctx2.events:
        print("❌ 触发禁术反噬！")
        for event in ctx2.events:
            print(f"   事件: {event.name}")
        
        # 检查业力惩罚
        if hasattr(character, 'karma'):
            karma_penalty = heaven_law.laws.get("FORBIDDEN_ARTS").params.get("karma_penalty", 100)
            print(f"   业力值减少: {karma_penalty}")
            print(f"   当前业力值: {character.karma}")


def demo_combat_integration():
    """演示与战斗系统的集成"""
    print("\n" + "=" * 60)
    print("演示3: 战斗系统集成")
    print("=" * 60)
    
    # 创建战斗系统
    heaven_law = HeavenLawEngine()
    combat_system = CombatSystem(None, None, heaven_law)
    
    # 创建角色
    high_level = create_test_character("高手", "化神期", 50)
    low_level = create_test_character("新手", "炼气期", 1)
    
    print(f"\n{high_level.name}({high_level.attributes.realm_name}) 试图攻击 {low_level.name}({low_level.attributes.realm_name})")
    
    # 执行攻击
    result = combat_system.attack(high_level, low_level)
    
    print(f"\n战斗结果:")
    print(f"成功: {result.success}")
    print(f"消息: {result.message}")


def demo_realm_breakthrough():
    """演示境界突破天劫"""
    print("\n" + "=" * 60)
    print("演示4: 境界突破天劫")
    print("=" * 60)
    
    heaven_law = HeavenLawEngine()
    character = create_test_character("修士", "炼气期", 9)
    
    print(f"\n{character.name}准备突破到筑基期...")
    
    ctx = ActionContext()
    heaven_law.check_breakthrough(character, "筑基期", ctx)
    
    if ctx.events:
        print("⚡ 天劫降临！")
        for event in ctx.events:
            print(f"   {event.name}")
            if "Level" in event.name:
                level = event.name.split("Level")[1]
                print(f"   天劫难度: {level}")
    else:
        print("✅ 无需渡劫")


def demo_law_configuration():
    """演示法则配置"""
    print("\n" + "=" * 60)
    print("演示5: 法则配置")
    print("=" * 60)
    
    heaven_law = HeavenLawEngine()
    
    print("\n当前激活的法则:")
    for code, law in heaven_law.laws.items():
        status = "✅ 启用" if law.enabled else "❌ 禁用"
        print(f"- {code}: {law.name} [{status}]")
        if law.params:
            for key, value in law.params.items():
                print(f"  • {key}: {value}")


def main():
    """主函数"""
    print("🌩️  天道法则引擎演示")
    print("=" * 60)
    
    demos = [
        ("跨境界斩杀限制", demo_cross_realm_kill),
        ("禁术反噬", demo_forbidden_arts),
        ("战斗系统集成", demo_combat_integration),
        ("境界突破天劫", demo_realm_breakthrough),
        ("法则配置", demo_law_configuration),
    ]
    
    while True:
        print("\n请选择演示项目:")
        for i, (name, _) in enumerate(demos, 1):
            print(f"{i}. {name}")
        print("0. 退出")
        
        try:
            choice = input("\n请输入选项 (0-5): ")
            if choice == "0":
                print("\n感谢使用天道法则引擎演示！")
                break
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(demos):
                _, demo_func = demos[choice_idx]
                demo_func()
                input("\n按回车继续...")
            else:
                print("无效的选项，请重新选择。")
        except (ValueError, KeyboardInterrupt):
            print("\n退出演示。")
            break


if __name__ == "__main__":
    main()
