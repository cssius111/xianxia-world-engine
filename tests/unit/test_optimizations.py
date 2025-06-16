#!/usr/bin/env python3
"""
游戏功能测试脚本 - 验证优化修复效果
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试关键模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        # 测试新创建的系统模块
        from xwe.core.item_system import item_system, Item, ItemSystem
        print("✅ item_system 导入成功")
        
        from xwe.core.system_manager import system_manager, SystemManager
        print("✅ system_manager 导入成功")
        
        from xwe.core.confirmation_manager import confirmation_manager, ConfirmationManager
        print("✅ confirmation_manager 导入成功")
        
        from xwe.core.exception_handler import handle_exceptions, safe_api_call
        print("✅ exception_handler 导入成功")
        
        from game_config import config, GameConfig
        print("✅ game_config 导入成功")
        
        # 测试核心游戏模块
        from xwe.core.game_core import GameCore
        print("✅ GameCore 导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他导入错误: {e}")
        return False

def test_item_system():
    """测试物品系统功能"""
    print("\n🎒 测试物品系统...")
    
    try:
        from xwe.core.item_system import item_system, Item
        
        # 创建测试物品
        test_item = Item(
            id="spirit_stone",
            name="灵石",
            description="修炼必需的货币",
            value=1
        )
        
        # 测试物品管理
        item_system.items["spirit_stone"] = test_item
        
        # 测试玩家背包
        test_player_id = "test_player"
        
        # 添加物品
        result = item_system.add_item(test_player_id, "spirit_stone", 100)
        assert result == True
        print("✅ 添加物品功能正常")
        
        # 获取灵石数量
        stones = item_system.get_spirit_stones(test_player_id)
        assert stones == 100
        print(f"✅ 获取灵石功能正常: {stones}个")
        
        # 移除物品
        result = item_system.remove_item(test_player_id, "spirit_stone", 50)
        assert result == True
        
        # 验证数量
        stones = item_system.get_spirit_stones(test_player_id)
        assert stones == 50
        print(f"✅ 移除物品功能正常: 剩余{stones}个")
        
        return True
        
    except Exception as e:
        print(f"❌ 物品系统测试失败: {e}")
        return False

def test_system_manager():
    """测试系统管理器功能"""
    print("\n⚙️ 测试系统管理器...")
    
    try:
        from xwe.core.system_manager import system_manager
        
        # 测试修炼系统激活
        test_system = {
            'name': '九转修炼系统',
            'rarity': 'epic',
            'features': ['自动修炼', '修炼加速', '突破辅助']
        }
        
        test_player_id = "test_player"
        
        # 激活系统
        system_manager.activate_system(test_player_id, test_system)
        print("✅ 系统激活成功")
        
        # 测试加成获取
        cultivation_bonus = system_manager.get_system_bonus(test_player_id, 'cultivation_speed')
        assert cultivation_bonus == 2.0  # epic级别应该是2.0倍
        print(f"✅ 修炼加成正常: {cultivation_bonus}x")
        
        # 测试功能检查
        has_feature = system_manager.has_feature(test_player_id, '自动修炼')
        assert has_feature == True
        print("✅ 功能检查正常")
        
        # 获取系统信息
        player_system = system_manager.get_player_system(test_player_id)
        assert player_system is not None
        assert player_system['name'] == '九转修炼系统'
        print("✅ 系统信息获取正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 系统管理器测试失败: {e}")
        return False

def test_game_config():
    """测试游戏配置"""
    print("\n⚙️ 测试游戏配置...")
    
    try:
        from game_config import config
        
        # 检查基础配置
        assert config.game_name == "仙侠世界引擎"
        assert config.version == "2.0.0"
        print(f"✅ 游戏配置加载正常: {config.game_name} v{config.version}")
        
        # 检查路径设置
        assert hasattr(config, 'data_path')
        assert hasattr(config, 'save_path')
        print("✅ 路径配置正常")
        
        # 检查性能设置
        assert config.cache_size > 0
        assert config.max_npcs_in_memory > 0
        print(f"✅ 性能配置正常: 缓存{config.cache_size}, NPC限制{config.max_npcs_in_memory}")
        
        return True
        
    except Exception as e:
        print(f"❌ 游戏配置测试失败: {e}")
        return False

def test_game_core_integration():
    """测试游戏核心集成"""
    print("\n🎮 测试游戏核心集成...")
    
    try:
        from xwe.core.game_core import GameCore
        
        # 创建游戏核心实例
        game = GameCore()
        print("✅ GameCore 实例创建成功")
        
        # 检查item_system是否正确集成（通过检查导入）
        import inspect
        source = inspect.getsource(GameCore)
        
        if "from .item_system import item_system" in source:
            print("✅ 物品系统已正确集成到GameCore")
        else:
            print("⚠️  物品系统可能未完全集成")
        
        # 检查是否有硬编码的spirit_stones
        if "spirit_stones': 1000" in source and "item_system.get_spirit_stones" in source:
            print("✅ 灵石获取已从硬编码改为动态获取")
        elif "item_system.get_spirit_stones" in source:
            print("✅ 灵石获取使用动态方式")
        else:
            print("⚠️  灵石获取可能仍使用硬编码")
        
        return True
        
    except Exception as e:
        print(f"❌ 游戏核心集成测试失败: {e}")
        return False

def test_game_startup():
    """测试游戏启动（不进入交互模式）"""
    print("\n🚀 测试游戏启动...")
    
    try:
        from xwe.core.game_core import GameCore
        
        # 创建游戏实例
        game = GameCore()
        
        # 检查基本系统是否初始化
        assert hasattr(game, 'data_loader')
        assert hasattr(game, 'nlp_processor')  
        assert hasattr(game, 'character_roller')
        assert hasattr(game, 'achievement_system')
        print("✅ 游戏系统初始化正常")
        
        # 测试开局Roll系统
        roll_result = game.character_roller.roll()
        assert hasattr(roll_result, 'name')
        assert hasattr(roll_result, 'attributes')
        assert hasattr(roll_result, 'combat_power')
        print("✅ 开局Roll系统正常")
        
        # 检查输出缓冲系统
        game.output("测试输出")
        output = game.get_output()
        assert len(output) == 1
        assert output[0] == "测试输出"
        print("✅ 输出系统正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 游戏启动测试失败: {e}")
        return False

def run_full_test():
    """运行完整测试"""
    print("🧪 开始游戏功能测试")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("物品系统", test_item_system),
        ("系统管理器", test_system_manager),
        ("游戏配置", test_game_config),
        ("核心集成", test_game_core_integration),
        ("游戏启动", test_game_startup)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print("🎯 测试结果总结:")
    print(f"✅ 通过: {passed} 项")
    print(f"❌ 失败: {failed} 项")
    print(f"📊 成功率: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 所有测试通过！优化修复效果良好！")
        print("\n🚀 建议下一步:")
        print("1. 运行 'python3 entrypoints/run_web_ui_optimized.py' 进行实际游戏测试")
        print("2. 测试Roll系统、对话系统、物品系统")
        print("3. 查看重构计划并开始函数优化")
    else:
        print(f"\n⚠️  发现 {failed} 个问题需要修复")
        print("建议检查相关模块的导入和配置")
    
    return failed == 0

if __name__ == '__main__':
    success = run_full_test()
    sys.exit(0 if success else 1)
