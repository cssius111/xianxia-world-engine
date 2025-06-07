#!/usr/bin/env python3
"""
拍卖行系统快速演示

展示拍卖行系统的基本使用
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from xwe.core.character import Character, CharacterType
from xwe.features.auction_system import auction_system
from xwe.features.auction_commands import auction_command_handler
from xwe.features.visual_enhancement import VisualEnhancement


def quick_auction_demo():
    """快速演示拍卖行功能"""
    visual = VisualEnhancement()
    
    print(visual.get_colored_text(
        "=== 修仙世界拍卖行快速演示 ===\n",
        'YELLOW'
    ))
    
    # 创建玩家
    player = Character(
        name="演示道友",
        character_type=CharacterType.PLAYER,
        level=25
    )
    player.add_lingshi(50000)  # 5万灵石
    
    print(f"欢迎{player.name}！")
    print(f"您的等级：{player.level}")
    print(f"您的灵石：{player.get_lingshi_description()}\n")
    
    # 模拟游戏命令循环
    print("输入命令与拍卖行互动（输入'退出'结束演示）：\n")
    print("可用命令：")
    print("- 拍卖行：查看拍卖行信息")
    print("- 参加拍卖：参加拍卖会")
    print("- 出价 [金额]：在拍卖中出价")
    print("- 拍卖帮助：查看帮助信息")
    print("- 退出：结束演示\n")
    
    while True:
        # 获取用户输入
        command = input("> ").strip()
        
        if command == "退出":
            print("\n感谢体验拍卖行系统！")
            break
        
        # 分离命令和参数
        parts = command.split(maxsplit=1)
        cmd = parts[0] if parts else ""
        params = parts[1] if len(parts) > 1 else None
        
        # 处理拍卖命令
        if cmd in ["拍卖行", "参加拍卖", "出价", "放弃", "离开拍卖行", "拍卖帮助"]:
            result = auction_command_handler.handle_auction_command(player, cmd, params)
            print(result)
            
            # 显示额外提示
            if auction_command_handler.is_in_auction():
                prompt = auction_command_handler.get_auction_prompt()
                if prompt:
                    print(f"\n{prompt}")
        else:
            print("未知命令。请输入'拍卖帮助'查看可用命令。")
        
        print()  # 空行分隔


def show_auction_features():
    """展示拍卖行特色功能"""
    visual = VisualEnhancement()
    
    print(visual.get_colored_text(
        "\n=== 拍卖行系统特色功能 ===\n",
        'CYAN'
    ))
    
    features = [
        ("🏛️ 真实拍卖体验", "完整的拍卖流程，从展示到成交"),
        ("🤖 智能NPC竞价", "5种性格的NPC，各有不同竞价策略"),
        ("⚔️ 仇敌系统", "仇敌会恶意抬价，增加游戏深度"),
        ("🎭 随机事件", "突发劫案、大能到场等意外情况"),
        ("💎 VIP特权", "高级玩家享受匿名竞拍等特权"),
        ("🗡️ 拍后剧情", "高价物品可能引发劫杀事件")
    ]
    
    for title, desc in features:
        print(f"{title}")
        print(f"  {desc}\n")


if __name__ == "__main__":
    # 显示特色功能
    show_auction_features()
    
    # 询问是否开始演示
    choice = input("是否开始拍卖行演示？(y/n): ").strip().lower()
    
    if choice == 'y':
        quick_auction_demo()
    else:
        print("\n您可以随时运行此脚本体验拍卖行系统。")
