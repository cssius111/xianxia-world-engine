#!/usr/bin/env python3
"""
简单的项目状态检查
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
# 脚本位于 tests/debug/debug_scripts，需要向上四级获取项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 60)
print("🔍 修仙世界引擎 - 项目状态检查")
print("=" * 60)
print(f"项目路径: {PROJECT_ROOT}")
print(f"Python版本: {sys.version}")
print("=" * 60)

# 测试基本导入
print("\n测试基本导入:")

tests = [
    ("Flask", "from flask import Flask"),
    ("游戏配置", "from game_config import config"),
    ("角色属性", "from xwe.core.attributes import CharacterAttributes"),
    ("角色类", "from xwe.core.character import Character"),
    ("游戏核心", "from xwe.core.game_core import create_enhanced_game"),
]

failed_imports = []

for name, import_statement in tests:
    try:
        exec(import_statement)
        print(f"✅ {name}")
    except Exception as e:
        print(f"❌ {name}: {e}")
        failed_imports.append((name, str(e)))

# 检查关键文件
print("\n检查关键文件:")

files_to_check = [
    "entrypoints/run_web_ui_optimized.py",
    "requirements.txt",
    "templates/welcome_optimized.html",
    "templates/intro_optimized.html",
    "templates/game_enhanced_optimized_v2.html",
    "static/css/ink_style.css",
    "static/js/game_controller.js",
    ".env",
]

missing_files = []

for file_path in files_to_check:
    full_path = PROJECT_ROOT / file_path
    if full_path.exists():
        print(f"✅ {file_path}")
    else:
        print(f"❌ {file_path}")
        missing_files.append(file_path)

# 总结
print("\n" + "=" * 60)
print("📊 检查总结:")

if not failed_imports and not missing_files:
    print("\n✅ 所有检查都通过！项目应该可以正常运行。")
    print("\n启动命令:")
    print(f"cd {PROJECT_ROOT}")
    print("python entrypoints/run_web_ui_optimized.py")
else:
    if failed_imports:
        print(f"\n❌ 有 {len(failed_imports)} 个导入失败:")
        for name, error in failed_imports:
            print(f"  - {name}: {error}")
        print("\n建议: pip install -r requirements.txt")

    if missing_files:
        print(f"\n❌ 有 {len(missing_files)} 个文件缺失:")
        for file in missing_files:
            print(f"  - {file}")

        if ".env" in missing_files and (PROJECT_ROOT / ".env.example").exists():
            print("\n建议: cp .env.example .env")

print("\n" + "=" * 60)

# 如果可能，尝试导入并显示配置
try:
    from game_config import config

    print("\n游戏配置信息:")
    print(f"  游戏名称: {config.game_name}")
    print(f"  版本: {config.version}")
    print(f"  调试模式: {config.debug_mode}")
except:
    pass
