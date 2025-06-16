#!/usr/bin/env python3
# @dev_only
"""
项目结构重组脚本
- 保留 entrypoints/run_web_ui_optimized.py 为主入口
- 整理测试、文档、脚本等文件到合理目录
- 支持 dry-run 模式预览更改
"""

import os
import shutil
import glob
import argparse
from pathlib import Path
from datetime import datetime

class ProjectRestructure:
    def __init__(self, project_root, dry_run=True):
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.actions = []
        
    def log_action(self, action_type, source, destination=None):
        """记录操作"""
        if destination:
            self.actions.append(f"{action_type}: {source} -> {destination}")
        else:
            self.actions.append(f"{action_type}: {source}")
            
    def ensure_dir(self, path):
        """确保目录存在"""
        dir_path = self.project_root / path
        if not dir_path.exists():
            self.log_action("CREATE_DIR", path)
            if not self.dry_run:
                dir_path.mkdir(parents=True, exist_ok=True)
                
    def move_file(self, source, destination):
        """移动文件"""
        src_path = self.project_root / source
        dst_path = self.project_root / destination
        
        if src_path.exists():
            self.log_action("MOVE", source, destination)
            if not self.dry_run:
                # 确保目标目录存在
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src_path), str(dst_path))
                
    def delete_file(self, path):
        """删除文件"""
        file_path = self.project_root / path
        if file_path.exists():
            self.log_action("DELETE", path)
            if not self.dry_run:
                if file_path.is_file():
                    file_path.unlink()
                else:
                    shutil.rmtree(str(file_path))
                    
    def restructure(self):
        """执行重构"""
        print(f"{'[DRY RUN] ' if self.dry_run else ''}开始重构项目...")
        
        # 1. 创建目录结构
        directories = [
            "archive/deprecated/entrypoints",
            "archive/backups",
            "tests/unit",
            "tests/web_ui",
            "scripts/tools",
            "docs/progress",
            "docs/guides",
            "output",
        ]
        
        for directory in directories:
            self.ensure_dir(directory)
            
        # 2. 移动废弃的入口文件
        deprecated_entrypoints = [
            "main.py",
            "run_game.py",
            "run_optimized_game.py",
            "run_web_ui.py",
            "start_game.sh"
        ]
        
        for entry in deprecated_entrypoints:
            if (self.project_root / entry).exists():
                self.move_file(entry, f"archive/deprecated/entrypoints/{entry}")
                
        # 3. 移动测试文件
        test_files = glob.glob(str(self.project_root / "test_*.py"))
        for test_file in test_files:
            filename = os.path.basename(test_file)
            # 根据文件名分类
            if "web" in filename.lower() or "ui" in filename.lower():
                self.move_file(filename, f"tests/web_ui/{filename}")
            else:
                self.move_file(filename, f"tests/unit/{filename}")
                
        # 4. 移动工具脚本
        tool_scripts = [
            "optimize.sh",
            "deep_optimize.sh",
            "verify_phase4.py",
            "verify_system.py", 
            "update_imports.py",
            "apply_refactor.py",
            "cleanup_ui.sh",
            "deploy_optimizations.sh",
            "run_tests.sh",
            "dedupe.py",
            "function_analyzer.py",
            "quality_optimizer.py",
            "quick_todo_fixer.py",
            "update_service_integration.py"
        ]
        
        for script in tool_scripts:
            if (self.project_root / script).exists():
                self.move_file(script, f"scripts/tools/{script}")
                
        # 5. 整理文档
        progress_docs = [
            "PHASE3_COMPLETE.md",
            "PHASE4_BATCH1_SUMMARY.md", 
            "PHASE4_BATCH2_PLAN.md",
            "REFACTOR_PROGRESS.md",
            "REFACTOR_APPLY_REPORT.md",
            "code_quality_report.md",
            "refactor_plan_1__fuzzy_parse.md",
            "refactor_plan_2_process_command.md",
            "refactor_plan_3_validate_with_error.md"
        ]
        
        for doc in progress_docs:
            if (self.project_root / doc).exists():
                self.move_file(doc, f"docs/progress/{doc}")
                
        guide_docs = [
            "FEATURES_GUIDE.md",
            "TODO_LIST.md",
            "AGENTS.md"
        ]
        
        for doc in guide_docs:
            if (self.project_root / doc).exists():
                self.move_file(doc, f"docs/guides/{doc}")
                
        # 6. 移动输出文件
        output_files = [
            "game_log.html",
            "test_output.html",
            "xianxia_game.html"
        ]
        
        for file in output_files:
            if (self.project_root / file).exists():
                self.move_file(file, f"output/{file}")
                
        # 移动所有 .save 文件
        save_files = glob.glob(str(self.project_root / "*.save"))
        for save_file in save_files:
            filename = os.path.basename(save_file)
            self.move_file(filename, f"archive/backups/{filename}")
            
        # 移动所有 .json 文件（除了配置文件）
        json_files = glob.glob(str(self.project_root / "*.json"))
        for json_file in json_files:
            filename = os.path.basename(json_file)
            if filename not in ["package.json", "tsconfig.json"]:
                self.move_file(filename, f"archive/backups/{filename}")
                
        # 7. 清理 __pycache__ 文件夹
        pycache_dirs = list(self.project_root.rglob("__pycache__"))
        for pycache in pycache_dirs:
            self.delete_file(str(pycache.relative_to(self.project_root)))
            
        # 清理 .pyc 文件
        pyc_files = list(self.project_root.rglob("*.pyc"))
        for pyc in pyc_files:
            self.delete_file(str(pyc.relative_to(self.project_root)))
            
        # 8. 移动示例和集成文件到 scripts/
        integration_files = [
            "api_integration_example.py",
            "demo_ai_features.py", 
            "phase4_integration_example.py",
            "service_integration_example.py",
            "service_layer_example.py",
            "optimization_test_script.py"
        ]
        
        for file in integration_files:
            if (self.project_root / file).exists():
                self.move_file(file, f"scripts/{file}")
                
        # 9. 更新 README.md
        self.update_readme()
        
        # 显示操作总结
        self.print_summary()
        
    def update_readme(self):
        """更新 README.md"""
        readme_path = self.project_root / "README.md"
        if not readme_path.exists():
            return
            
        self.log_action("UPDATE", "README.md")
        
        if self.dry_run:
            return
            
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 添加重构说明
        restructure_note = """
## 项目结构说明（重构于 {date}）

### 主入口
- `entrypoints/run_web_ui_optimized.py` - **主入口文件**，运行 Flask Web UI

### 目录结构
- `xwe/` - 核心游戏引擎模块
- `templates/` - Flask 模板文件
- `static/` - 静态资源文件
- `scripts/` - 辅助脚本和示例代码
  - `tools/` - 项目工具脚本
- `tests/` - 测试文件
  - `unit/` - 单元测试
  - `web_ui/` - Web UI 相关测试
- `docs/` - 项目文档
  - `guides/` - 使用指南
  - `progress/` - 开发进度记录
- `archive/` - 归档文件
  - `deprecated/entrypoints/` - 废弃的入口文件
  - `backups/` - 备份文件
- `output/` - 输出文件（HTML报告等）
- `plugins/` - 插件系统
- `mods/` - 游戏模组

### 废弃入口说明
以下入口文件已归档至 `archive/deprecated/entrypoints/`：
- `main.py` - 原命令行入口
- `run_game.py` - 原游戏运行脚本
- `run_web_ui.py` - 原Web UI入口
- 其他旧版入口文件

---

""".format(date=datetime.now().strftime("%Y-%m-%d"))
        
        # 在合适位置插入说明
        if "## 项目结构说明" not in content:
            # 在第一个 ## 之前插入
            lines = content.split('\n')
            insert_index = 0
            for i, line in enumerate(lines):
                if line.startswith('## ') and i > 0:
                    insert_index = i
                    break
            
            if insert_index > 0:
                lines.insert(insert_index, restructure_note)
                content = '\n'.join(lines)
            else:
                content += '\n' + restructure_note
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    def print_summary(self):
        """打印操作总结"""
        print(f"\n{'='*60}")
        print(f"重构操作总结 {'(DRY RUN)' if self.dry_run else '(已执行)'}")
        print(f"{'='*60}")
        
        # 按操作类型分组
        creates = [a for a in self.actions if a.startswith("CREATE_DIR")]
        moves = [a for a in self.actions if a.startswith("MOVE")]
        deletes = [a for a in self.actions if a.startswith("DELETE")]
        updates = [a for a in self.actions if a.startswith("UPDATE")]
        
        if creates:
            print(f"\n创建目录 ({len(creates)} 个):")
            for action in creates[:10]:  # 只显示前10个
                print(f"  {action}")
            if len(creates) > 10:
                print(f"  ... 还有 {len(creates) - 10} 个")
                
        if moves:
            print(f"\n移动文件 ({len(moves)} 个):")
            for action in moves[:20]:  # 显示前20个
                print(f"  {action}")
            if len(moves) > 20:
                print(f"  ... 还有 {len(moves) - 20} 个")
                
        if deletes:
            print(f"\n删除文件 ({len(deletes)} 个):")
            for action in deletes[:10]:
                print(f"  {action}")
            if len(deletes) > 10:
                print(f"  ... 还有 {len(deletes) - 10} 个")
                
        if updates:
            print(f"\n更新文件 ({len(updates)} 个):")
            for action in updates:
                print(f"  {action}")
                
        print(f"\n总计: {len(self.actions)} 个操作")
        
        if self.dry_run:
            print("\n这是 DRY RUN 模式，没有实际执行任何操作。")
            print("使用 --execute 参数来真正执行重构。")
        else:
            print("\n重构完成！")

def main():
    parser = argparse.ArgumentParser(description="仙侠世界引擎项目重构工具")
    parser.add_argument(
        "--execute", 
        action="store_true", 
        help="执行重构（默认为 dry-run 模式）"
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="项目根目录路径（默认为当前目录）"
    )
    
    args = parser.parse_args()
    
    # 确认项目路径
    project_root = Path(args.project_root).resolve()
    if not (project_root / "entrypoints" / "run_web_ui_optimized.py").exists():
        print(f"错误：在 {project_root} 找不到 entrypoints/run_web_ui_optimized.py")
        print("请确保在正确的项目根目录运行此脚本。")
        return
        
    print(f"项目路径: {project_root}")
    
    # 执行重构
    restructure = ProjectRestructure(
        project_root=project_root,
        dry_run=not args.execute
    )
    
    restructure.restructure()

if __name__ == "__main__":
    main()
