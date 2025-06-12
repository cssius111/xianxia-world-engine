#!/usr/bin/env python3
"""
快速修复 MyPy 常见错误的脚本
"""

import os
import re
from pathlib import Path
import sys


def fix_any_to_Any(content):
    """修复 Any -> Any"""
    # 先确保导入了 Any
    if "from typing import" in content and "Any" not in content:
        content = re.sub(
            r'(from typing import .*?)(\n)',
            lambda m: m.group(1) + ", Any" + m.group(2),
            content,
            count=1
        )
    elif "from typing import" not in content and re.search(r'\bany\b', content):
        # 在文件开头添加导入
        lines = content.split('\n')
        import_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith(('import ', 'from ')):
                import_idx = i + 1
                break
        lines.insert(import_idx, "from typing import Any")
        content = '\n'.join(lines)
    
    # 替换 Any 为 Any
    content = re.sub(r'\bany\b(?!\w)', 'Any', content)
    return content


def fix_requests_import(content):
    """为 requests 导入添加 type: ignore"""
    content = re.sub(
        r'^(import requests)(?!.*# type: ignore)(.*)$',
        r'\1  # type: ignore[import-untyped]\2',
        content,
        flags=re.MULTILINE
    )
    content = re.sub(
        r'^(from requests import .*)(?!.*# type: ignore)(.*)$',
        r'\1  # type: ignore[import-untyped]\2',
        content,
        flags=re.MULTILINE
    )
    return content


def fix_none_to_empty_list(content):
    """修复简单的 None 赋值给 list"""
    # 匹配 self.xxx = None 模式，其中 xxx 包含 list, commands, events 等关键词
    patterns = [
        (r'(self\.\w*(?:list|commands|events|handlers)\w*)\s*=\s*None', r'\1 = []'),
        (r'(self\.\w*(?:dict|config|state|data)\w*)\s*=\s*None', r'\1 = {}'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content


def add_type_annotations(content):
    """为常见变量添加类型注解"""
    # 为空列表和字典添加注解
    content = re.sub(
        r'^(\s*)(logs|events|commands|items)\s*=\s*\[\]',
        r'\1\2: List[Any] = []',
        content,
        flags=re.MULTILINE
    )
    content = re.sub(
        r'^(\s*)(status|config|state|data)\s*=\s*\{\}',
        r'\1\2: Dict[str, Any] = {}',
        content,
        flags=re.MULTILINE
    )
    
    # 确保导入了必要的类型
    if re.search(r':\s*(?:List|Dict)\[', content):
        if "from typing import" not in content:
            lines = content.split('\n')
            import_idx = 0
            for i, line in enumerate(lines):
                if line.strip().startswith(('import ', 'from ')):
                    import_idx = i + 1
                    break
            lines.insert(import_idx, "from typing import List, Dict, Any, Optional")
            content = '\n'.join(lines)
    
    return content


def process_file(filepath):
    """处理单个文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # 应用各种修复
        content = fix_any_to_Any(content)
        content = fix_requests_import(content)
        content = fix_none_to_empty_list(content)
        content = add_type_annotations(content)
        
        # 如果有改动，写回文件
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False


def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 处理指定的文件
        files = sys.argv[1:]
    else:
        # 处理所有 Python 文件
        files = []
        for root, dirs, filenames in os.walk('.'):
            # 跳过虚拟环境和缓存目录
            dirs[:] = [d for d in dirs if d not in {'venv', 'env', '__pycache__', '.git'}]
            
            for filename in filenames:
                if filename.endswith('.py'):
                    files.append(os.path.join(root, filename))
    
    print(f"找到 {len(files)} 个 Python 文件")
    
    fixed_count = 0
    for filepath in files:
        if process_file(filepath):
            fixed_count += 1
            print(f"✓ 修复: {filepath}")
    
    print(f"\n完成！修复了 {fixed_count} 个文件")


if __name__ == "__main__":
    main()
