#!/usr/bin/env python3
# @dev_only
"""
运行 mypy 并分析类型错误
"""
import subprocess
import re
from collections import defaultdict
from pathlib import Path

def run_mypy():
    """运行 mypy 并获取输出"""
    cmd = ["mypy", "xwe", "--config-file", "mypy.ini"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def parse_mypy_output(output):
    """解析 mypy 输出，分类错误"""
    errors = defaultdict(list)
    
    # 匹配错误模式：file.py:line: error: message
    pattern = r'(.+?):(\d+): error: (.+)'
    
    for line in output.split('\n'):
        match = re.match(pattern, line)
        if match:
            file_path, line_num, error_msg = match.groups()
            
            # 分类错误类型
            if "has no attribute" in error_msg:
                error_type = "no_attribute"
            elif "Incompatible return value type" in error_msg:
                error_type = "return_type"
            elif "Incompatible types in assignment" in error_msg:
                error_type = "assignment_type"
            elif "Argument" in error_msg and "has incompatible type" in error_msg:
                error_type = "argument_type"
            elif "Cannot determine type" in error_msg:
                error_type = "cannot_determine"
            elif "Missing type parameters" in error_msg:
                error_type = "missing_type_params"
            elif "has no attribute" in error_msg:
                error_type = "no_attribute"
            elif "Optional" in error_msg:
                error_type = "optional_type"
            else:
                error_type = "other"
            
            errors[error_type].append({
                'file': file_path,
                'line': int(line_num),
                'message': error_msg
            })
    
    return errors

def print_error_summary(errors):
    """打印错误摘要"""
    print("=== MyPy 错误分析 ===\n")
    
    total = sum(len(errs) for errs in errors.values())
    print(f"总错误数: {total}\n")
    
    print("按错误类型分类:")
    for error_type, error_list in sorted(errors.items()):
        print(f"  {error_type}: {len(error_list)} 个错误")
    
    print("\n详细错误列表:\n")
    
    # 按文件分组显示
    file_errors = defaultdict(list)
    for error_type, error_list in errors.items():
        for error in error_list:
            file_errors[error['file']].append({
                'line': error['line'],
                'type': error_type,
                'message': error['message']
            })
    
    for file_path, file_error_list in sorted(file_errors.items()):
        print(f"\n{file_path} ({len(file_error_list)} 个错误):")
        for error in sorted(file_error_list, key=lambda x: x['line']):
            print(f"  L{error['line']}: [{error['type']}] {error['message']}")

def generate_fix_suggestions(errors):
    """生成修复建议"""
    print("\n=== 修复建议 ===\n")
    
    suggestions = {
        'no_attribute': "添加类型注解或检查属性是否存在",
        'return_type': "检查函数返回值类型注解是否正确",
        'assignment_type': "确保赋值类型与变量声明类型匹配",
        'argument_type': "检查函数参数类型是否正确",
        'cannot_determine': "添加明确的类型注解",
        'missing_type_params': "为泛型类型添加类型参数，如 List[str] 而不是 List",
        'optional_type': "使用 Optional[T] 或确保值不为 None",
        'other': "检查具体错误信息并相应修复"
    }
    
    for error_type, suggestion in suggestions.items():
        if error_type in errors:
            print(f"{error_type}: {suggestion}")

if __name__ == "__main__":
    print("正在运行 mypy...")
    output = run_mypy()
    
    if not output.strip():
        print("没有发现类型错误！")
    else:
        errors = parse_mypy_output(output)
        print_error_summary(errors)
        generate_fix_suggestions(errors)
        
        # 保存到文件
        with open("mypy_errors.txt", "w") as f:
            f.write(output)
        print("\n完整输出已保存到 mypy_errors.txt")
