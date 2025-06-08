"""
修仙世界引擎 V3 - 数据驱动增强版
集成了DataManager、FormulaEngine和优化后的各个系统
"""

import os
import sys
import logging
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from xwe.core import (
    load_game_data,
    get_config,
    GameCore,
    Character,
    cultivation_system,
    combat_system,
    create_combat
)
from xwe.core.game_core_enhanced import GameCoreEnhanced
from xwe.core.chinese_dragon_art import print_chinese_dragon

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataDrivenGameCore(GameCoreEnhanced):
    """
    数据驱动的游戏核心
    使用V3版本的新系统
    """
    
    def __init__(self):
        # 先加载游戏数据
        logger.info("Loading game data...")
        try:
            load_game_data()
            logger.info("Game data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load game data: {e}")
            raise
        
        # 初始化父类
        super().__init__()
        
        # 集成新系统
        self.cultivation_system = cultivation_system
        self.combat_system_v3 = combat_system
        
    def initialize(self):
        """初始化游戏"""
        super().initialize()
        
        # 打印欢迎信息
        print("\n" + "="*50)
        print_chinese_dragon()
        print("="*50)
        print("欢迎来到修仙世界 V3.0 - 数据驱动版")
        print("="*50)
        
        # 显示加载的模块
        from xwe.core.data_manager_v3 import DM
        loaded_modules = DM.get_loaded_modules()
        print(f"\n已加载 {len(loaded_modules)} 个数据模块:")
        for module in loaded_modules:
            print(f"  - {module}")
        
        print("\n输入 '帮助' 查看所有命令")
        print("="*50)
    
    def handle_cultivate(self, args: list) -> str:
        """处理修炼命令 - 使用新的修炼系统"""
        try:
            # 默认修炼时长
            hours = 1
            if args and args[0].isdigit():
                hours = int(args[0])
                hours = max(1, min(hours, 24))  # 限制在1-24小时
            
            # 使用新的修炼系统
            result = self.cultivation_system.cultivate(self.player, hours)
            
            # 构建输出信息
            output = [
                f"\n你闭关修炼了 {hours} 小时...\n",
                f"获得经验: {result['exp_gained']:.0f} 点"
            ]
            
            # 消耗的资源
            if result['resource_consumed']:
                output.append("\n消耗资源:")
                for resource, amount in result['resource_consumed'].items():
                    output.append(f"  {resource}: {amount:.0f}")
            
            # 特殊事件
            if result['insights']:
                output.append("\n✨ 修炼感悟:")
                for insight in result['insights']:
                    output.append(f"  【{insight['name']}】{insight['description']}")
            
            if result['special_events']:
                output.append("\n🎭 特殊事件:")
                for event in result['special_events']:
                    output.append(f"  【{event['name']}】{event['description']}")
            
            # 检查是否可以突破
            current_realm = get_config(f"cultivation_realm.realms")
            player_realm_info = next((r for r in current_realm if r['id'] == self.player.realm), None)
            
            if player_realm_info and self.player.level >= player_realm_info['levels']:
                output.append(f"\n💫 你已达到{player_realm_info['name']}的巅峰，可以尝试突破了！")
                output.append("输入 '突破' 尝试突破到下一境界")
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Cultivation error: {e}")
            return "修炼过程中出现异常，请稍后再试"
    
    def handle_breakthrough(self, args: list) -> str:
        """处理突破命令"""
        try:
            # 检查是否可以突破
            current_realm_info = get_config(f"cultivation_realm.realms")
            player_realm = next((r for r in current_realm_info if r['id'] == self.player.realm), None)
            
            if not player_realm:
                return "当前境界信息异常"
            
            # 使用新的突破系统
            result = self.cultivation_system.attempt_breakthrough(self.player)
            
            output = [f"\n{result['message']}"]
            
            if result['success']:
                # 突破成功
                output.append("\n🎊 恭喜你突破成功！")
                
                if 'effects' in result:
                    effects = result['effects']
                    if 'lifespan_bonus' in effects:
                        output.append(f"寿命增加: {effects['lifespan_bonus']} 年")
                    if 'power_multiplier' in effects:
                        output.append(f"实力倍数: {effects['power_multiplier']}x")
                
                output.append("\n你感受到体内的力量发生了质的飞跃！")
                
            else:
                # 突破失败
                output.append("\n😞 突破失败...")
                
                if 'penalties' in result:
                    penalties = result['penalties']
                    if 'health_damage' in penalties:
                        output.append(f"受到反噬伤害: {penalties['health_damage']} 点")
                    if 'exp_loss' in penalties:
                        output.append(f"损失经验: {penalties['exp_loss']:.0f} 点")
                    if 'dao_injury' in penalties:
                        output.append("你受到了道伤，需要时间恢复")
                    if 'death' in penalties:
                        output.append("\n💀 你在突破中身陨道消...")
                        # TODO: 处理角色死亡
                
                output.append("\n不要气馁，调整状态后再次尝试")
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Breakthrough error: {e}")
            return "突破过程中出现异常"
    
    def handle_combat_v3(self, target_name: str) -> str:
        """使用V3战斗系统处理战斗"""
        try:
            # 创建敌人（临时实现）
            class Enemy:
                def __init__(self, name):
                    self.id = name.lower().replace(" ", "_")
                    self.name = name
                    self.team = 1
                    self.level = self.player.level
                    self.health = 500
                    self.max_health = 500
                    self.attributes = {
                        "strength": 40,
                        "speed": 25,
                        "accuracy": 60,
                        "evasion": 15,
                        "critical_rate": 0.05,
                        "armor": 15,
                        "defense": 20
                    }
                    self.equipment = {"weapon": {"damage": 20}}
                    self.element = "earth"
                    self.realm = "qi_gathering"
                    self.status_effects = []
                    self.ai_behavior = "aggressive"
                    
                def has_status(self, status):
                    return status in self.status_effects
                
                def take_damage(self, damage):
                    self.health -= damage
                    self.health = max(0, self.health)
                
                # ... 其他必要方法 ...
            
            enemy = Enemy(target_name)
            
            # 创建战斗
            combat = create_combat([self.player, enemy])
            
            output = [
                f"\n⚔️ 战斗开始！",
                f"你遭遇了 {enemy.name}！",
                f"战斗顺序: {[p.name for p in combat.turn_order]}"
            ]
            
            # 简化的战斗循环（实际应该是交互式的）
            while not combat._check_combat_end() and combat.round < 10:
                current = combat.turn_order[combat.current_turn]
                
                if current.id == self.player.id:
                    # 玩家回合 - 自动攻击
                    action = {
                        "action": combat_system.ActionType.ATTACK,
                        "target": enemy.id
                    }
                else:
                    # AI回合
                    action = self.combat_system_v3.get_ai_action(current, combat.state)
                
                result = combat.execute_turn(action)
                
                # 显示战斗信息
                if current.id == self.player.id and result.get('success'):
                    if 'damage' in result:
                        damage_info = result['damage']
                        if damage_info['hit']:
                            output.append(f"你攻击了{enemy.name}，造成 {damage_info['damage']} 点伤害")
                
            # 战斗结束
            if self.player.health > 0:
                output.append(f"\n🎉 战斗胜利！")
            else:
                output.append(f"\n💀 战斗失败...")
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Combat V3 error: {e}")
            return "战斗系统出现异常"
    
    def show_status_v3(self) -> str:
        """显示增强的状态信息"""
        # 获取境界信息
        realm_info = get_config(f"cultivation_realm.realms")
        current_realm = next((r for r in realm_info if r['id'] == self.player.realm), None)
        
        # 计算修炼速度
        cultivation_speed = self.cultivation_system.calculate_cultivation_speed(self.player)
        
        output = [
            "\n" + "="*50,
            f"姓名: {self.player.name}",
            f"境界: {current_realm['name'] if current_realm else self.player.realm} (等级 {self.player.level})",
            f"经验: {self.player.exp}/{self.player.exp_needed}",
            f"修炼速度: {cultivation_speed:.2f}x",
            "",
            "【基础属性】",
            f"力量: {self.player.attributes.strength}  敏捷: {self.player.attributes.agility}",
            f"智力: {self.player.attributes.intelligence}  体质: {self.player.attributes.constitution}",
            "",
            "【资源状态】",
            f"生命: {self.player.health}/{self.player.max_health}",
            f"法力: {self.player.mana}/{self.player.max_mana}",
            f"体力: {self.player.stamina}/{self.player.max_stamina}",
            "",
            "【战斗属性】",
            f"攻击力: {self.player.attack}  防御力: {self.player.defense}",
            f"速度: {self.player.speed}     精准度: {self.player.accuracy}",
            "="*50
        ]
        
        return "\n".join(output)

    def handle_command(self, command: str, args: list) -> str:
        """通过基础引擎处理命令并返回结果"""
        try:
            full_input = " ".join([command, *args])
            self.running = True  # 确保底层处理逻辑生效
            self.process_command(full_input)
            return "\n".join(self.get_output())
        except Exception as e:
            logger.error(f"Command handling error: {e}")
            return "命令处理出错"
    
    def run(self):
        """运行游戏主循环"""
        self.running = True
        
        while self.running:
            try:
                # 获取用户输入
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue
                
                # 解析命令
                parts = user_input.split()
                command = parts[0]
                args = parts[1:] if len(parts) > 1 else []
                
                # 处理命令
                response = ""
                
                # 基础命令
                if command in ["退出", "exit", "quit"]:
                    self.running = False
                    response = "感谢游玩，再见！"
                
                elif command in ["帮助", "help", "?"]:
                    response = self.show_help()
                
                elif command in ["状态", "status", "s"]:
                    response = self.show_status_v3()
                
                # 数据驱动的命令
                elif command in ["修炼", "修练", "cultivate", "c"]:
                    response = self.handle_cultivate(args)
                
                elif command in ["突破", "breakthrough", "b"]:
                    response = self.handle_breakthrough(args)
                
                elif command in ["攻击", "attack", "a"]:
                    if args:
                        response = self.handle_combat_v3(" ".join(args))
                    else:
                        response = "请指定攻击目标"
                
                elif command in ["公式", "formula", "f"]:
                    # 显示公式信息
                    if args:
                        formula_id = args[0]
                        formula = get_config(f"formula_library.formulas.{formula_id}")
                        if formula:
                            response = f"公式 {formula_id}:\n{formula.get('description', '')}\n表达式: {formula.get('expression', '')}"
                        else:
                            response = "未找到该公式"
                    else:
                        formulas = get_config("formula_library.formulas")
                        response = "可用公式:\n" + "\n".join([f"- {f['id']}: {f['description']}" for f in formulas[:10]])
                
                else:
                    # 使用父类的命令处理
                    response = self.handle_command(command, args)
                
                # 显示响应
                if response:
                    print(response)
                
            except KeyboardInterrupt:
                print("\n\n游戏已暂停，输入 '退出' 结束游戏")
            except Exception as e:
                logger.error(f"Game loop error: {e}")
                print(f"发生错误: {e}")
    
    def show_help(self) -> str:
        """显示帮助信息"""
        help_text = """
=== 修仙世界 V3.0 命令帮助 ===

【基础命令】
  状态/s      - 查看角色状态
  帮助/?      - 显示帮助信息
  退出        - 退出游戏

【修炼命令】
  修炼 [时长] - 闭关修炼（默认1小时，最多24小时）
  突破        - 尝试突破到下一境界

【战斗命令】
  攻击 <目标> - 攻击指定目标

【数据命令】
  公式 [ID]   - 查看公式信息

【其他命令】
  探索        - 探索当前区域
  背包        - 查看物品
  技能        - 查看技能列表
  地图        - 查看当前位置

提示：本版本使用数据驱动架构，所有游戏数值均可通过配置文件调整
"""
        return help_text


def main():
    """主函数"""
    try:
        # 创建游戏实例
        game = DataDrivenGameCore()
        
        # 运行游戏
        game.run()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n游戏启动失败: {e}")
        print("请检查数据文件是否完整")
        
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
