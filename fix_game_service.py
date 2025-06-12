#!/usr/bin/env python3
"""
手动修复 game_service.py 的示例脚本
展示如何精确修复特定文件的错误
"""

import re
from pathlib import Path


def fix_game_service():
    """修复 game_service.py 中的类型错误"""
    
    # 文件路径
    file_path = Path("xwe/services/interfaces/game_service.py")
    
    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        return
    
    content = file_path.read_text(encoding='utf-8')
    
    # 1. 添加必要的导入
    if "from typing import" not in content:
        import_line = "from typing import List, Dict, Any, Optional\n"
        lines = content.split('\n')
        
        # 找到合适的位置插入
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.strip().startswith(('import ', 'from ')):
                insert_pos = i + 1
            elif line.strip() and not line.strip().startswith('#'):
                # 找到第一个非空非注释行
                if insert_pos == 0:
                    insert_pos = i
                break
        
        lines.insert(insert_pos, import_line)
        content = '\n'.join(lines)
    
    # 2. 修复 None 赋值错误
    # 错误：self.commands = []  # 应该是 list[str]
    replacements = [
        # (错误模式, 正确替换)
        (r'self\.commands\s*=\s*None', 'self.commands: List[str] = []'),
        (r'self\.events\s*=\s*None', 'self.events: List[Dict[str, Any]] = []'),
        (r'self\.command_handlers\s*=\s*None', 'self.command_handlers: List[str] = []'),
        (r'self\.state\s*=\s*None', 'self.state: Dict[str, Any] = {}'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # 3. 修复类定义
    # 确保是抽象基类
    if "from abc import" not in content:
        content = "from abc import ABC, abstractmethod\n" + content
    
    # 修改类定义
    content = re.sub(
        r'class\s+IGameService\s*(?:\([^)]*\))?\s*:',
        'class IGameService(ABC):',
        content
    )
    
    # 4. 为抽象方法添加装饰器
    # 查找所有应该是抽象的方法
    abstract_methods = [
        'process_command',
        'execute_command',
        'get_state',
        'update_state'
    ]
    
    for method in abstract_methods:
        # 添加 @abstractmethod 装饰器
        pattern = rf'(\n\s*)def\s+{method}\s*\('
        replacement = r'\1@abstractmethod\1def ' + method + '('
        content = re.sub(pattern, replacement, content)
    
    # 5. 保存修复后的文件
    file_path.write_text(content, encoding='utf-8')
    print(f"✓ 修复完成: {file_path}")
    
    # 显示修复后的部分内容
    print("\n修复后的文件开头：")
    print("-" * 60)
    lines = content.split('\n')[:30]
    for i, line in enumerate(lines, 1):
        print(f"{i:3d}: {line}")


def fix_specific_errors():
    """修复特定的错误模式"""
    
    # 错误映射表
    error_fixes = {
        # 文件路径: [(错误行号, 修复方法)]
        "xwe/features/html_output.py": [
            (7, "logs: List[str] = []"),
            (8, "status: Dict[str, Any] = {}")
        ],
        "xwe/engine/expression/tokenizer.py": [
            # 修复 Any -> Any
            (39, lambda line: line.replace("Any", "Any"))
        ],
        "xwe/core/achievement_system.py": [
            # 修复返回值
            (179, 'return ""  # 返回空字符串而不是 None')
        ]
    }
    
    for file_path, fixes in error_fixes.items():
        path = Path(file_path)
        if not path.exists():
            continue
            
        lines = path.read_text(encoding='utf-8').splitlines()
        
        for line_num, fix in fixes:
            if line_num <= len(lines):
                if callable(fix):
                    lines[line_num - 1] = fix(lines[line_num - 1])
                else:
                    # 保持缩进
                    indent = len(lines[line_num - 1]) - len(lines[line_num - 1].lstrip())
                    lines[line_num - 1] = ' ' * indent + fix
        
        path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        print(f"✓ 修复: {file_path}")


if __name__ == "__main__":
    print("开始修复 game_service.py...")
    fix_game_service()
    
    print("\n修复其他特定错误...")
    fix_specific_errors()
    
    print("\n完成！建议运行 mypy 检查剩余错误：")
    print("mypy xwe/services/interfaces/game_service.py")
