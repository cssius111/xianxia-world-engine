#!/usr/bin/env python
"""修仙世界引擎 - 主菜单"""

import sys
from pathlib import Path
import argparse

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.main_menu_display import (
    clear_screen,
    show_main_menu,
    test_roll_system,
    test_nlp_system,
    show_settings,
)
from core.player_initializer import start_new_game, start_with_roll


def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(description="修仙世界引擎主菜单")
    parser.add_argument("--mode", default="player", help="运行模式：player 或 dev")
    args = parser.parse_args()
    game_mode = args.mode

    while True:
        clear_screen()
        choice = show_main_menu()

        if choice == '1':
            start_new_game(game_mode)
        elif choice == '2':
            start_with_roll(game_mode)
        elif choice == '3':
            test_roll_system()
        elif choice == '4':
            test_nlp_system()
        elif choice == '5':
            print("\n继续游戏功能开发中...")
            input("按Enter返回主菜单...")
        elif choice == '6':
            show_settings()
        elif choice == '7':
            print("\n感谢游玩，再见！")
            break
        else:
            print("\n无效的选择，请重新输入")
            input("按Enter继续...")


if __name__ == "__main__":
    main()

