#!/usr/bin/env python3
"""
快速验证修复脚本
检查所有修复文件是否正确创建和配置
"""

import os
import json
from pathlib import Path

def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (缺失)")
        return False

def check_file_content(file_path, search_text, description):
    """检查文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_text in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description} (内容未找到)")
                return False
    except Exception as e:
        print(f"❌ {description} (读取失败: {e})")
        return False

def main():
    print("🔍 修仙游戏侧边栏修复验证")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    checks_passed = 0
    total_checks = 0
    
    # 检查核心修复文件
    files_to_check = [
        (project_root / "api_fixes.py", "API修复模块"),
        (project_root / "static/js/game_panels_enhanced.js", "增强版游戏面板脚本"),
        (project_root / "test_sidebar.sh", "侧边栏测试脚本"),
        (project_root / "SIDEBAR_FIX_REPORT.md", "修复报告"),
        (project_root / "run.py", "主程序"),
        (project_root / "templates/game_enhanced_optimized_v2.html", "游戏主模板"),
    ]
    
    print("\n📁 文件存在性检查:")
    for file_path, description in files_to_check:
        total_checks += 1
        if check_file_exists(file_path, description):
            checks_passed += 1
    
    # 检查关键内容
    print("\n📝 内容完整性检查:")
    
    content_checks = [
        (project_root / "run.py", "register_sidebar_apis", "API修复模块集成"),
        (project_root / "api_fixes.py", "/api/cultivation/status", "修炼API实现"),
        (project_root / "api_fixes.py", "/api/achievements", "成就API实现"),
        (project_root / "static/js/game_panels_enhanced.js", "loadCultivationData", "修炼数据加载"),
        (project_root / "templates/game_enhanced_optimized_v2.html", "game_panels_enhanced.js", "增强脚本引用"),
    ]
    
    for file_path, search_text, description in content_checks:
        total_checks += 1
        if check_file_content(file_path, search_text, description):
            checks_passed += 1
    
    # 检查配置文件
    print("\n⚙️ 配置文件检查:")
    
    # .env文件检查
    env_file = project_root / ".env"
    total_checks += 1
    if check_file_exists(env_file, ".env配置文件"):
        checks_passed += 1
        # 检查关键配置
        total_checks += 1
        if check_file_content(env_file, "PORT=5001", "端口配置"):
            checks_passed += 1
    
    # package.json检查
    package_file = project_root / "package.json"
    total_checks += 1
    if check_file_exists(package_file, "package.json"):
        checks_passed += 1
        try:
            with open(package_file, 'r') as f:
                package_data = json.load(f)
                if "@playwright/test" in package_data.get("devDependencies", {}):
                    print("✅ Playwright依赖配置正确")
                    checks_passed += 1
                else:
                    print("❌ Playwright依赖缺失")
                total_checks += 1
        except Exception as e:
            print(f"❌ package.json解析失败: {e}")
            total_checks += 1
    
    # 权限检查
    print("\n🔐 权限检查:")
    test_script = project_root / "test_sidebar.sh"
    total_checks += 1
    if os.path.exists(test_script):
        import stat
        file_stat = os.stat(test_script)
        if file_stat.st_mode & stat.S_IXUSR:
            print("✅ 测试脚本有执行权限")
            checks_passed += 1
        else:
            print("⚠️ 测试脚本缺少执行权限，正在修复...")
            try:
                os.chmod(test_script, 0o755)
                print("✅ 执行权限已添加")
                checks_passed += 1
            except Exception as e:
                print(f"❌ 无法添加执行权限: {e}")
    
    # 目录结构检查
    print("\n📂 目录结构检查:")
    directories_to_check = [
        (project_root / "logs", "日志目录"),
        (project_root / "saves", "存档目录"),
        (project_root / "static/js", "JavaScript目录"),
        (project_root / "templates/components", "组件模板目录"),
    ]
    
    for dir_path, description in directories_to_check:
        total_checks += 1
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            print(f"✅ {description}: {dir_path}")
            checks_passed += 1
        else:
            print(f"⚠️ {description}: {dir_path} (不存在，将创建)")
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"✅ {description}已创建")
                checks_passed += 1
            except Exception as e:
                print(f"❌ 无法创建{description}: {e}")
    
    # 生成验证报告
    print("\n" + "=" * 50)
    print(f"📊 验证结果: {checks_passed}/{total_checks} 项检查通过")
    
    success_rate = (checks_passed / total_checks) * 100
    
    if success_rate >= 90:
        print("🎉 修复验证成功！可以开始测试")
        print("\n🚀 下一步执行:")
        print("1. 运行: ./test_sidebar.sh")
        print("2. 选择选项3: 启动服务器并运行测试")
        print("3. 访问: http://localhost:5001")
        
        # 生成快速启动命令
        print("\n📋 快速启动命令:")
        print("cd " + str(project_root))
        print("./test_sidebar.sh")
        
    elif success_rate >= 70:
        print("⚠️ 修复基本完成，但有一些问题需要解决")
        print("建议手动检查失败的项目")
    else:
        print("❌ 修复验证失败，需要重新检查")
        print("请参考错误信息进行修复")
    
    print(f"\n💡 成功率: {success_rate:.1f}%")
    
    # 输出详细的启动指令
    print("\n" + "=" * 50)
    print("🎯 完整启动指令:")
    print(f"cd {project_root}")
    print("chmod +x test_sidebar.sh")
    print("./test_sidebar.sh")
    print("\n选择选项3进行完整测试")

if __name__ == "__main__":
    main()
