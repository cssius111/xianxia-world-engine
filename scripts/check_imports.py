#!/usr/bin/env python3
"""
快速测试脚本 - 检查修复后的导入问题
"""

import sys
import importlib
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试关键模块的导入"""
    modules_to_test = [
        # 核心模块
        'xwe.engine.expression',
        'xwe.engine.expression.exceptions',
        'xwe.features',
        'xwe.metrics',
        'xwe.core',
        'xwe.services',
        
        # API模块
        'api',
        
        # 其他模块
        'core.player_initializer',
        'entrypoints.run_web_ui_optimized',
    ]
    
    failed = []
    success = []
    
    for module_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            success.append(module_name)
            print(f"✅ {module_name}")
        except Exception as e:
            failed.append((module_name, str(e)))
            print(f"❌ {module_name}: {e}")
    
    print(f"\n📊 结果统计:")
    print(f"✅ 成功: {len(success)}")
    print(f"❌ 失败: {len(failed)}")
    
    if failed:
        print("\n❌ 失败的模块:")
        for module, error in failed:
            print(f"  - {module}: {error}")
    
    return len(failed) == 0

if __name__ == "__main__":
    print("🔍 检查修复后的导入问题...\n")
    if test_imports():
        print("\n🎉 所有模块导入成功!")
    else:
        print("\n⚠️ 仍有模块导入失败，需要进一步修复")
