#!/usr/bin/env python3
# @dev_only
"""
MyPy 错误自动修复脚本
用于批量修复常见的类型错误
"""

import os
import re
import ast
import subprocess
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MypyError:
    """MyPy 错误信息"""
    file: str
    line: int
    column: int
    error_type: str
    message: str


class TypeFixer:
    """类型错误修复器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.errors: List[MypyError] = []
        
    def run_mypy(self) -> List[MypyError]:
        """运行 mypy 并解析错误"""
        cmd = ["mypy", str(self.project_root), "--config-file", "mypy.ini"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        errors = []
        for line in result.stdout.split('\n'):
            match = re.match(r'(.+?):(\d+):\s*(.*?):\s*(.+)', line)
            if match:
                file_path, line_no, error_info, message = match.groups()
                
                # 解析错误类型
                error_match = re.match(r'(error|note):\s*(.+?)\s*\[(.+?)\]', error_info + ': ' + message)
                if error_match:
                    _, full_message, error_type = error_match.groups()
                    errors.append(MypyError(
                        file=file_path,
                        line=int(line_no),
                        column=0,
                        error_type=error_type,
                        message=full_message
                    ))
        
        self.errors = errors
        return errors
    
    def fix_return_none(self, file_path: str) -> int:
        """修复返回 None 但没有标注的函数"""
        fixes = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 查找需要修复的函数
        for i, line in enumerate(lines):
            # 匹配函数定义
            match = re.match(r'^(\s*)def\s+(\w+)\s*\((.*?)\)\s*:\s*$', line)
            if match:
                indent, func_name, params = match.groups()
                
                # 检查是否已有返回类型注解
                if '->' not in line:
                    # 查找函数体，检查是否有显式 return
                    has_explicit_return = False
                    j = i + 1
                    func_indent = len(indent)
                    
                    while j < len(lines):
                        current_line = lines[j]
                        # 检查缩进
                        if current_line.strip() and len(current_line) - len(current_line.lstrip()) <= func_indent:
                            break
                        
                        if 'return ' in current_line and 'return None' not in current_line:
                            has_explicit_return = True
                            break
                        j += 1
                    
                    # 如果没有显式返回值，添加 -> None
                    if not has_explicit_return:
                        lines[i] = f'{indent}def {func_name}({params}) -> None:\n'
                        fixes += 1
        
        if fixes > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        
        return fixes
    
    def add_type_annotations(self, file_path: str) -> int:
        """添加基础类型注解"""
        fixes = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用 AST 解析
        try:
            tree = ast.parse(content)
        except SyntaxError:
            print(f"语法错误，跳过文件: {file_path}")
            return 0
        
        class TypeAnnotator(ast.NodeTransformer):
            def __init__(self):
                self.fixes = 0
            
            def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
                # 为常见参数添加类型注解
                for arg in node.args.args:
                    if arg.annotation is None:
                        # 根据参数名推测类型
                        if arg.arg in ['self', 'cls']:
                            continue
                        elif arg.arg.endswith('_id') or arg.arg == 'id':
                            arg.annotation = ast.Name(id='str', ctx=ast.Load())
                            self.fixes += 1
                        elif arg.arg in ['count', 'index', 'level', 'amount']:
                            arg.annotation = ast.Name(id='int', ctx=ast.Load())
                            self.fixes += 1
                        elif arg.arg in ['value', 'price', 'rate']:
                            arg.annotation = ast.Name(id='float', ctx=ast.Load())
                            self.fixes += 1
                        elif arg.arg in ['name', 'message', 'text', 'path']:
                            arg.annotation = ast.Name(id='str', ctx=ast.Load())
                            self.fixes += 1
                        elif arg.arg in ['enabled', 'active', 'debug']:
                            arg.annotation = ast.Name(id='bool', ctx=ast.Load())
                            self.fixes += 1
                
                self.generic_visit(node)
                return node
        
        annotator = TypeAnnotator()
        new_tree = annotator.visit(tree)
        
        if annotator.fixes > 0:
            # 将 AST 转换回代码
            import astor
            new_code = astor.to_source(new_tree)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_code)
            fixes = annotator.fixes
        
        return fixes
    
    def fix_optional_access(self, file_path: str) -> int:
        """修复 Optional 类型的属性访问"""
        fixes = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 查找 Optional 属性访问错误
        for error in self.errors:
            if error.file == file_path and 'union-attr' in error.error_type:
                line_idx = error.line - 1
                if line_idx < len(lines):
                    line = lines[line_idx]
                    indent = len(line) - len(line.lstrip())
                    
                    # 提取变量名
                    match = re.search(r'(\w+)\.(\w+)', line)
                    if match:
                        var_name = match.group(1)
                        # 在该行前添加 None 检查
                        check_line = f'{" " * indent}if {var_name} is not None:\n'
                        lines.insert(line_idx, check_line)
                        # 增加原行的缩进
                        lines[line_idx + 1] = '    ' + lines[line_idx + 1]
                        fixes += 1
        
        if fixes > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        
        return fixes
    
    def fix_dict_annotations(self, file_path: str) -> int:
        """修复字典类型注解"""
        fixes = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找需要注解的字典
        pattern = r'^(\s*)(\w+)\s*=\s*\{\s*\}(?!\s*#\s*type:)'
        
        def replacer(match):
            nonlocal fixes
            indent, var_name = match.groups()
            fixes += 1
            return f'{indent}{var_name}: Dict[str, Any] = {{}}'
        
        # 添加必要的导入
        if 'from typing import' not in content:
            content = 'from typing import Dict, Any\n' + content
        elif 'Dict' not in content:
            content = content.replace('from typing import', 'from typing import Dict, Any,')
        
        new_content = re.sub(pattern, replacer, content, flags=re.MULTILINE)
        
        if fixes > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        
        return fixes
    
    def process_file(self, file_path: str) -> Dict[str, int]:
        """处理单个文件"""
        results = {
            'return_none': 0,
            'type_annotations': 0,
            'optional_access': 0,
            'dict_annotations': 0
        }
        
        if not os.path.exists(file_path):
            return results
        
        print(f"处理文件: {file_path}")
        
        # 应用各种修复
        results['return_none'] = self.fix_return_none(file_path)
        results['dict_annotations'] = self.fix_dict_annotations(file_path)
        # results['type_annotations'] = self.add_type_annotations(file_path)  # 需要 astor
        results['optional_access'] = self.fix_optional_access(file_path)
        
        return results
    
    def fix_all(self) -> None:
        """修复所有错误"""
        print("运行 mypy 检查...")
        errors = self.run_mypy()
        print(f"发现 {len(errors)} 个错误")
        
        # 按文件分组错误
        files_with_errors = set(error.file for error in errors)
        
        total_fixes = {
            'return_none': 0,
            'type_annotations': 0,
            'optional_access': 0,
            'dict_annotations': 0
        }
        
        for file_path in files_with_errors:
            if file_path.startswith('xwe/'):
                results = self.process_file(file_path)
                for key, value in results.items():
                    total_fixes[key] += value
        
        print("\n修复统计:")
        print(f"- 返回值类型注解: {total_fixes['return_none']}")
        print(f"- 字典类型注解: {total_fixes['dict_annotations']}")
        print(f"- Optional 访问修复: {total_fixes['optional_access']}")
        
        # 再次运行 mypy 查看剩余错误
        print("\n重新运行 mypy 检查...")
        new_errors = self.run_mypy()
        print(f"剩余 {len(new_errors)} 个错误")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MyPy 错误自动修复工具')
    parser.add_argument('--project', default='xwe', help='项目目录')
    parser.add_argument('--dry-run', action='store_true', help='只显示将要修复的内容，不实际修改')
    
    args = parser.parse_args()
    
    fixer = TypeFixer(args.project)
    fixer.fix_all()


if __name__ == '__main__':
    main()
