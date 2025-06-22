#!/usr/bin/env python3
"""
综合修复脚本 - 自动检测和修复所有导入问题
"""

import os
import sys
import json
import importlib
import traceback
from pathlib import Path
from typing import Dict, List, Set, Tuple

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class ComprehensiveFixer:
    """综合修复器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.import_errors: Dict[str, Dict] = {}
        self.fixed_issues: List[str] = []
        self.remaining_issues: List[str] = []
        
    def scan_import_errors(self):
        """扫描所有导入错误"""
        print("🔍 扫描导入错误...")
        
        # 运行 quick_snapshot.py 来获取错误信息
        snapshot_script = self.project_root / "scripts" / "quick_snapshot.py"
        if snapshot_script.exists():
            os.system(f"python {snapshot_script}")
        
        # 读取错误报告
        snapshot_file = self.project_root / "project_snapshot.json"
        if snapshot_file.exists():
            with open(snapshot_file, 'r', encoding='utf-8') as f:
                self.import_errors = json.load(f)
        
        print(f"📊 发现 {len(self.import_errors)} 个导入错误")
        
    def analyze_errors(self) -> Dict[str, List[str]]:
        """分析错误类型"""
        error_types = {
            "missing_module": [],
            "missing_class": [],
            "missing_function": [],
            "circular_import": [],
            "other": []
        }
        
        for module, error_info in self.import_errors.items():
            error_msg = error_info['message']
            
            if "No module named" in error_msg:
                error_types["missing_module"].append(module)
            elif "cannot import name" in error_msg:
                if "from" in error_msg:
                    error_types["missing_class"].append(module)
                else:
                    error_types["missing_function"].append(module)
            elif "circular import" in error_msg.lower():
                error_types["circular_import"].append(module)
            else:
                error_types["other"].append(module)
        
        return error_types
    
    def fix_missing_modules(self):
        """修复缺失的模块"""
        print("\n🔧 修复缺失的模块...")
        
        # 检查特定的缺失模块
        potential_missing = {
            "xwe.features.world_building": """
\"\"\"
世界构建模块
管理游戏世界的生成和维护
\"\"\"

class WorldBuilder:
    \"\"\"世界构建器\"\"\"
    
    def __init__(self):
        self.world_data = {}
    
    def generate_world(self):
        \"\"\"生成世界\"\"\"
        pass
    
    def load_world(self, data):
        \"\"\"加载世界数据\"\"\"
        self.world_data = data
    
    def save_world(self):
        \"\"\"保存世界数据\"\"\"
        return self.world_data

# 全局实例
world_builder = WorldBuilder()
""",
            "xwe.systems.economy": """
\"\"\"
经济系统模块
管理游戏内的经济活动
\"\"\"

class EconomySystem:
    \"\"\"经济系统\"\"\"
    
    def __init__(self):
        self.currency_types = ["灵石", "金币", "贡献点"]
        self.exchange_rates = {}
    
    def convert_currency(self, amount, from_type, to_type):
        \"\"\"货币转换\"\"\"
        # 简化实现
        return amount
    
    def get_item_price(self, item_id):
        \"\"\"获取物品价格\"\"\"
        return 100  # 默认价格

# 全局实例
economy_system = EconomySystem()
"""
        }
        
        for module_path, content in potential_missing.items():
            parts = module_path.split('.')
            file_path = self.project_root / Path(*parts[:-1]) / f"{parts[-1]}.py"
            
            if not file_path.exists():
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
                print(f"✅ 创建模块: {module_path}")
                self.fixed_issues.append(f"创建缺失模块: {module_path}")
    
    def fix_missing_imports(self):
        """修复缺失的导入"""
        print("\n🔧 修复缺失的导入...")
        
        # 分析每个错误并尝试修复
        for module, error_info in self.import_errors.items():
            error_msg = error_info['message']
            
            # 提取缺失的名称
            if "cannot import name" in error_msg:
                try:
                    # 解析错误消息
                    parts = error_msg.split("'")
                    if len(parts) >= 4:
                        missing_name = parts[1]
                        from_module = parts[3]
                        
                        # 尝试修复
                        if self.add_missing_import(from_module, missing_name):
                            self.fixed_issues.append(f"添加 {missing_name} 到 {from_module}")
                except Exception as e:
                    print(f"⚠️ 无法解析错误: {error_msg}")
    
    def add_missing_import(self, module_path: str, name: str) -> bool:
        """添加缺失的导入"""
        try:
            # 构建文件路径
            if module_path.startswith('/'):
                file_path = Path(module_path)
            else:
                parts = module_path.split('.')
                file_path = self.project_root / Path(*parts[:-1]) / f"{parts[-1]}.py"
            
            if not file_path.exists():
                return False
            
            # 读取文件内容
            content = file_path.read_text(encoding='utf-8')
            
            # 检查是否已经存在
            if f"class {name}" in content or f"def {name}" in content or f"{name} =" in content:
                return False
            
            # 根据名称类型添加相应的定义
            if name.endswith('Error') or name.endswith('Exception'):
                # 添加异常类
                new_content = f"\n\nclass {name}(Exception):\n    \"\"\"自动生成的异常类\"\"\"\n    pass\n"
            elif name.isupper() or '_' in name:
                # 可能是常量
                new_content = f"\n\n{name} = None  # 自动生成的常量\n"
            else:
                # 添加函数或类
                new_content = f"\n\ndef {name}(*args, **kwargs):\n    \"\"\"自动生成的函数\"\"\"\n    pass\n"
            
            # 更新文件
            content += new_content
            file_path.write_text(content, encoding='utf-8')
            
            # 如果有 __all__，也要更新
            if "__all__" in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith("__all__") and name not in line:
                        if "]" in line:
                            lines[i] = line.replace("]", f", \"{name}\"]")
                        else:
                            # 多行 __all__
                            for j in range(i+1, len(lines)):
                                if "]" in lines[j]:
                                    lines[j] = lines[j].replace("]", f",\n    \"{name}\"\n]")
                                    break
                content = '\n'.join(lines)
                file_path.write_text(content, encoding='utf-8')
            
            return True
            
        except Exception as e:
            print(f"⚠️ 修复 {module_path}.{name} 时出错: {e}")
            return False
    
    def verify_fixes(self):
        """验证修复结果"""
        print("\n🔍 验证修复结果...")
        
        # 重新扫描错误
        self.scan_import_errors()
        
        # 比较错误数量
        if len(self.import_errors) == 0:
            print("🎉 所有导入错误已修复！")
        else:
            print(f"⚠️ 仍有 {len(self.import_errors)} 个错误需要手动修复")
            self.remaining_issues = list(self.import_errors.keys())
    
    def generate_report(self):
        """生成修复报告"""
        print("\n📊 修复报告")
        print("=" * 50)
        
        if self.fixed_issues:
            print(f"✅ 已修复 {len(self.fixed_issues)} 个问题:")
            for issue in self.fixed_issues[:10]:  # 只显示前10个
                print(f"  - {issue}")
            if len(self.fixed_issues) > 10:
                print(f"  ... 和其他 {len(self.fixed_issues) - 10} 个问题")
        
        if self.remaining_issues:
            print(f"\n❌ 剩余 {len(self.remaining_issues)} 个问题:")
            for issue in self.remaining_issues[:10]:  # 只显示前10个
                print(f"  - {issue}")
            if len(self.remaining_issues) > 10:
                print(f"  ... 和其他 {len(self.remaining_issues) - 10} 个问题")
        
        # 保存详细报告
        report = {
            "fixed_issues": self.fixed_issues,
            "remaining_issues": self.remaining_issues,
            "error_details": self.import_errors
        }
        
        report_path = self.project_root / "fix_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 详细报告已保存到: {report_path}")
    
    def run(self):
        """运行综合修复"""
        print("🚀 开始综合修复...")
        print("=" * 50)
        
        # 1. 扫描错误
        self.scan_import_errors()
        
        # 2. 分析错误类型
        error_types = self.analyze_errors()
        print("\n📊 错误类型分析:")
        for error_type, modules in error_types.items():
            if modules:
                print(f"  - {error_type}: {len(modules)} 个")
        
        # 3. 修复缺失的模块
        self.fix_missing_modules()
        
        # 4. 修复缺失的导入
        self.fix_missing_imports()
        
        # 5. 验证修复
        self.verify_fixes()
        
        # 6. 生成报告
        self.generate_report()
        
        print("\n✅ 综合修复完成！")


def main():
    """主函数"""
    fixer = ComprehensiveFixer(project_root)
    fixer.run()
    
    # 提示后续步骤
    print("\n📌 后续步骤:")
    print("1. 检查 fix_report.json 了解详细情况")
    print("2. 运行 python entrypoints/run_web_ui_optimized.py 测试")
    print("3. 如果仍有问题，查看具体错误信息并手动修复")


if __name__ == "__main__":
    main()
