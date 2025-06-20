#!/usr/bin/env python
# @dev_only
"""
项目验证脚本
检查项目结构、依赖和功能是否正常
"""

import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class ProjectVerifier:
    """项目验证器"""

    def __init__(self):
        self.project_root = project_root
        self.errors = []
        self.warnings = []
        self.success = []

    def check_all(self):
        """执行所有检查"""
        print("=" * 60)
        print("修仙世界引擎 - 项目验证")
        print("=" * 60)

        # 1. 检查目录结构
        print("\n【1. 检查目录结构】")
        self.check_directory_structure()

        # 2. 检查Python模块
        print("\n【2. 检查Python模块】")
        self.check_python_modules()

        # 3. 检查数据文件
        print("\n【3. 检查数据文件】")
        self.check_data_files()

        # 4. 检查功能模块
        print("\n【4. 检查功能模块】")
        self.check_functionality()

        # 5. 检查测试
        print("\n【5. 检查测试】")
        self.check_tests()

        # 显示总结
        self.show_summary()

    def check_directory_structure(self):
        """检查目录结构"""
        required_dirs = [
            "xwe",
            "xwe/core",
            "xwe/core/nlp",
            "xwe/core/roll_system",
            "xwe/data",
            "xwe/engine",
            "xwe/world",
            "xwe/npc",
            "tests",
            "tests/unit",
            "scripts",
            "docs",
            "examples",
            "saves",
        ]

        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists() and full_path.is_dir():
                self.success.append(f"✅ 目录存在: {dir_path}")
            else:
                self.errors.append(f"❌ 目录缺失: {dir_path}")

    def check_python_modules(self):
        """检查Python模块是否可以导入"""
        modules_to_check = [
            ("xwe", "主包"),
            ("xwe.core", "核心模块"),
            ("xwe.core.game_core", "游戏核心"),
            ("xwe.core.character", "角色系统"),
            ("xwe.core.skills", "技能系统"),
            ("xwe.core.combat", "战斗系统"),
            ("xwe.core.roll_system", "Roll系统"),
            ("xwe.core.roll_system.character_roller", "角色生成器"),
            ("xwe.core.nlp", "NLP模块"),
            ("xwe.world", "世界系统"),
            ("xwe.npc", "NPC系统"),
            ("xwe.engine.expression", "表达式引擎"),
        ]

        for module_name, description in modules_to_check:
            try:
                importlib.import_module(module_name)
                self.success.append(f"✅ {description}: {module_name}")
            except ImportError as e:
                self.errors.append(f"❌ {description}: {module_name} - {str(e)}")
            except Exception as e:
                self.warnings.append(f"⚠️ {description}: {module_name} - {str(e)}")

    def check_data_files(self):
        """检查数据文件"""
        data_files = [
            "xwe/data/attribute/base.json",
            "xwe/data/attribute/cultivation.json",
            "xwe/data/character/player_template.json",
            "xwe/data/character/templates.json",
            "xwe/data/character/roll_data.json",
            "xwe/data/combat/effects.json",
            "xwe/data/skills/skills.json",
            "xwe/data/world/config.json",
            "xwe/data/world/areas.json",
            "xwe/data/npc/profiles.json",
            "xwe/data/npc/dialogues.json",
        ]

        for file_path in data_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                # 尝试加载JSON验证格式
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        json.load(f)
                    self.success.append(f"✅ 数据文件正常: {file_path}")
                except json.JSONDecodeError as e:
                    self.errors.append(f"❌ JSON格式错误: {file_path} - {str(e)}")
                except Exception as e:
                    self.warnings.append(f"⚠️ 读取错误: {file_path} - {str(e)}")
            else:
                self.errors.append(f"❌ 数据文件缺失: {file_path}")

    def check_functionality(self):
        """检查核心功能"""
        # 1. 检查Roll系统
        try:
            from xwe.core.roll_system import CharacterRoller

            roller = CharacterRoller()
            character = roller.roll_character()

            # 验证生成的角色数据
            required_fields = [
                "attributes",
                "spiritual_root",
                "physique",
                "destinies",
                "talents",
                "overall_rating",
            ]

            missing_fields = [f for f in required_fields if f not in character]
            if missing_fields:
                self.errors.append(f"❌ Roll系统: 缺少字段 {missing_fields}")
            else:
                self.success.append("✅ Roll系统: 功能正常")

        except Exception as e:
            self.errors.append(f"❌ Roll系统: {str(e)}")

        # 2. 检查游戏核心
        try:
            from xwe.core import GameCore

            game = GameCore()
            self.success.append("✅ 游戏核心: 初始化成功")
        except Exception as e:
            self.errors.append(f"❌ 游戏核心: {str(e)}")

        # 3. 检查NLP系统
        try:
            from xwe.core.nlp import NLPConfig, NLPProcessor

            config = NLPConfig(enable_llm=False)
            nlp = NLPProcessor(None, config)
            self.success.append("✅ NLP系统: 初始化成功")

            # 检查是否使用mock
            if config.llm_provider == "mock":
                self.warnings.append("⚠️ NLP系统: 当前使用mock模式，未接入真实LLM")
        except Exception as e:
            self.errors.append(f"❌ NLP系统: {str(e)}")

    def check_tests(self):
        """检查测试文件"""
        test_files = [
            "tests/unit/test_roll_system.py",
            "tests/unit/test_character.py",
            "tests/unit/test_skills.py",
            "tests/unit/test_combat.py",
        ]

        for test_file in test_files:
            full_path = self.project_root / test_file
            if full_path.exists():
                self.success.append(f"✅ 测试文件存在: {test_file}")
            else:
                self.warnings.append(f"⚠️ 测试文件缺失: {test_file}")

    def show_summary(self):
        """显示检查总结"""
        print("\n" + "=" * 60)
        print("【检查总结】")
        print("=" * 60)

        # 显示成功项
        if self.success:
            print(f"\n✅ 成功项 ({len(self.success)}个):")
            for item in self.success[:5]:  # 只显示前5个
                print(f"  {item}")
            if len(self.success) > 5:
                print(f"  ... 还有{len(self.success)-5}个成功项")

        # 显示警告
        if self.warnings:
            print(f"\n⚠️ 警告 ({len(self.warnings)}个):")
            for warning in self.warnings:
                print(f"  {warning}")

        # 显示错误
        if self.errors:
            print(f"\n❌ 错误 ({len(self.errors)}个):")
            for error in self.errors:
                print(f"  {error}")

        # 总体评估
        print("\n" + "-" * 60)
        if not self.errors:
            print("✅ 项目验证通过！所有核心功能正常。")
            if self.warnings:
                print(f"   但有{len(self.warnings)}个警告需要注意。")
        else:
            print(f"❌ 项目存在{len(self.errors)}个错误需要修复！")

        # 建议
        print("\n【建议】")
        if any("Roll系统" in error for error in self.errors):
            print("- Roll系统有问题，请检查 xwe/core/roll_system/ 目录")

        if any("mock" in warning for warning in self.warnings):
            print("- NLP系统使用mock模式，建议集成真实的LLM API")
            print("  可以设置环境变量或修改配置文件来启用")

        if any("测试文件缺失" in warning for warning in self.warnings):
            print("- 部分测试文件缺失，建议补充单元测试")

        # 运行建议
        print("\n【可以尝试运行】")
        print("1. python main.py              # 运行主游戏")
        print("2. python scripts/test_roll.py  # 测试Roll系统")
        print("3. python -m pytest tests/      # 运行所有测试")


def main():
    """主函数"""
    verifier = ProjectVerifier()

    try:
        verifier.check_all()
    except Exception as e:
        print(f"\n发生严重错误: {e}")
        import traceback

        traceback.print_exc()

    return 0 if not verifier.errors else 1


if __name__ == "__main__":
    sys.exit(main())
