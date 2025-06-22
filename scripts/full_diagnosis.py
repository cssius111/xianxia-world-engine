#!/usr/bin/env python3
"""
完整诊断和修复脚本
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path

# 项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def clean_cache():
    """清理Python缓存"""
    print("🧹 清理Python缓存...")
    count = 0
    for root, dirs, files in os.walk(project_root):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                count += 1
            except:
                pass
    print(f"   ✅ 删除了 {count} 个缓存目录")

def run_snapshot():
    """运行快照脚本"""
    print("\n📸 生成新的项目快照...")
    snapshot_script = project_root / "scripts" / "quick_snapshot.py"
    
    result = subprocess.run(
        [sys.executable, str(snapshot_script)],
        capture_output=True,
        text=True,
        cwd=str(project_root)
    )
    
    if result.returncode == 0:
        print("   ✅ 快照生成成功")
    else:
        print("   ❌ 快照生成失败")
        if result.stderr:
            print(f"   错误: {result.stderr}")

def analyze_errors():
    """分析错误"""
    print("\n🔍 分析当前错误...")
    snapshot_file = project_root / "project_snapshot.json"
    
    if not snapshot_file.exists():
        print("   ❌ 找不到快照文件")
        return
    
    with open(snapshot_file, 'r', encoding='utf-8') as f:
        errors = json.load(f)
    
    if not errors:
        print("   ✅ 没有发现导入错误!")
        return
    
    print(f"   ❌ 发现 {len(errors)} 个错误:")
    
    # 分类错误
    error_types = {}
    for module, error_info in errors.items():
        error_msg = error_info['message']
        if "No module named" in error_msg:
            error_type = "缺失模块"
        elif "cannot import name" in error_msg:
            error_type = "缺失导入"
        else:
            error_type = "其他错误"
        
        if error_type not in error_types:
            error_types[error_type] = []
        error_types[error_type].append((module, error_msg))
    
    # 显示分类结果
    for error_type, error_list in error_types.items():
        print(f"\n   {error_type} ({len(error_list)}个):")
        for module, msg in error_list[:3]:  # 只显示前3个
            print(f"      - {module}")
            print(f"        {msg[:80]}...")

def test_specific_imports():
    """测试特定的导入"""
    print("\n🧪 测试关键导入...")
    
    tests = [
        ("ValidationError", "from xwe.engine.expression.exceptions import ValidationError"),
        ("content_ecosystem", "import xwe.features.content_ecosystem"),
        ("metrics_registry", "from xwe.metrics import metrics_registry"),
        ("Web UI", "from entrypoints.run_web_ui_optimized import app"),
    ]
    
    for name, import_statement in tests:
        try:
            exec(import_statement)
            print(f"   ✅ {name}")
        except Exception as e:
            print(f"   ❌ {name}: {str(e)[:60]}...")

def suggest_fixes():
    """建议修复方案"""
    print("\n💡 修复建议:")
    
    snapshot_file = project_root / "project_snapshot.json"
    if snapshot_file.exists():
        with open(snapshot_file, 'r', encoding='utf-8') as f:
            errors = json.load(f)
        
        if not errors:
            print("   ✅ 所有导入错误已修复!")
            print("\n   你现在可以运行:")
            print("   python entrypoints/run_web_ui_optimized.py")
            return
    
    print("   1. 运行综合修复脚本:")
    print("      python scripts/comprehensive_fix.py")
    print("\n   2. 如果仍有问题，手动检查:")
    print("      - 文件名是否正确")
    print("      - 导入路径是否正确")
    print("      - 是否有循环导入")
    print("\n   3. 查看详细错误:")
    print("      cat project_snapshot.json | python -m json.tool")

def main():
    """主函数"""
    print("🔧 修仙世界引擎 - 完整诊断")
    print("=" * 60)
    
    # 1. 清理缓存
    clean_cache()
    
    # 2. 生成新快照
    run_snapshot()
    
    # 3. 分析错误
    analyze_errors()
    
    # 4. 测试关键导入
    test_specific_imports()
    
    # 5. 提供建议
    suggest_fixes()
    
    print("\n" + "=" * 60)
    print("✅ 诊断完成!")

if __name__ == "__main__":
    main()
