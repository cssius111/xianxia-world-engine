#!/usr/bin/env python3
"""
拍卖行系统测试演示

展示拍卖行的各种功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from xwe.core.character import Character, CharacterType
from xwe.features.auction_system import AuctionSystem
from xwe.features.auction_commands import AuctionCommandHandler
from xwe.features.interactive_auction import InteractiveAuction
from xwe.features.visual_enhancement import VisualEnhancement


def test_auction_system():
    """测试拍卖行系统"""
    print("=== 修仙世界拍卖行系统演示 ===\n")
    
    # 创建测试角色
    player = Character(
        name="陈道友",
        character_type=CharacterType.PLAYER,
        level=20,
        charisma=70,
        bargain_skill=3
    )
    
    # 给玩家一些初始资金
    player.add_lingshi(100000)  # 10万下品灵石
    
    # 添加一些仇敌关系（测试仇敌竞价）
    if not hasattr(player, 'grudges'):
        player.grudges = ['血刀门']
    
    print(f"玩家信息：")
    print(f"  姓名：{player.name}")
    print(f"  等级：{player.level}")
    print(f"  灵石：{player.get_lingshi_description()}")
    print(f"  仇敌：{player.grudges}")
    
    # 创建系统实例
    auction_system = AuctionSystem()
    command_handler = AuctionCommandHandler()
    visual = VisualEnhancement()
    
    # 测试进入拍卖行
    print("\n" + "="*60)
    print("测试1：进入拍卖行")
    print("="*60)
    result = command_handler.handle_auction_command(player, "拍卖行")
    print(result)
    
    # 等待用户确认
    input("\n按回车键继续...")
    
    # 测试参加拍卖会
    print("\n" + "="*60)
    print("测试2：参加拍卖会（自动模式）")
    print("="*60)
    result = command_handler.handle_auction_command(player, "参加拍卖")
    print(result)
    
    print(f"\n拍卖后灵石：{player.get_lingshi_description()}")
    
    # 等待用户确认
    input("\n按回车键继续交互式拍卖演示...")
    
    # 交互式拍卖演示
    print("\n" + "="*60)
    print("测试3：交互式拍卖体验")
    print("="*60)
    
    # 重置玩家资金
    player.add_lingshi(50000)
    
    # 创建交互式拍卖
    interactive = InteractiveAuction(auction_system)
    
    # 生成一些精选拍品
    items = auction_system._generate_auction_items("regular")[:3]  # 只拍3件
    
    # 确保有一件高价值物品
    if items:
        items[-1].tier = "高阶"
        items[-1].name = "九转还魂丹"
        items[-1].description = "传说级丹药，可起死回生，甚至能让元婴期修士恢复全盛状态"
        items[-1].base_price = 20000
        items[-1].max_price = 80000
    
    # 开始交互式拍卖
    results = interactive.start_interactive_auction(player, items)
    
    # 显示拍卖结果
    print("\n" + "="*60)
    print("拍卖会总结")
    print("="*60)
    print(f"拍得物品数：{len(results['items_won'])}")
    print(f"总花费：{results['total_spent']}灵石")
    print(f"剩余灵石：{player.get_lingshi_description()}")
    
    if results['items_won']:
        print("\n获得物品：")
        for item in results['items_won']:
            print(f"  - {item.name} ({item.tier})")
    
    # 测试拍后事件
    print("\n" + "="*60)
    print("测试4：拍后事件")
    print("="*60)
    
    # 模拟触发劫杀事件
    if results['items_won'] and results['total_spent'] > 30000:
        print(visual.get_colored_text(
            "\n【危险！】离开拍卖行时，您察觉到暗中有人跟踪...",
            'RED'
        ))
        print("\n三个蒙面人突然现身！")
        print("蒙面人首领：「识相的把刚才拍得的宝物交出来！」")
        print("\n选项：")
        print("1. 交出宝物保命")
        print("2. 拼死一战")
        print("3. 试图谈判")
        
        choice = input("\n您的选择 (1/2/3): ")
        
        if choice == '1':
            print("\n您不甘心地交出了宝物...")
            print("蒙面人首领冷笑：「算你识相！」")
            print("（失去所有拍得的物品）")
        elif choice == '2':
            print("\n您决定拼死一战！")
            print("战斗开始...")
            print("（此处应触发战斗系统）")
        else:
            print("\n您试图与劫匪谈判...")
            print("蒙面人首领：「少废话！要么交出宝物，要么死！」")
    
    # 测试帮助信息
    print("\n" + "="*60)
    print("测试5：查看拍卖帮助")
    print("="*60)
    result = command_handler.handle_auction_command(player, "拍卖帮助")
    print(result)
    
    print("\n=== 演示完成 ===")


def demonstrate_auction_features():
    """演示拍卖行的特色功能"""
    print("\n=== 拍卖行特色功能展示 ===\n")
    
    visual = VisualEnhancement()
    
    # 1. VIP包厢系统
    print(visual.get_colored_text("1. VIP包厢系统", 'GOLD'))
    print("   - 消费满5万灵石自动升级VIP")
    print("   - 享受匿名竞拍特权")
    print("   - 专属包厢和优先座位")
    print("   - 可设置自动代理竞拍\n")
    
    # 2. 多种竞拍模式
    print(visual.get_colored_text("2. 多种竞拍模式", 'CYAN'))
    print("   - 英式拍卖：价高者得")
    print("   - 荷兰式拍卖：递减竞价")
    print("   - 密封投标：暗标竞争\n")
    
    # 3. 动态事件系统
    print(visual.get_colored_text("3. 动态事件系统", 'YELLOW'))
    print("   - 仇敌恶意抬价")
    print("   - 突发劫案事件")
    print("   - 神秘大能到场")
    print("   - 虚假报价捣乱\n")
    
    # 4. 智能NPC系统
    print(visual.get_colored_text("4. 智能NPC系统", 'GREEN'))
    print("   - 5种NPC性格：激进、保守、策略、神秘、暴发户")
    print("   - 基于价值评估的理性出价")
    print("   - 情绪化竞价和报复性抬价")
    print("   - 不同性格的专属台词\n")
    
    # 5. 拍后事件链
    print(visual.get_colored_text("5. 拍后事件链", 'RED'))
    print("   - 劫杀事件：高价值物品引发觊觎")
    print("   - 结盟机会：财力引起强者注意")
    print("   - 黑市线索：流拍物品的去向")
    print("   - 仇恨升级：竞拍失败结下梁子\n")


if __name__ == "__main__":
    # 先展示特色功能
    demonstrate_auction_features()
    
    input("\n按回车键开始系统测试...")
    
    # 运行主测试
    test_auction_system()
