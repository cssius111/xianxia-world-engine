#!/usr/bin/env python3
# @dev_only
"""
函数重构分析器 - 分析超长函数并提供重构建议
"""

import ast
import os
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class FunctionInfo:
    """函数信息"""
    name: str
    file_path: str
    start_line: int
    end_line: int
    line_count: int
    complexity: int
    suggestions: List[str]


class FunctionAnalyzer:
    """函数分析器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.long_functions = []
        self.complex_functions = []
    
    def analyze_all_functions(self):
        """分析所有函数"""
        print("🔍 分析项目中的所有函数...")
        
        for file_path in self.project_root.rglob("*.py"):
            self._analyze_file(file_path)
        
        # 排序
        self.long_functions.sort(key=lambda x: x.line_count, reverse=True)
        self.complex_functions.sort(key=lambda x: x.complexity, reverse=True)
        
        print(f"📊 发现 {len(self.long_functions)} 个超长函数")
        print(f"🔀 发现 {len(self.complex_functions)} 个高复杂度函数")
    
    def _analyze_file(self, file_path: Path):
        """分析单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        info = self._analyze_function(node, file_path)
                        if info:
                            if info.line_count > 50:
                                self.long_functions.append(info)
                            if info.complexity > 10:
                                self.complex_functions.append(info)
            except SyntaxError:
                pass
                
        except UnicodeDecodeError:
            pass
    
    def _analyze_function(self, node: ast.FunctionDef, file_path: Path) -> FunctionInfo:
        """分析单个函数"""
        line_count = (node.end_lineno or node.lineno) - node.lineno
        complexity = self._calculate_complexity(node)
        suggestions = self._generate_suggestions(node, line_count, complexity)
        
        return FunctionInfo(
            name=node.name,
            file_path=str(file_path),
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
            line_count=line_count,
            complexity=complexity,
            suggestions=suggestions
        )
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """计算函数复杂度"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.Try):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _generate_suggestions(self, node: ast.FunctionDef, line_count: int, complexity: int) -> List[str]:
        """生成重构建议"""
        suggestions = []
        
        if line_count > 100:
            suggestions.append("🔴 极长函数 - 建议拆分为3-5个小函数")
        elif line_count > 50:
            suggestions.append("🟡 长函数 - 考虑拆分为2-3个函数")
        
        if complexity > 15:
            suggestions.append("🔴 极高复杂度 - 使用策略模式或状态机")
        elif complexity > 10:
            suggestions.append("🟡 高复杂度 - 使用早期返回减少嵌套")
        
        # 分析具体的重构点
        if self._has_multiple_responsibilities(node):
            suggestions.append("📦 职责过多 - 按功能拆分函数")
        
        if self._has_deep_nesting(node):
            suggestions.append("🏗️ 嵌套过深 - 提取函数或使用卫语句")
        
        if self._has_long_parameter_list(node):
            suggestions.append("📝 参数过多 - 考虑使用配置对象")
        
        return suggestions
    
    def _has_multiple_responsibilities(self, node: ast.FunctionDef) -> bool:
        """检查是否有多个职责"""
        # 简单检查：如果有多个不同类型的操作
        operation_types = set()
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if hasattr(child.func, 'attr'):
                    attr = child.func.attr
                    if any(keyword in attr for keyword in ['save', 'load', 'write', 'read']):
                        operation_types.add('io')
                    elif any(keyword in attr for keyword in ['process', 'parse', 'analyze']):
                        operation_types.add('processing')
                    elif any(keyword in attr for keyword in ['render', 'display', 'show']):
                        operation_types.add('ui')
        
        return len(operation_types) > 2
    
    def _has_deep_nesting(self, node: ast.FunctionDef) -> bool:
        """检查是否有深层嵌套"""
        max_depth = 0
        
        def calculate_depth(node, current_depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, current_depth)
            
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                    calculate_depth(child, current_depth + 1)
                else:
                    calculate_depth(child, current_depth)
        
        calculate_depth(node)
        return max_depth > 4
    
    def _has_long_parameter_list(self, node: ast.FunctionDef) -> bool:
        """检查是否有过长的参数列表"""
        return len(node.args.args) > 5
    
    def get_top_priority_functions(self, limit: int = 10) -> List[FunctionInfo]:
        """获取最需要重构的函数"""
        # 综合考虑长度和复杂度
        all_functions = {}
        
        for func in self.long_functions:
            key = f"{func.file_path}:{func.name}"
            all_functions[key] = func
        
        for func in self.complex_functions:
            key = f"{func.file_path}:{func.name}"
            if key in all_functions:
                # 如果既长又复杂，提高优先级
                all_functions[key].suggestions.insert(0, "⚠️ 高优先级 - 既长又复杂")
            else:
                all_functions[key] = func
        
        # 按优先级排序（长度 + 复杂度的组合分数）
        functions = list(all_functions.values())
        functions.sort(key=lambda x: x.line_count * x.complexity, reverse=True)
        
        return functions[:limit]
    
    def generate_refactor_plan(self, target_function: FunctionInfo) -> str:
        """为特定函数生成重构计划"""
        plan = f"""
# 🔧 重构计划：{target_function.name}

**文件**: {target_function.file_path}
**位置**: 第{target_function.start_line}-{target_function.end_line}行
**长度**: {target_function.line_count}行
**复杂度**: {target_function.complexity}

## 🎯 重构建议
"""
        
        for suggestion in target_function.suggestions:
            plan += f"- {suggestion}\n"
        
        plan += f"""
## 📋 重构步骤

### 1. 分析当前函数职责
```python
# 在 {target_function.file_path} 中找到函数
def {target_function.name}(...):
    # 分析这个函数在做什么
    # 识别可以独立出来的逻辑块
```

### 2. 识别拆分点
- 寻找逻辑上独立的代码块
- 找出重复的代码段
- 识别可以提取的工具函数

### 3. 逐步重构
```python
# 原始函数
def {target_function.name}(self, ...):
    # 100+ 行混合逻辑
    pass

# 重构后
def {target_function.name}(self, ...):
    # 主要流程控制 (20-30行)
    result1 = self._handle_step1(...)
    result2 = self._handle_step2(...)
    return self._combine_results(result1, result2)

def _handle_step1(self, ...):
    # 具体逻辑1 (20-30行)
    pass

def _handle_step2(self, ...):
    # 具体逻辑2 (20-30行)
    pass
```

### 4. 测试验证
- 确保重构后功能不变
- 检查性能是否有提升
- 验证代码可读性提升
"""
        
        return plan
    
    def print_summary(self):
        """打印分析总结"""
        print("\n" + "="*60)
        print("📊 函数重构分析总结")
        print("="*60)
        
        print(f"\n🔴 最需要重构的函数 (TOP 10):")
        for i, func in enumerate(self.get_top_priority_functions(10), 1):
            print(f"{i:2d}. {func.name} ({Path(func.file_path).name})")
            print(f"     📏 {func.line_count}行 | 🔀 复杂度{func.complexity}")
            if func.suggestions:
                print(f"     💡 {func.suggestions[0]}")
            print()
        
        print("🎯 建议优先重构前3个函数，预期收益最大！")


def main():
    """主函数"""
    analyzer = FunctionAnalyzer()
    analyzer.analyze_all_functions()
    analyzer.print_summary()
    
    # 为最复杂的函数生成重构计划
    top_functions = analyzer.get_top_priority_functions(3)
    
    for i, func in enumerate(top_functions, 1):
        plan = analyzer.generate_refactor_plan(func)
        
        plan_file = f"refactor_plan_{i}_{func.name}.md"
        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write(plan)
        
        print(f"📄 已生成重构计划: {plan_file}")


if __name__ == '__main__':
    main()
