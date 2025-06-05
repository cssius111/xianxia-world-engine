#!/usr/bin/env python3
"""
交易系统集成示例

展示如何将交易系统集成到游戏中。
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from xwe.core.character import Character, CharacterType
from xwe.core.trade_system import TradeSystem
from xwe.core.trade_commands import TradeCommandHandler


class SimpleGame:
    """简单的游戏示例，集成交易系统"""
    
    def __init__(self):
        self.player = Character(
            name="张三",
            character_type=CharacterType.PLAYER,
            charisma=50,
            bargain_skill=1
        )
        
        # 初始化交易系统
        self.trade_system = TradeSystem()
        self.trade_handler = TradeCommandHandler(self.trade_system)
        
        # 给玩家一些初始资源
        self.player.add_lingshi(1000)  # 1000下品灵石
        self.player.inventory.add("ju_ling_cao", 5)  # 5个聚灵草
        
        self.running = True
        self.in_shop = False
    
    def display_status(self):
        """显示玩家状态"""
        print("\n" + "="*40)
        print(f"玩家：{self.player.name}")
        print(f"境界：{self.player.get_realm_info()}")
        print(f"灵石：{self.player.get_lingshi_description()}")
        print(f"背包：{self.player.inventory.get_used_slots()}/{self.player.inventory.max_slots} 格")
        print("="*40)
    
    def display_help(self):
        """显示帮助信息"""
        print("\n可用命令：")
        if not self.in_shop:
            print("  商店 - 进入万宝楼")
            print("  丹药店 - 进入灵丹阁")
            print("  炼器店 - 进入炼器坊")
            print("  背包 - 查看背包物品")
            print("  状态 - 查看角色状态")
            print("  退出 - 退出游戏")
        else:
            print("  购买 [编号] [数量] - 购买商品")
            print("  出售 [物品名] [数量] - 出售物品")
            print("  详情 [编号] - 查看商品详情")
            print("  还价 [编号] [价格] - 讨价还价")
            print("  离开 - 离开商店")
    
    def display_inventory(self):
        """显示背包物品"""
        print("\n【背包物品】")
        items = self.player.inventory.list_items()
        if not items:
            print("背包空空如也。")
            return
        
        for item_id, qty in items:
            item_info = self.trade_system.get_item_info(item_id)
            if item_info:
                print(f"  {item_info['name']} x{qty}")
            else:
                print(f"  {item_id} x{qty}")
        
        print(f"\n剩余空间：{self.player.inventory.get_free_slots()} 格")
    
    def process_command(self, command: str):
        """处理玩家命令"""
        parts = command.strip().split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        
        # 非商店命令
        if not self.in_shop:
            if cmd in ["商店", "shop"]:
                result = self.trade_handler.handle_shop_command(self.player, "wanbao")
                print(result)
                self.in_shop = True
            
            elif cmd in ["丹药店", "pills"]:
                result = self.trade_handler.handle_shop_command(self.player, "lingdan")
                print(result)
                self.in_shop = True
            
            elif cmd in ["炼器店", "weapons"]:
                result = self.trade_handler.handle_shop_command(self.player, "lianqi")
                print(result)
                self.in_shop = True
            
            elif cmd in ["背包", "bag", "inventory"]:
                self.display_inventory()
            
            elif cmd in ["状态", "status"]:
                self.display_status()
            
            elif cmd in ["帮助", "help", "?"]:
                self.display_help()
            
            elif cmd in ["退出", "exit", "quit"]:
                self.running = False
                print("再见！祝您修仙顺利！")
            
            else:
                print("未知命令。输入'帮助'查看可用命令。")
        
        # 商店内命令
        else:
            if cmd in ["购买", "buy"]:
                if len(parts) >= 2:
                    try:
                        item_index = int(parts[1])
                        quantity = int(parts[2]) if len(parts) >= 3 else 1
                        result = self.trade_handler.handle_buy_command(self.player, item_index, quantity)
                        print(result)
                    except ValueError:
                        print("请输入有效的数字。")
                else:
                    print("用法：购买 [编号] [数量]")
            
            elif cmd in ["出售", "sell"]:
                if len(parts) >= 2:
                    item_name = parts[1]
                    quantity = int(parts[2]) if len(parts) >= 3 else 1
                    result = self.trade_handler.handle_sell_command(self.player, item_name, quantity)
                    print(result)
                else:
                    print("用法：出售 [物品名] [数量]")
            
            elif cmd in ["详情", "detail", "info"]:
                if len(parts) >= 2:
                    try:
                        item_index = int(parts[1])
                        result = self.trade_handler.handle_item_detail_command(item_index)
                        print(result)
                    except ValueError:
                        print("请输入有效的商品编号。")
                else:
                    print("用法：详情 [编号]")
            
            elif cmd in ["还价", "bargain"]:
                if len(parts) >= 3:
                    try:
                        item_index = int(parts[1])
                        price = int(parts[2])
                        result = self.trade_handler.handle_bargain_command(self.player, item_index, price)
                        print(result)
                    except ValueError:
                        print("请输入有效的数字。")
                else:
                    print("用法：还价 [编号] [价格]")
            
            elif cmd in ["离开", "leave", "exit"]:
                result = self.trade_handler.handle_leave_shop_command(self.player)
                print(result)
                
                # 检查是否需要处理挽留
                if "是否接受" in result:
                    response = input("你的选择（接受/拒绝）: ")
                    if response in ["接受", "accept", "yes", "y"]:
                        result = self.trade_handler.handle_accept_offer_command(self.player)
                        print(result)
                    else:
                        result = self.trade_handler.handle_reject_offer_command(self.player)
                        print(result)
                        self.in_shop = False
                else:
                    self.in_shop = False
            
            elif cmd in ["接受", "accept"]:
                result = self.trade_handler.handle_accept_offer_command(self.player)
                print(result)
            
            elif cmd in ["拒绝", "reject"]:
                result = self.trade_handler.handle_reject_offer_command(self.player)
                print(result)
                self.in_shop = False
            
            else:
                print("未知命令。可用命令：购买、出售、详情、还价、离开")
    
    def run(self):
        """运行游戏主循环"""
        print("=== 修仙世界 - 交易系统示例 ===")
        print(f"\n欢迎来到修仙世界，{self.player.name}！")
        
        self.display_status()
        self.display_help()
        
        while self.running:
            try:
                command = input("\n> ")
                self.process_command(command)
            except KeyboardInterrupt:
                print("\n\n游戏已暂停。")
                self.running = False
            except Exception as e:
                print(f"发生错误：{e}")


def main():
    """主函数"""
    game = SimpleGame()
    game.run()


if __name__ == "__main__":
    main()
