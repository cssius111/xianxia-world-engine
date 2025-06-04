#!/usr/bin/env python
"""
修仙世界引擎 - 快速测试指南
一步步验证所有功能是否正常
"""

import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


class QuickTester:
    """快速测试器"""
    
    def __init__(self):
        self.results = []
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
    
    def test_1_environment(self):
        """测试1: 环境检查"""
        print("\n🔍 测试1: 环境检查")
        print("-"*50)
        
        checks = []
        
        # Python版本
        py_version = sys.version.split()[0]
        checks.append(("Python版本", py_version, "✅" if py_version >= "3.8" else "❌"))
        
        # API密钥
        checks.append(("DeepSeek API密钥", 
                      f"{self.api_key[:10]}..." if self.api_key else "未设置",
                      "✅" if self.api_key else "⚠️"))
        
        # 核心文件
        core_files = [
            "main.py",
            "xwe/core/game_core.py",
            "xwe/core/nlp/nlp_processor.py",
            "xwe/core/character.py"
        ]
        
        for file in core_files:
            exists = (PROJECT_ROOT / file).exists()
            checks.append((f"文件: {file}", "存在" if exists else "缺失", "✅" if exists else "❌"))
        
        # 显示结果
        for name, status, icon in checks:
            print(f"{icon} {name}: {status}")
        
        return all(icon != "❌" for _, _, icon in checks)
    
    def test_2_roll_system(self):
        """测试2: Roll系统"""
        print("\n\n🎲 测试2: Roll系统")
        print("-"*50)
        
        try:
            from xwe.core.character import CharacterCreator
            
            creator = CharacterCreator()
            character = creator.roll_character()
            
            print(f"✅ 成功生成角色: {character.name}")
            print(f"   灵根: {character.spiritual_root['name']}")
            print(f"   命格: {character.fate['name']}")
            
            # 测试随机性
            names = set()
            for _ in range(10):
                char = creator.roll_character()
                names.add(char.name)
            
            if len(names) > 1:
                print(f"✅ 随机性验证: 10次Roll产生了{len(names)}个不同名字")
            else:
                print("❌ 随机性问题: 名字没有变化")
            
            return True
            
        except Exception as e:
            print(f"❌ Roll系统错误: {e}")
            return False
    
    def test_3_nlp_basic(self):
        """测试3: NLP基础功能"""
        print("\n\n🧠 测试3: NLP基础功能")
        print("-"*50)
        
        if not self.api_key:
            print("⚠️  跳过NLP测试（未设置API密钥）")
            return True
        
        try:
            from xwe.core.nlp.nlp_processor import NLPProcessor, NLPConfig
            from xwe.core.command_parser import CommandParser
            
            parser = CommandParser()
            config = NLPConfig(enable_llm=True)
            nlp = NLPProcessor(parser, config)
            
            # 简单测试
            test_input = "看看我的状态"
            print(f"测试输入: '{test_input}'")
            
            start = time.time()
            result = nlp.parse(test_input)
            elapsed = time.time() - start
            
            print(f"解析耗时: {elapsed:.2f}秒")
            print(f"命令类型: {result.command_type}")
            print(f"置信度: {result.confidence:.2f}")
            
            if result.confidence > 0:
                print("✅ NLP基础功能正常")
                return True
            else:
                print("❌ NLP解析失败")
                return False
                
        except Exception as e:
            print(f"❌ NLP系统错误: {e}")
            return False
    
    def test_4_data_system(self):
        """测试4: 数据系统"""
        print("\n\n💾 测试4: 数据系统")
        print("-"*50)
        
        try:
            from xwe.core.data_manager import DynamicDataManager
            
            dm = DynamicDataManager()
            
            # 测试数据加载
            print(f"✅ 玩家数据加载成功")
            print(f"   当前等级: Lv.{dm.player_data['level']}")
            print(f"   当前境界: {dm.player_data['realm']}")
            
            # 测试修炼
            before_exp = dm.player_data['exp']
            result = dm.cultivate_dynamic(1)
            after_exp = dm.player_data['exp']
            
            if after_exp > before_exp:
                print(f"✅ 修炼系统正常")
                print(f"   获得经验: {result['total_exp']}")
            else:
                print("❌ 修炼没有获得经验")
            
            # 测试保存
            dm.save_all()
            print("✅ 数据保存成功")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据系统错误: {e}")
            return False
    
    def test_5_game_flow(self):
        """测试5: 游戏主流程"""
        print("\n\n🎮 测试5: 游戏主流程")
        print("-"*50)
        
        try:
            from xwe.core.game_core import GameCore
            
            # 检查关键方法
            methods = ['run', 'main_loop', 'handle_command']
            
            for method in methods:
                if hasattr(GameCore, method):
                    print(f"✅ GameCore.{method}() 存在")
                else:
                    print(f"❌ GameCore.{method}() 缺失")
            
            return True
            
        except Exception as e:
            print(f"❌ 游戏核心错误: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 修仙世界引擎 - 快速功能测试")
        print("="*60)
        
        tests = [
            ("环境检查", self.test_1_environment),
            ("Roll系统", self.test_2_roll_system),
            ("NLP功能", self.test_3_nlp_basic),
            ("数据系统", self.test_4_data_system),
            ("游戏流程", self.test_5_game_flow)
        ]
        
        results = []
        
        for name, test_func in tests:
            try:
                success = test_func()
                results.append((name, success))
            except Exception as e:
                print(f"\n❌ {name}测试崩溃: {e}")
                results.append((name, False))
        
        # 总结
        print("\n\n" + "="*60)
        print("📊 测试总结")
        print("="*60)
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for name, success in results:
            icon = "✅" if success else "❌"
            print(f"{icon} {name}: {'通过' if success else '失败'}")
        
        print(f"\n总计: {passed}/{total} 通过")
        
        if passed == total:
            print("\n🎉 所有测试通过！游戏可以正常运行！")
            print("\n建议：")
            print("1. 运行 python main.py 开始游戏")
            print("2. 在主菜单选择不同功能体验")
        elif passed > 0:
            print("\n⚠️  部分功能可用，建议修复失败的测试")
        else:
            print("\n❌ 测试全部失败，请检查项目配置")


def quick_fix_suggestions():
    """快速修复建议"""
    print("\n\n💡 常见问题快速修复")
    print("="*60)
    
    print("\n1. NLP不工作？")
    print("   - 设置API密钥: export DEEPSEEK_API_KEY='sk-xxx'")
    print("   - 运行修复: python fix_deepseek_json.py")
    
    print("\n2. 导入错误？")
    print("   - 检查Python路径")
    print("   - 在项目根目录运行")
    
    print("\n3. Roll系统问题？")
    print("   - 检查 xwe/data/character/roll_data.json")
    print("   - 确保数据文件完整")
    
    print("\n4. 游戏无法启动？")
    print("   - 运行: python fix_game_core.py")
    print("   - 检查 main.py 是否存在")


def main():
    """主函数"""
    tester = QuickTester()
    tester.run_all_tests()
    quick_fix_suggestions()


if __name__ == "__main__":
    main()
