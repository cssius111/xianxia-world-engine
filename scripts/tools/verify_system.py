#!/usr/bin/env python3
# @dev_only
"""
验证游戏是否能正常运行
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_game_core():
    """测试GameCore主循环"""
    print("🧪 测试游戏核心系统...")
    print("=" * 50)

    try:
        from xwe.core.game_core import GameCore

        print("✅ GameCore导入成功")

        # 创建游戏实例
        game = GameCore()
        print("✅ GameCore实例创建成功")

        # 测试初始状态
        print(f"\n初始状态:")
        print(f"  is_running() = {game.is_running()}")
        print(f"  running属性 = {getattr(game, 'running', 'undefined')}")

        # 测试start_new_game
        print("\n调用start_new_game('测试玩家')...")
        game.start_new_game("测试玩家")

        print(f"\n调用后状态:")
        print(f"  is_running() = {game.is_running()}")
        print(f"  running属性 = {getattr(game, 'running', 'undefined')}")

        if game.is_running():
            print("\n✅ 主循环修复成功！游戏可以正常运行")
        else:
            print("\n❌ 主循环仍有问题")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()


def test_roll_system():
    """测试Roll系统"""
    print("\n\n🎲 测试Roll系统...")
    print("=" * 50)

    try:
        from xwe.core.roll_system import CharacterRoller

        print("✅ Roll系统导入成功")

        roller = CharacterRoller()
        result = roller.roll()

        print(f"\nRoll结果:")
        print(f"  姓名: {result.name}")
        print(f"  身份: {result.identity}")
        print(f"  灵根: {result.spiritual_root_type}")
        print(f"  命格: {result.destiny}")
        print(f"  评级: {result.overall_rating}")
        print(f"  战力: {result.combat_power}")

        print("\n✅ Roll系统工作正常")

    except Exception as e:
        print(f"\n❌ Roll系统测试失败: {e}")


def test_nlp_system():
    """测试NLP系统"""
    print("\n\n🤖 测试NLP系统...")
    print("=" * 50)

    try:
        from xwe.core.command_parser import CommandParser
        from xwe.core.nlp import NLPProcessor

        print("✅ NLP系统导入成功")

        parser = CommandParser()
        nlp = NLPProcessor(parser)

        test_inputs = ["查看状态", "我想修炼一会儿", "用剑气斩攻击敌人"]

        for test_input in test_inputs:
            result = nlp.parse(test_input)
            print(f"\n输入: {test_input}")
            print(f"  命令类型: {result.command_type}")
            print(f"  置信度: {result.confidence}")

        print("\n✅ NLP系统基本功能正常")

    except Exception as e:
        print(f"\n❌ NLP系统测试失败: {e}")


def main():
    """主测试函数"""
    print("🚀 XianXia World Engine - 系统验证")
    print("=" * 60)

    # 测试各个系统
    test_game_core()
    test_roll_system()
    test_nlp_system()

    print("\n\n📊 验证完成！")
    print("\n如果所有测试都通过，可以运行:")
    print("  python main.py          # 开始游戏")
    print("  python main_menu.py     # 主菜单模式")


if __name__ == "__main__":
    main()
