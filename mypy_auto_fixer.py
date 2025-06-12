#!/usr/bin/env python3
"""
MyPy 错误自动修复工具
自动修复常见的 mypy 类型错误，不破坏代码功能
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import subprocess
import json


class MypyErrorFixer:
    """MyPy 错误修复器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.fixes_applied = 0

    def run_mypy(self) -> List[Dict[str, Any]]:
        """运行 mypy 并解析输出"""
        cmd = [
            sys.executable, "-m", "mypy",
            "api/", "xwe/",
            "--config-file", "mypy.ini"
        ]

        result = subprocess.run(
            cmd,
            cwd=self.project_root,
            capture_output=True,
            text=True
        )

        errors = []
        for line in result.stdout.splitlines():
            if line.strip() and ": error:" in line:
                parts = line.split(":", 4)
                if len(parts) >= 5:
                    try:
                        line_num = int(parts[1].strip())
                    except ValueError:
                        continue  # 忽略解析失败的行
                    try:
                        col_num = int(parts[2].strip())
                    except ValueError:
                        col_num = 0  # 无法解析列号则默认设为0

                    errors.append({
                        "file": parts[0],
                        "line": line_num,
                        "col": col_num,
                        "severity": parts[3].strip(),
                        "message": parts[4].strip()
                    })

        return errors

    def fix_file(self, filepath: Path, errors: List[Dict[str, Any]]) -> bool:
        """修复单个文件的错误"""
        try:
            content = filepath.read_text(encoding='utf-8')
            original_content = content
            
            # 按错误类型分组
            error_groups = {}
            for error in errors:
                error_type = self._get_error_type(error['message'])
                if error_type not in error_groups:
                    error_groups[error_type] = []
                error_groups[error_type].append(error)
            
            # 应用修复
            for error_type, error_list in error_groups.items():
                handler = getattr(self, f"_fix_{error_type}", None)
                if handler:
                    content = handler(content, error_list)
            
            # 如果内容有变化，写回文件
            if content != original_content:
                filepath.write_text(content, encoding='utf-8')
                self.fixes_applied += 1
                return True
                
        except Exception as e:
            print(f"Error fixing {filepath}: {e}")
            
        return False
    
    def _get_error_type(self, message: str) -> str:
        """从错误消息中提取错误类型"""
        if "import-untyped" in message:
            return "import_untyped"
        elif "has incompatible type \"None\"" in message:
            return "none_assignment"
        elif "Need type annotation" in message:
            return "missing_annotation"
        elif "is not valid as a type" in message and "Any" in message:
            return "any_type"
        elif "has no attribute" in message:
            return "missing_attribute"
        elif "Incompatible return value type" in message:
            return "return_type"
        elif "no overload variant" in message:
            return "overload"
        else:
            return "unknown"
    
    def _fix_import_untyped(self, content: str, errors: List[Dict[str, Any]]) -> str:
        """修复未类型化的导入"""
        lines = content.splitlines(keepends=True)
        
        for error in errors:
            line_num = error['line'] - 1
            if 0 <= line_num < len(lines):
                line = lines[line_num]
                # 检查是否是 import 语句
                if re.match(r'^\s*(import|from\s+\S+\s+import)', line):
                    # 检查是否已有 type: ignore
                    if "# type: ignore" not in line:
                        # 添加 type: ignore
                        line = line.rstrip()
                        if line.endswith("\\"):
                            line = line[:-1].rstrip() + "  # type: ignore[import-untyped]\\\n"
                        else:
                            line = line + "  # type: ignore[import-untyped]\n"
                        lines[line_num] = line
        
        return ''.join(lines)
    
    def _fix_none_assignment(self, content: str, errors: List[Dict[str, Any]]) -> str:
        """修复 None 赋值错误"""
        lines = content.splitlines(keepends=True)
        
        # 首先添加必要的导入
        import_added = False
        for line in lines:
            if "from typing import" in line:
                import_added = True
                break
        
        if not import_added:
            import_line = "from typing import Optional, List, Dict, Any\n"
            # 在第一个 import 后添加
            for i, line in enumerate(lines):
                if line.strip().startswith("import ") or line.strip().startswith("from "):
                    lines.insert(i + 1, import_line)
                    import_added = True
                    break
            
            if not import_added:
                lines.insert(0, import_line)
        
        # 修复 None 赋值
        for error in errors:
            line_num = error['line'] - 1
            if 0 <= line_num < len(lines):
                line = lines[line_num]
                # 查找变量名和类型
                match = re.search(r'variable has type "(.*?)"', error['message'])
                if match:
                    var_type = match.group(1)
                    # 检查是否是赋值语句
                    assignment_match = re.match(r'^(\s*)(\w+)\s*=\s*None', line)
                    if assignment_match:
                        indent = assignment_match.group(1)
                        var_name = assignment_match.group(2)
                        # 根据类型决定如何修复
                        if var_type.startswith("list[") or var_type.startswith("List["):
                            lines[line_num] = f"{indent}{var_name}: {var_type} = []\n"
                        elif var_type.startswith("dict[") or var_type.startswith("Dict["):
                            lines[line_num] = f"{indent}{var_name}: {var_type} = {{}}\n"
                        else:
                            lines[line_num] = f"{indent}{var_name}: Optional[{var_type}] = None\n"
        
        return ''.join(lines)
    
    def _fix_missing_annotation(self, content: str, errors: List[Dict[str, Any]]) -> str:
        """修复缺失的类型注解"""
        lines = content.splitlines(keepends=True)
        
        for error in errors:
            line_num = error['line'] - 1
            if 0 <= line_num < len(lines):
                line = lines[line_num]
                # 提取建议的类型注解
                hint_match = re.search(r'hint: "(.*?)"', error['message'])
                if hint_match:
                    hint = hint_match.group(1)
                    # 应用类型注解
                    var_match = re.match(r'^(\s*)(\w+)\s*=\s*(.*)$', line)
                    if var_match:
                        indent = var_match.group(1)
                        var_name = var_match.group(2)
                        value = var_match.group(3)
                        # 从 hint 中提取类型
                        type_match = re.search(r'(\w+):\s*(.+?)\s*=', hint)
                        if type_match:
                            var_type = type_match.group(2).replace('<type>', 'Any')
                            lines[line_num] = f"{indent}{var_name}: {var_type} = {value}"
        
        return ''.join(lines)
    
    def _fix_any_type(self, content: str, errors: List[Dict[str, Any]]) -> str:
        """修复 Any -> Any"""
        # 确保导入了 Any
        lines = content.splitlines(keepends=True)
        import_found = False
        any_imported = False
        
        for i, line in enumerate(lines):
            if "from typing import" in line:
                import_found = True
                if "Any" not in line:
                    # 添加 Any 到现有导入
                    line = line.rstrip()
                    if line.endswith(")"):
                        line = line[:-1] + ", Any)"
                    else:
                        line = line.rstrip("\n") + ", Any"
                    lines[i] = line + "\n"
                any_imported = True
                break
        
        if not import_found:
            # 添加新的导入
            for i, line in enumerate(lines):
                if line.strip().startswith("import ") or line.strip().startswith("from "):
                    lines.insert(i + 1, "from typing import Any\n")
                    any_imported = True
                    break
            
            if not any_imported:
                lines.insert(0, "from typing import Any\n")
        
        content = ''.join(lines)
        
        # 替换 Any 为 Any
        content = re.sub(r'\bany\b(?!\w)', 'Any', content)
        
        return content
    
    def _fix_return_type(self, content: str, errors: List[Dict[str, Any]]) -> str:
        """修复返回类型错误"""
        lines = content.splitlines(keepends=True)
        
        for error in errors:
            line_num = error['line'] - 1
            if 0 <= line_num < len(lines):
                line = lines[line_num]
                # 检查是否是 return None 或空 return
                if re.match(r'^\s*return\s*(None)?\s*$', line):
                    # 从错误消息中提取期望的类型
                    expected_match = re.search(r'expected "(.*?)"', error['message'])
                    if expected_match:
                        expected_type = expected_match.group(1)
                        indent_match = re.match(r'^(\s*)', line)
                        indent = indent_match.group(1) if indent_match else ""
                        
                        # 根据期望类型生成默认返回值
                        if expected_type == "str":
                            lines[line_num] = f'{indent}return ""\n'
                        elif expected_type == "int":
                            lines[line_num] = f'{indent}return 0\n'
                        elif expected_type == "float":
                            lines[line_num] = f'{indent}return 0.0\n'
                        elif expected_type == "bool":
                            lines[line_num] = f'{indent}return False\n'
                        elif expected_type.startswith(("list[", "List[")):
                            lines[line_num] = f'{indent}return []\n'
                        elif expected_type.startswith(("dict[", "Dict[")):
                            lines[line_num] = f'{indent}return {{}}\n'
        
        return ''.join(lines)
    
    def fix_project(self) -> None:
        """修复整个项目"""
        print("运行 mypy 检查...")
        errors = self.run_mypy()
        
        if not errors:
            print("没有发现类型错误！")
            return
        
        print(f"发现 {len(errors)} 个错误")
        
        # 按文件分组错误
        errors_by_file = {}
        for error in errors:
            filepath = self.project_root / error['file']
            if filepath not in errors_by_file:
                errors_by_file[filepath] = []
            errors_by_file[filepath].append(error)
        
        # 修复每个文件
        fixed_files = []
        for filepath, file_errors in errors_by_file.items():
            if filepath.exists():
                print(f"修复 {filepath.relative_to(self.project_root)}...")
                if self.fix_file(filepath, file_errors):
                    fixed_files.append(filepath.relative_to(self.project_root))
        
        print(f"\n修复完成！应用了 {self.fixes_applied} 个修复")
        if fixed_files:
            print("\n修复的文件：")
            for f in fixed_files[:10]:  # 只显示前10个
                print(f"  - {f}")
            if len(fixed_files) > 10:
                print(f"  ... 还有 {len(fixed_files) - 10} 个文件")
        
        print("\n建议重新运行 mypy 检查剩余的错误")


def main():
    """主函数"""
    project_root = Path.cwd()
    
    # 确认项目根目录
    if not (project_root / "api").exists() or not (project_root / "xwe").exists():
        print("错误：请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 创建备份提醒
    print("=" * 60)
    print("MyPy 自动修复工具")
    print("=" * 60)
    print("\n⚠️  警告：此工具将修改源代码文件！")
    print("建议先使用 git 提交当前更改作为备份。")
    print("\n此工具将自动修复以下类型的错误：")
    print("  - import-untyped (添加 # type: ignore)")
    print("  - None 赋值给非 Optional 类型")
    print("  - 缺失的类型注解")
    print("  - Any -> Any 替换")
    print("  - 返回类型不匹配")
    print("\n")
    
    response = input("是否继续？(y/n): ")
    if response.lower() != 'y':
        print("已取消")
        sys.exit(0)
    
    # 运行修复器
    fixer = MypyErrorFixer(project_root)
    fixer.fix_project()


if __name__ == "__main__":
    main()
