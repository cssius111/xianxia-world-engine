# test_basic.py
"""
基础功能测试

测试各个核心系统是否正常工作。
"""


# 添加项目根目录到Python路径

from xwe.engine.expression import ExpressionParser
from xwe.core import (
    DataLoader, AttributeSystem, CharacterAttributes,
    Character, SkillSystem, CombatSystem, AIController,
    CommandParser
)
from xwe.world import WorldMap, LocationManager, EventSystem


def test_expression_parser():
    """测试表达式解析器"""
    print("=== 测试表达式解析器 ===")
    
    parser = ExpressionParser()
    
    # 基础运算
    result = parser.evaluate("2 + 3 * 4")
    print(f"2 + 3 * 4 = {result}")
    assert result == 14
    
    # 使用变量
    context = {"attack": 100, "multiplier": 1.5}
    result = parser.evaluate("attack * multiplier", context)
    print(f"attack * multiplier = {result}")
    assert result == 150
    
    # 使用函数
    result = parser.evaluate("max(10, 20, 30)")
    print(f"max(10, 20, 30) = {result}")
    assert result == 30
    
    print("✓ 表达式解析器测试通过\n")


def test_data_loader():
    """测试数据加载器"""
    print("=== 测试数据加载器 ===")
    
    loader = DataLoader()
    
    # 加载世界配置
    world_config = loader.get_world_config()
    print(f"世界名称: {world_config['meta']['universe_name']}")
    
    # 加载修炼规则
    cultivation_rules = loader.get_cultivation_rules()
    print(f"境界数量: {len(cultivation_rules['realm_system']['mortal_realms'])}")
    
    print("✓ 数据加载器测试通过\n")


def test_character_system():
    """测试角色系统"""
    print("=== 测试角色系统 ===")
    
    # 创建角色
    character = Character(name="测试侠客")
    print(f"角色名称: {character.name}")
    print(f"境界: {character.get_realm_info()}")
    print(f"灵根: {character.get_spiritual_root_description()}")
    
    # 测试属性
    print(f"气血值: {character.attributes.current_health}/{character.attributes.max_health}")
    
    # 测试伤害
    character.take_damage(30)
    print(f"受到30点伤害后: {character.attributes.current_health}/{character.attributes.max_health}")
    
    # 测试治疗
    character.heal(20)
    print(f"治疗20点后: {character.attributes.current_health}/{character.attributes.max_health}")
    
    print("✓ 角色系统测试通过\n")


def test_skill_system():
    """测试技能系统"""
    print("=== 测试技能系统 ===")
    
    loader = DataLoader()
    parser = ExpressionParser()
    skill_system = SkillSystem(loader, parser)
    
    # 获取技能
    skill = skill_system.get_skill("sword_qi_slash")
    if skill:
        print(f"技能名称: {skill.name}")
        print(f"技能描述: {skill.description}")
        print(f"灵力消耗: {skill.mana_cost}")
    
    # 创建角色并学习技能
    character = Character(name="剑修")
    character.learn_skill("sword_qi_slash")
    
    # 检查可用技能
    available_skills = skill_system.get_available_skills(character)
    print(f"可用技能数量: {len(available_skills)}")
    
    print("✓ 技能系统测试通过\n")


def test_command_parser():
    """测试命令解析器"""
    print("=== 测试命令解析器 ===")
    
    parser = CommandParser()
    
    test_commands = [
        "攻击 妖兽",
        "使用 剑气斩 攻击 敌人",
        "防御",
        "状态",
        "修炼"
    ]
    
    for cmd in test_commands:
        parsed = parser.parse(cmd)
        print(f"命令: {cmd}")
        print(f"  类型: {parsed.command_type.value}")
        if parsed.target:
            print(f"  目标: {parsed.target}")
        if parsed.parameters:
            print(f"  参数: {parsed.parameters}")
    
    print("✓ 命令解析器测试通过\n")


def test_combat_system():
    """测试战斗系统"""
    print("=== 测试战斗系统 ===")
    
    # 初始化系统
    loader = DataLoader()
    parser = ExpressionParser()
    skill_system = SkillSystem(loader, parser)
    combat_system = CombatSystem(skill_system, parser)
    
    # 创建战斗
    combat_id = "test_combat"
    combat_state = combat_system.create_combat(combat_id)
    
    # 创建参与者
    from xwe.core.character import CharacterType
    player = Character(name="玩家", character_type=CharacterType.PLAYER)
    player.learn_skill("basic_attack")
    
    enemy = Character(name="测试敌人")
    enemy.attributes.current_health = 50
    enemy.attributes.max_health = 50
    
    # 添加到战斗
    combat_state.add_participant(player, "player_team")
    combat_state.add_participant(enemy, "enemy_team")
    
    print(f"战斗参与者: {len(combat_state.participants)}")
    print(f"战斗是否结束: {combat_state.is_combat_over()}")
    
    # 执行一次攻击
    from xwe.core.combat import CombatAction, CombatActionType
    
    action = CombatAction(
        action_type=CombatActionType.ATTACK,
        actor_id=player.id,
        target_ids=[enemy.id]
    )
    
    result = combat_system.execute_action(combat_id, action)
    print(f"攻击结果: {result.success}")
    if result.damage_dealt:
        for target_id, damage_info in result.damage_dealt.items():
            print(f"造成伤害: {damage_info.damage:.0f}")
    
    print("✓ 战斗系统测试通过\n")


def test_world_system():
    """测试世界系统"""
    print("=== 测试世界系统 ===")
    
    # 创建世界地图
    world_map = WorldMap()
    location_manager = LocationManager(world_map)
    
    # 加载默认地图数据
    from xwe.world.world_map import DEFAULT_MAP_DATA, Area
    for area_data in DEFAULT_MAP_DATA['areas'][:3]:
        area = Area.from_dict(area_data)
        world_map.add_area(area)
    
    print(f"加载了 {len(world_map.areas)} 个区域")
    
    # 测试位置管理
    player = Character(name="测试侠客")
    location_manager.set_location(player.id, "qingyun_city")
    
    location = location_manager.get_location(player.id)
    print(f"玩家位置: {location}")
    
    # 测试附近区域
    nearby = location_manager.get_nearby_areas(player.id)
    print(f"附近区域数: {len(nearby)}")
    
    print("✓ 世界系统测试通过\n")


def main():
    """运行所有测试"""
    print("仙侠世界引擎 - 基础功能测试")
    print("=" * 50)
    print()
    
    try:
        test_expression_parser()
        test_data_loader()
        test_character_system()
        test_skill_system()
        test_command_parser()
        test_combat_system()
        test_world_system()
        
        print("=" * 50)
        print("所有测试通过！游戏系统正常。")
        print("\n运行 python main.py 开始游戏")
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
