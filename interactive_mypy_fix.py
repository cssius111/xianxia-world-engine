#!/usr/bin/env python3
"""
交互式 MyPy 错误修复指南
根据错误类型提供具体的修复建议
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class InteractiveFixer:
    """交互式修复器"""
    
    def __init__(self):
        self.error_patterns = {
            'import-untyped': {
                'pattern': r'Library stubs not installed for "(.*?)"',
                'fix': self.fix_import_untyped,
                'description': '缺少类型存根'
            },
            'incompatible-none': {
                'pattern': r'Incompatible types in assignment \(expression has type "None", variable has type "(.*?)"\)',
                'fix': self.fix_incompatible_none,
                'description': 'None 赋值给非 Optional 类型'
            },
            'need-annotation': {
                'pattern': r'Need type annotation for "(.*?)"',
                'fix': self.fix_need_annotation,
                'description': '需要类型注解'
            },
            'Any-not-valid': {
                'pattern': r'Function "builtins.Any" is not valid as a type',
                'fix': self.fix_any_not_valid,
                'description': 'Any 应该是 Any'
            },
            'no-attribute': {
                'pattern': r'"(.*?)" has no attribute "(.*?)"',
                'fix': self.fix_no_attribute,
                'description': '属性不存在'
            },
            'return-value': {
                'pattern': r'Incompatible return value type \(got "(.*?)", expected "(.*?)"\)',
                'fix': self.fix_return_value,
                'description': '返回值类型不匹配'
            }
        }
    
    def run(self):
        """运行交互式修复"""
        print("=" * 70)
        print("MyPy 错误修复指南")
        print("=" * 70)
        print("\n选择修复模式：")
        print("1. 自动扫描并修复")
        print("2. 查看特定错误的修复方法")
        print("3. 修复单个文件")
        print("4. 生成修复报告")
        
        choice = input("\n请选择 (1-4): ")
        
        if choice == '1':
            self.auto_fix()
        elif choice == '2':
            self.show_fix_methods()
        elif choice == '3':
            self.fix_single_file()
        elif choice == '4':
            self.generate_report()
        else:
            print("无效选择")
    
    def fix_import_untyped(self, error_info: Dict) -> str:
        """修复导入类型存根问题"""
        module = error_info.get('module', 'requests')
        
        fixes = []
        fixes.append(f"# 方法 1: 安装类型存根")
        fixes.append(f"pip install types-{module}")
        fixes.append("")
        fixes.append(f"# 方法 2: 添加 type: ignore")
        fixes.append(f"import {module}  # type: ignore[import-untyped]")
        
        return '\n'.join(fixes)
    
    def fix_incompatible_none(self, error_info: Dict) -> str:
        """修复 None 赋值问题"""
        var_type = error_info.get('type', 'list[str]')
        
        fixes = []
        fixes.append(f"# 原代码：variable = None")
        fixes.append(f"# 错误类型：{var_type}")
        fixes.append("")
        fixes.append("# 修复方法 1: 使用 Optional")
        fixes.append(f"from typing import Optional")
        fixes.append(f"variable: Optional[{var_type}] = None")
        fixes.append("")
        fixes.append("# 修复方法 2: 初始化为空值")
        
        if 'list' in var_type.lower():
            fixes.append(f"variable: {var_type} = []")
        elif 'dict' in var_type.lower():
            fixes.append(f"variable: {var_type} = {{}}")
        elif 'set' in var_type.lower():
            fixes.append(f"variable: {var_type} = set()")
        else:
            fixes.append(f"variable: {var_type} = {var_type}()  # 使用默认构造函数")
        
        return '\n'.join(fixes)
    
    def fix_need_annotation(self, error_info: Dict) -> str:
        """修复缺少类型注解"""
        var_name = error_info.get('variable', 'variable')
        hint = error_info.get('hint', '')
        
        fixes = []
        fixes.append(f"# 变量：{var_name}")
        fixes.append(f"# 建议：{hint}")
        fixes.append("")
        fixes.append("# 常见类型注解：")
        fixes.append(f"{var_name}: List[str] = []")
        fixes.append(f"{var_name}: Dict[str, Any] = {{}}")
        fixes.append(f"{var_name}: Set[int] = set()")
        fixes.append(f"{var_name}: Optional[str] = None")
        fixes.append("")
        fixes.append("# 记得导入类型：")
        fixes.append("from typing import List, Dict, Set, Optional, Any")
        
        return '\n'.join(fixes)
    
    def fix_any_not_valid(self, error_info: Dict) -> str:
        """修复 Any -> Any"""
        fixes = []
        fixes.append("# 错误：使用了内置函数 Any 作为类型")
        fixes.append("")
        fixes.append("# 修复：")
        fixes.append("from typing import Any")
        fixes.append("")
        fixes.append("# 替换所有的 Any 为 Any：")
        fixes.append("def function(param: Any) -> Any:")
        fixes.append("    return param")
        
        return '\n'.join(fixes)
    
    def fix_no_attribute(self, error_info: Dict) -> str:
        """修复属性不存在"""
        obj_type = error_info.get('object', 'object')
        attribute = error_info.get('attribute', 'attribute')
        
        fixes = []
        fixes.append(f"# 错误：{obj_type} 没有属性 {attribute}")
        fixes.append("")
        fixes.append("# 可能的修复方法：")
        fixes.append("")
        fixes.append("1. 添加缺失的属性或方法：")
        fixes.append(f"class {obj_type}:")
        fixes.append(f"    def {attribute}(self):")
        fixes.append(f"        pass")
        fixes.append("")
        fixes.append("2. 检查拼写错误")
        fixes.append("")
        fixes.append("3. 使用 getattr 安全访问：")
        fixes.append(f"value = getattr(obj, '{attribute}', default_value)")
        
        return '\n'.join(fixes)
    
    def fix_return_value(self, error_info: Dict) -> str:
        """修复返回值类型"""
        got_type = error_info.get('got', 'None')
        expected_type = error_info.get('expected', 'str')
        
        fixes = []
        fixes.append(f"# 错误：返回 {got_type}，期望 {expected_type}")
        fixes.append("")
        
        if got_type == "None":
            fixes.append("# 修复方法：")
            if expected_type == "str":
                fixes.append('return ""  # 返回空字符串')
            elif expected_type == "int":
                fixes.append('return 0  # 返回 0')
            elif expected_type == "float":
                fixes.append('return 0.0  # 返回 0.0')
            elif expected_type == "bool":
                fixes.append('return False  # 返回 False')
            elif 'list' in expected_type.lower():
                fixes.append('return []  # 返回空列表')
            elif 'dict' in expected_type.lower():
                fixes.append('return {}  # 返回空字典')
            
            fixes.append("")
            fixes.append("# 或者修改函数签名允许返回 None：")
            fixes.append(f"def function() -> Optional[{expected_type}]:")
            fixes.append("    return None")
        
        return '\n'.join(fixes)
    
    def show_fix_methods(self):
        """显示修复方法"""
        print("\n选择错误类型：")
        for i, (key, info) in enumerate(self.error_patterns.items(), 1):
            print(f"{i}. {info['description']}")
        
        choice = input("\n请选择 (输入数字): ")
        
        try:
            idx = int(choice) - 1
            error_type = list(self.error_patterns.keys())[idx]
            pattern_info = self.error_patterns[error_type]
            
            print(f"\n{pattern_info['description']} 的修复方法：")
            print("-" * 50)
            
            # 示例错误信息
            example_info = {
                'module': 'requests',
                'type': 'List[str]',
                'variable': 'items',
                'hint': 'items: List[<type>] = ...',
                'object': 'MyClass',
                'attribute': 'missing_method',
                'got': 'None',
                'expected': 'str'
            }
            
            fix_suggestion = pattern_info['fix'](example_info)
            print(fix_suggestion)
            
        except (ValueError, IndexError):
            print("无效选择")
    
    def auto_fix(self):
        """自动扫描并提供修复建议"""
        print("\n正在运行 mypy...")
        
        result = subprocess.run(
            [sys.executable, '-m', 'mypy', 'api/', 'xwe/', '--config-file', 'mypy.ini'],
            capture_output=True,
            text=True
        )
        
        errors = self.parse_mypy_output(result.stdout)
        
        if not errors:
            print("没有发现错误！")
            return
        
        print(f"\n发现 {len(errors)} 个错误")
        
        # 按错误类型分组
        error_groups = {}
        for error in errors:
            error_type = error['type']
            if error_type not in error_groups:
                error_groups[error_type] = []
            error_groups[error_type].append(error)
        
        # 显示统计
        print("\n错误统计：")
        for error_type, errors in error_groups.items():
            pattern_info = self.error_patterns.get(error_type, {})
            description = pattern_info.get('description', error_type)
            print(f"  - {description}: {len(errors)} 个")
        
        # 询问是否查看详细修复建议
        if input("\n查看详细修复建议？(y/n): ").lower() == 'y':
            for error_type, errors in error_groups.items():
                pattern_info = self.error_patterns.get(error_type)
                if pattern_info:
                    print(f"\n\n{'=' * 60}")
                    print(f"{pattern_info['description']} 的修复建议：")
                    print('=' * 60)
                    
                    # 显示前3个错误作为示例
                    for error in errors[:3]:
                        print(f"\n文件: {error['file']}:{error['line']}")
                        print(f"错误: {error['message']}")
                    
                    print("\n修复方法：")
                    print(pattern_info['fix'](errors[0]))
                    
                    if len(errors) > 3:
                        print(f"\n... 还有 {len(errors) - 3} 个类似错误")
    
    def parse_mypy_output(self, output: str) -> List[Dict]:
        """解析 mypy 输出"""
        errors = []
        
        for line in output.splitlines():
            if ': error:' in line:
                parts = line.split(':', 4)
                if len(parts) >= 5:
                    error = {
                        'file': parts[0],
                        'line': int(parts[1]),
                        'message': parts[4].strip()
                    }
                    
                    # 判断错误类型
                    for error_type, pattern_info in self.error_patterns.items():
                        if re.search(pattern_info['pattern'], error['message']):
                            error['type'] = error_type
                            match = re.search(pattern_info['pattern'], error['message'])
                            if match:
                                error['match_groups'] = match.groups()
                            break
                    else:
                        error['type'] = 'unknown'
                    
                    errors.append(error)
        
        return errors
    
    def fix_single_file(self):
        """修复单个文件"""
        filename = input("\n输入要修复的文件路径: ")
        
        if not Path(filename).exists():
            print(f"文件不存在: {filename}")
            return
        
        print(f"\n正在检查 {filename}...")
        
        result = subprocess.run(
            [sys.executable, '-m', 'mypy', filename],
            capture_output=True,
            text=True
        )
        
        errors = self.parse_mypy_output(result.stdout)
        
        if not errors:
            print("该文件没有类型错误！")
            return
        
        print(f"\n发现 {len(errors)} 个错误")
        
        for i, error in enumerate(errors, 1):
            print(f"\n错误 {i}/{len(errors)}:")
            print(f"行 {error['line']}: {error['message']}")
            
            pattern_info = self.error_patterns.get(error['type'])
            if pattern_info:
                print(f"\n建议修复：")
                print(pattern_info['fix'](error))
            
            if i < len(errors):
                input("\n按 Enter 查看下一个错误...")
    
    def generate_report(self):
        """生成修复报告"""
        print("\n生成 MyPy 错误修复报告...")
        
        result = subprocess.run(
            [sys.executable, '-m', 'mypy', 'api/', 'xwe/', '--config-file', 'mypy.ini'],
            capture_output=True,
            text=True
        )
        
        errors = self.parse_mypy_output(result.stdout)
        
        # 生成 Markdown 报告
        report = []
        report.append("# MyPy 错误修复报告")
        report.append(f"\n总错误数：{len(errors)}")
        report.append("\n## 错误分类统计")
        
        # 统计
        error_stats = {}
        for error in errors:
            error_type = error.get('type', 'unknown')
            if error_type not in error_stats:
                error_stats[error_type] = 0
            error_stats[error_type] += 1
        
        for error_type, count in sorted(error_stats.items(), key=lambda x: x[1], reverse=True):
            pattern_info = self.error_patterns.get(error_type, {})
            description = pattern_info.get('description', error_type)
            report.append(f"- {description}: {count} 个")
        
        report.append("\n## 详细错误列表")
        
        # 按文件分组
        errors_by_file = {}
        for error in errors:
            file = error['file']
            if file not in errors_by_file:
                errors_by_file[file] = []
            errors_by_file[file].append(error)
        
        for file, file_errors in sorted(errors_by_file.items()):
            report.append(f"\n### {file}")
            for error in file_errors:
                report.append(f"- 行 {error['line']}: {error['message']}")
        
        # 保存报告
        report_path = Path("mypy_fix_report.md")
        report_path.write_text('\n'.join(report), encoding='utf-8')
        
        print(f"\n报告已保存到：{report_path}")
        
        # 询问是否生成修复脚本
        if input("\n是否生成自动修复脚本？(y/n): ").lower() == 'y':
            self.generate_fix_script(errors)
    
    def generate_fix_script(self, errors: List[Dict]):
        """生成修复脚本"""
        script = []
        script.append("#!/usr/bin/env python3")
        script.append('"""自动生成的 MyPy 错误修复脚本"""')
        script.append("")
        script.append("import re")
        script.append("from pathlib import Path")
        script.append("")
        script.append("def main():")
        script.append("    fixes = {")
        
        # 生成修复字典
        for error in errors[:50]:  # 只处理前50个错误
            file = error['file']
            line = error['line']
            error_type = error.get('type', 'unknown')
            
            if error_type == 'import-untyped':
                fix = f"# type: ignore[import-untyped]"
                script.append(f'        ("{file}", {line}, "append", "{fix}"),')
            elif error_type == 'incompatible-none':
                script.append(f'        ("{file}", {line}, "replace_none"),')
        
        script.append("    }")
        script.append("")
        script.append("    # 应用修复")
        script.append("    for file, line, fix_type, *args in fixes:")
        script.append("        apply_fix(file, line, fix_type, *args)")
        script.append("")
        script.append('if __name__ == "__main__":')
        script.append("    main()")
        
        # 保存脚本
        script_path = Path("auto_fix_script.py")
        script_path.write_text('\n'.join(script), encoding='utf-8')
        
        print(f"修复脚本已保存到：{script_path}")


if __name__ == "__main__":
    fixer = InteractiveFixer()
    fixer.run()
