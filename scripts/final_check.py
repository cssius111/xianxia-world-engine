#!/usr/bin/env python3
"""
最终项目状态检查
验证所有修复是否成功
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)

def check_files_exist() -> Dict[str, bool]:
    """检查关键文件是否存在"""
    files_to_check = {
        "DeepSeek客户端": "deepseek/__init__.py",
        "ContentPreference类": "xwe/features/ai_personalization.py",
        "表达式异常": "xwe/engine/expression/exceptions.py",
        "Prometheus监控": "xwe/metrics/prometheus/__init__.py",
        "环境配置": ".env",
        "依赖列表": "requirements.txt"
    }
    
    results = {}
    for name, path in files_to_check.items():
        results[name] = Path(path).exists()
    
    return results

def check_env_vars() -> Dict[str, bool]:
    """检查环境变量"""
    from dotenv import load_dotenv
    load_dotenv()
    
    env_vars = {
        "DEEPSEEK_API_KEY": os.environ.get("DEEPSEEK_API_KEY"),
        "DEFAULT_LLM_PROVIDER": os.environ.get("DEFAULT_LLM_PROVIDER", "未设置")
    }
    
    return {
        "API密钥": bool(env_vars["DEEPSEEK_API_KEY"]),
        "API密钥长度": len(env_vars["DEEPSEEK_API_KEY"]) if env_vars["DEEPSEEK_API_KEY"] else 0,
        "默认LLM提供商": env_vars["DEFAULT_LLM_PROVIDER"]
    }

def run_import_test() -> Dict[str, any]:
    """运行导入测试"""
    print("🔍 运行快速导入扫描...")
    
    result = subprocess.run(
        [sys.executable, "scripts/quick_snapshot.py"],
        capture_output=True,
        text=True
    )
    
    # 读取结果
    snapshot_path = Path("project_snapshot.json")
    if snapshot_path.exists():
        with open(snapshot_path, "r") as f:
            issues = json.load(f)
        return {
            "成功": result.returncode == 0,
            "错误数量": len(issues),
            "错误模块": list(issues.keys())[:5]  # 只显示前5个
        }
    
    return {"成功": False, "错误": "无法生成快照"}

def test_deepseek_import() -> bool:
    """测试 DeepSeek 导入"""
    try:
        from deepseek import DeepSeek
        return True
    except ImportError:
        return False

def test_contentpreference_import() -> bool:
    """测试 ContentPreference 导入"""
    try:
        from xwe.features.ai_personalization import ContentPreference
        return True
    except ImportError:
        return False

def display_results(results: Dict[str, any]):
    """显示检查结果"""
    print("\n" + "="*60)
    print("📊 项目状态检查报告")
    print("="*60)
    
    # 文件检查
    print("\n📁 文件存在性检查:")
    file_results = results["files"]
    all_files_ok = all(file_results.values())
    for name, exists in file_results.items():
        status = "✅" if exists else "❌"
        print(f"  {status} {name}")
    
    # 环境变量检查
    print("\n🔑 环境变量检查:")
    env_results = results["env"]
    print(f"  {'✅' if env_results['API密钥'] else '❌'} DEEPSEEK_API_KEY (长度: {env_results['API密钥长度']})")
    print(f"  📝 默认LLM提供商: {env_results['默认LLM提供商']}")
    
    # 导入测试
    print("\n📦 关键模块导入测试:")
    print(f"  {'✅' if results['deepseek_import'] else '❌'} DeepSeek 模块")
    print(f"  {'✅' if results['contentpreference_import'] else '❌'} ContentPreference 类")
    
    # 项目扫描结果
    print("\n🔍 项目导入扫描:")
    scan_results = results["import_scan"]
    if scan_results.get("成功"):
        error_count = scan_results.get("错误数量", 0)
        if error_count == 0:
            print("  ✅ 所有模块导入成功！")
        else:
            print(f"  ⚠️ 发现 {error_count} 个导入错误")
            if scan_results.get("错误模块"):
                print("  错误模块:")
                for module in scan_results["错误模块"]:
                    print(f"    - {module}")
    else:
        print(f"  ❌ 扫描失败: {scan_results.get('错误', '未知错误')}")
    
    # 总体评估
    print("\n" + "="*60)
    print("🎯 总体评估:")
    
    all_ok = (
        all_files_ok and 
        env_results["API密钥"] and 
        results["deepseek_import"] and 
        results["contentpreference_import"] and
        scan_results.get("错误数量", 999) == 0
    )
    
    if all_ok:
        print("  🎉 项目已完全修复，可以正常运行！")
        print("\n  下一步:")
        print("  1. 安装依赖: pip install -r requirements.txt")
        print("  2. 测试API: python scripts/test_deepseek_api.py")
        print("  3. 运行项目: python entrypoints/run_web_ui_optimized.py")
    else:
        print("  ⚠️ 还有一些问题需要解决:")
        if not all_files_ok:
            print("    - 某些必要文件缺失")
        if not env_results["API密钥"]:
            print("    - DEEPSEEK_API_KEY 未设置")
        if not results["deepseek_import"]:
            print("    - DeepSeek 模块无法导入")
        if scan_results.get("错误数量", 0) > 0:
            print(f"    - 还有 {scan_results['错误数量']} 个导入错误")
        
        print("\n  建议:")
        print("  1. 运行: python scripts/fix_remaining_issues.py")
        print("  2. 安装依赖: pip install openai python-dotenv")
        print("  3. 重新运行本脚本验证")

def main():
    """主函数"""
    print("🚀 修仙世界引擎 - 项目状态最终检查")
    print(f"📍 项目目录: {PROJECT_ROOT}")
    
    # 收集所有检查结果
    results = {
        "files": check_files_exist(),
        "env": check_env_vars(),
        "deepseek_import": test_deepseek_import(),
        "contentpreference_import": test_contentpreference_import(),
        "import_scan": run_import_test()
    }
    
    # 显示结果
    display_results(results)
    
    print("\n" + "="*60)
    print("📝 详细报告已生成")

if __name__ == "__main__":
    main()
