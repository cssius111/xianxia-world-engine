#!/usr/bin/env python3
"""检查xwe目录中未迁移的文件"""

from pathlib import Path


def check_unmigrated_files():
    """检查哪些文件还没有从xwe迁移到xwe_v2"""

    xwe_dir = Path("xwe")
    xwe_v2_dir = Path("xwe_v2")

    if not xwe_dir.exists() or not xwe_v2_dir.exists():
        print("错误：xwe或xwe_v2目录不存在")
        return

    print("=" * 70)
    print("检查未迁移的文件")
    print("=" * 70)

    # 收集所有文件
    xwe_files = set()
    for file in xwe_dir.rglob("*"):
        if file.is_file() and "__pycache__" not in str(file) and not file.name.endswith(".pyc"):
            relative_path = file.relative_to(xwe_dir)
            xwe_files.add(str(relative_path))

    # 检查在xwe_v2中对应的文件
    migrated_count = 0
    unmigrated_files = []

    for file_path in sorted(xwe_files):
        # 检查直接对应的路径
        v2_path = xwe_v2_dir / file_path

        # 检查可能的重映射路径
        path_mappings = {
            "features/": "plugins/",
            "core/": "domain/",
            "services/": "application/services/",
            "engine/": "engine/",
            "data/": "data/",
            "world/": "domain/world/",
            "models/": "domain/models/",
            "npc/": "domain/npc/",
            "systems/": "domain/systems/",
            "utils/": "infrastructure/utils/",
            "metrics/": "infrastructure/metrics/",
        }

        migrated = False

        # 检查是否已迁移
        if v2_path.exists():
            migrated = True
        else:
            # 尝试映射路径
            for old_prefix, new_prefix in path_mappings.items():
                if file_path.startswith(old_prefix.rstrip("/")):
                    new_path = file_path.replace(old_prefix.rstrip("/"), new_prefix.rstrip("/"), 1)
                    if (xwe_v2_dir / new_path).exists():
                        migrated = True
                        break

        if migrated:
            migrated_count += 1
        else:
            unmigrated_files.append(file_path)

    # 显示结果
    print(f"\n总文件数: {len(xwe_files)}")
    print(f"已迁移: {migrated_count}")
    print(f"未迁移: {len(unmigrated_files)}")

    if unmigrated_files:
        print("\n未迁移的文件:")

        # 按目录分组
        by_directory = {}
        for file in unmigrated_files:
            dir_path = str(Path(file).parent)
            if dir_path not in by_directory:
                by_directory[dir_path] = []
            by_directory[dir_path].append(Path(file).name)

        for directory, files in sorted(by_directory.items()):
            print(f"\n  {directory}/")
            for file in sorted(files):
                print(f"    - {file}")

    # 检查可能需要特殊处理的文件
    print("\n\n需要特殊注意的文件类型:")

    special_files = {
        "配置文件": [
            f for f in unmigrated_files if f.endswith((".json", ".yaml", ".yml", ".ini", ".toml"))
        ],
        "文档文件": [f for f in unmigrated_files if f.endswith((".md", ".rst", ".txt"))],
        "测试文件": [f for f in unmigrated_files if "test" in f or f.startswith("tests/")],
        "数据文件": [f for f in unmigrated_files if f.startswith("data/")],
        "示例文件": [f for f in unmigrated_files if "example" in f or f.startswith("examples/")],
    }

    for file_type, files in special_files.items():
        if files:
            print(f"\n{file_type}: {len(files)} 个")
            for file in files[:5]:  # 只显示前5个
                print(f"  - {file}")
            if len(files) > 5:
                print(f"  ... 还有 {len(files) - 5} 个")


if __name__ == "__main__":
    check_unmigrated_files()
