#!/usr/bin/env python3
"""修仙世界引擎 - 错误诊断工具"""

import os
import sys
import subprocess

print("=== 修仙世界引擎 - 错误诊断 ===\n")

# 1. 检查Python版本
print("1. Python版本检查...")
python_version = sys.version
print(f"   当前版本: {python_version.split()[0]}")
if sys.version_info >= (3, 8):
    print("   ✅ Python版本符合要求（3.8+）")
else:
    print("   ❌ Python版本过低，需要3.8或更高版本")

# 2. 检查工作目录
print("\n2. 工作目录检查...")
current_dir = os.getcwd()
print(f"   当前目录: {current_dir}")
if "xianxia_world_engine" in current_dir:
    print("   ✅ 在正确的项目目录中")
else:
    print("   ⚠️  可能不在项目目录中")

# 3. 检查关键文件
print("\n3. 关键文件检查...")
key_files = [
    "xwe/__init__.py",
    "xwe/core/__init__.py",
    "xwe/engine/__init__.py",
    "xwe/npc/__init__.py",
    "xwe/world/__init__.py",
    "main.py"
]

all_files_exist = True
for file in key_files:
    if os.path.exists(file):
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ 缺失: {file}")
        all_files_exist = False

# 4. 测试导入
print("\n4. 模块导入测试...")
import_tests = [
    ("表达式解析器", "from xwe.engine.expression import ExpressionParser"),
    ("NPC管理器", "from xwe.npc.npc_manager import NPCManager"),
    ("游戏核心", "from xwe.core.game_core import GameCore"),
]

import_success = True
for name, import_stmt in import_tests:
    try:
        exec(import_stmt)
        print(f"   ✅ {name}")
    except Exception as e:
        print(f"   ❌ {name}: {str(e)[:60]}...")
        import_success = False

# 5. 诊断结果
print("\n" + "="*50)
print("诊断结果：")

if all_files_exist and import_success:
    print("✅ 所有检查通过！")
    print("\n建议运行：")
    print("  python play_demo.py")
    print("  或")
    print("  python main.py")
else:
    print("❌ 发现问题")
    print("\n建议操作：")
    print("1. 确保在项目根目录运行")
    print("2. 运行修复脚本: python complete_fix.py")
    print("3. 如果问题持续，查看 FIX_NOTES.md")

print("\n" + "="*50)

# 询问是否运行修复
if not (all_files_exist and import_success):
    response = input("\n是否立即运行修复脚本？(y/n): ")
    if response.lower() == 'y':
        print("\n运行修复脚本...")
        subprocess.run([sys.executable, "complete_fix.py"])
