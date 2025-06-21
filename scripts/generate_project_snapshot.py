#!/usr/bin/env python3
"""
项目快照生成器 - 扫描项目中的所有模块并记录导入错误
用于AI分析和修复任务规划
"""

import pkgutil
import importlib
import pathlib
import sys
import traceback
import json
from datetime import datetime
from typing import Dict, List, Any

class ProjectSnapshotGenerator:
    def __init__(self, root_path: pathlib.Path):
        self.root = root_path
        self.results = {}
        self.stats = {
            "total_modules": 0,
            "success_imports": 0,
            "failed_imports": 0,
            "error_types": {}
        }
        
    def scan_project(self) -> Dict[str, Any]:
        """扫描项目中的所有Python模块"""
        # 将项目根目录添加到Python路径
        sys.path.insert(0, str(self.root))
        
        print(f"🔍 开始扫描项目: {self.root}")
        print("-" * 50)
        
        # 遍历所有模块
        for mod_info in pkgutil.walk_packages([str(self.root)], prefix=""):
            self.stats["total_modules"] += 1
            module_name = mod_info.name
            
            # 跳过测试文件和临时文件
            if any(skip in module_name for skip in ['__pycache__', '.pyc', 'test_', '_test']):
                continue
                
            try:
                # 尝试导入模块
                importlib.import_module(module_name)
                self.stats["success_imports"] += 1
                print(f"✅ {module_name}")
                
            except Exception as e:
                self.stats["failed_imports"] += 1
                error_type = type(e).__name__
                
                # 统计错误类型
                if error_type not in self.stats["error_types"]:
                    self.stats["error_types"][error_type] = 0
                self.stats["error_types"][error_type] += 1
                
                # 记录错误详情
                self.results[module_name] = {
                    "error_type": error_type,
                    "error_message": str(e),
                    "traceback_lines": traceback.format_exc().splitlines()[-5:],
                    "file_path": self._find_module_file(module_name),
                    "missing_dependencies": self._extract_missing_deps(str(e))
                }
                
                print(f"❌ {module_name} - {error_type}: {str(e)[:50]}...")
        
        return self._generate_report()
    
    def _find_module_file(self, module_name: str) -> str:
        """查找模块对应的文件路径"""
        parts = module_name.split('.')
        possible_paths = [
            self.root / pathlib.Path(*parts).with_suffix('.py'),
            self.root / pathlib.Path(*parts) / '__init__.py'
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path.relative_to(self.root))
        return "unknown"
    
    def _extract_missing_deps(self, error_msg: str) -> List[str]:
        """从错误信息中提取缺失的依赖"""
        missing_deps = []
        
        # 常见的导入错误模式
        patterns = [
            "No module named '([^']+)'",
            "cannot import name '([^']+)'",
            "Failed to import ([^ ]+)"
        ]
        
        import re
        for pattern in patterns:
            matches = re.findall(pattern, error_msg)
            missing_deps.extend(matches)
            
        return list(set(missing_deps))
    
    def _generate_report(self) -> Dict[str, Any]:
        """生成完整的报告"""
        return {
            "metadata": {
                "scan_time": datetime.now().isoformat(),
                "project_root": str(self.root),
                "python_version": sys.version,
                "total_modules": self.stats["total_modules"],
                "success_imports": self.stats["success_imports"],
                "failed_imports": self.stats["failed_imports"]
            },
            "error_summary": {
                "by_type": self.stats["error_types"],
                "most_common_errors": self._get_most_common_errors()
            },
            "failed_modules": self.results,
            "dependency_analysis": self._analyze_dependencies()
        }
    
    def _get_most_common_errors(self) -> List[Dict[str, Any]]:
        """获取最常见的错误"""
        error_counts = {}
        for module_data in self.results.values():
            error = module_data["error_message"]
            # 简化错误消息用于分组
            simplified = error.split("'")[1] if "'" in error else error[:50]
            if simplified not in error_counts:
                error_counts[simplified] = {"count": 0, "modules": []}
            error_counts[simplified]["count"] += 1
            
        # 排序并返回前10个
        sorted_errors = sorted(
            error_counts.items(), 
            key=lambda x: x[1]["count"], 
            reverse=True
        )[:10]
        
        return [
            {"error": err, "count": data["count"]} 
            for err, data in sorted_errors
        ]
    
    def _analyze_dependencies(self) -> Dict[str, Any]:
        """分析缺失的依赖"""
        all_missing_deps = {}
        
        for module_name, data in self.results.items():
            for dep in data.get("missing_dependencies", []):
                if dep not in all_missing_deps:
                    all_missing_deps[dep] = []
                all_missing_deps[dep].append(module_name)
        
        # 按影响的模块数量排序
        sorted_deps = sorted(
            all_missing_deps.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        
        return {
            "missing_packages": dict(sorted_deps),
            "priority_installs": [dep for dep, _ in sorted_deps[:10]]
        }
    
    def save_report(self, report: Dict[str, Any], output_path: pathlib.Path):
        """保存报告到JSON文件"""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 50)
        print(f"📊 扫描完成！")
        print(f"📁 报告已保存到: {output_path}")
        print(f"📈 统计信息:")
        print(f"   - 总模块数: {report['metadata']['total_modules']}")
        print(f"   - 成功导入: {report['metadata']['success_imports']}")
        print(f"   - 失败导入: {report['metadata']['failed_imports']}")
        print(f"   - 错误类型: {len(report['error_summary']['by_type'])}")
        print(f"   - 缺失依赖: {len(report['dependency_analysis']['missing_packages'])}")
        

def main():
    """主函数"""
    # 获取项目根目录（脚本所在目录的上一级）
    script_dir = pathlib.Path(__file__).resolve().parent
    project_root = script_dir.parent
    
    # 创建快照生成器
    generator = ProjectSnapshotGenerator(project_root)
    
    # 扫描项目
    report = generator.scan_project()
    
    # 保存报告
    output_path = project_root / "project_snapshot.json"
    generator.save_report(report, output_path)
    
    # 可选：同时保存带时间戳的版本
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamped_path = project_root / f"snapshots/snapshot_{timestamp}.json"
    if not timestamped_path.parent.exists():
        timestamped_path.parent.mkdir(parents=True)
    generator.save_report(report, timestamped_path)
    
    return report


if __name__ == "__main__":
    main()
