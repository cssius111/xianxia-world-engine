#!/usr/bin/env python3
# @dev_only
"""
批量修复 xianxia_world_engine 项目的 MyPy 类型错误
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple


def fix_python_file(file_path: Path) -> Tuple[bool, List[str]]:
    """
    修复单个 Python 文件的类型错误
    返回: (是否修改, 修改列表)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        original_lines = lines.copy()
        changes = []

        # 1. 修复 Union 类型 (str | Path -> Union[str, Path])
        for i, line in enumerate(lines):
            if "|" in line and ("str" in line or "Path" in line):
                # 处理 str | Path 模式
                new_line = re.sub(r"(\w+:\s*)str\s*\|\s*Path", r"\1Union[str, Path]", line)
                if new_line != line:
                    lines[i] = new_line
                    changes.append(f"Line {i+1}: 修复 Union 类型")

                # 处理 str | Path | None 模式
                new_line = re.sub(
                    r"(\w+:\s*)str\s*\|\s*Path\s*\|\s*None",
                    r"\1Optional[Union[str, Path]]",
                    lines[i],
                )
                if new_line != lines[i]:
                    lines[i] = new_line
                    changes.append(f"Line {i+1}: 修复 Optional Union 类型")

        # 2. 修复缺少的类型参数
        for i, line in enumerate(lines):
            # Dict -> Dict[str, Any]
            new_line = re.sub(r"(\s*:\s*)Dict(\s*[=\),\n])", r"\1Dict[str, Any]\2", line)
            if new_line != line:
                lines[i] = new_line
                changes.append(f"Line {i+1}: Dict -> Dict[str, Any]")
                continue

            # List -> List[Any]
            new_line = re.sub(r"(\s*:\s*)List(\s*[=\),\n])", r"\1List[Any]\2", lines[i])
            if new_line != lines[i]:
                lines[i] = new_line
                changes.append(f"Line {i+1}: List -> List[Any]")
                continue

            # Set -> Set[Any]
            new_line = re.sub(r"(\s*:\s*)Set(\s*[=\),\n])", r"\1Set[Any]\2", lines[i])
            if new_line != lines[i]:
                lines[i] = new_line
                changes.append(f"Line {i+1}: Set -> Set[Any]")

        # 3. 修复 Optional 类型 (x = None 但没有 Optional)
        for i, line in enumerate(lines):
            # 匹配 param: Type = None 模式
            match = re.search(r"(\w+):\s*([A-Za-z_]\w*)(\[[^\]]*\])?\s*=\s*None", line)
            if match and "Optional" not in line:
                param_name = match.group(1)
                type_name = match.group(2) + (match.group(3) or "")
                new_line = line.replace(
                    f"{param_name}: {type_name}", f"{param_name}: Optional[{type_name}]"
                )
                lines[i] = new_line
                changes.append(f"Line {i+1}: 添加 Optional[{type_name}]")

        # 4. 修复函数返回类型
        for i, line in enumerate(lines):
            # 检查函数定义
            if (
                line.strip().startswith("def ")
                and ") ->" not in line
                and line.strip().endswith(":")
            ):
                func_match = re.match(r"(\s*def\s+\w+\s*\([^)]*\))\s*:", line)
                if func_match:
                    # 检查函数名
                    if "__init__" in line:
                        continue  # __init__ 不需要返回类型

                    # 查看后续几行是否有 return
                    has_return = False
                    returns_none = True
                    for j in range(i + 1, min(i + 20, len(lines))):
                        if lines[j].strip().startswith("def "):
                            break
                        if "return" in lines[j]:
                            has_return = True
                            if "return None" not in lines[j] and not lines[j].strip() == "return":
                                returns_none = False
                            break

                    # 添加返回类型
                    return_type = " -> None" if not has_return or returns_none else " -> Any"
                    new_line = func_match.group(1) + return_type + ":\n"
                    lines[i] = new_line
                    changes.append(f"Line {i+1}: 添加返回类型{return_type}")

        # 5. 确保正确的导入
        imports_needed = set()
        content = "".join(lines)

        if "Dict[" in content:
            imports_needed.add("Dict")
        if "List[" in content:
            imports_needed.add("List")
        if "Set[" in content:
            imports_needed.add("Set")
        if "Optional[" in content:
            imports_needed.add("Optional")
        if "Union[" in content:
            imports_needed.add("Union")
        if "-> Any" in content or ": Any" in content:
            imports_needed.add("Any")
        if "Tuple[" in content:
            imports_needed.add("Tuple")

        # 查找现有的 typing 导入
        typing_import_line = -1
        for i, line in enumerate(lines):
            if line.startswith("from typing import"):
                typing_import_line = i
                break

        if imports_needed:
            if typing_import_line >= 0:
                # 更新现有导入
                current_imports = re.findall(
                    r"from typing import ([^\n]+)", lines[typing_import_line]
                )[0]
                current_items = [item.strip() for item in current_imports.split(",")]

                # 添加缺失的导入
                for item in imports_needed:
                    if item not in current_items:
                        current_items.append(item)
                        changes.append(f"添加 typing 导入: {item}")

                # 排序并重新构建导入行
                current_items.sort()
                new_import_line = f"from typing import {', '.join(current_items)}\n"
                lines[typing_import_line] = new_import_line
            else:
                # 添加新的导入行
                import_items = sorted(list(imports_needed))
                new_import = f"from typing import {', '.join(import_items)}\n"

                # 在文件开头适当位置插入
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.strip() and not line.startswith("#") and not line.startswith('"""'):
                        if line.startswith("import ") or line.startswith("from "):
                            insert_pos = i + 1
                        else:
                            break

                lines.insert(insert_pos, new_import)
                changes.append(f"添加 typing 导入行")

        # 如果有修改，写回文件
        if lines != original_lines:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            return True, changes

        return False, []

    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return False, [f"错误: {e}"]


def main():
    """主函数"""
    # 项目根目录位于 scripts/ 的上一级
    project_root = Path(__file__).resolve().parent.parent
    xwe_dir = project_root / "xwe"

    if not xwe_dir.exists():
        print(f"错误: 找不到 xwe 目录: {xwe_dir}")
        return

    print("开始批量修复 MyPy 类型错误...")
    print(f"项目目录: {project_root}")
    print("")

    # 收集所有 Python 文件
    python_files = []
    exclude_patterns = ["__pycache__", ".pytest_cache", "test_", "tests/"]

    for file_path in xwe_dir.rglob("*.py"):
        # 检查是否应该排除
        should_exclude = any(pattern in str(file_path) for pattern in exclude_patterns)
        if not should_exclude:
            python_files.append(file_path)

    print(f"找到 {len(python_files)} 个 Python 文件")
    print("")

    # 处理每个文件
    total_fixed = 0
    all_changes = []

    for file_path in sorted(python_files):
        fixed, changes = fix_python_file(file_path)
        if fixed:
            total_fixed += 1
            relative_path = file_path.relative_to(project_root)
            print(f"修复: {relative_path}")
            for change in changes:
                print(f"  - {change}")
                all_changes.append(f"{relative_path}: {change}")
            print("")

    # 总结
    print("=" * 60)
    print(f"修复完成！共修复 {total_fixed} 个文件")
    print(f"总计 {len(all_changes)} 处修改")

    # 保存修改日志
    if all_changes:
        log_file = project_root / "mypy_fixes.log"
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("MyPy 类型错误修复日志\n")
            f.write("=" * 60 + "\n")
            f.write(f"修复时间: {__import__('datetime').datetime.now()}\n")
            f.write(f"修复文件数: {total_fixed}\n")
            f.write(f"修改总数: {len(all_changes)}\n")
            f.write("=" * 60 + "\n\n")

            for change in all_changes:
                f.write(f"{change}\n")

        print(f"\n修改日志已保存到: {log_file}")

    print("\n建议接下来的步骤:")
    print("1. 运行 'mypy xwe' 检查剩余的类型错误")
    print("2. 运行测试确保功能正常: 'pytest'")
    print("3. 提交修改: 'git add -A && git commit -m \"[PHASE4-B2] fix: 批量修复 MyPy 类型错误\"'")


if __name__ == "__main__":
    main()
