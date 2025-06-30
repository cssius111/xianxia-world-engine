#!/usr/bin/env python3
"""
修仙世界引擎 - 项目清理脚本
安全地清理冗余文件并整理项目结构
"""

import os
import shutil
import datetime
import json
from pathlib import Path

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

class ProjectCleaner:
    def __init__(self, project_root):
        self.root = Path(project_root)
        self.backup_dir = self.root / f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.dry_run = True
        self.files_to_delete = []
        self.dirs_to_delete = []
        self.files_to_move = {}
        
    def analyze_project(self):
        """分析项目结构，找出需要清理的文件"""
        print("\n📊 分析项目结构...")
        
        # 临时文件
        temp_files = [
            'fix_e2e.sh',
            'patch1_e2e_full.diff',
            'patch2_move_legacy.diff',
            'test_quick.py',
            'verify_e2e.py',
            'generated_characters.jsonl',
        ]
        
        # 重复的测试脚本（保留enhanced版本）
        duplicate_test_scripts = [
            'run-e2e-tests.sh',
            'run-all-e2e-tests.sh',
            'test-e2e-verify.sh',
            'test_character_creation.sh',
            'run_e2e_test_verification.sh',
            'run-test.sh',
            'quick-test.sh',
        ]
        
        # 缓存目录
        cache_dirs = [
            '__pycache__',
            '.pytest_cache',
            'playwright-report',
        ]
        
        # 检查临时文件
        for file in temp_files:
            path = self.root / file
            if path.exists():
                self.files_to_delete.append(path)
                
        # 检查重复的测试脚本
        for file in duplicate_test_scripts:
            path = self.root / file
            if path.exists():
                self.files_to_delete.append(path)
                
        # 递归查找所有缓存目录
        for cache_dir in cache_dirs:
            for path in self.root.rglob(cache_dir):
                if path.is_dir():
                    self.dirs_to_delete.append(path)
                    
        # 查找所有.pyc文件
        for pyc_file in self.root.rglob('*.pyc'):
            self.files_to_delete.append(pyc_file)
            
        # 检查重复的核心模块
        duplicate_modules = {
            'core': 'xwe/core',
            'event_system': 'xwe/events',
            'data': 'xwe/data',
        }
        
        for old_module, new_module in duplicate_modules.items():
            old_path = self.root / old_module
            new_path = self.root / new_module
            if old_path.exists() and new_path.exists():
                self.dirs_to_delete.append(old_path)
                print_warning(f"发现重复模块: {old_module} (将使用 {new_module})")
                
    def create_backup(self):
        """创建备份"""
        print(f"\n📦 创建备份到: {self.backup_dir}")
        
        if not self.dry_run:
            self.backup_dir.mkdir(exist_ok=True)
            
            # 备份将要删除的文件
            for file in self.files_to_delete:
                if file.exists():
                    relative_path = file.relative_to(self.root)
                    backup_path = self.backup_dir / relative_path
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file, backup_path)
                    
            # 备份将要删除的目录
            for dir in self.dirs_to_delete:
                if dir.exists():
                    relative_path = dir.relative_to(self.root)
                    backup_path = self.backup_dir / relative_path
                    shutil.copytree(dir, backup_path, dirs_exist_ok=True)
                    
            print_success("备份完成")
        else:
            print_info("（演示模式：跳过备份）")
            
    def clean_logs(self):
        """清理旧日志文件（保留最近7天）"""
        print("\n🗄️ 清理日志文件...")
        
        logs_dir = self.root / 'logs'
        if logs_dir.exists():
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=7)
            
            for log_file in logs_dir.glob('*.log'):
                # 跳过当前使用的日志
                if log_file.name == 'app.log':
                    continue
                    
                mtime = datetime.datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff_date:
                    self.files_to_delete.append(log_file)
                    
    def execute_cleanup(self):
        """执行清理操作"""
        print("\n🧹 执行清理...")
        
        # 删除文件
        deleted_files = 0
        for file in self.files_to_delete:
            if file.exists():
                if not self.dry_run:
                    file.unlink()
                deleted_files += 1
                print(f"  删除文件: {file.relative_to(self.root)}")
                
        # 删除目录
        deleted_dirs = 0
        for dir in sorted(self.dirs_to_delete, reverse=True):  # 反向排序确保先删除子目录
            if dir.exists():
                if not self.dry_run:
                    shutil.rmtree(dir)
                deleted_dirs += 1
                print(f"  删除目录: {dir.relative_to(self.root)}")
                
        print(f"\n总计: 删除 {deleted_files} 个文件, {deleted_dirs} 个目录")
        
    def update_imports(self):
        """更新代码中的导入路径"""
        print("\n🔄 更新导入路径...")
        
        replacements = {
            'from xwe.core.': 'from xwe.core.',
            'import xwe.core.': 'import xwe.core.',
            'from xwe.events': 'from xwe.events',
            'import xwe.events': 'import xwe.events',
            '"xwe/data/': '"xwe/data/',
            "'xwe/data/": "'xwe/data/",
        }
        
        # 查找所有Python文件
        python_files = list(self.root.rglob('*.py'))
        updated_files = 0
        
        for py_file in python_files:
            # 跳过备份目录和虚拟环境
            if 'backup_' in str(py_file) or 'venv' in str(py_file):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8')
                original_content = content
                
                for old, new in replacements.items():
                    content = content.replace(old, new)
                    
                if content != original_content:
                    if not self.dry_run:
                        py_file.write_text(content, encoding='utf-8')
                    updated_files += 1
                    print(f"  更新: {py_file.relative_to(self.root)}")
                    
            except Exception as e:
                print_warning(f"无法处理文件 {py_file}: {e}")
                
        print(f"更新了 {updated_files} 个文件")
        
    def generate_report(self):
        """生成清理报告"""
        report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'files_deleted': [str(f.relative_to(self.root)) for f in self.files_to_delete],
            'dirs_deleted': [str(d.relative_to(self.root)) for d in self.dirs_to_delete],
            'backup_location': str(self.backup_dir) if not self.dry_run else None,
        }
        
        report_file = self.root / 'cleanup_report.json'
        if not self.dry_run:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
                
        return report
        
    def run(self, dry_run=True):
        """运行清理流程"""
        self.dry_run = dry_run
        
        print("=" * 60)
        print("🧹 修仙世界引擎 - 项目清理工具")
        print("=" * 60)
        
        if self.dry_run:
            print_warning("当前为演示模式，不会实际删除文件")
        else:
            print_warning("⚠️  警告：将实际删除文件！")
            
        # 执行分析
        self.analyze_project()
        self.clean_logs()
        
        # 显示将要清理的内容
        print(f"\n📋 将要清理的内容:")
        print(f"  - 文件: {len(self.files_to_delete)} 个")
        print(f"  - 目录: {len(self.dirs_to_delete)} 个")
        
        if not self.dry_run:
            # 确认操作
            response = input("\n确定要继续吗？(yes/no): ")
            if response.lower() != 'yes':
                print_error("操作已取消")
                return
                
        # 执行清理
        if not self.dry_run:
            self.create_backup()
        self.execute_cleanup()
        self.update_imports()
        
        # 生成报告
        report = self.generate_report()
        
        print("\n" + "=" * 60)
        print_success("清理完成！")
        
        if not self.dry_run:
            print(f"\n📁 备份位置: {self.backup_dir}")
            print("📄 清理报告: cleanup_report.json")
            print("\n下一步建议:")
            print("1. 运行测试确保功能正常: pytest")
            print("2. 启动服务检查: python run.py")
            print("3. 如无问题，可以删除备份目录")
        else:
            print("\n💡 提示: 使用 --execute 参数来实际执行清理")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='清理修仙世界引擎项目')
    parser.add_argument('--execute', action='store_true', help='实际执行清理（默认为演示模式）')
    parser.add_argument('--path', default='.', help='项目根目录路径')
    
    args = parser.parse_args()
    
    # 确认项目路径
    project_root = Path(args.path).resolve()
    if not (project_root / 'run.py').exists():
        print_error(f"错误：在 {project_root} 未找到 run.py，请确认项目路径")
        return
        
    cleaner = ProjectCleaner(project_root)
    cleaner.run(dry_run=not args.execute)

if __name__ == '__main__':
    main()
