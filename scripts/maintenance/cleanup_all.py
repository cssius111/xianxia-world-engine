#!/usr/bin/env python3
"""
综合清理脚本 - 一键清理和重构项目
"""

import os
import sys
from pathlib import Path

# 添加scripts目录到Python路径
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

# 导入清理和重构模块
from cleanup_duplicates import ProjectCleaner
from restructure_project import ProjectRestructurer


def main():
    """主函数"""
    project_root = "/path/to/xianxia_world_engine"

    print("=" * 70)
    print("🚀 仙侠世界引擎项目综合清理工具")
    print("=" * 70)
    print("\n本工具将执行以下操作：")
    print("1. 扫描并删除重复的JSON文件")
    print("2. 重新组织目录结构")
    print("3. 生成路径更新脚本")
    print("\n所有操作都会创建备份，可以随时恢复。")
    print("=" * 70)

    # 询问执行模式
    print("\n请选择执行模式：")
    print("1. 完整清理（推荐）- 删除重复文件并重构目录")
    print("2. 仅分析 - 生成报告但不执行任何操作")
    print("3. 仅清理重复 - 只删除重复文件")
    print("4. 仅重构目录 - 只重新组织目录结构")
    print("5. 退出")

    choice = input("\n请输入选择 (1-5): ").strip()

    if choice == "1":
        # 完整清理流程
        print("\n" + "=" * 70)
        print("📋 步骤 1/3: 清理重复文件")
        print("=" * 70)

        cleaner = ProjectCleaner(project_root)
        cleaner.find_json_duplicates()
        cleanup_plan = cleaner.generate_cleanup_plan()

        if cleanup_plan["delete_files"]:
            confirm = input(
                f"\n将删除 {len(cleanup_plan['delete_files'])} 个重复文件。继续？(y/n): "
            )
            if confirm.lower() == "y":
                cleaner.execute_cleanup(cleanup_plan, interactive=False)
            else:
                print("跳过文件删除")

        print("\n" + "=" * 70)
        print("📋 步骤 2/3: 重构目录结构")
        print("=" * 70)

        restructurer = ProjectRestructurer(project_root)
        restructurer.analyze_current_structure()
        restructurer.create_file_mapping()
        restructure_plan = restructurer.generate_restructure_plan()

        confirm = input(
            f"\n将移动 {restructure_plan['summary']['files_to_move']} 个文件。继续？(y/n): "
        )
        if confirm.lower() == "y":
            restructurer.execute_restructure(restructure_plan, dry_run=False)
        else:
            print("跳过目录重构")

        print("\n" + "=" * 70)
        print("📋 步骤 3/3: 生成路径更新脚本")
        print("=" * 70)

        restructurer.generate_path_update_script()
        print("\n✅ 清理完成！请运行 'python update_paths.py' 更新代码中的路径引用。")

    elif choice == "2":
        # 仅分析
        print("\n🔍 执行分析模式...")

        cleaner = ProjectCleaner(project_root)
        cleaner.find_json_duplicates()
        cleanup_plan = cleaner.generate_cleanup_plan()
        cleaner._generate_final_report([], [], cleanup_plan)

        restructurer = ProjectRestructurer(project_root)
        restructurer.analyze_current_structure()
        restructurer.create_file_mapping()
        restructure_plan = restructurer.generate_restructure_plan()
        restructurer.execute_restructure(restructure_plan, dry_run=True)

        print("\n✅ 分析完成！查看生成的报告文件了解详情。")

    elif choice == "3":
        # 仅清理重复
        print("\n🧹 执行重复文件清理...")
        cleaner = ProjectCleaner(project_root)
        cleaner.run(interactive=True)

    elif choice == "4":
        # 仅重构目录
        print("\n📁 执行目录重构...")
        restructurer = ProjectRestructurer(project_root)
        restructurer.analyze_current_structure()
        restructurer.create_file_mapping()
        plan = restructurer.generate_restructure_plan()
        restructurer.execute_restructure(plan, dry_run=False)
        restructurer.generate_path_update_script()

    else:
        print("\n👋 退出程序")
        return

    print("\n" + "=" * 70)
    print("💡 后续步骤建议：")
    print("1. 查看生成的报告文件")
    print("2. 手动合并需要合并的配置文件")
    print("3. 运行 update_paths.py 更新代码路径")
    print("4. 测试项目功能是否正常")
    print("5. 提交更改到版本控制系统")
    print("=" * 70)


if __name__ == "__main__":
    main()
