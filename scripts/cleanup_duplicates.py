#!/usr/bin/env python3
"""
智能项目清理脚本 - 用于清理仙侠世界引擎项目中的重复文件
"""

import difflib
import hashlib
import json
import os
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple


class ProjectCleaner:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.duplicate_groups = defaultdict(list)
        self.file_checksums = {}
        self.cleanup_report = {
            "scanned_files": 0,
            "duplicate_groups": 0,
            "files_to_delete": [],
            "space_to_free": 0,
            "warnings": [],
            "recommendations": [],
        }

    def calculate_checksum(self, file_path: Path) -> str:
        """计算文件的MD5校验和"""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            self.cleanup_report["warnings"].append(f"无法读取文件 {file_path}: {e}")
            return None

    def calculate_similarity(self, file1: Path, file2: Path) -> float:
        """计算两个文件的相似度（仅用于文本文件）"""
        try:
            with open(file1, "r", encoding="utf-8") as f1:
                content1 = f1.read()
            with open(file2, "r", encoding="utf-8") as f2:
                content2 = f2.read()

            # 使用difflib计算相似度
            similarity = difflib.SequenceMatcher(None, content1, content2).ratio()
            return similarity
        except Exception:
            return 0.0

    def find_json_duplicates(self):
        """查找所有JSON文件并分析重复"""
        print("🔍 扫描JSON文件...")
        json_files = []

        # 收集所有JSON文件
        for root, dirs, files in os.walk(self.project_root):
            # 跳过git目录和node_modules
            if ".git" in root or "node_modules" in root or "__pycache__" in root:
                continue

            for file in files:
                if file.endswith(".json"):
                    file_path = Path(root) / file
                    json_files.append(file_path)
                    self.cleanup_report["scanned_files"] += 1

        print(f"📊 找到 {len(json_files)} 个JSON文件")

        # 分析文件内容
        self._analyze_duplicate_content(json_files)

        # 分析嵌套目录问题
        self._analyze_nested_directories()

        # 分析同名文件
        self._analyze_same_name_files(json_files)

    def _analyze_duplicate_content(self, files: List[Path]):
        """分析文件内容的重复性"""
        print("\n🔍 分析文件内容...")

        # 按文件名分组
        name_groups = defaultdict(list)
        for file_path in files:
            base_name = file_path.stem  # 不含扩展名的文件名
            name_groups[base_name].append(file_path)

        # 分析每组同名文件
        for base_name, file_list in name_groups.items():
            if len(file_list) > 1:
                print(f"\n📄 分析 '{base_name}' 文件组 ({len(file_list)} 个文件)...")

                # 计算每个文件的大小和校验和
                file_info = []
                for file_path in file_list:
                    size = file_path.stat().st_size
                    checksum = self.calculate_checksum(file_path)
                    mtime = file_path.stat().st_mtime

                    file_info.append(
                        {
                            "path": file_path,
                            "size": size,
                            "checksum": checksum,
                            "mtime": mtime,
                            "relative_path": file_path.relative_to(self.project_root),
                        }
                    )

                # 按校验和分组
                checksum_groups = defaultdict(list)
                for info in file_info:
                    if info["checksum"]:
                        checksum_groups[info["checksum"]].append(info)

                # 记录完全相同的文件
                for checksum, group in checksum_groups.items():
                    if len(group) > 1:
                        self.duplicate_groups[f"{base_name}_{checksum[:8]}"] = group
                        self.cleanup_report["duplicate_groups"] += 1

                # 对于内容不同的同名文件，计算相似度
                if len(checksum_groups) > 1:
                    self._analyze_similar_files(base_name, file_info)

    def _analyze_similar_files(self, base_name: str, file_info: List[Dict]):
        """分析相似但不完全相同的文件"""
        print(f"  📊 分析 '{base_name}' 的不同版本...")

        # 找出最大和最新的文件
        largest = max(file_info, key=lambda x: x["size"])
        newest = max(file_info, key=lambda x: x["mtime"])

        recommendation = {
            "file_group": base_name,
            "files": [str(f["relative_path"]) for f in file_info],
            "suggested_keep": str(newest["relative_path"]),
            "reason": "最新修改时间",
            "largest_file": str(largest["relative_path"]),
            "size_difference": f"{max(f['size'] for f in file_info) - min(f['size'] for f in file_info)} bytes",
        }

        self.cleanup_report["recommendations"].append(recommendation)

    def _analyze_nested_directories(self):
        """分析嵌套的重复目录结构"""
        print("\n🔍 检查嵌套目录问题...")

        # 查找可疑的嵌套模式
        suspicious_patterns = [
            "data/restructured",
            "xwe/data/restructured",
            "xwe/data/refactored",
        ]

        for pattern in suspicious_patterns:
            pattern_path = self.project_root / pattern
            if pattern_path.exists():
                self.cleanup_report["warnings"].append(f"发现可疑的嵌套目录: {pattern}")

    def _analyze_same_name_files(self, files: List[Path]):
        """分析同名文件的分布"""
        print("\n🔍 分析同名文件分布...")

        name_locations = defaultdict(list)
        for file_path in files:
            name_locations[file_path.name].append(
                str(file_path.relative_to(self.project_root))
            )

        # 记录分散在多处的同名文件
        for filename, locations in name_locations.items():
            if len(locations) > 2:  # 超过2个位置
                self.cleanup_report["warnings"].append(
                    f"文件 '{filename}' 分散在 {len(locations)} 个位置"
                )

    def generate_cleanup_plan(self):
        """生成清理计划"""
        print("\n📋 生成清理计划...")

        cleanup_plan = {
            "delete_files": [],
            "merge_suggestions": [],
            "restructure_suggestions": [],
        }

        # 1. 标记完全重复的文件
        for group_name, duplicates in self.duplicate_groups.items():
            if len(duplicates) > 1:
                # 保留最新的文件
                keep = max(duplicates, key=lambda x: x["mtime"])
                for dup in duplicates:
                    if dup != keep:
                        cleanup_plan["delete_files"].append(
                            {
                                "file": str(dup["relative_path"]),
                                "reason": f"与 {keep['relative_path']} 完全相同",
                                "size": dup["size"],
                            }
                        )
                        self.cleanup_report["space_to_free"] += dup["size"]

        # 2. 建议合并相似文件
        cleanup_plan["merge_suggestions"] = [
            {
                "description": "合并多个restructured目录",
                "affected_dirs": [
                    "data/restructured",
                    "xwe/data/restructured",
                    "xwe/data/refactored",
                ],
                "suggested_location": "data/game_configs",
            }
        ]

        # 3. 重构建议
        cleanup_plan["restructure_suggestions"] = [
            "将所有游戏配置JSON文件统一放在 data/game_configs 目录",
            "将不同版本的配置文件（如combat_system_v2.json）改为使用版本控制系统管理",
            "删除空的JSON文件和测试文件",
            "为配置文件建立清晰的命名规范",
        ]

        return cleanup_plan

    def execute_cleanup(self, cleanup_plan: Dict, interactive: bool = True):
        """执行清理计划"""
        print("\n🧹 准备执行清理...")

        deleted_files = []
        skipped_files = []

        # 创建备份目录
        backup_dir = (
            self.project_root / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        if interactive:
            print(f"\n⚠️  将要删除 {len(cleanup_plan['delete_files'])} 个文件")
            print(f"💾 备份将保存在: {backup_dir}")

            response = input("\n是否继续？(y/n): ")
            if response.lower() != "y":
                print("❌ 清理已取消")
                return

        backup_dir.mkdir(exist_ok=True)

        # 执行文件删除
        for file_info in cleanup_plan["delete_files"]:
            file_path = self.project_root / file_info["file"]

            try:
                if interactive:
                    print(f"\n📄 文件: {file_info['file']}")
                    print(f"   原因: {file_info['reason']}")
                    print(f"   大小: {file_info['size']} bytes")
                    action = input("   删除此文件？(y/n/s跳过所有): ")

                    if action.lower() == "s":
                        interactive = False
                    elif action.lower() != "y":
                        skipped_files.append(file_info["file"])
                        continue

                # 备份文件
                backup_path = backup_dir / file_info["file"]
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_path)

                # 删除文件
                file_path.unlink()
                deleted_files.append(file_info["file"])
                print(f"   ✅ 已删除")

            except Exception as e:
                print(f"   ❌ 错误: {e}")
                self.cleanup_report["warnings"].append(f"无法删除 {file_info['file']}: {e}")

        # 生成清理报告
        self._generate_final_report(deleted_files, skipped_files, cleanup_plan)

    def _generate_final_report(
        self, deleted_files: List[str], skipped_files: List[str], cleanup_plan: Dict
    ):
        """生成最终清理报告"""
        report_path = (
            self.project_root
            / f"cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# 项目清理报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## 清理摘要\n\n")
            f.write(f"- 扫描文件数: {self.cleanup_report['scanned_files']}\n")
            f.write(f"- 发现重复组: {self.cleanup_report['duplicate_groups']}\n")
            f.write(f"- 删除文件数: {len(deleted_files)}\n")
            f.write(f"- 跳过文件数: {len(skipped_files)}\n")
            f.write(f"- 释放空间: {self.cleanup_report['space_to_free'] / 1024:.2f} KB\n\n")

            if deleted_files:
                f.write("## 已删除文件\n\n")
                for file in deleted_files:
                    f.write(f"- {file}\n")
                f.write("\n")

            if skipped_files:
                f.write("## 跳过的文件\n\n")
                for file in skipped_files:
                    f.write(f"- {file}\n")
                f.write("\n")

            if self.cleanup_report["warnings"]:
                f.write("## 警告\n\n")
                for warning in self.cleanup_report["warnings"]:
                    f.write(f"- ⚠️  {warning}\n")
                f.write("\n")

            if self.cleanup_report["recommendations"]:
                f.write("## 文件合并建议\n\n")
                for rec in self.cleanup_report["recommendations"]:
                    f.write(f"### {rec['file_group']}\n")
                    f.write(f"- 建议保留: `{rec['suggested_keep']}`\n")
                    f.write(f"- 原因: {rec['reason']}\n")
                    f.write(f"- 涉及文件:\n")
                    for file in rec["files"]:
                        f.write(f"  - {file}\n")
                    f.write("\n")

            if cleanup_plan["restructure_suggestions"]:
                f.write("## 项目重构建议\n\n")
                for suggestion in cleanup_plan["restructure_suggestions"]:
                    f.write(f"- {suggestion}\n")
                f.write("\n")

            f.write("## 下一步建议\n\n")
            f.write("1. 审查合并建议，手动合并相似但不完全相同的配置文件\n")
            f.write("2. 实施项目重构建议，建立更清晰的目录结构\n")
            f.write("3. 使用版本控制系统管理配置文件的不同版本\n")
            f.write("4. 建立文件命名和组织规范，避免未来出现类似问题\n")

        print(f"\n📄 清理报告已保存至: {report_path}")

    def run(self, interactive: bool = True):
        """运行清理流程"""
        print("🚀 开始项目清理分析...\n")

        # 1. 查找重复文件
        self.find_json_duplicates()

        # 2. 生成清理计划
        cleanup_plan = self.generate_cleanup_plan()

        # 3. 显示清理计划摘要
        print("\n📊 清理计划摘要:")
        print(f"  - 将删除 {len(cleanup_plan['delete_files'])} 个重复文件")
        print(f"  - 可释放空间: {self.cleanup_report['space_to_free'] / 1024:.2f} KB")
        print(f"  - 发现 {len(self.cleanup_report['warnings'])} 个潜在问题")

        # 4. 执行清理
        if cleanup_plan["delete_files"]:
            self.execute_cleanup(cleanup_plan, interactive)
        else:
            print("\n✨ 未发现需要删除的完全重复文件")

            # 仍然生成报告，包含建议
            self._generate_final_report([], [], cleanup_plan)

        print("\n✅ 清理完成！")


def main():
    """主函数"""
    # 获取项目根目录
    project_root = "/path/to/xianxia_world_engine"

    print("=" * 60)
    print("🧹 仙侠世界引擎项目清理工具")
    print("=" * 60)

    # 创建清理器实例
    cleaner = ProjectCleaner(project_root)

    # 运行清理
    cleaner.run(interactive=True)

    print("\n💡 提示: 所有被删除的文件都已备份，如需恢复请查看backup目录")


if __name__ == "__main__":
    main()
