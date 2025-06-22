#!/usr/bin/env python3
"""
终极自动修复脚本 - 一键修复所有问题
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path

# 项目根目录
project_root = Path(__file__).parent

def print_header(title):
    """打印标题"""
    print(f"\n{'=' * 60}")
    print(f"🔧 {title}")
    print(f"{'=' * 60}")

def run_script(script_name, description):
    """运行脚本"""
    print_header(description)
    script_path = project_root / "scripts" / script_name
    
    if not script_path.exists():
        print(f"❌ 脚本不存在: {script_path}")
        return False
    
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(project_root),
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(f"\n错误输出:\n{result.stderr}")
    
    return result.returncode == 0

def clean_all_cache():
    """清理所有缓存"""
    print_header("清理所有缓存")
    count = 0
    
    for root, dirs, files in os.walk(project_root):
        # 删除 __pycache__ 目录
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                count += 1
            except:
                pass
        
        # 删除 .pyc 文件
        for file in files:
            if file.endswith('.pyc'):
                try:
                    os.remove(os.path.join(root, file))
                    count += 1
                except:
                    pass
    
    print(f"✅ 清理了 {count} 个缓存项")
    return True

def ensure_critical_files():
    """确保关键文件存在"""
    print_header("检查并创建关键文件")
    
    # 确保 __init__.py 文件存在
    init_dirs = [
        "xwe/features",
        "xwe/engine/expression",
        "xwe/metrics",
        "xwe/metrics/prometheus",
    ]
    
    for dir_path in init_dirs:
        full_path = project_root / dir_path
        init_file = full_path / "__init__.py"
        
        if not init_file.exists() and full_path.exists():
            init_file.write_text("")
            print(f"✅ 创建 {dir_path}/__init__.py")
    
    return True

def final_test():
    """最终测试"""
    print_header("最终测试")
    
    try:
        sys.path.insert(0, str(project_root))
        
        # 测试关键导入
        print("测试关键导入...")
        
        from xwe.engine.expression.exceptions import ValidationError
        print("✅ ValidationError 导入成功")
        
        from xwe.features.content_ecosystem import content_ecosystem
        print("✅ content_ecosystem 导入成功")
        
        from xwe.metrics import metrics_registry
        print("✅ metrics_registry 导入成功")
        
        from entrypoints.run_web_ui_optimized import app
        print("✅ Web UI 导入成功")
        
        print("\n🎉 所有测试通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 终极自动修复脚本")
    print("=" * 60)
    print("这个脚本将自动执行所有必要的修复步骤")
    
    steps = [
        (clean_all_cache, "步骤 1/6: 清理缓存"),
        (lambda: run_script("fix_typos.py", "步骤 2/6: 修复文件名错误"), None),
        (ensure_critical_files, "步骤 3/6: 确保关键文件存在"),
        (lambda: run_script("comprehensive_fix.py", "步骤 4/6: 运行综合修复"), None),
        (lambda: run_script("quick_snapshot.py", "步骤 5/6: 生成项目快照"), None),
        (final_test, "步骤 6/6: 最终测试"),
    ]
    
    success_count = 0
    total_steps = len(steps)
    
    for i, (func, desc) in enumerate(steps):
        if desc:
            print(f"\n[{i+1}/{total_steps}] {desc}")
        
        try:
            if func():
                success_count += 1
            else:
                print(f"⚠️ 步骤 {i+1} 完成但有警告")
        except Exception as e:
            print(f"❌ 步骤 {i+1} 失败: {e}")
    
    # 最终报告
    print_header("修复完成")
    print(f"成功执行: {success_count}/{total_steps} 个步骤")
    
    if success_count == total_steps:
        print("\n🎉 恭喜! 所有问题已经修复!")
        print("\n你现在可以运行:")
        print("  python entrypoints/run_web_ui_optimized.py")
        print("\n或者使用测试脚本:")
        print("  python test_webui.py")
    else:
        print("\n⚠️ 部分步骤失败，请查看上面的错误信息")
        print("\n建议:")
        print("1. 查看 project_snapshot.json 了解具体错误")
        print("2. 手动检查失败的模块")
        print("3. 确保所有依赖已安装: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
