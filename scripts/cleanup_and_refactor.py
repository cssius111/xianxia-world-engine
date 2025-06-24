#!/usr/bin/env python3
"""
仙侠世界引擎 - 项目清理和重构脚本
彻底清理重复文件，统一使用xwe作为核心引擎，只保留Web UI
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

class ProjectRefactorer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / f"backup_refactor_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.actions_log = []
        
    def analyze_project(self):
        """分析项目结构，找出所有问题"""
        print("🔍 分析项目结构...\n")
        
        issues = {
            "duplicate_modules": [],
            "terminal_files": [],
            "misplaced_files": [],
            "redundant_data": [],
            "obsolete_files": []
        }
        
        # 1. 找出重复的核心模块
        duplicate_pairs = [
            ("/core", "/xwe/core", "核心模块重复"),
            ("/event_system", "/xwe/events", "事件系统重复"),
            ("/data", "/xwe/data", "数据文件重复"),
        ]
        
        for old_path, new_path, desc in duplicate_pairs:
            old_full = self.project_root / old_path.lstrip('/')
            new_full = self.project_root / new_path.lstrip('/')
            if old_full.exists() and new_full.exists():
                issues["duplicate_modules"].append({
                    "old": str(old_full),
                    "new": str(new_full),
                    "description": desc
                })
        
        # 2. 找出终端相关文件（需要删除）
        terminal_files = [
            "main_menu.py",
            "start_game.py",  # 这个调用终端版本
            "ui/",  # 终端UI目录
            "core/player_initializer.py",  # 终端版本的初始化
            "core/state_manager.py",  # 终端版本的状态管理
        ]
        
        for file_path in terminal_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                issues["terminal_files"].append(str(full_path))
        
        # 3. 检查错误放置的文件
        root_files = [f for f in self.project_root.iterdir() if f.is_file() and f.suffix == '.py']
        for file in root_files:
            if file.name not in ['run.py', 'setup.py', 'setup.sh']:
                issues["misplaced_files"].append(str(file))
        
        # 4. 检查重复的数据文件
        if (self.project_root / "data").exists() and (self.project_root / "xwe/data").exists():
            # 比较两个data目录的内容
            old_data_files = set((self.project_root / "data").rglob("*.json"))
            new_data_files = set((self.project_root / "xwe/data").rglob("*.json"))
            
            for old_file in old_data_files:
                rel_path = old_file.relative_to(self.project_root / "data")
                new_file = self.project_root / "xwe/data" / rel_path
                if new_file.exists():
                    issues["redundant_data"].append({
                        "old": str(old_file),
                        "new": str(new_file),
                        "name": old_file.name
                    })
        
        # 5. 找出过时的文件
        obsolete_patterns = [
            "*_old.py",
            "*_backup.py",
            "cleanup_project.py",  # 旧的清理脚本
            "deepseek/",  # 如果有单独的deepseek目录
        ]
        
        for pattern in obsolete_patterns:
            for file in self.project_root.rglob(pattern):
                if not any(skip in str(file) for skip in ['.git', '__pycache__', 'backup']):
                    issues["obsolete_files"].append(str(file))
        
        # 打印分析结果
        self._print_analysis_results(issues)
        return issues
    
    def _print_analysis_results(self, issues: Dict):
        """打印分析结果"""
        print("=" * 60)
        print("📊 项目分析结果")
        print("=" * 60)
        
        total_issues = sum(len(v) if isinstance(v, list) else len(v) for v in issues.values())
        print(f"\n发现 {total_issues} 个问题需要处理：\n")
        
        if issues["duplicate_modules"]:
            print("❌ 重复的模块：")
            for dup in issues["duplicate_modules"]:
                print(f"  - {dup['description']}")
                print(f"    旧: {Path(dup['old']).relative_to(self.project_root)}")
                print(f"    新: {Path(dup['new']).relative_to(self.project_root)}")
        
        if issues["terminal_files"]:
            print(f"\n❌ 终端相关文件 ({len(issues['terminal_files'])} 个):")
            for file in issues["terminal_files"]:
                print(f"  - {Path(file).relative_to(self.project_root)}")
        
        if issues["misplaced_files"]:
            print(f"\n⚠️  根目录下的Python文件 ({len(issues['misplaced_files'])} 个):")
            for file in issues["misplaced_files"]:
                print(f"  - {Path(file).name}")
        
        if issues["redundant_data"]:
            print(f"\n❌ 重复的数据文件 ({len(issues['redundant_data'])} 个)")
        
        if issues["obsolete_files"]:
            print(f"\n🗑️  过时的文件 ({len(issues['obsolete_files'])} 个)")
    
    def create_refactor_plan(self, issues: Dict) -> Dict:
        """创建重构计划"""
        print("\n\n📋 创建重构计划...")
        
        plan = {
            "backup_files": [],
            "delete_files": [],
            "move_files": [],
            "update_imports": [],
            "create_files": [],
            "summary": {
                "files_to_delete": 0,
                "files_to_move": 0,
                "files_to_update": 0,
                "files_to_create": 0
            }
        }
        
        # 1. 删除重复的模块（保留xwe中的版本）
        for dup in issues["duplicate_modules"]:
            plan["delete_files"].append(dup["old"])
            plan["backup_files"].append(dup["old"])
        
        # 2. 删除终端相关文件
        for file in issues["terminal_files"]:
            plan["delete_files"].append(file)
            plan["backup_files"].append(file)
        
        # 3. 移动错误放置的文件
        for file in issues["misplaced_files"]:
            file_path = Path(file)
            if file_path.name in ['game_config.py']:
                # 移到config目录
                plan["move_files"].append({
                    "from": file,
                    "to": str(self.project_root / "config" / file_path.name)
                })
            else:
                # 其他文件标记为删除
                plan["delete_files"].append(file)
        
        # 4. 删除重复的数据文件
        for dup_data in issues["redundant_data"]:
            plan["delete_files"].append(dup_data["old"])
        
        # 5. 删除过时的文件
        for file in issues["obsolete_files"]:
            plan["delete_files"].append(file)
        
        # 6. 创建新的启动脚本
        plan["create_files"].append({
            "path": "start_web.py",
            "content": self._generate_new_launcher()
        })
        
        # 7. 更新run.py使其使用xwe
        plan["update_imports"].append({
            "file": "run.py",
            "updates": [
                ("from core.", "from xwe.core."),
                ("from event_system", "from xwe.events"),
                ("data/", "xwe/data/"),
            ]
        })
        
        # 更新统计
        plan["summary"]["files_to_delete"] = len(plan["delete_files"])
        plan["summary"]["files_to_move"] = len(plan["move_files"])
        plan["summary"]["files_to_update"] = len(plan["update_imports"])
        plan["summary"]["files_to_create"] = len(plan["create_files"])
        
        return plan
    
    def _generate_new_launcher(self) -> str:
        """生成新的Web启动脚本"""
        return '''#!/usr/bin/env python3
"""
仙侠世界引擎 - Web UI 启动器
"""

import os
import sys
import webbrowser
from pathlib import Path
from time import sleep

# 确保项目根目录在Python路径中
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def check_dependencies():
    """检查依赖"""
    try:
        import flask
        import flask_cors
        from dotenv import load_dotenv
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🎮 仙侠世界引擎 - Web版")
    print("=" * 60)
    
    if not check_dependencies():
        return
    
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    # 设置环境变量
    os.environ['FLASK_ENV'] = 'development'
    port = int(os.getenv('PORT', 5001))
    
    print(f"🌐 游戏地址: http://localhost:{port}")
    print("🎯 正在启动服务器...")
    print("=" * 60)
    
    # 尝试自动打开浏览器
    def open_browser():
        sleep(1.5)  # 等待服务器启动
        webbrowser.open(f'http://localhost:{port}')
    
    # 在后台打开浏览器
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # 启动Flask应用
    try:
        from run import app
        app.run(host="0.0.0.0", port=port, debug=True)
    except KeyboardInterrupt:
        print("\\n\\n👋 游戏服务器已停止")

if __name__ == "__main__":
    main()
'''
    
    def execute_plan(self, plan: Dict, dry_run: bool = True):
        """执行重构计划"""
        if dry_run:
            print("\n\n🔍 试运行模式 - 不会实际修改文件")
        else:
            print("\n\n🚀 执行重构计划...")
            # 创建备份目录
            self.backup_dir.mkdir(exist_ok=True)
            print(f"💾 备份目录: {self.backup_dir}")
        
        # 1. 备份文件
        if not dry_run and plan["backup_files"]:
            print("\n📦 备份文件...")
            for file_path in plan["backup_files"]:
                if Path(file_path).exists():
                    self._backup_file(file_path)
        
        # 2. 删除文件
        print(f"\n🗑️  删除文件 ({len(plan['delete_files'])} 个):")
        for i, file_path in enumerate(plan["delete_files"]):
            if i < 10:  # 只显示前10个
                rel_path = Path(file_path).relative_to(self.project_root)
                print(f"  - {rel_path}")
            
            if not dry_run and Path(file_path).exists():
                if Path(file_path).is_dir():
                    shutil.rmtree(file_path)
                else:
                    Path(file_path).unlink()
                self.actions_log.append(f"删除: {rel_path}")
        
        if len(plan["delete_files"]) > 10:
            print(f"  ... 还有 {len(plan['delete_files']) - 10} 个文件")
        
        # 3. 移动文件
        if plan["move_files"]:
            print(f"\n📂 移动文件 ({len(plan['move_files'])} 个):")
            for move_info in plan["move_files"]:
                from_path = Path(move_info["from"])
                to_path = Path(move_info["to"])
                print(f"  - {from_path.name} → {to_path.parent.name}/")
                
                if not dry_run:
                    to_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(from_path), str(to_path))
                    self.actions_log.append(f"移动: {from_path} → {to_path}")
        
        # 4. 创建新文件
        if plan["create_files"]:
            print(f"\n✨ 创建新文件 ({len(plan['create_files'])} 个):")
            for file_info in plan["create_files"]:
                file_path = self.project_root / file_info["path"]
                print(f"  - {file_info['path']}")
                
                if not dry_run:
                    file_path.write_text(file_info["content"], encoding='utf-8')
                    # 设置为可执行
                    os.chmod(file_path, 0o755)
                    self.actions_log.append(f"创建: {file_info['path']}")
        
        # 5. 更新导入
        if plan["update_imports"]:
            print(f"\n🔧 更新导入 ({len(plan['update_imports'])} 个文件):")
            for update_info in plan["update_imports"]:
                print(f"  - {update_info['file']}")
                
                if not dry_run:
                    self._update_imports(update_info["file"], update_info["updates"])
        
        # 6. 生成报告
        self._generate_report(plan, dry_run)
    
    def _backup_file(self, file_path: str):
        """备份文件或目录"""
        source = Path(file_path)
        if not source.exists():
            return
        
        rel_path = source.relative_to(self.project_root)
        backup_path = self.backup_dir / rel_path
        
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        if source.is_dir():
            shutil.copytree(source, backup_path)
        else:
            shutil.copy2(source, backup_path)
    
    def _update_imports(self, file_path: str, updates: List[tuple]):
        """更新文件中的导入语句"""
        full_path = self.project_root / file_path
        if not full_path.exists():
            return
        
        content = full_path.read_text(encoding='utf-8')
        original_content = content
        
        for old_pattern, new_pattern in updates:
            content = content.replace(old_pattern, new_pattern)
        
        if content != original_content:
            full_path.write_text(content, encoding='utf-8')
            self.actions_log.append(f"更新导入: {file_path}")
    
    def _generate_report(self, plan: Dict, dry_run: bool):
        """生成重构报告"""
        report_name = f"refactor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        if dry_run:
            report_name = f"dry_run_{report_name}"
        
        report_path = self.project_root / report_name
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 项目重构报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"模式: {'试运行' if dry_run else '实际执行'}\n\n")
            
            f.write("## 重构摘要\n\n")
            f.write(f"- 删除文件: {plan['summary']['files_to_delete']} 个\n")
            f.write(f"- 移动文件: {plan['summary']['files_to_move']} 个\n")
            f.write(f"- 更新文件: {plan['summary']['files_to_update']} 个\n")
            f.write(f"- 创建文件: {plan['summary']['files_to_create']} 个\n\n")
            
            f.write("## 主要改动\n\n")
            f.write("1. **统一使用xwe作为核心引擎**\n")
            f.write("   - 删除了重复的 `/core`、`/event_system`、`/data` 目录\n")
            f.write("   - 所有代码现在统一引用 `xwe` 模块\n\n")
            
            f.write("2. **删除终端版本**\n")
            f.write("   - 移除了所有终端UI相关代码\n")
            f.write("   - 只保留Web UI作为唯一界面\n\n")
            
            f.write("3. **清理项目结构**\n")
            f.write("   - 整理了根目录下的文件\n")
            f.write("   - 删除了过时和重复的文件\n\n")
            
            if not dry_run and self.actions_log:
                f.write("## 执行日志\n\n")
                for action in self.actions_log[-20:]:  # 最近20个操作
                    f.write(f"- {action}\n")
                if len(self.actions_log) > 20:
                    f.write(f"\n... 还有 {len(self.actions_log) - 20} 个操作\n")
            
            f.write("\n## 后续步骤\n\n")
            f.write("1. 运行 `python start_web.py` 启动Web版游戏\n")
            f.write("2. 测试所有功能是否正常\n")
            f.write("3. 如果发现问题，可以从备份目录恢复文件\n")
            f.write("4. 确认无误后，提交到版本控制\n")
            
            f.write("\n## 新的项目结构\n\n")
            f.write("```\n")
            f.write("xianxia_world_engine/\n")
            f.write("├── xwe/              # 核心引擎（唯一）\n")
            f.write("│   ├── core/         # 核心功能\n")
            f.write("│   ├── data/         # 游戏数据\n")
            f.write("│   ├── events/       # 事件系统\n")
            f.write("│   └── ...\n")
            f.write("├── templates/        # Web模板\n")
            f.write("├── static/           # 静态资源\n")
            f.write("├── api/              # API接口\n")
            f.write("├── config/           # 配置文件\n")
            f.write("├── scripts/          # 工具脚本\n")
            f.write("├── run.py            # Flask应用\n")
            f.write("└── start_web.py      # 启动脚本\n")
            f.write("```\n")
        
        print(f"\n\n📄 报告已保存至: {report_path}")
    
    def validate_refactor(self):
        """验证重构结果"""
        print("\n\n✅ 验证重构结果...")
        
        issues = []
        
        # 检查是否还有重复的目录
        duplicate_dirs = [
            ("core", "xwe/core"),
            ("event_system", "xwe/events"),
            ("data", "xwe/data")
        ]
        
        for old_dir, new_dir in duplicate_dirs:
            if (self.project_root / old_dir).exists():
                issues.append(f"❌ {old_dir} 目录仍然存在")
        
        # 检查终端文件是否已删除
        terminal_files = ["main_menu.py", "ui/"]
        for file in terminal_files:
            if (self.project_root / file).exists():
                issues.append(f"❌ 终端文件 {file} 仍然存在")
        
        # 检查新文件是否创建
        if not (self.project_root / "start_web.py").exists():
            issues.append("❌ start_web.py 未创建")
        
        if issues:
            print("\n发现以下问题：")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("\n✨ 重构验证通过！项目结构已优化。")
        
        return len(issues) == 0


def main():
    """主函数"""
    project_root = "/Users/chenpinle/Desktop/杂/pythonProject/xianxia_world_engine"
    
    print("=" * 60)
    print("🛠️  仙侠世界引擎 - 项目重构工具")
    print("=" * 60)
    print("\n本工具将：")
    print("1. 删除重复的模块（统一使用xwe）")
    print("2. 删除所有终端相关代码")
    print("3. 清理和优化项目结构")
    print("4. 只保留Web UI作为唯一界面")
    print("=" * 60)
    
    refactorer = ProjectRefactorer(project_root)
    
    # 1. 分析项目
    issues = refactorer.analyze_project()
    
    # 2. 创建重构计划
    plan = refactorer.create_refactor_plan(issues)
    
    # 3. 询问执行模式
    print("\n\n请选择执行模式：")
    print("1. 试运行（查看将要执行的操作）")
    print("2. 执行重构（会创建备份）")
    print("3. 退出")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == "1":
        refactorer.execute_plan(plan, dry_run=True)
    elif choice == "2":
        confirm = input("\n⚠️  确定要执行重构吗？所有改动都会备份。(yes/no): ")
        if confirm.lower() == "yes":
            refactorer.execute_plan(plan, dry_run=False)
            refactorer.validate_refactor()
        else:
            print("❌ 操作已取消")
    else:
        print("👋 退出程序")


if __name__ == "__main__":
    main()
