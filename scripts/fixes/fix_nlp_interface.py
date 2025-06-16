#!/usr/bin/env python
# @dev_only
"""
紧急修复：NLP接口不一致问题

问题：NLPProcessor类实现的是parse()方法，但所有调用方都在使用process()方法
解决方案：统一接口，修复所有调用点
"""

import sys
from pathlib import Path
import re

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

def find_nlp_calls():
    """查找所有调用NLP process方法的文件"""
    problematic_files = []
    
    # 搜索所有Python文件
    for file_path in PROJECT_ROOT.rglob("*.py"):
        if ".git" in str(file_path) or "__pycache__" in str(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 查找调用process方法的地方
            if re.search(r'nlp\.process\s*\(', content):
                problematic_files.append(file_path)
                print(f"❌ 发现问题调用: {file_path.relative_to(PROJECT_ROOT)}")
                
        except Exception as e:
            pass
    
    return problematic_files

def fix_nlp_calls(files):
    """修复所有错误的调用"""
    fixed_count = 0
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换process为parse
            new_content = re.sub(r'nlp\.process\s*\(', 'nlp.parse(', content)
            
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                fixed_count += 1
                print(f"✅ 已修复: {file_path.relative_to(PROJECT_ROOT)}")
                
        except Exception as e:
            print(f"⚠️  修复失败 {file_path}: {e}")
    
    return fixed_count

def verify_nlp_implementation():
    """验证NLPProcessor的实际方法实现"""
    nlp_file = PROJECT_ROOT / "xwe/core/nlp/nlp_processor.py"
    
    if not nlp_file.exists():
        print("❌ 找不到NLPProcessor文件!")
        return False
    
    with open(nlp_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    has_parse = 'def parse(' in content
    has_process = 'def process(' in content
    
    print("\n📋 NLPProcessor方法检查:")
    print(f"  - parse() 方法: {'✅ 存在' if has_parse else '❌ 不存在'}")
    print(f"  - process() 方法: {'✅ 存在' if has_process else '❌ 不存在'}")
    
    return has_parse

def create_compatibility_wrapper():
    """为NLPProcessor添加兼容性包装"""
    nlp_file = PROJECT_ROOT / "xwe/core/nlp/nlp_processor.py"
    
    with open(nlp_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已有process方法
    if 'def process(' in content:
        print("ℹ️  process方法已存在，跳过添加包装器")
        return
    
    # 在类的最后添加兼容性方法
    wrapper_code = '''
    def process(self, *args, **kwargs):
        """兼容性包装器：将process调用转发到parse方法"""
        import warnings
        warnings.warn(
            "process()方法已弃用，请使用parse()方法。此包装器将在未来版本中移除。",
            DeprecationWarning,
            stacklevel=2
        )
        return self.parse(*args, **kwargs)
'''
    
    # 找到类定义的结束位置
    class_end = content.rfind('\nclass ')
    if class_end == -1:
        # 如果没有其他类，就在文件末尾添加
        new_content = content.rstrip() + '\n' + wrapper_code
    else:
        # 在下一个类定义之前插入
        new_content = content[:class_end] + wrapper_code + '\n' + content[class_end:]
    
    with open(nlp_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ 已添加兼容性包装器")

def main():
    """主修复流程"""
    print("🔧 NLP接口修复工具")
    print("="*60)
    
    # 1. 验证NLP实现
    print("\n1️⃣ 验证NLP实现...")
    if not verify_nlp_implementation():
        print("❌ NLPProcessor实现有问题!")
        return
    
    # 2. 查找问题调用
    print("\n2️⃣ 查找错误的process()调用...")
    problematic_files = find_nlp_calls()
    
    if not problematic_files:
        print("✅ 没有发现错误的调用!")
        return
    
    print(f"\n发现 {len(problematic_files)} 个文件存在问题")
    
    # 3. 询问修复方式
    print("\n3️⃣ 选择修复方式:")
    print("1. 修改所有调用点，将process改为parse（推荐）")
    print("2. 为NLPProcessor添加process兼容方法")
    print("3. 两种方式都执行（最安全）")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == '1' or choice == '3':
        print("\n🔄 修复调用点...")
        fixed = fix_nlp_calls(problematic_files)
        print(f"✅ 成功修复 {fixed} 个文件")
    
    if choice == '2' or choice == '3':
        print("\n🔄 添加兼容性包装...")
        create_compatibility_wrapper()
    
    # 4. 验证修复
    print("\n4️⃣ 验证修复结果...")
    remaining = find_nlp_calls()
    if not remaining:
        print("✅ 所有问题已修复!")
    else:
        print(f"⚠️  仍有 {len(remaining)} 个文件存在问题")
    
    print("\n✨ 修复完成!")
    print("\n建议运行以下命令测试:")
    print("  python scripts/test_nlp.py")
    print("  python main_menu.py")

if __name__ == "__main__":
    main()
