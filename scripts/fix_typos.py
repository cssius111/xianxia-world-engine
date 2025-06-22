#!/usr/bin/env python3
"""
搜索并修复文件名错误
"""

import os
import re
from pathlib import Path

def search_and_fix_typos(root_dir):
    """搜索并修复文件名拼写错误"""
    print("🔍 搜索文件名拼写错误...")
    
    # 要搜索的错误模式
    typo_patterns = [
        (r'xceptions\.py', 'exceptions.py'),
        (r'from xwe\.engine\.expression\.xceptions', 'from xwe.engine.expression.exceptions'),
        (r'import xceptions', 'import exceptions'),
    ]
    
    fixed_count = 0
    
    # 遍历所有Python文件
    for root, dirs, files in os.walk(root_dir):
        # 跳过特定目录
        if '__pycache__' in root or '.git' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # 应用所有修复模式
                    for pattern, replacement in typo_patterns:
                        content = re.sub(pattern, replacement, content)
                    
                    # 如果内容有变化，保存文件
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"   ✅ 修复: {file_path}")
                        fixed_count += 1
                        
                except Exception as e:
                    print(f"   ❌ 处理 {file_path} 时出错: {e}")
    
    # 检查是否有错误命名的文件
    xceptions_file = root_dir / "xwe" / "engine" / "expression" / "xceptions.py"
    exceptions_file = root_dir / "xwe" / "engine" / "expression" / "exceptions.py"
    
    if xceptions_file.exists() and not exceptions_file.exists():
        print(f"\n🔧 发现错误命名的文件: {xceptions_file}")
        xceptions_file.rename(exceptions_file)
        print(f"   ✅ 重命名为: {exceptions_file}")
        fixed_count += 1
    
    return fixed_count

def verify_files():
    """验证关键文件是否存在"""
    print("\n📁 验证关键文件...")
    
    project_root = Path(__file__).parent.parent
    critical_files = [
        "xwe/engine/expression/exceptions.py",
        "xwe/features/content_ecosystem.py",
        "xwe/metrics/__init__.py",
        "xwe/metrics/prometheus/__init__.py",
    ]
    
    all_exist = True
    for file_path in critical_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - 不存在!")
            all_exist = False
    
    return all_exist

def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    
    print("🔧 修复文件名错误")
    print("=" * 60)
    
    # 1. 搜索并修复拼写错误
    fixed = search_and_fix_typos(project_root)
    print(f"\n📊 修复了 {fixed} 个文件")
    
    # 2. 验证文件
    if verify_files():
        print("\n✅ 所有关键文件都存在")
    else:
        print("\n❌ 某些关键文件缺失")
    
    print("\n💡 下一步:")
    print("1. 清理缓存: python scripts/clean_cache.py")
    print("2. 运行诊断: python scripts/full_diagnosis.py")
    print("3. 启动应用: python test_webui.py")

if __name__ == "__main__":
    main()
