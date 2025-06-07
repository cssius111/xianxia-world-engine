"""
测试数据驱动系统
验证DataManager、FormulaEngine和各个系统是否正常工作
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import logging
from xwe.core import (
    load_game_data, 
    get_config,
    calculate,
    evaluate_expression,
    cultivation_system,
    combat_system
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_data_loading():
    """测试数据加载"""
    print("\n=== 测试数据加载 ===")
    
    try:
        # 加载所有游戏数据
        load_game_data()
        print("✓ 数据加载成功")
        
        # 测试获取配置
        realms = get_config("cultivation_realm.realms")
        print(f"✓ 加载了 {len(realms)} 个境界")
        
        # 获取第一个境界
        qi_gathering = realms[0]
        print(f"✓ 第一个境界: {qi_gathering['name']} (等级: {qi_gathering['levels']})")
        
        # 测试公式库
        formulas = get_config("formula_library.formulas")
        print(f"✓ 加载了 {len(formulas)} 个公式")
        
        return True
        
    except Exception as e:
        print(f"✗ 数据加载失败: {e}")
        return False

def test_formula_engine():
    """测试公式引擎"""
    print("\n=== 测试公式引擎 ===")
    
    try:
        # 测试简单表达式
        result = evaluate_expression("10 + 20 * 3", {})
        print(f"✓ 简单表达式: 10 + 20 * 3 = {result}")
        assert result == 70
        
        # 测试带变量的表达式
        result = evaluate_expression("health * 0.1 + base_regen", {
            "health": 1000,
            "base_regen": 5
        })
        print(f"✓ 变量表达式: health * 0.1 + base_regen = {result}")
        assert result == 105
        
        # 测试预定义公式
        result = calculate("hit_chance", 
            accuracy=80,
            evasion=30,
            level_difference=5
        )
        print(f"✓ 命中率计算: {result:.2%}")
        
        # 测试物理伤害公式
        result = calculate("physical_damage",
            attack_power=100,
            weapon_damage=50,
            skill_multiplier=1.5,
            defense=30,
            armor=20
        )
        print(f"✓ 物理伤害计算: {result}")
        
        return True
        
    except Exception as e:
        print(f"✗ 公式引擎测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cultivation_system():
    """测试修炼系统"""
    print("\n=== 测试修炼系统 ===")
    
    try:
        # 创建测试角色
        class TestPlayer:
            def __init__(self):
                self.id = "test_player"
                self.name = "测试修士"
                self.realm = "qi_gathering"
                self.realm_level = 9
                self.level = 10
                self.exp = 1000
                self.attributes = {
                    "strength": 20,
                    "agility": 18,
                    "intelligence": 25,
                    "vitality": 22,
                    "comprehension": 60,
                    "willpower": 50,
                    "luck": 10
                }
                self.resources = {
                    "health": 500,
                    "max_health": 500,
                    "mana": 200,
                    "max_mana": 200,
                    "spiritual_power": 150,
                    "stamina": 100,
                    "max_stamina": 100
                }
                self.spiritual_root = {
                    "type": "single",
                    "quality": "medium",
                    "element": "fire"
                }
                self.cultivation = {
                    "total_hours": 100,
                    "breakthrough_count": 0,
                    "failure_count": 0
                }
                self.current_location = None
                self.cultivation_technique = {"tier": 1, "efficiency": 1.0}
                self.status_effects = []
                self.skills = {}
            
            def has_item(self, item_name):
                return item_name == "筑基丹"
            
            def has_status_effect(self, status):
                return status in self.status_effects
            
            def add_status_effect(self, status, duration):
                self.status_effects.append(status)
            
            def unlock_ability(self, ability):
                print(f"  解锁能力: {ability}")
            
            def improve_skill(self, skill, level):
                self.skills[skill] = self.skills.get(skill, 0) + level
        
        player = TestPlayer()
        
        # 测试修炼速度计算
        speed = cultivation_system.calculate_cultivation_speed(player)
        print(f"✓ 修炼速度: {speed:.2f}x")
        
        # 测试修炼
        result = cultivation_system.cultivate(player, duration_hours=2)
        print(f"✓ 修炼2小时，获得经验: {result['exp_gained']:.0f}")
        print(f"  消耗资源: {result['resource_consumed']}")
        
        # 测试突破
        print("\n尝试突破到筑基期...")
        breakthrough_result = cultivation_system.attempt_breakthrough(player)
        print(f"✓ 突破{'成功' if breakthrough_result['success'] else '失败'}: {breakthrough_result['message']}")
        
        return True
        
    except Exception as e:
        print(f"✗ 修炼系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_combat_system():
    """测试战斗系统"""
    print("\n=== 测试战斗系统 ===")
    
    try:
        # 创建测试角色
        class TestCombatant:
            def __init__(self, name, team=0):
                self.id = name.lower().replace(" ", "_")
                self.name = name
                self.team = team
                self.level = 10
                self.health = 1000
                self.max_health = 1000
                self.mana = 500
                self.max_mana = 500
                self.attributes = {
                    "strength": 50,
                    "speed": 30,
                    "accuracy": 70,
                    "evasion": 20,
                    "critical_rate": 0.1,
                    "armor": 20,
                    "defense": 30,
                    "spell_power": 40,
                    "magic_resistance": 0.1
                }
                self.equipment = {
                    "weapon": {"damage": 30, "critical_rate": 0.05}
                }
                self.element = "fire"
                self.realm = "qi_gathering"
                self.status_effects = []
                self.passive_skills = []
                self.ai_behavior = "aggressive"
            
            def has_status(self, status):
                return status in self.status_effects
            
            def add_status_effect(self, status, duration):
                self.status_effects.append(status)
                print(f"  {self.name} 获得状态: {status} (持续 {duration} 回合)")
            
            def take_damage(self, damage):
                self.health -= damage
                self.health = max(0, self.health)
            
            def heal(self, amount):
                old_health = self.health
                self.health = min(self.health + amount, self.max_health)
                return self.health - old_health
            
            def update_status_durations(self):
                pass
            
            def process_dot_effects(self):
                pass
            
            def get_skill(self, skill_id):
                return None
            
            def has_skill(self, skill_id):
                return False
            
            def can_use_skill(self, skill_id):
                return False
            
            def get_available_skills(self):
                return []
            
            def gain_experience(self, exp):
                print(f"  {self.name} 获得 {exp} 点经验")
        
        # 创建战斗参与者
        player = TestCombatant("玩家", team=0)
        enemy = TestCombatant("妖兽", team=1)
        
        # 测试伤害计算
        damage_result = combat_system.calculate_damage(player, enemy, "physical")
        print(f"✓ 伤害计算: {'命中' if damage_result['hit'] else '未命中'}")
        if damage_result['hit']:
            print(f"  伤害值: {damage_result['damage']}")
            print(f"  暴击: {'是' if damage_result['critical'] else '否'}")
        
        # 创建战斗
        combat = combat_system.create_combat("test_combat", [player, enemy])
        print(f"✓ 创建战斗成功，参与者: {len(combat.participants)}人")
        
        # 执行一个回合
        print("\n执行战斗回合...")
        
        # 玩家攻击
        action = {
            "action": combat_system.ActionType.ATTACK,
            "target": enemy.id
        }
        result = combat.execute_turn(action)
        print(f"✓ 玩家攻击: {'成功' if result['success'] else '失败'}")
        
        # AI决策
        ai_action = combat_system.get_ai_action(enemy, combat.state)
        print(f"✓ AI决策: {ai_action['action'].value}")
        
        return True
        
    except Exception as e:
        print(f"✗ 战斗系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("=" * 50)
    print("修仙世界引擎 V3 - 数据驱动系统测试")
    print("=" * 50)
    
    tests = [
        ("数据加载", test_data_loading),
        ("公式引擎", test_formula_engine),
        ("修炼系统", test_cultivation_system),
        ("战斗系统", test_combat_system)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n✗ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！数据驱动系统工作正常。")
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
