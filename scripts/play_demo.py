#!/usr/bin/env python3
# @dev_only
# play_demo.py
"""
游戏演示程序

展示新的世界系统功能。
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from xwe.core import GameCore


def show_demo_commands():
    """显示演示命令"""
    print("\n" + "=" * 50)
    print("欢迎体验修仙世界引擎！")
    print("=" * 50)
    print("\n推荐尝试以下命令：")
    print("\n【世界探索】")
    print("  地图        - 查看当前位置和附近区域")
    print("  探索        - 探索当前区域")
    print("  去天南坊市  - 移动到天南坊市")
    print("  前往黄枫谷  - 移动到黄枫谷")
    print("\n【角色管理】")
    print("  状态        - 查看角色属性")
    print("  技能        - 查看已学技能")
    print("  修炼        - 打坐修炼")
    print("\n【自然语言】")
    print("  我想看看周围有什么")
    print("  带我去坊市逛逛")
    print("  我要修炼一会儿")
    print("  攻击那个妖兽")
    print("\n输入 '帮助' 查看所有命令")
    print("输入 '退出' 结束游戏")
    print("=" * 50 + "\n")


def main():
    """主函数"""
    # 显示演示命令
    show_demo_commands()

    # 创建游戏实例
    game = GameCore()

    # 开始新游戏
    player_name = input("请输入你的角色名（直接回车使用默认）: ").strip()
    if not player_name:
        player_name = "演示侠客"

    game.start_new_game(player_name)

    print("\n提示：你现在在青云城，这是一个安全的主城。")
    print("可以使用 '地图' 命令查看附近的区域。")
    print("使用 '探索' 命令可能会发现有趣的事物！\n")

    # 主游戏循环
    while game.is_running():
        # 显示游戏输出
        output = game.get_output()
        for line in output:
            print(line)

        # 获取玩家输入
        try:
            command = input("\n> ").strip()

            if command.lower() in ["quit", "exit", "退出"]:
                print("\n感谢游玩演示版本！")
                break
            else:
                # 处理命令
                game.process_command(command)

        except KeyboardInterrupt:
            print("\n\n游戏中断")
            break
        except Exception as e:
            print(f"发生错误: {e}")


if __name__ == "__main__":
    main()
