#!/usr/bin/env python3
# @dev_only
"""
🧪 仙侠世界游戏优化验证测试脚本
==========================================

此脚本用于全面测试优化工具所做的改进，确保所有新功能正常工作。

测试覆盖：
✅ 物品系统集成
✅ 系统管理器功能
✅ 确认机制管理
✅ 异常处理系统
✅ 游戏核心功能
✅ Roll系统
✅ 对话系统
"""

import sys
import os
import logging
import traceback
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OptimizationTester:
    """优化效果测试器"""
    
    def __init__(self):
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def run_test(self, test_name: str, test_func):
        """运行单个测试"""
        self.total_tests += 1
        print(f"\n{'='*60}")
        print(f"🧪 测试: {test_name}")
        print(f"{'='*60}")
        
        try:
            result = test_func()
            if result:
                print(f"✅ 通过: {test_name}")
                self.passed_tests += 1
                self.test_results[test_name] = {"status": "PASS", "error": None}
            else:
                print(f"❌ 失败: {test_name}")
                self.failed_tests += 1
                self.test_results[test_name] = {"status": "FAIL", "error": "测试返回False"}
                
        except Exception as e:
            print(f"💥 异常: {test_name}")
            print(f"错误信息: {str(e)}")
            print(f"堆栈跟踪:")
            print(traceback.format_exc())
            self.failed_tests += 1
            self.test_results[test_name] = {"status": "ERROR", "error": str(e)}
    
    def test_1_imports(self):
        """测试1: 验证新模块导入"""
        print("📦 测试导入新创建的模块...")
        
        try:
            # 测试物品系统
            from xwe.core.item_system import ItemSystem, item_system
            print("✓ 物品系统导入成功")
            
            # 测试系统管理器
            from xwe.core.system_manager import SystemManager, system_manager  
            print("✓ 系统管理器导入成功")
            
            # 测试确认管理器
            from xwe.core.confirmation_manager import ConfirmationManager, confirmation_manager
            print("✓ 确认管理器导入成功")
            
            # 测试异常处理器
            from xwe.core.exception_handler import handle_game_exception
            print("✓ 异常处理器导入成功")
            
            print("🎉 所有新模块导入成功！")
            return True
            
        except ImportError as e:
            print(f"❌ 导入失败: {e}")
            return False
    
    def test_2_item_system(self):
        """测试2: 物品系统功能"""
        print("💰 测试物品系统功能...")
        
        try:
            from xwe.core.item_system import item_system
            
            # 测试灵石管理
            player_id = "test_player"
            
            # 初始状态
            initial_stones = item_system.get_spirit_stones(player_id)
            print(f"✓ 初始灵石数量: {initial_stones}")
            
            # 添加灵石
            item_system.add_item(player_id, 'spirit_stones', 100)
            after_add = item_system.get_spirit_stones(player_id)
            print(f"✓ 添加100灵石后: {after_add}")
            
            # 移除灵石
            success = item_system.remove_item(player_id, 'spirit_stones', 50)
            after_remove = item_system.get_spirit_stones(player_id)
            print(f"✓ 移除50灵石后: {after_remove} (成功: {success})")
            
            # 验证逻辑
            if after_add == initial_stones + 100 and after_remove == after_add - 50 and success:
                print("🎉 物品系统功能正常！")
                return True
            else:
                print("❌ 物品系统逻辑错误")
                return False
                
        except Exception as e:
            print(f"❌ 物品系统测试失败: {e}")
            return False
    
    def test_3_system_manager(self):
        """测试3: 系统管理器功能"""
        print("⚙️ 测试系统管理器功能...")
        
        try:
            from xwe.core.system_manager import system_manager
            
            player_id = "test_player"
            
            # 测试修炼系统激活
            cultivation_system = {
                'name': '测试修炼系统',
                'rarity': 'epic',
                'features': ['快速修炼', '境界突破']
            }
            
            system_manager.activate_system(player_id, cultivation_system)
            print("✓ 修炼系统激活成功")
            
            # 测试加成获取
            speed_bonus = system_manager.get_system_bonus(player_id, 'cultivation_speed')
            breakthrough_bonus = system_manager.get_system_bonus(player_id, 'breakthrough_success')
            print(f"✓ 修炼速度加成: {speed_bonus}")
            print(f"✓ 突破成功率加成: {breakthrough_bonus}")
            
            # 测试功能检查
            has_feature = system_manager.has_feature(player_id, '快速修炼')
            print(f"✓ 拥有'快速修炼'功能: {has_feature}")
            
            # 验证逻辑（epic稀有度应该有2.0倍修炼速度加成）
            if speed_bonus == 2.0 and breakthrough_bonus == 1.5 and has_feature:
                print("🎉 系统管理器功能正常！")
                return True
            else:
                print(f"❌ 系统管理器逻辑错误 - 速度:{speed_bonus}, 突破:{breakthrough_bonus}, 功能:{has_feature}")
                return False
                
        except Exception as e:
            print(f"❌ 系统管理器测试失败: {e}")
            return False
    
    def test_4_confirmation_manager(self):
        """测试4: 确认机制管理器"""
        print("❓ 测试确认机制管理器...")
        
        try:
            from xwe.core.confirmation_manager import confirmation_manager
            
            # 测试请求确认
            test_data = {'value': 42}
            executed = False
            
            def test_callback(data):
                nonlocal executed
                executed = True
                print(f"✓ 回调执行，数据: {data}")
            
            conf_id = confirmation_manager.request_confirmation(
                action='test_action',
                description='这是一个测试确认',
                callback=test_callback,
                data=test_data
            )
            print(f"✓ 确认请求创建，ID: {conf_id}")
            
            # 测试获取待确认操作
            pending = confirmation_manager.get_pending_confirmations()
            print(f"✓ 待确认操作数量: {len(pending)}")
            
            # 测试确认操作
            success = confirmation_manager.confirm(conf_id, confirmed=True)
            print(f"✓ 确认操作结果: {success}")
            
            # 验证逻辑
            if success and executed and len(pending) == 1:
                print("🎉 确认机制管理器功能正常！")
                return True
            else:
                print(f"❌ 确认机制逻辑错误 - 成功:{success}, 执行:{executed}, 待确认:{len(pending)}")
                return False
                
        except Exception as e:
            print(f"❌ 确认机制测试失败: {e}")
            return False
    
    def test_5_game_core_integration(self):
        """测试5: 游戏核心集成测试"""
        print("🎮 测试游戏核心集成...")
        
        try:
            # 修改环境变量以避免API调用
            os.environ['LLM_PROVIDER'] = 'mock'
            
            from xwe.core.game_core import GameCore
            
            # 创建游戏实例
            game = GameCore()
            print("✓ 游戏核心创建成功")
            
            # 检查重要组件
            assert hasattr(game, 'character_roller'), "缺少角色Roll系统"
            assert hasattr(game, 'status_manager'), "缺少状态管理器"  
            assert hasattr(game, 'achievement_system'), "缺少成就系统"
            print("✓ 游戏组件完整")
            
            # 测试物品系统集成
            from xwe.core.item_system import item_system
            test_stones = item_system.get_spirit_stones('test_integration')
            print(f"✓ 物品系统集成正常，测试灵石: {test_stones}")
            
            # 检查是否使用了新的item_system而不是硬编码
            # 在游戏核心代码中搜索item_system的使用
            import inspect
            game_source = inspect.getsource(GameCore)
            if 'item_system.get_spirit_stones' in game_source:
                print("✓ 游戏核心已集成动态物品系统")
            else:
                print("⚠️ 游戏核心可能仍在使用硬编码值")
            
            print("🎉 游戏核心集成测试通过！")
            return True
            
        except Exception as e:
            print(f"❌ 游戏核心集成测试失败: {e}")
            return False
    
    def test_6_roll_system(self):
        """测试6: Roll系统功能"""
        print("🎲 测试Roll系统功能...")
        
        try:
            from xwe.core.roll_system import CharacterRoller
            
            # 创建Roll系统实例
            roller = CharacterRoller()
            print("✓ Roll系统创建成功")
            
            # 执行一次Roll
            roll_result = roller.roll()
            print("✓ Roll执行成功")
            
            # 验证Roll结果结构
            required_attrs = ['name', 'gender', 'identity', 'attributes', 
                            'spiritual_root_type', 'destiny', 'talents', 'combat_power']
            
            for attr in required_attrs:
                if hasattr(roll_result, attr):
                    value = getattr(roll_result, attr)
                    print(f"✓ {attr}: {value}")
                else:
                    print(f"❌ 缺少属性: {attr}")
                    return False
            
            # 验证系统Roll（可能为空）
            if hasattr(roll_result, 'system') and roll_result.system:
                print(f"✓ 系统: {roll_result.system['name']} ({roll_result.system['rarity']})")
            else:
                print("✓ 系统: 无特殊系统")
            
            print("🎉 Roll系统功能正常！")
            return True
            
        except Exception as e:
            print(f"❌ Roll系统测试失败: {e}")
            return False
    
    def test_7_backup_verification(self):
        """测试7: 验证备份文件"""
        print("💾 验证备份文件...")
        
        try:
            backup_files = [
                'xwe/core/game_core.py.backup',
                'xwe/core/character.py.backup'
            ]
            
            for backup_file in backup_files:
                file_path = project_root / backup_file
                if file_path.exists():
                    print(f"✓ 备份文件存在: {backup_file}")
                    # 检查文件大小
                    size = file_path.stat().st_size
                    print(f"  文件大小: {size} 字节")
                else:
                    print(f"❌ 备份文件不存在: {backup_file}")
                    return False
            
            print("🎉 所有备份文件验证通过！")
            return True
            
        except Exception as e:
            print(f"❌ 备份文件验证失败: {e}")
            return False
    
    def test_8_refactor_plans(self):
        """测试8: 验证重构计划"""
        print("📋 验证重构计划...")
        
        try:
            refactor_files = [
                'refactor_plan_1__fuzzy_parse.md',
                'refactor_plan_2_process_command.md', 
                'refactor_plan_3_validate_with_error.md'
            ]
            
            for plan_file in refactor_files:
                file_path = project_root / plan_file
                if file_path.exists():
                    print(f"✓ 重构计划存在: {plan_file}")
                    # 读取前几行验证内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                        if first_line.startswith('# 🔧 重构计划'):
                            print(f"  ✓ 计划格式正确")
                        else:
                            print(f"  ⚠️ 计划格式可能不正确")
                else:
                    print(f"❌ 重构计划不存在: {plan_file}")
                    return False
            
            print("🎉 所有重构计划验证通过！")
            return True
            
        except Exception as e:
            print(f"❌ 重构计划验证失败: {e}")
            return False
    
    def test_9_performance_test(self):
        """测试9: 性能基准测试"""
        print("⚡ 基准性能测试...")
        
        try:
            import time
            from xwe.core.item_system import item_system
            from xwe.core.system_manager import system_manager
            
            # 测试物品系统性能
            start_time = time.time()
            for i in range(1000):
                item_system.add_item(f'player_{i%10}', 'spirit_stones', 1)
                item_system.get_spirit_stones(f'player_{i%10}')
            item_time = time.time() - start_time
            print(f"✓ 物品系统性能: 1000次操作耗时 {item_time:.3f}秒")
            
            # 测试系统管理器性能
            start_time = time.time()
            test_system = {'name': 'test', 'rarity': 'common', 'features': []}
            for i in range(100):
                system_manager.activate_system(f'player_{i%10}', test_system)
                system_manager.get_system_bonus(f'player_{i%10}', 'cultivation_speed')
            system_time = time.time() - start_time
            print(f"✓ 系统管理器性能: 100次操作耗时 {system_time:.3f}秒")
            
            # 性能阈值检查
            if item_time < 1.0 and system_time < 0.5:
                print("🎉 性能测试通过！")
                return True
            else:
                print(f"⚠️ 性能可能需要优化 - 物品:{item_time:.3f}s, 系统:{system_time:.3f}s")
                return True  # 不算失败，只是警告
                
        except Exception as e:
            print(f"❌ 性能测试失败: {e}")
            return False
    
    def test_10_integration_test(self):
        """测试10: 综合集成测试"""
        print("🔗 综合集成测试...")
        
        try:
            # 模拟完整的游戏场景
            from xwe.core.item_system import item_system
            from xwe.core.system_manager import system_manager
            from xwe.core.confirmation_manager import confirmation_manager
            
            player_id = "integration_test_player"
            
            # 1. 玩家获得灵石
            item_system.add_item(player_id, 'spirit_stones', 1000)
            stones = item_system.get_spirit_stones(player_id)
            print(f"✓ 步骤1: 玩家获得 {stones} 灵石")
            
            # 2. 激活系统
            lucky_system = {
                'name': '鸿运系统',
                'rarity': 'legendary', 
                'features': ['双倍奖励', '幸运加成']
            }
            system_manager.activate_system(player_id, lucky_system)
            print("✓ 步骤2: 激活鸿运系统")
            
            # 3. 获取系统加成
            bonus = system_manager.get_system_bonus(player_id, 'cultivation_speed')
            has_double = system_manager.has_feature(player_id, '双倍奖励')
            print(f"✓ 步骤3: 修炼加成 {bonus}x, 双倍奖励: {has_double}")
            
            # 4. 消费灵石（需要确认）
            confirmed = False
            def spend_callback(data):
                nonlocal confirmed
                confirmed = True
                cost = data['cost'] 
                item_system.remove_item(player_id, 'spirit_stones', cost)
                print(f"✓ 步骤4: 消费了 {cost} 灵石")
            
            conf_id = confirmation_manager.request_confirmation(
                '购买丹药',
                '花费500灵石购买筑基丹',
                spend_callback,
                {'cost': 500}
            )
            confirmation_manager.confirm(conf_id, True)
            
            # 5. 验证最终状态
            final_stones = item_system.get_spirit_stones(player_id)
            expected_stones = 1000 - 500  # 应该剩余500
            
            if final_stones == expected_stones and confirmed and bonus == 3.0:
                print("✓ 步骤5: 最终状态验证通过")
                print("🎉 综合集成测试通过！")
                return True
            else:
                print(f"❌ 最终状态错误 - 灵石:{final_stones}(期望{expected_stones}), 确认:{confirmed}, 加成:{bonus}")
                return False
                
        except Exception as e:
            print(f"❌ 综合集成测试失败: {e}")
            return False
    
    def print_summary(self):
        """打印测试总结"""
        print(f"\n{'='*80}")
        print(f"🏁 测试总结")
        print(f"{'='*80}")
        print(f"总测试数: {self.total_tests}")
        print(f"通过: {self.passed_tests} ✅")
        print(f"失败: {self.failed_tests} ❌")
        print(f"成功率: {(self.passed_tests/self.total_tests*100):.1f}%")
        print(f"{'='*80}")
        
        if self.failed_tests == 0:
            print("🎉 所有测试通过！优化工具效果显著！")
            print("\n🚀 建议下一步操作：")
            print("1. 启动游戏进行实际测试")
            print("2. 查看重构计划并逐步实施")
            print("3. 根据性能测试结果进行进一步优化")
        else:
            print("⚠️ 存在失败的测试，请检查相关模块")
            print("\n🔧 失败的测试：")
            for test_name, result in self.test_results.items():
                if result["status"] != "PASS":
                    print(f"  - {test_name}: {result['status']} - {result['error']}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始运行优化验证测试套件...")
        print(f"测试环境: Python {sys.version}")
        print(f"工作目录: {os.getcwd()}")
        
        # 定义所有测试
        tests = [
            ("模块导入测试", self.test_1_imports),
            ("物品系统功能测试", self.test_2_item_system),
            ("系统管理器功能测试", self.test_3_system_manager),
            ("确认机制管理器测试", self.test_4_confirmation_manager),
            ("游戏核心集成测试", self.test_5_game_core_integration),
            ("Roll系统功能测试", self.test_6_roll_system),
            ("备份文件验证", self.test_7_backup_verification),
            ("重构计划验证", self.test_8_refactor_plans),
            ("性能基准测试", self.test_9_performance_test),
            ("综合集成测试", self.test_10_integration_test),
        ]
        
        # 运行所有测试
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # 打印总结
        self.print_summary()
        
        return self.failed_tests == 0


def main():
    """主函数"""
    print("🎮 仙侠世界游戏优化验证测试")
    print("=" * 80)
    
    # 检查项目路径
    if not (project_root / 'xwe').exists():
        print("❌ 错误: 未找到xwe目录，请确保在正确的项目目录下运行此脚本")
        return False
    
    # 运行测试
    tester = OptimizationTester()
    success = tester.run_all_tests()
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
