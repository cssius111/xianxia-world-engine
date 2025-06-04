#!/usr/bin/env python3
"""
文件迁移脚本 - 整理 xianxia_world_engine 项目结构
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


class ProjectMigrator:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.tests_dir = self.project_root / "tests"
        self.delete_dir = self.project_root / "delete"
        self.migration_log = []

    def setup_directories(self):
        """创建必要的目录结构"""
        # 测试目录结构
        dirs_to_create = [
            self.tests_dir,
            self.tests_dir / "unit",
            self.tests_dir / "integration",
            self.tests_dir / "scripts",
            self.tests_dir / "fixes",
            self.tests_dir / "verify",
            self.delete_dir
        ]

        for dir_path in dirs_to_create:
            dir_path.mkdir(exist_ok=True)

        # 创建删除目录说明文件
        readme_content = """# 归档删除目录

此目录包含已经废弃或不再需要的文件。
所有文件内容已被清空，仅保留文件名作为历史记录。

归档时间：{}
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        (self.delete_dir / "_README.md").write_text(readme_content, encoding='utf-8')

    def move_to_tests(self, files_to_move):
        """移动文件到tests目录"""
        for src, dest_subdir in files_to_move:
            src_path = self.project_root / src
            if src_path.exists():
                dest_path = self.tests_dir / dest_subdir / src_path.name
                try:
                    shutil.move(str(src_path), str(dest_path))
                    self.migration_log.append(f"✓ 移动: {src} → tests/{dest_subdir}/{src_path.name}")
                except Exception as e:
                    self.migration_log.append(f"✗ 失败: {src} - {str(e)}")

    def soft_delete(self, files_to_delete):
        """软删除文件（清空内容后移动到delete目录）"""
        for file_name in files_to_delete:
            src_path = self.project_root / file_name
            if src_path.exists():
                try:
                    # 清空文件内容
                    src_path.write_text("", encoding='utf-8')
                    # 移动到delete目录
                    dest_path = self.delete_dir / src_path.name
                    shutil.move(str(src_path), str(dest_path))
                    self.migration_log.append(f"✓ 归档: {file_name} → delete/{src_path.name}")
                except Exception as e:
                    self.migration_log.append(f"✗ 失败: {file_name} - {str(e)}")

    def move_scripts_tests(self):
        """移动scripts目录下的测试文件"""
        scripts_dir = self.project_root / "scripts"
        if scripts_dir.exists():
            test_patterns = ["test_", "demo_", "verify_"]
            for file_path in scripts_dir.glob("*.py"):
                if any(file_path.name.startswith(pattern) for pattern in test_patterns):
                    dest_path = self.tests_dir / "scripts" / file_path.name
                    try:
                        shutil.move(str(file_path), str(dest_path))
                        self.migration_log.append(f"✓ 移动: scripts/{file_path.name} → tests/scripts/{file_path.name}")
                    except Exception as e:
                        self.migration_log.append(f"✗ 失败: scripts/{file_path.name} - {str(e)}")

    def create_env_example(self):
        """创建.env.example文件"""
        env_content = """# DeepSeek API配置
DEEPSEEK_API_KEY=sk-your-api-key-here

# OpenAI API配置（可选）
OPENAI_API_KEY=sk-your-openai-key-here

# 游戏配置
GAME_DEBUG_MODE=false
GAME_AUTO_SAVE=true
GAME_SAVE_INTERVAL=300

# NLP配置
NLP_PROVIDER=deepseek  # 可选: deepseek, openai, local
NLP_CACHE_ENABLED=true
NLP_TIMEOUT=30

# 开发配置
LOG_LEVEL=INFO
LOG_FILE=game.log
"""
        env_path = self.project_root / ".env"
        env_path.write_text(env_content, encoding='utf-8')
        self.migration_log.append("✓ 创建: .env")

    def generate_report(self):
        """生成迁移报告"""
        report = f"""
# 文件迁移报告

迁移时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
项目路径：{self.project_root}

## 操作日志

"""
        for log in self.migration_log:
            report += f"- {log}\n"

        report += "\n## 新的项目结构\n\n"
        report += self.generate_tree_structure()

        report_path = self.project_root / "MIGRATION_REPORT.md"
        report_path.write_text(report, encoding='utf-8')
        return report

    def generate_tree_structure(self):
        """生成项目结构树"""
        tree = """```
xianxia_world_engine/
├── xwe/                # 游戏核心
├── tests/              # 测试文件
│   ├── unit/          # 单元测试
│   ├── integration/   # 集成测试
│   ├── scripts/       # 测试脚本
│   ├── fixes/         # 修复脚本
│   └── verify/        # 验证脚本
├── delete/            # 归档文件
├── docs/              # 项目文档
├── saves/             # 游戏存档
├── main.py            # 主程序
├── main_menu.py       # 主菜单
├── run_game.py        # 启动脚本
├── requirements.txt   # 依赖列表
└── .env       # 环境配置
```"""
        return tree

    def run(self):
        """执行迁移"""
        print("🚀 开始整理项目结构...")

        # 1. 创建目录
        self.setup_directories()

        # 2. 定义要移动的文件
        files_to_tests = [
            # (源文件, 目标子目录)
            ("test_basic.py", ""),
            ("test_minimal.py", ""),
            ("test_parser_simple.py", ""),
            ("verify_fix.py", "verify"),
            ("complete_fix.py", "fixes"),
            ("fix_and_verify.py", "fixes"),
            ("diagnose_loop.py", "fixes"),
            ("quick_fix_loop.py", "fixes"),
            ("fix_nlp_real_api.py", "fixes"),
            ("verify_nlp_real.py", "verify"),
            ("fix_deepseek_json.py", "fixes"),
            ("test_fixed_nlp.py", ""),
            ("run_tests.py", ""),
            ("quick_test_fixes.py", ""),
        ]

        # 3. 定义要软删除的文件
        files_to_delete = [
            "fix_now_final.py",
            "execute_overhaul.py",
            "nlp_oneshot_fix.py",
            "quick_nlp_fix.py",
            "force_fix_game_core.py",
            "direct_fix_game.py",
            "real_nlp_system.py",
        ]

        # 4. 执行迁移
        self.move_to_tests(files_to_tests)
        self.soft_delete(files_to_delete)
        self.move_scripts_tests()
        self.create_env_example()

        # 5. 生成报告
        report = self.generate_report()
        print("\n✅ 迁移完成！")
        print(f"📄 查看详细报告：MIGRATION_REPORT.md")

        return report


if __name__ == "__main__":
    # 设置项目路径
    project_path = "/Users/chenpinle/Desktop/xianxia_world_engine"

    # 执行迁移
    migrator = ProjectMigrator(project_path)
    migrator.run()