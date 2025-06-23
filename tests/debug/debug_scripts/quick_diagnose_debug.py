#!/usr/bin/env python3
"""
快速诊断脚本 - 检查最常见的问题
"""

import sys
import os
from pathlib import Path
import json
import subprocess

# 脚本位于 tests/debug/debug_scripts，需要向上四级得到项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[3]
os.chdir(PROJECT_ROOT)

print("=" * 60)
print("🔍 修仙世界引擎 - 快速诊断")
print("=" * 60)

issues_found = []

# 1. Python版本检查
print("\n1. 检查Python版本...")
python_version = sys.version_info
if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
    print(f"❌ Python版本过低: {sys.version}")
    print("   需要: Python 3.8+")
    issues_found.append("Python版本过低")
else:
    print(f"✅ Python版本: {sys.version.split()[0]}")

# 2. 检查虚拟环境
print("\n2. 检查虚拟环境...")
in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
if in_venv:
    print("✅ 正在虚拟环境中运行")
else:
    print("⚠️  未在虚拟环境中运行")
    print("   建议创建虚拟环境: python -m venv .venv")

# 3. 检查关键依赖
print("\n3. 检查关键依赖...")
required_packages = {
    "flask": "Flask",
    "werkzeug": "Werkzeug",
    "jinja2": "Jinja2"
}

for package, display_name in required_packages.items():
    try:
        __import__(package)
        print(f"✅ {display_name} 已安装")
    except ImportError:
        print(f"❌ {display_name} 未安装")
        issues_found.append(f"{display_name} 未安装")

# 4. 检查项目结构
print("\n4. 检查项目结构...")
critical_paths = {
    "templates": "模板目录",
    "static": "静态资源目录",
    "data/restructured": "数据目录",
    "run_web_ui_v2.py": "启动脚本"
}

for path, description in critical_paths.items():
    full_path = PROJECT_ROOT / path
    if full_path.exists():
        print(f"✅ {description}: {path}")
    else:
        print(f"❌ {description}不存在: {path}")
        issues_found.append(f"{description}不存在")

# 5. 检查配置文件
print("\n5. 检查配置文件...")
env_file = PROJECT_ROOT / ".env"
env_example = PROJECT_ROOT / ".env.example"

if env_file.exists():
    print("✅ .env 文件存在")
else:
    print("❌ .env 文件不存在")
    if env_example.exists():
        print("   💡 运行以下命令创建:")
        print(f"      cp {env_example} {env_file}")
        issues_found.append(".env 文件不存在")

# 6. 检查端口可用性
print("\n6. 检查端口5001...")
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('localhost', 5001))
sock.close()

if result == 0:
    print("⚠️  端口5001已被占用")
    print("   可能已有服务运行在该端口")
else:
    print("✅ 端口5001可用")

# 7. 检查关键模板文件
print("\n7. 检查关键模板文件...")
template_files = [
    "templates/welcome_optimized.html",
    "templates/intro_optimized.html",
    "templates/game_enhanced_optimized_v2.html"
]

for template in template_files:
    if (PROJECT_ROOT / template).exists():
        print(f"✅ {template}")
    else:
        print(f"❌ {template} 不存在")
        issues_found.append(f"模板文件 {template} 不存在")

# 8. 检查静态资源
print("\n8. 检查静态资源...")
static_files = [
    "static/css/ink_style.css",
    "static/js/game_controller.js"
]

for static_file in static_files:
    if (PROJECT_ROOT / static_file).exists():
        print(f"✅ {static_file}")
    else:
        print(f"❌ {static_file} 不存在")
        issues_found.append(f"静态文件 {static_file} 不存在")

# 诊断结果
print("\n" + "=" * 60)
print("📊 诊断结果:")

if not issues_found:
    print("\n🎉 太好了！没有发现明显问题。")
    print("\n可以尝试启动项目:")
    print("  python run_web_ui_v2.py")
else:
    print(f"\n⚠️  发现 {len(issues_found)} 个问题:")
    for i, issue in enumerate(issues_found, 1):
        print(f"  {i}. {issue}")
    
    print("\n💡 修复建议:")
    
    if any("未安装" in issue for issue in issues_found):
        print("\n1. 安装缺失的依赖:")
        print("   pip install -r requirements.txt")
    
    if any("不存在" in issue for issue in issues_found):
        print("\n2. 运行完整测试获取详细信息:")
        print("   python tests/debug/debug_scripts/run_all_tests_debug.py")
    
    if ".env 文件不存在" in issues_found:
        print("\n3. 创建配置文件:")
        print("   cp .env.example .env")

# 生成快速修复脚本
if issues_found:
    fix_script = PROJECT_ROOT / "quick_fix.sh"
    with open(fix_script, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# 快速修复脚本\n\n")
        f.write("echo '开始快速修复...'\n\n")
        
        if any("未安装" in issue for issue in issues_found):
            f.write("# 安装依赖\n")
            f.write("pip install -r requirements.txt\n\n")
        
        if ".env 文件不存在" in issues_found and env_example.exists():
            f.write("# 创建配置文件\n")
            f.write("cp .env.example .env\n\n")
        
        if any("目录不存在" in issue for issue in issues_found):
            f.write("# 创建缺失的目录\n")
            for path in ["templates", "static", "data/restructured"]:
                f.write(f"mkdir -p {path}\n")
            f.write("\n")
        
        f.write("echo '修复完成！'\n")
    
    # 设置执行权限
    os.chmod(fix_script, 0o755)
    
    print(f"\n🔧 已生成快速修复脚本: {fix_script}")
    print("   运行: ./quick_fix.sh")

print("\n" + "=" * 60)
