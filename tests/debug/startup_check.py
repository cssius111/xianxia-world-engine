#!/usr/bin/env python3
"""
修仙世界引擎 - 启动前检查脚本
确保所有依赖和配置都正确
"""

import sys
import os
from pathlib import Path
import json
import subprocess

# 设置项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 70)
print("🚀 修仙世界引擎 - 启动前检查")
print("=" * 70)
print(f"项目路径: {PROJECT_ROOT}")
print(f"Python版本: {sys.version.split()[0]}")
print(f"工作目录: {os.getcwd()}")
print("=" * 70)

errors = []
warnings = []

# 1. 检查Python版本
print("\n1. 检查Python版本...")
if sys.version_info < (3, 8):
    errors.append("Python版本过低，需要3.8或更高版本")
    print("❌ Python版本过低")
else:
    print("✅ Python版本符合要求")

# 2. 检查并创建必要的目录
print("\n2. 检查并创建必要的目录...")
required_dirs = [
    "logs",
    "saves", 
    "static/audio",
    "templates/modals",
    "data/restructured"
]

for dir_path in required_dirs:
    full_path = PROJECT_ROOT / dir_path
    if not full_path.exists():
        try:
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ 创建目录: {dir_path}")
        except Exception as e:
            errors.append(f"无法创建目录 {dir_path}: {e}")
            print(f"❌ 无法创建目录: {dir_path}")
    else:
        print(f"✅ 目录存在: {dir_path}")

# 3. 检查环境配置
print("\n3. 检查环境配置...")
env_file = PROJECT_ROOT / ".env"
env_example = PROJECT_ROOT / ".env.example"

if not env_file.exists():
    if env_example.exists():
        try:
            import shutil
            shutil.copy(env_example, env_file)
            print("✅ 已从 .env.example 创建 .env 文件")
        except Exception as e:
            warnings.append(f"无法创建 .env 文件: {e}")
            print("⚠️  无法自动创建 .env 文件")
    else:
        warnings.append(".env 和 .env.example 文件都不存在")
        print("⚠️  配置文件缺失")
else:
    print("✅ .env 文件存在")

# 4. 检查核心依赖
print("\n4. 检查核心依赖...")
core_dependencies = {
    "flask": "Flask",
    "werkzeug": "Werkzeug",
    "click": "Click"
}

missing_deps = []
for module, name in core_dependencies.items():
    try:
        __import__(module)
        print(f"✅ {name} 已安装")
    except ImportError:
        missing_deps.append(name)
        print(f"❌ {name} 未安装")

if missing_deps:
    errors.append(f"缺少依赖: {', '.join(missing_deps)}")

# 5. 测试核心模块导入
print("\n5. 测试核心模块导入...")
import_tests = [
    ("from game_config import config", "游戏配置"),
    ("from api import register_api", "API注册"),
    ("from routes import character, intel, lore", "路由模块"),
    ("from xwe.core.game_core import create_enhanced_game", "游戏核心"),
    ("from xwe.core.attributes import CharacterAttributes", "角色属性"),
    ("from xwe.core.character import Character, CharacterType", "角色系统")
]

for import_statement, description in import_tests:
    try:
        exec(import_statement)
        print(f"✅ {description}")
    except Exception as e:
        errors.append(f"{description}导入失败: {str(e)}")
        print(f"❌ {description}: {str(e)}")

# 6. 检查关键文件
print("\n6. 检查关键文件...")
critical_files = {
    "run_web_ui_v2.py": "启动脚本",
    "templates/welcome_optimized.html": "欢迎页面",
    "templates/intro_optimized.html": "角色创建页面",
    "templates/game_enhanced_optimized_v2.html": "游戏主页面",
    "static/css/ink_style.css": "水墨风样式"
}

for file_path, description in critical_files.items():
    if (PROJECT_ROOT / file_path).exists():
        print(f"✅ {description}")
    else:
        errors.append(f"{description}文件缺失: {file_path}")
        print(f"❌ {description}缺失")

# 7. 尝试初始化Flask应用
print("\n7. 测试Flask应用初始化...")
try:
    # 设置环境变量
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['FLASK_SECRET_KEY'] = 'test_key'
    
    from run_web_ui_v2 import XianxiaWebServer
    server = XianxiaWebServer()
    
    if server.app is not None:
        print("✅ Flask应用初始化成功")
        
        # 检查路由数量
        routes = list(server.app.url_map.iter_rules())
        print(f"   注册的路由数: {len(routes)}")
    else:
        errors.append("Flask应用初始化失败")
        print("❌ Flask应用初始化失败")
        
except Exception as e:
    errors.append(f"Flask应用测试失败: {str(e)}")
    print(f"❌ Flask应用测试失败: {e}")

# 总结和建议
print("\n" + "=" * 70)
print("📊 检查结果总结")
print("=" * 70)

if not errors and not warnings:
    print("\n✅ 所有检查都通过！项目已准备就绪。")
    print("\n🎮 启动游戏:")
    print(f"cd {PROJECT_ROOT}")
    print("python run_web_ui_v2.py")
    print("\n然后在浏览器中访问: http://localhost:5001")
else:
    if errors:
        print(f"\n❌ 发现 {len(errors)} 个错误:")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
    
    if warnings:
        print(f"\n⚠️  发现 {len(warnings)} 个警告:")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
    
    print("\n💡 修复建议:")
    
    if missing_deps:
        print("\n1. 安装缺失的依赖:")
        print("   pip install -r requirements.txt")
        print("   或:")
        print(f"   pip install {' '.join(missing_deps).lower()}")
    
    if any("导入失败" in error for error in errors):
        print("\n2. 确保所有项目模块都存在，可能需要:")
        print("   - 检查项目文件是否完整")
        print("   - 确认Python路径设置正确")
        print("   - 检查是否有语法错误")
    
    if any("文件缺失" in error for error in errors):
        print("\n3. 关键文件缺失，请检查:")
        print("   - 是否完整克隆了项目")
        print("   - 文件是否被意外删除")
    
    print("\n📝 如果问题持续，请运行完整的测试套件:")
    print("   python tests/debug/run_all_tests.py")

# 保存检查结果
report = {
    "timestamp": str(Path.ctime(Path(__file__))),
    "python_version": sys.version,
    "project_root": str(PROJECT_ROOT),
    "errors": errors,
    "warnings": warnings,
    "status": "ready" if not errors else "not_ready"
}

report_file = PROJECT_ROOT / "tests" / "debug" / "startup_check_report.json"
try:
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n检查报告已保存到: {report_file}")
except:
    pass

print("=" * 70)

# 返回状态码
sys.exit(0 if not errors else 1)
