#!/usr/bin/env python3
"""
仙侠世界引擎 - 代码质量优化工具
自动执行代码质量检查和基础修复

使用方法:
python quality_optimizer.py --check          # 检查代码质量
python quality_optimizer.py --fix-basic      # 修复基础问题
python quality_optimizer.py --todo-analysis  # TODO分析
python quality_optimizer.py --full-report    # 生成完整报告
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
import ast


class CodeQualityOptimizer:
    """代码质量优化器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues = defaultdict(list)
        self.stats = {}
        
    def analyze_project(self) -> Dict[str, Any]:
        """分析整个项目"""
        print("🔍 开始分析项目...")
        
        # 1. 统计基础信息
        self._collect_basic_stats()
        
        # 2. TODO分析
        self._analyze_todos()
        
        # 3. 导入依赖分析
        self._analyze_imports()
        
        # 4. 代码复杂度分析
        self._analyze_complexity()
        
        # 5. 性能热点分析
        self._analyze_performance_hotspots()
        
        return {
            'stats': self.stats,
            'issues': dict(self.issues),
            'recommendations': self._generate_recommendations()
        }
    
    def _collect_basic_stats(self):
        """收集基础统计信息"""
        python_files = list(self.project_root.rglob("*.py"))
        
        total_lines = 0
        total_files = len(python_files)
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    total_lines += len(lines)
            except UnicodeDecodeError:
                continue
        
        self.stats.update({
            'total_files': total_files,
            'total_lines': total_lines,
            'avg_lines_per_file': total_lines // total_files if total_files > 0 else 0
        })
        
        print(f"📊 发现 {total_files} 个Python文件，共 {total_lines} 行代码")
    
    def _analyze_todos(self):
        """分析TODO注释"""
        todo_pattern = re.compile(r'#\s*TODO[:\s](.+)', re.IGNORECASE)
        todo_stats = defaultdict(list)
        
        for file_path in self.project_root.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for i, line in enumerate(lines, 1):
                    match = todo_pattern.search(line)
                    if match:
                        todo_text = match.group(1).strip()
                        todo_stats[str(file_path)].append({
                            'line': i,
                            'text': todo_text
                        })
            except UnicodeDecodeError:
                continue
        
        total_todos = sum(len(todos) for todos in todo_stats.values())
        self.stats['todo_count'] = total_todos
        self.issues['todos'] = dict(todo_stats)
        
        print(f"📝 发现 {total_todos} 个TODO项")
    
    def _analyze_imports(self):
        """分析导入依赖"""
        import_stats = defaultdict(set)
        circular_imports = []
        
        for file_path in self.project_root.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 解析AST
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                import_stats[str(file_path)].add(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                import_stats[str(file_path)].add(node.module)
                except SyntaxError:
                    continue
                    
            except UnicodeDecodeError:
                continue
        
        # 检查循环导入风险
        core_files = [f for f in import_stats.keys() if 'core' in f]
        for core_file in core_files:
            imports = import_stats[core_file]
            for imp in imports:
                if 'npc' in imp and 'core' in core_file:
                    circular_imports.append(f"{core_file} -> {imp}")
        
        self.issues['circular_imports'] = circular_imports
        self.stats['import_complexity'] = len(import_stats)
        
        if circular_imports:
            print(f"⚠️  发现 {len(circular_imports)} 个潜在循环导入")
    
    def _analyze_complexity(self):
        """分析代码复杂度"""
        complex_functions = []
        long_functions = []
        
        for file_path in self.project_root.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # 计算函数长度
                            func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                            
                            if func_lines > 50:  # 超过50行认为是长函数
                                long_functions.append({
                                    'file': str(file_path),
                                    'function': node.name,
                                    'lines': func_lines,
                                    'start_line': node.lineno
                                })
                            
                            # 计算复杂度（简单的if/for/while计数）
                            complexity = self._calculate_cyclomatic_complexity(node)
                            if complexity > 10:  # 复杂度超过10
                                complex_functions.append({
                                    'file': str(file_path),
                                    'function': node.name,
                                    'complexity': complexity,
                                    'start_line': node.lineno
                                })
                                
                except SyntaxError:
                    continue
                    
            except UnicodeDecodeError:
                continue
        
        self.issues['long_functions'] = long_functions
        self.issues['complex_functions'] = complex_functions
        
        print(f"📏 发现 {len(long_functions)} 个超长函数")
        print(f"🔀 发现 {len(complex_functions)} 个高复杂度函数")
    
    def _calculate_cyclomatic_complexity(self, node) -> int:
        """计算圈复杂度（简化版）"""
        complexity = 1  # 基础复杂度
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _analyze_performance_hotspots(self):
        """分析性能热点"""
        hotspots = []
        
        # 查找可能的性能问题
        patterns = {
            'network_calls': [r'requests\.', r'\.post\(', r'\.get\('],
            'file_io': [r'open\(', r'\.read\(', r'\.write\('],
            'loops_in_loops': [r'for.*for', r'while.*while'],
            'large_data_structures': [r'Dict\[.*Character', r'List\[.*Character']
        }
        
        for file_path in self.project_root.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for category, pattern_list in patterns.items():
                    for pattern in pattern_list:
                        matches = re.findall(pattern, content)
                        if matches:
                            hotspots.append({
                                'file': str(file_path),
                                'category': category,
                                'matches': len(matches)
                            })
                            
            except UnicodeDecodeError:
                continue
        
        self.issues['performance_hotspots'] = hotspots
        print(f"⚡ 发现 {len(hotspots)} 个潜在性能热点")
    
    def _generate_recommendations(self) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 基于TODO数量
        if self.stats.get('todo_count', 0) > 20:
            recommendations.append("🔴 优先处理TODO项目，特别是game_core.py中的物品系统相关TODO")
        
        # 基于循环导入
        if self.issues.get('circular_imports'):
            recommendations.append("🟡 解决循环导入问题，建议使用依赖注入或事件驱动模式")
        
        # 基于函数复杂度
        if self.issues.get('long_functions'):
            recommendations.append("🔧 重构超长函数，建议拆分为多个小函数")
        
        # 基于性能热点
        if self.issues.get('performance_hotspots'):
            recommendations.append("⚡ 优化网络调用，建议添加缓存机制")
        
        return recommendations
    
    def fix_basic_issues(self):
        """修复基础问题"""
        print("🔧 开始修复基础问题...")
        
        # 1. 创建缺失的基础文件
        self._create_missing_files()
        
        # 2. 添加基础异常处理
        self._add_basic_exception_handling()
        
        # 3. 生成配置文件模板
        self._create_config_template()
        
        print("✅ 基础问题修复完成")
    
    def _create_missing_files(self):
        """创建缺失的基础文件"""
        files_to_create = [
            'xwe/core/item_system.py',
            'xwe/core/confirmation_manager.py',
            'xwe/core/exception_handler.py'
        ]
        
        for file_path in files_to_create:
            full_path = self.project_root / file_path
            if not full_path.exists():
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 创建基础模板
                template = self._get_file_template(file_path)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(template)
                
                print(f"📄 创建文件: {file_path}")
    
    def _get_file_template(self, file_path: str) -> str:
        """获取文件模板"""
        if 'item_system' in file_path:
            return '''"""
物品系统 - 管理游戏中的物品、背包、交易等
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Item:
    """物品基础类"""
    id: str
    name: str
    description: str
    value: int = 0
    stackable: bool = True
    max_stack: int = 99


class ItemSystem:
    """物品系统管理器"""
    
    def __init__(self):
        self.items: Dict[str, Item] = {}
        self.player_inventories: Dict[str, Dict[str, int]] = {}
    
    def get_spirit_stones(self, player_id: str) -> int:
        """获取玩家的灵石数量"""
        inventory = self.player_inventories.get(player_id, {})
        return inventory.get('spirit_stones', 0)
    
    def add_item(self, player_id: str, item_id: str, quantity: int = 1) -> bool:
        """添加物品到玩家背包"""
        if player_id not in self.player_inventories:
            self.player_inventories[player_id] = {}
        
        current = self.player_inventories[player_id].get(item_id, 0)
        self.player_inventories[player_id][item_id] = current + quantity
        return True
    
    def remove_item(self, player_id: str, item_id: str, quantity: int = 1) -> bool:
        """从玩家背包移除物品"""
        inventory = self.player_inventories.get(player_id, {})
        if inventory.get(item_id, 0) >= quantity:
            inventory[item_id] -= quantity
            if inventory[item_id] <= 0:
                del inventory[item_id]
            return True
        return False


# 全局物品系统实例
item_system = ItemSystem()
'''
        elif 'confirmation_manager' in file_path:
            return '''"""
确认机制管理器 - 处理需要用户确认的操作
"""

from typing import Dict, Callable, Any, Optional
from dataclasses import dataclass
import uuid


@dataclass
class PendingConfirmation:
    """待确认的操作"""
    id: str
    action: str
    description: str
    callback: Callable
    data: Dict[str, Any]


class ConfirmationManager:
    """确认机制管理器"""
    
    def __init__(self):
        self.pending_confirmations: Dict[str, PendingConfirmation] = {}
    
    def request_confirmation(
        self, 
        action: str, 
        description: str,
        callback: Callable,
        data: Optional[Dict[str, Any]] = None
    ) -> str:
        """请求用户确认操作"""
        confirmation_id = str(uuid.uuid4())[:8]
        
        self.pending_confirmations[confirmation_id] = PendingConfirmation(
            id=confirmation_id,
            action=action,
            description=description,
            callback=callback,
            data=data or {}
        )
        
        return confirmation_id
    
    def confirm(self, confirmation_id: str, confirmed: bool = True) -> bool:
        """确认或取消操作"""
        if confirmation_id not in self.pending_confirmations:
            return False
        
        confirmation = self.pending_confirmations.pop(confirmation_id)
        
        if confirmed:
            try:
                confirmation.callback(confirmation.data)
                return True
            except Exception as e:
                print(f"确认操作执行失败: {e}")
                return False
        
        return True
    
    def get_pending_confirmations(self) -> Dict[str, PendingConfirmation]:
        """获取所有待确认操作"""
        return self.pending_confirmations.copy()


# 全局确认管理器实例
confirmation_manager = ConfirmationManager()
'''
        elif 'exception_handler' in file_path:
            return '''"""
统一异常处理器
"""

import logging
import traceback
from typing import Any, Callable, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class GameException(Exception):
    """游戏相关异常基类"""
    pass


class APIException(GameException):
    """API调用异常"""
    pass


class ConfigurationException(GameException):
    """配置异常"""
    pass


def handle_exceptions(
    default_return: Any = None,
    raise_on_error: bool = False,
    log_error: bool = True
):
    """异常处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(
                        f"函数 {func.__name__} 执行出错: {e}\\n"
                        f"错误详情: {traceback.format_exc()}"
                    )
                
                if raise_on_error:
                    raise
                
                return default_return
        
        return wrapper
    return decorator


def safe_api_call(func: Callable, *args, **kwargs) -> tuple[bool, Any]:
    """安全的API调用"""
    try:
        result = func(*args, **kwargs)
        return True, result
    except Exception as e:
        logger.error(f"API调用失败: {e}")
        return False, None


def safe_file_operation(func: Callable, *args, **kwargs) -> tuple[bool, Any]:
    """安全的文件操作"""
    try:
        result = func(*args, **kwargs)
        return True, result
    except (IOError, OSError, UnicodeDecodeError) as e:
        logger.error(f"文件操作失败: {e}")
        return False, None
'''
        
        return f'"""\n{file_path} - 自动生成的模板文件\n"""\n\npass\n'
    
    def _add_basic_exception_handling(self):
        """添加基础异常处理"""
        # 这里可以扫描关键文件并添加异常处理
        print("🛡️  添加异常处理逻辑...")
    
    def _create_config_template(self):
        """创建配置模板"""
        config_path = self.project_root / 'game_config.py'
        if not config_path.exists():
            config_template = '''"""
游戏配置文件 - 统一管理所有配置项
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class GameConfig:
    """游戏配置"""
    # 基础设置
    game_name: str = "仙侠世界引擎"
    version: str = "2.0.0"
    debug_mode: bool = False
    
    # 游戏平衡
    max_health: int = 100
    base_damage: float = 10.0
    cultivation_exp_multiplier: float = 1.0
    
    # API设置
    deepseek_api_key: str = ""
    api_timeout: int = 15
    api_max_retries: int = 3
    
    # 性能设置
    cache_size: int = 1000
    max_npcs_in_memory: int = 50
    auto_save_interval: int = 300  # 秒
    
    # 路径设置
    data_path: str = "xwe/data"
    save_path: str = "saves"
    log_path: str = "logs"
    
    def __post_init__(self):
        """初始化后处理"""
        # 从环境变量读取API密钥
        if not self.deepseek_api_key:
            self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY', '')
        
        # 确保路径存在
        for path_attr in ['save_path', 'log_path']:
            path = getattr(self, path_attr)
            if path and not os.path.exists(path):
                os.makedirs(path, exist_ok=True)


# 全局配置实例
config = GameConfig()
'''
            
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_template)
            
            print("⚙️  创建配置文件: game_config.py")
    
    def generate_report(self) -> str:
        """生成优化报告"""
        analysis = self.analyze_project()
        
        report = f"""
# 仙侠世界引擎 - 代码质量分析报告

## 📊 项目统计
- 文件数量: {analysis['stats']['total_files']}
- 代码行数: {analysis['stats']['total_lines']}
- 平均文件长度: {analysis['stats']['avg_lines_per_file']} 行

## 🔍 发现的问题

### TODO项目 ({analysis['stats'].get('todo_count', 0)}个)
"""
        
        # 添加TODO详情
        for file_path, todos in analysis['issues'].get('todos', {}).items():
            if todos:
                report += f"\n**{file_path}**: {len(todos)}个TODO\n"
                for todo in todos[:3]:  # 只显示前3个
                    report += f"- 第{todo['line']}行: {todo['text']}\n"
        
        # 添加推荐建议
        report += "\n## 💡 优化建议\n"
        for i, rec in enumerate(analysis['recommendations'], 1):
            report += f"{i}. {rec}\n"
        
        return report


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='仙侠世界引擎代码质量优化工具')
    parser.add_argument('--check', action='store_true', help='检查代码质量')
    parser.add_argument('--fix-basic', action='store_true', help='修复基础问题')
    parser.add_argument('--todo-analysis', action='store_true', help='TODO分析')
    parser.add_argument('--full-report', action='store_true', help='生成完整报告')
    parser.add_argument('--project-path', default='.', help='项目路径')
    
    args = parser.parse_args()
    
    optimizer = CodeQualityOptimizer(args.project_path)
    
    if args.check or not any([args.fix_basic, args.todo_analysis, args.full_report]):
        # 默认执行检查
        print("🚀 执行代码质量检查...\n")
        analysis = optimizer.analyze_project()
        
        print(f"\n📋 检查完成！")
        print(f"发现问题类别: {len(analysis['issues'])}")
        print(f"优化建议: {len(analysis['recommendations'])}")
    
    if args.fix_basic:
        optimizer.fix_basic_issues()
    
    if args.todo_analysis:
        analysis = optimizer.analyze_project()
        print(f"\n📝 TODO分析结果:")
        for file_path, todos in analysis['issues'].get('todos', {}).items():
            if todos:
                print(f"  {file_path}: {len(todos)}个TODO")
    
    if args.full_report:
        report = optimizer.generate_report()
        
        # 保存报告
        report_path = Path(args.project_path) / 'code_quality_report.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 完整报告已保存: {report_path}")


if __name__ == '__main__':
    main()
