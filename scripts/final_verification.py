#!/usr/bin/env python3
"""
最终验证脚本 - 测试项目是否能正常运行
"""

import sys
import subprocess
import time
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试核心模块导入"""
    print("🔍 测试核心模块导入...")
    
    try:
        # 测试表达式模块
        from xwe.engine.expression import ExpressionParser
        from xwe.engine.expression.exceptions import ValidationError
        print("✅ 表达式模块导入成功")
        
        # 测试功能模块
        from xwe.features import content_ecosystem
        print("✅ 功能模块导入成功")
        
        # 测试度量模块
        from xwe.metrics import metrics_registry, time_histogram
        print("✅ 度量模块导入成功")
        
        # 测试API模块
        from api import register_api
        print("✅ API模块导入成功")
        
        # 测试入口点
        from entrypoints.run_web_ui_optimized import app
        print("✅ Web UI模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("\n🔍 测试基本功能...")
    
    try:
        # 测试表达式解析
        from xwe.engine.expression import ExpressionParser
        parser = ExpressionParser()
        result = parser.evaluate("2 + 3 * 4")
        assert result == 14.0, f"表达式计算错误: {result}"
        print("✅ 表达式解析功能正常")
        
        # 测试游戏核心
        from xwe.core import GameCore
        game = GameCore()
        print("✅ 游戏核心初始化成功")
        
        # 测试角色系统
        from xwe.core.character import Character, CharacterType
        player = Character("测试玩家", CharacterType.PLAYER)
        print("✅ 角色系统功能正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_ui():
    """测试Web UI是否能启动"""
    print("\n🔍 测试 Web UI...")
    
    try:
        # 尝试导入并创建app
        from entrypoints.run_web_ui_optimized import app
        
        # 测试路由是否注册
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                routes.append(str(rule))
        
        print(f"✅ Web UI 创建成功，发现 {len(routes)} 个路由")
        print("   部分路由:")
        for route in routes[:5]:
            print(f"   - {route}")
        
        return True
        
    except Exception as e:
        print(f"❌ Web UI 测试失败: {e}")
        return False

def run_quick_test():
    """运行快速测试"""
    print("\n🔍 运行快速集成测试...")
    
    try:
        # 创建测试脚本
        test_script = project_root / "test_integration.py"
        test_content = '''
import sys
sys.path.insert(0, ".")

try:
    from xwe.core import GameCore
    from xwe.core.character import Character, CharacterType
    
    # 创建游戏实例
    game = GameCore()
    
    # 创建角色
    player = Character("测试者", CharacterType.PLAYER)
    
    # 测试基本操作
    player.gain_exp(100)
    
    print("✅ 集成测试通过")
    sys.exit(0)
except Exception as e:
    print(f"❌ 集成测试失败: {e}")
    sys.exit(1)
'''
        
        test_script.write_text(test_content)
        
        # 运行测试
        result = subprocess.run(
            [sys.executable, str(test_script)],
            cwd=str(project_root),
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:", result.stderr)
        
        # 清理
        test_script.unlink()
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 快速测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始最终验证...")
    print("=" * 50)
    
    all_passed = True
    
    # 1. 测试导入
    if not test_imports():
        all_passed = False
    
    # 2. 测试基本功能
    if not test_basic_functionality():
        all_passed = False
    
    # 3. 测试Web UI
    if not test_web_ui():
        all_passed = False
    
    # 4. 运行集成测试
    if not run_quick_test():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！项目可以正常运行。")
        print("\n📌 你现在可以运行:")
        print("   python entrypoints/run_web_ui_optimized.py")
        print("   然后访问 http://localhost:5000")
    else:
        print("⚠️ 部分测试失败，请查看上面的错误信息。")
        print("\n📌 建议:")
        print("1. 运行 python scripts/comprehensive_fix.py 进行自动修复")
        print("2. 查看 project_snapshot.json 了解具体错误")
        print("3. 手动修复剩余问题")

if __name__ == "__main__":
    main()
