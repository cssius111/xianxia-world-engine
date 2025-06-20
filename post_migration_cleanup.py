#!/usr/bin/env python3
"""迁移后的项目清理脚本 - 清理冗余文件和临时内容"""

import json
import os
import shutil
from pathlib import Path


def post_migration_cleanup():
    """执行迁移后的清理工作"""

    project_root = Path.cwd()

    # 清理统计
    stats = {"files_deleted": 0, "dirs_deleted": 0, "space_freed": 0, "cache_cleared": 0}

    print("=" * 70)
    print("仙侠世界引擎 - 迁移后清理工具")
    print("=" * 70)

    # 1. 删除迁移相关的临时文件
    print("\n[1/8] 清理迁移相关文件...")
    migration_files = [
        "check_migration_status.py",
        "post_migration_cleanup.py",  # 运行后可删除自己
        "run_v2_tests.sh",
        "analyze_project.py",
        "cleanup.py",
        "project_analysis_report.json",
    ]

    for file in migration_files:
        file_path = project_root / file
        if file_path.exists() and file != "post_migration_cleanup.py":  # 不删除自己
            size = file_path.stat().st_size
            print(f"  删除: {file} ({size} bytes)")
            file_path.unlink()
            stats["files_deleted"] += 1
            stats["space_freed"] += size

    # 2. 清理迁移报告目录
    print("\n[2/8] 清理迁移报告...")
    migration_reports_dir = project_root / "migration_reports"
    if migration_reports_dir.exists():
        size = sum(f.stat().st_size for f in migration_reports_dir.rglob("*") if f.is_file())
        print(f"  删除目录: migration_reports/ ({size} bytes)")
        shutil.rmtree(migration_reports_dir)
        stats["dirs_deleted"] += 1
        stats["space_freed"] += size

    # 3. 清理所有MyPy相关文件
    print("\n[3/8] 清理MyPy相关文件...")
    mypy_patterns = ["*.mypy*", "*mypy*.py", "MYPY*.md", "fix_*.py", "*_fix_*.py", "*_fixer.py"]

    mypy_files_found = []
    for pattern in mypy_patterns:
        mypy_files_found.extend(project_root.glob(pattern))

    # 排除虚拟环境中的文件
    mypy_files_found = [f for f in mypy_files_found if ".venv" not in f.parts]

    for file_path in mypy_files_found:
        if file_path.is_file():
            size = file_path.stat().st_size
            print(f"  删除: {file_path.name} ({size} bytes)")
            file_path.unlink()
            stats["files_deleted"] += 1
            stats["space_freed"] += size

    # 4. 清理日志和输出文件
    print("\n[4/8] 清理日志和输出...")

    # 清理logs目录但保留目录本身
    logs_dir = project_root / "logs"
    if logs_dir.exists():
        for file in logs_dir.rglob("*"):
            if file.is_file():
                size = file.stat().st_size
                print(f"  删除: {file.relative_to(logs_dir)} ({size} bytes)")
                file.unlink()
                stats["files_deleted"] += 1
                stats["space_freed"] += size

    # 清理output目录但保留目录本身
    output_dir = project_root / "output"
    if output_dir.exists():
        for file in output_dir.rglob("*"):
            if file.is_file():
                size = file.stat().st_size
                print(f"  删除: {file.relative_to(output_dir)} ({size} bytes)")
                file.unlink()
                stats["files_deleted"] += 1
                stats["space_freed"] += size

    # 清理根目录的日志文件
    for log_file in project_root.glob("*.log"):
        size = log_file.stat().st_size
        print(f"  删除: {log_file.name} ({size} bytes)")
        log_file.unlink()
        stats["files_deleted"] += 1
        stats["space_freed"] += size

    # 5. 清理Python缓存
    print("\n[5/8] 清理Python缓存...")
    cache_patterns = ["__pycache__", ".pytest_cache", ".mypy_cache"]

    for pattern in cache_patterns:
        for cache_dir in project_root.rglob(pattern):
            if ".venv" not in cache_dir.parts:  # 排除虚拟环境
                size = sum(f.stat().st_size for f in cache_dir.rglob("*") if f.is_file())
                print(f"  删除: {cache_dir.relative_to(project_root)} ({size} bytes)")
                shutil.rmtree(cache_dir)
                stats["cache_cleared"] += 1
                stats["space_freed"] += size

    # 清理.pyc文件
    for pyc_file in project_root.rglob("*.pyc"):
        if ".venv" not in pyc_file.parts:
            size = pyc_file.stat().st_size
            pyc_file.unlink()
            stats["files_deleted"] += 1
            stats["space_freed"] += size

    # 6. 清理系统文件
    print("\n[6/8] 清理系统文件...")
    system_files = [".DS_Store", "Thumbs.db", "desktop.ini"]

    for sys_file in system_files:
        for file in project_root.rglob(sys_file):
            size = file.stat().st_size
            print(f"  删除: {file.relative_to(project_root)} ({size} bytes)")
            file.unlink()
            stats["files_deleted"] += 1
            stats["space_freed"] += size

    # 7. 清理可能的冗余目录
    print("\n[7/8] 检查冗余目录...")
    potentially_redundant = ["analytics", "feedback", "patches", "lore", "delete"]

    for dir_name in potentially_redundant:
        dir_path = project_root / dir_name
        if dir_path.exists():
            # 检查是否为空或只有少量文件
            files = list(dir_path.rglob("*"))
            file_count = sum(1 for f in files if f.is_file())

            if file_count == 0 or (file_count == 1 and files[0].name == ".DS_Store"):
                print(f"  删除空目录: {dir_name}/")
                shutil.rmtree(dir_path)
                stats["dirs_deleted"] += 1
            else:
                print(f"  保留: {dir_name}/ (包含 {file_count} 个文件)")

    # 8. 整理templates目录（如果需要）
    print("\n[8/8] 检查templates目录...")
    templates_dir = project_root / "templates"
    templates_enhanced_dir = project_root / "templates_enhanced"

    if templates_dir.exists() and templates_enhanced_dir.exists():
        print("  发现两个模板目录，建议手动合并")
    elif templates_enhanced_dir.exists() and not templates_dir.exists():
        print(f"  重命名: templates_enhanced/ -> templates/")
        templates_enhanced_dir.rename(templates_dir)

    # 创建必要的空目录
    necessary_dirs = ["logs", "output", "saves"]
    for dir_name in necessary_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            dir_path.mkdir()
            print(f"\n创建必要目录: {dir_name}/")

    # 更新.gitignore
    print("\n更新.gitignore...")
    gitignore_path = project_root / ".gitignore"
    gitignore_rules = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.project
.pydevproject

# Testing
.pytest_cache/
.mypy_cache/
.coverage
htmlcov/
.tox/
.cache
nosetests.xml
coverage.xml
*.cover

# Logs
logs/
*.log
log/

# Output files
output/
*.html
!templates/*.html
!templates_enhanced/*.html

# OS
.DS_Store
Thumbs.db
desktop.ini

# Project specific
migration_reports/
project_analysis_report.json
game_log.html

# Temporary files
*.tmp
*.bak
*.swp
*~
"""

    with open(gitignore_path, "w") as f:
        f.write(gitignore_rules.strip())

    # 显示清理统计
    print("\n" + "=" * 70)
    print("清理完成！")
    print(f"\n统计信息:")
    print(f"  删除文件: {stats['files_deleted']} 个")
    print(f"  删除目录: {stats['dirs_deleted']} 个")
    print(f"  清理缓存: {stats['cache_cleared']} 个")
    print(f"  释放空间: {stats['space_freed'] / 1024 / 1024:.2f} MB")

    # 保存清理报告
    report = {
        "timestamp": str(Path.cwd()),
        "stats": stats,
        "actions_taken": [
            "删除迁移相关文件",
            "清理迁移报告",
            "删除MyPy相关文件",
            "清理日志和输出",
            "删除Python缓存",
            "清理系统文件",
            "检查冗余目录",
            "更新.gitignore",
        ],
    }

    report_path = project_root / "cleanup_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n清理报告已保存到: {report_path}")

    # 后续建议
    print("\n后续建议:")
    print("1. 运行 'git status' 查看更改")
    print("2. 运行 'pytest tests/v2/' 测试新架构")
    print("3. 检查 xwe/ 目录是否还有需要迁移的内容")
    print("4. 考虑是否删除旧的 xwe/ 目录（如果迁移完成）")
    print("5. 运行 'poetry install' 确保依赖正确")
    print("6. 提交清理后的代码到Git")


def main():
    """主函数"""
    try:
        # 检查是否在项目根目录
        if not Path("pyproject.toml").exists():
            print("错误：请在项目根目录运行此脚本")
            return

        print("此脚本将清理迁移后的临时文件和缓存")
        print("建议先提交当前代码以便需要时回滚")

        response = input("\n确定要继续吗？(y/n): ")
        if response.lower() == "y":
            post_migration_cleanup()
        else:
            print("已取消清理")

    except KeyboardInterrupt:
        print("\n\n清理被中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
