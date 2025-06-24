#!/usr/bin/env python3
"""
测试脚本2：检查文件系统结构
"""

import os
import json
from pathlib import Path

# 项目根目录
# 脚本位于 tests/debug/debug_scripts，需要向上四级获取根目录
PROJECT_ROOT = Path(__file__).resolve().parents[3]

print("=" * 60)
print("📁 修仙世界引擎 - 文件系统测试")
print("=" * 60)

# 检查结果
check_results = {
    "directories": {},
    "files": {},
    "data_files": {},
    "missing": []
}

# 1. 检查必要的目录
print("\n1. 检查目录结构:")
required_dirs = [
    "api",
    "core", 
    "data",
    "data/restructured",
    "docs",
    "entrypoints",
    "examples",
    "feedback",
    "logs",
    "mods",
    "output",
    "plugins",
    "routes",
    "saves",
    "scripts",
    "static",
    "static/css",
    "static/js",
    "static/js/modules",
    "static/audio",
    "static/audio/sfx",
    "static/audio/music",
    "static/audio/ambient",
    "templates",
    "templates/modals",
    "tests",
    "tools",
    "ui",
    "xwe",
    "xwe/core",
    "xwe/features"
]

for dir_path in required_dirs:
    full_path = PROJECT_ROOT / dir_path
    exists = full_path.exists() and full_path.is_dir()
    check_results["directories"][dir_path] = exists
    status = "✅" if exists else "❌"
    print(f"{status} {dir_path}")
    if not exists:
        check_results["missing"].append(f"目录: {dir_path}")

# 2. 检查必要的文件
print("\n2. 检查关键文件:")
required_files = [
    "run_web_ui_v2.py",
    "game_config.py",
    "requirements.txt",
    "README.md",
    ".env.example",
    
    # 模板文件
    "templates/welcome_optimized.html",
    "templates/intro_optimized.html",
    "templates/game_enhanced_optimized_v2.html",
    
    # 样式文件
    "static/css/ink_style.css",
    
    # JavaScript文件
    "static/js/game_controller.js",
    "static/js/modules/ui_controller.js",
    "static/js/modules/audio_controller.js",
    "static/js/modules/player_profile.js",
    "static/js/modules/modal_controller.js",
    
    # Service Worker
    "static/sw.js"
]

for file_path in required_files:
    full_path = PROJECT_ROOT / file_path
    exists = full_path.exists() and full_path.is_file()
    check_results["files"][file_path] = exists
    status = "✅" if exists else "❌"
    print(f"{status} {file_path}")
    if not exists:
        check_results["missing"].append(f"文件: {file_path}")

# 3. 检查数据文件
print("\n3. 检查游戏数据文件:")
data_files = [
    "data/game_data/templates/attribute_model.json",
    "data/game_configs/cultivation/cultivation_realm.json",
    "data/game_configs/skills/skill_library.json",
    "data/game_configs/cultivation/spiritual_root.json",
    "data/game_data/templates/faction_data.json",
    "data/game_configs/system/achievement.json"
]

for data_file in data_files:
    full_path = PROJECT_ROOT / data_file
    exists = full_path.exists()
    check_results["data_files"][data_file] = exists
    status = "✅" if exists else "❌"
    print(f"{status} {data_file}")
    
    if exists:
        try:
            # 尝试加载JSON确保格式正确
            with open(full_path, 'r', encoding='utf-8') as f:
                json.load(f)
            print(f"   JSON格式: ✅")
        except json.JSONDecodeError as e:
            print(f"   JSON格式: ❌ 错误: {e}")
            check_results["missing"].append(f"JSON错误: {data_file}")
    else:
        check_results["missing"].append(f"数据文件: {data_file}")

# 4. 检查模态框模板
print("\n4. 检查模态框模板:")
modal_templates = [
    'status', 'inventory', 'cultivation', 'achievement', 
    'exploration', 'map', 'quest', 'save', 'load', 
    'help', 'settings', 'exit'
]

for modal in modal_templates:
    modal_path = f"templates/modals/{modal}.html"
    full_path = PROJECT_ROOT / modal_path
    exists = full_path.exists()
    check_results["files"][modal_path] = exists
    status = "✅" if exists else "❌"
    print(f"{status} {modal}.html")
    if not exists:
        check_results["missing"].append(f"模态框: {modal}.html")

# 5. 检查环境配置
print("\n5. 检查环境配置:")
env_file = PROJECT_ROOT / ".env"
env_example = PROJECT_ROOT / ".env.example"

if env_file.exists():
    print("✅ .env 文件存在")
else:
    print("❌ .env 文件不存在")
    if env_example.exists():
        print("   💡 提示: 可以复制 .env.example 为 .env")
    check_results["missing"].append("配置文件: .env")

# 总结
print("\n" + "=" * 60)
print("📊 检查总结:")

total_dirs = len(check_results["directories"])
existing_dirs = sum(1 for v in check_results["directories"].values() if v)
total_files = len(check_results["files"]) + len(check_results["data_files"])
existing_files = sum(1 for v in check_results["files"].values() if v) + \
                sum(1 for v in check_results["data_files"].values() if v)

print(f"目录: {existing_dirs}/{total_dirs}")
print(f"文件: {existing_files}/{total_files}")
print(f"缺失项: {len(check_results['missing'])}")

if check_results["missing"]:
    print("\n缺失的内容:")
    for item in check_results["missing"]:
        print(f"  - {item}")

# 保存结果
results_file = PROJECT_ROOT / "tests" / "debug" / "filesystem_test_results.json"
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(check_results, f, indent=2, ensure_ascii=False)

print(f"\n详细结果已保存到: {results_file}")
print("=" * 60)

# 生成修复脚本
if check_results["missing"]:
    fix_script = PROJECT_ROOT / "tests" / "debug" / "fix_missing_files.py"
    with open(fix_script, 'w', encoding='utf-8') as f:
        f.write("#!/usr/bin/env python3\n")
        f.write('"""自动创建缺失的文件和目录"""\n\n')
        f.write("from pathlib import Path\n\n")
        f.write(f"PROJECT_ROOT = Path('{PROJECT_ROOT}')\n\n")
        
        # 创建缺失的目录
        f.write("# 创建缺失的目录\n")
        for dir_path, exists in check_results["directories"].items():
            if not exists:
                f.write(f"(PROJECT_ROOT / '{dir_path}').mkdir(parents=True, exist_ok=True)\n")
                f.write(f"print('创建目录: {dir_path}')\n")
        
        f.write("\n# 创建缺失的文件（空文件）\n")
        for file_path, exists in {**check_results["files"], **check_results["data_files"]}.items():
            if not exists:
                f.write(f"(PROJECT_ROOT / '{file_path}').touch()\n")
                f.write(f"print('创建文件: {file_path}')\n")
    
    print(f"\n💡 生成了修复脚本: {fix_script}")
    print("   运行 python tests/debug/fix_missing_files.py 可以创建缺失的文件")
