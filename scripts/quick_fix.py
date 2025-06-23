#!/usr/bin/env python3
"""
快速修复脚本
"""

print("=== 修仙世界UI快速修复 ===")

print("\n1. 检查依赖...")
try:
    import flask
    print("✓ Flask 已安装")
except ImportError:
    print("✗ Flask 未安装，请运行: pip install flask")

print("\n2. 创建必要目录...")
from pathlib import Path
project_root = Path(__file__).parent.parent

dirs_to_create = [
    "logs/char_gen",
    "saves",
    "static/audio"
]

for dir_path in dirs_to_create:
    full_path = project_root / dir_path
    full_path.mkdir(parents=True, exist_ok=True)
    print(f"✓ 创建目录: {dir_path}")

print("\n3. 测试角色生成...")
import sys
sys.path.append(str(project_root))
try:
    from scripts.gen_character import gen_random, check_jackpot
    char = gen_random()
    print(f"✓ 生成角色: {char['name']}")
    jackpot = check_jackpot(char)
    if jackpot['triggered']:
        print(f"✓ {jackpot['title']}")
except Exception as e:
    print(f"✗ 角色生成错误: {e}")

print("\n4. 启动说明:")
print("运行以下命令启动服务器:")
print(f"python {project_root}/entrypoints/run_web_ui_optimized.py")
print("\n或使用测试脚本:")
print(f"python {project_root}/scripts/test_ui.py")

print("\n5. 访问地址:")
print("http://localhost:5001")

print("\n=== 修复完成 ===")
