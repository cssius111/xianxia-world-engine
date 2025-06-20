#!/usr/bin/env python
# @dev_only
"""
快速检查项目状态
显示当前修复情况
"""

import json
import os
import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent


def check_roll_system():
    """检查Roll系统"""
    print("\n【Roll系统】")
    try:
        from xwe.core.roll_system import CharacterRoller

        roller = CharacterRoller()

        # 检查两个方法
        has_roll = hasattr(roller, "roll")
        has_roll_character = hasattr(roller, "roll_character")

        print(f"✅ roll() 方法: {'存在' if has_roll else '缺失'}")
        print(f"✅ roll_character() 方法: {'存在' if has_roll_character else '缺失'}")

        # 测试运行
        result = roller.roll()
        print(f"✅ 测试Roll: 成功生成 {result.name}")

        return True
    except Exception as e:
        print(f"❌ Roll系统错误: {e}")
        return False


def check_data_files():
    """检查数据文件"""
    print("\n【数据文件】")

    required_files = [
        "xwe/data/attribute/base.json",
        "xwe/data/attribute/cultivation.json",
        "xwe/data/character/templates.json",
        "xwe/data/character/roll_data.json",
        "xwe/data/combat/effects.json",
        "xwe/data/world/config.json",
        "xwe/data/world/areas.json",
        "xwe/data/npc/profiles.json",
        "xwe/data/interaction/nlp_config.json",
    ]

    missing = []
    for file_path in required_files:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing.append(file_path)

    return len(missing) == 0


def check_nlp_config():
    """检查NLP配置"""
    print("\n【NLP配置】")

    # 检查API密钥
    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")

    print(f"✅ DeepSeek API: {'已设置' if deepseek_key else '未设置'}")
    print(f"{'✅' if openai_key else '⚪'} OpenAI API: {'已设置' if openai_key else '未设置'}")

    # 检查配置文件
    config_path = PROJECT_ROOT / "xwe/data/interaction/nlp_config.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        provider = config.get("llm_provider", "mock")
        enabled = config.get("enable_llm", False)

        print(f"\n当前配置:")
        print(f"- 提供者: {provider}")
        print(f"- 启用状态: {enabled}")

        if provider != "mock" and enabled:
            print("✅ NLP已配置为使用真实LLM")
        else:
            print("⚠️  NLP仍在使用mock模式")
    else:
        print("❌ 配置文件不存在")

    return True


def check_scripts():
    """检查脚本文件"""
    print("\n【脚本文件】")

    scripts = [
        ("scripts/test_roll.py", "Roll系统测试"),
        ("scripts/simple_roll.py", "简化Roll测试"),
        ("scripts/test_nlp.py", "NLP测试"),
        ("main_menu.py", "增强主菜单"),
        ("scripts/verify_project.py", "项目验证"),
    ]

    all_exist = True
    for script_path, desc in scripts:
        full_path = PROJECT_ROOT / script_path
        if full_path.exists():
            print(f"✅ {desc}: {script_path}")
        else:
            print(f"❌ {desc}: {script_path}")
            all_exist = False

    return all_exist


def main():
    """主函数"""
    print("=" * 60)
    print("修仙世界引擎 - 快速状态检查")
    print("=" * 60)

    # 执行检查
    roll_ok = check_roll_system()
    data_ok = check_data_files()
    nlp_ok = check_nlp_config()
    scripts_ok = check_scripts()

    # 总结
    print("\n" + "=" * 60)
    print("【总结】")

    if roll_ok and data_ok and scripts_ok:
        print("✅ 项目基本功能正常！")
        print("\n可以运行：")
        print("1. python main_menu.py       # 增强主菜单")
        print("2. python scripts/simple_roll.py  # Roll系统")
        print("3. python scripts/test_roll.py    # 完整Roll测试")
        print("4. python scripts/test_nlp.py     # NLP测试")
        print("5. python main.py                 # 原版游戏")
    else:
        print("❌ 还有一些问题需要修复")
        if not roll_ok:
            print("- Roll系统需要修复")
        if not data_ok:
            print("- 数据文件有缺失")
        if not scripts_ok:
            print("- 脚本文件有缺失")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
