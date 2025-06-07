"""
修仙世界引擎 V3 综合示例
展示如何使用数据驱动的各个系统
"""

import os
import sys
import logging
from typing import Dict, Any

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from xwe.core import (
    # 数据管理
    load_game_data,
    get_config,
    # 公式引擎
    calculate,
    evaluate_expression,
    # 修炼系统
    cultivation_system,
    # 战斗系统
    combat_system,
    create_combat,
    # 事件系统
    event_system,
    trigger_events,
    process_event_choice,
    register_event_handler,
    # NPC系统
    npc_system,
    create_npc,
    spawn_npcs_for_location
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GameExample:
    """游戏示例类"""
    
    def __init__(self):
        # 加载游戏数据
        logger.info("Loading game data...")
        load_game_data()
        
        # 创建玩家
        self.player = self.create_test_player()
        
        # 当前位置
        self.current_location = {
            "id": "tiannan_market",
            "name": "天南坊市",
            "type": "market",
            "description": "繁华的修仙者集市"
        }
        
        # 游戏时间
        self.game_time = 0
        
        # 注册事件处理器
        self._register_event_handlers()
    
    def create_test_player(self):
        """创建测试玩家"""
        class Player:
            def __init__(self):
                self.id = "player_1"
                self.name = "陈无名"
                self.level = 10
                self.realm = "qi_gathering"
                self.exp = 5000
                self.exp_needed = 10000
                self.gold = 1000
                
                # 属性
                self.attributes = type('Attributes', (), {
                    'strength': 30,
                    'agility': 25,
                    'intelligence': 35,
                    'constitution': 28,
                    'comprehension': 60,
                    'willpower': 50,
                    'luck': 15,
                    'accuracy': 70,
                    'evasion': 20,
                    'critical_rate': 0.15,
                    'armor': 20,
                    'defense': 30,
                    'spell_power': 40,
                    'magic_resistance': 0.1
                })()
                
                # 资源
                self.health = 800
                self.max_health = 1000
                self.mana = 400
                self.max_mana = 500
                self.stamina = 80
                self.max_stamina = 100
                self.spiritual_power = 200
                
                # 装备
                self.equipment = {
                    "weapon": {"name": "精铁剑", "damage": 50, "critical_rate": 0.05}
                }
                
                # 其他
                self.team = 0
                self.element = "fire"
                self.status_effects = []
                self.inventory = ["筑基丹", "回灵丹", "疗伤丹"]
                self.quests = []
                self.skills = {}
                
                # 修炼相关
                self.spiritual_root = {"type": "single", "quality": "high", "element": "fire"}
                self.cultivation = {
                    "total_hours": 500,
                    "breakthrough_count": 1,
                    "failure_count": 0
                }
                self.cultivation_technique = {"tier": 2, "efficiency": 1.2}
                
            def has_item(self, item_name):
                return item_name in self.inventory
            
            def add_item(self, item_name):
                self.inventory.append(item_name)
                print(f"  获得物品: {item_name}")
            
            def remove_item(self, item_name):
                if item_name in self.inventory:
                    self.inventory.remove(item_name)
            
            def has_status(self, status):
                return status in self.status_effects
            
            def has_status_effect(self, status):
                return status in self.status_effects
            
            def add_status_effect(self, status, duration):
                self.status_effects.append(status)
                print(f"  获得状态: {status} (持续 {duration} 秒)")
            
            def gain_experience(self, exp):
                self.exp += exp
                print(f"  获得经验: {exp}")
                
                # 检查升级
                while self.exp >= self.exp_needed:
                    self.exp -= self.exp_needed
                    self.level += 1
                    self.exp_needed = int(self.exp_needed * 1.5)
                    print(f"  升级！当前等级: {self.level}")
            
            def add_quest(self, quest_id):
                self.quests.append(quest_id)
                print(f"  接受任务: {quest_id}")
            
            def unlock_ability(self, ability):
                print(f"  解锁能力: {ability}")
            
            def improve_skill(self, skill, level):
                self.skills[skill] = self.skills.get(skill, 0) + level
                print(f"  技能提升: {skill} +{level}")
            
            def take_damage(self, damage):
                self.health -= damage
                self.health = max(0, self.health)
                print(f"  受到伤害: {damage}")
            
            def heal(self, amount):
                old_health = self.health
                self.health = min(self.health + amount, self.max_health)
                return self.health - old_health
        
        return Player()
    
    def _register_event_handlers(self):
        """注册事件处理器"""
        # 注册探索事件处理器
        def exploration_handler(event):
            print(f"\n🌟 触发事件: {event['name']}")
            print(f"描述: {event['description']}")
        
        register_event_handler("exploration", exploration_handler)
        register_event_handler("all", lambda e: logger.debug(f"Event triggered: {e['id']}"))
    
    def run_example(self):
        """运行示例"""
        print("\n" + "="*60)
        print("修仙世界引擎 V3 - 数据驱动系统综合示例")
        print("="*60)
        
        # 1. 展示玩家状态
        print("\n### 1. 玩家状态")
        self.show_player_status()
        
        # 2. 测试公式引擎
        print("\n### 2. 公式引擎测试")
        self.test_formula_engine()
        
        # 3. 测试修炼系统
        print("\n### 3. 修炼系统测试")
        self.test_cultivation()
        
        # 4. 测试NPC系统
        print("\n### 4. NPC系统测试")
        self.test_npc_system()
        
        # 5. 测试事件系统
        print("\n### 5. 事件系统测试")
        self.test_event_system()
        
        # 6. 测试战斗系统
        print("\n### 6. 战斗系统测试")
        self.test_combat_system()
        
        # 7. 测试突破系统
        print("\n### 7. 突破系统测试")
        self.test_breakthrough()
        
        print("\n" + "="*60)
        print("示例运行完成！")
        print("="*60)
    
    def show_player_status(self):
        """显示玩家状态"""
        realm_info = get_config("cultivation_realm.realms")
        current_realm = next((r for r in realm_info if r['id'] == self.player.realm), None)
        
        print(f"姓名: {self.player.name}")
        print(f"境界: {current_realm['name'] if current_realm else self.player.realm}")
        print(f"等级: {self.player.level}")
        print(f"经验: {self.player.exp}/{self.player.exp_needed}")
        print(f"生命: {self.player.health}/{self.player.max_health}")
        print(f"法力: {self.player.mana}/{self.player.max_mana}")
        print(f"金币: {self.player.gold}")
        print(f"灵根: {self.player.spiritual_root['quality']}品{self.player.spiritual_root['element']}灵根")
    
    def test_formula_engine(self):
        """测试公式引擎"""
        print("计算修炼速度...")
        cultivation_speed = cultivation_system.calculate_cultivation_speed(self.player)
        print(f"  修炼速度: {cultivation_speed:.2f}x")
        
        print("\n计算物理伤害...")
        damage = calculate("physical_damage",
            attack_power=100,
            weapon_damage=50,
            skill_multiplier=1.5,
            defense=30,
            armor=20
        )
        print(f"  伤害值: {damage}")
        
        print("\n计算命中率...")
        hit_chance = calculate("hit_chance",
            accuracy=self.player.attributes.accuracy,
            evasion=20,
            level_difference=5
        )
        print(f"  命中率: {hit_chance:.2%}")
    
    def test_cultivation(self):
        """测试修炼系统"""
        print("进行2小时修炼...")
        result = cultivation_system.cultivate(self.player, 2)
        
        print(f"  获得经验: {result['exp_gained']:.0f}")
        print(f"  消耗法力: {result['resource_consumed'].get('mana', 0):.0f}")
        print(f"  消耗体力: {result['resource_consumed'].get('stamina', 0):.0f}")
        
        if result['insights']:
            print("  触发顿悟:")
            for insight in result['insights']:
                print(f"    - {insight['name']}: {insight['description']}")
        
        if result['special_events']:
            print("  特殊事件:")
            for event in result['special_events']:
                print(f"    - {event['name']}: {event['description']}")
    
    def test_npc_system(self):
        """测试NPC系统"""
        print("创建NPC...")
        
        # 创建商人NPC
        merchant = create_npc("wang_merchant", "merchant_template")
        merchant.name = "王老板"
        merchant.is_merchant = True
        merchant.shop_inventory = [
            {"id": "healing_pill", "name": "疗伤丹", "price": 100, "stock": 10},
            {"id": "mana_pill", "name": "回灵丹", "price": 150, "stock": 5},
            {"id": "breakthrough_pill", "name": "破障丹", "price": 1000, "stock": 1}
        ]
        
        print(f"  创建了NPC: {merchant.name}")
        
        # 测试对话
        print("\n与NPC对话...")
        dialogue_result = merchant.start_dialogue(self.player)
        print(f"  {merchant.name}: {dialogue_result['text']}")
        print("  选项:")
        for i, option in enumerate(dialogue_result['options']):
            print(f"    {i+1}. {option['text']}")
        
        # 测试交易
        print("\n测试交易...")
        trade_result = merchant.process_trade(self.player, "healing_pill", "buy")
        print(f"  {trade_result['message']}")
        if trade_result['success']:
            print(f"  花费: {trade_result['cost']} 金币")
    
    def test_event_system(self):
        """测试事件系统"""
        print("触发探索事件...")
        
        # 创建探索上下文
        context = {
            "action": "explore",
            "player": self.player,
            "location": self.current_location,
            "game_time": self.game_time
        }
        
        # 手动创建一个测试事件
        test_event = event_system.create_custom_event({
            "id": "mysterious_encounter",
            "name": "神秘遭遇",
            "description": f"{self.player.name}在{self.current_location['name']}遇到了一位神秘的修士。",
            "choices": [
                {
                    "id": "approach",
                    "text": "上前搭话",
                    "outcomes": [{
                        "type": "reward",
                        "weight": 1.0,
                        "text": "神秘修士赠送了你一些物品。",
                        "rewards": {
                            "experience": 500,
                            "items": ["spirit_stone"]
                        }
                    }]
                },
                {
                    "id": "ignore",
                    "text": "无视离开",
                    "outcomes": [{
                        "type": "information",
                        "weight": 1.0,
                        "text": "你选择了谨慎行事。"
                    }]
                }
            ]
        })
        
        print(f"  事件: {test_event['name']}")
        print(f"  描述: {test_event['description']}")
        
        # 处理选择
        print("\n处理事件选择...")
        choice_result = process_event_choice(test_event, "approach")
        print(f"  结果: {choice_result['message']}")
        if choice_result.get('effects'):
            for effect in choice_result['effects']:
                print(f"    - {effect}")
    
    def test_combat_system(self):
        """测试战斗系统"""
        print("创建战斗...")
        
        # 创建敌人
        class Enemy:
            def __init__(self):
                self.id = "test_enemy"
                self.name = "妖兽"
                self.team = 1
                self.level = 8
                self.health = 600
                self.max_health = 600
                self.realm = "qi_gathering"
                self.element = "earth"
                self.attributes = type('Attributes', (), {
                    'strength': 40,
                    'speed': 20,
                    'accuracy': 60,
                    'evasion': 15,
                    'critical_rate': 0.1,
                    'armor': 15,
                    'defense': 25
                })()
                self.equipment = {"weapon": {"damage": 30}}
                self.status_effects = []
                self.ai_behavior = "aggressive"
                self.passive_skills = []
            
            def has_status(self, status):
                return status in self.status_effects
            
            def add_status_effect(self, status, duration):
                self.status_effects.append(status)
            
            def take_damage(self, damage):
                self.health -= damage
                self.health = max(0, self.health)
            
            def update_status_durations(self):
                pass
            
            def process_dot_effects(self):
                pass
            
            def has_skill(self, skill_id):
                return False
            
            def get_available_skills(self):
                return []
            
            def gain_experience(self, exp):
                pass
        
        enemy = Enemy()
        
        # 测试伤害计算
        print(f"\n计算对{enemy.name}的伤害...")
        damage_result = combat_system.calculate_damage(self.player, enemy, "physical")
        
        if damage_result['hit']:
            print(f"  命中！造成 {damage_result['damage']} 点伤害")
            if damage_result['critical']:
                print("  暴击！")
            
            # 检查元素克制
            if 'element_multiplier' in damage_result['details']:
                mult = damage_result['details']['element_multiplier']
                if mult > 1:
                    print(f"  元素克制！伤害x{mult}")
                elif mult < 1:
                    print(f"  元素被克！伤害x{mult}")
        else:
            print("  攻击被闪避！")
        
        # 测试AI决策
        print(f"\n{enemy.name}的AI决策...")
        
        # 创建简单的战斗状态
        class SimpleCombatState:
            def get_enemies(self, character):
                return [self.player] if character.team == 1 else [enemy]
            
            def get_damage_dealt_by(self, char_id):
                return 100 if char_id == self.player.id else 50
            
            def get_healing_done_by(self, char_id):
                return 0
            
            def get_distance(self, char1, char2):
                return 1.0
        
        combat_state = SimpleCombatState()
        combat_state.player = self.player
        
        ai_action = combat_system.get_ai_action(enemy, combat_state)
        print(f"  AI选择: {ai_action['action'].value}")
        if 'target' in ai_action:
            print(f"  目标: {ai_action['target'].name}")
    
    def test_breakthrough(self):
        """测试突破系统"""
        # 临时修改玩家等级以满足突破条件
        old_level = self.player.level
        self.player.level = 9  # 聚气期九层
        
        print(f"当前境界: 聚气期九层")
        print("尝试突破到筑基期...")
        
        result = cultivation_system.attempt_breakthrough(self.player)
        
        print(f"\n结果: {result['message']}")
        
        if result['success']:
            print("突破成功的效果:")
            if 'effects' in result:
                for key, value in result['effects'].items():
                    print(f"  - {key}: {value}")
        else:
            print("突破失败的惩罚:")
            if 'penalties' in result:
                for key, value in result['penalties'].items():
                    print(f"  - {key}: {value}")
        
        # 恢复等级
        self.player.level = old_level


def main():
    """主函数"""
    try:
        # 创建并运行示例
        example = GameExample()
        example.run_example()
        
    except Exception as e:
        logger.error(f"Error running example: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
