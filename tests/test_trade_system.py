#!/usr/bin/env python3
"""
交易系统测试脚本

测试商店、讨价还价、物品买卖等功能。
"""


# 添加项目根目录到 Python 路径

from xwe.core.character import Character, CharacterType
from xwe.core.trade_system import TradeSystem
from xwe.core.trade_commands import TradeCommandHandler


def test_trade_system():
    """测试交易系统"""
    print("=== 交易系统测试 ===\n")
    
    # 创建测试角色
    player = Character(
        name="测试玩家",
        character_type=CharacterType.PLAYER,
        charisma=60,
        bargain_skill=2
    )
    
    # 给玩家一些初始灵石
    player.add_lingshi(5000)  # 5000下品灵石
    
    # 给玩家一些初始物品（用于测试出售）
    player.inventory.add("ju_ling_cao", 10)
    player.inventory.add("huo_ball_fu", 5)
    
    print(f"玩家初始状态：")
    print(f"  姓名：{player.name}")
    print(f"  灵石：{player.get_lingshi_description()}")
    print(f"  魅力：{player.charisma}")
    print(f"  讨价还价技能：{player.bargain_skill}")
    print(f"  背包物品：")
    for item_id, qty in player.inventory.list_items():
        print(f"    - {item_id} x{qty}")
    
    # 创建交易系统
    trade_system = TradeSystem()
    handler = TradeCommandHandler(trade_system)
    
    print("\n--- 测试1：进入商店 ---")
    result = handler.handle_shop_command(player, "wanbao")
    print(result)
    
    print("\n--- 测试2：查看商品详情 ---")
    result = handler.handle_item_detail_command(1)  # 查看第1个商品
    print(result)
    
    print("\n--- 测试3：直接购买 ---")
    result = handler.handle_buy_command(player, 1, 2)  # 购买第1个商品2个
    print(result)
    print(f"购买后灵石：{player.get_lingshi_description()}")
    
    print("\n--- 测试4：讨价还价（合理价格）---")
    # 查看第3个商品的价格
    goods = handler.current_shop.list_goods()
    original_price = goods[2].sell_price if len(goods) > 2 else 50
    offer_price = int(original_price * 0.85)  # 出价85%
    
    result = handler.handle_bargain_command(player, 3, offer_price)
    print(f"商品原价：{original_price}")
    print(f"玩家出价：{offer_price}")
    print(f"结果：{result}")
    
    print("\n--- 测试5：讨价还价（价格过低）---")
    low_price = int(original_price * 0.5)  # 出价50%
    result = handler.handle_bargain_command(player, 3, low_price)
    print(f"玩家出价：{low_price}")
    print(f"结果：{result}")
    
    print("\n--- 测试6：假装离开触发挽留 ---")
    # 先出一个接近底价的价格
    near_floor_price = int(original_price * 0.88)
    result = handler.handle_bargain_command(player, 3, near_floor_price)
    print(f"玩家出价：{near_floor_price}")
    print(f"结果：{result}")
    
    # 尝试离开
    result = handler.handle_leave_shop_command(player)
    print(f"离开时：{result}")
    
    if "是否接受" in result:
        # 接受掌柜的报价
        result = handler.handle_accept_offer_command(player)
        print(f"接受报价：{result}")
        
        # 以新价格购买
        result = handler.handle_buy_command(player, 3, 1)
        print(f"购买结果：{result}")
    
    print("\n--- 测试7：出售物品 ---")
    # 重新进入商店
    handler.handle_shop_command(player, "wanbao")
    
    result = handler.handle_sell_command(player, "聚灵草", 5)
    print(result)
    print(f"出售后灵石：{player.get_lingshi_description()}")
    
    print("\n--- 测试8：背包空间限制 ---")
    # 尝试购买超过背包容量的物品
    player.inventory.max_slots = 5  # 临时设置小背包
    current_slots = player.inventory.get_used_slots()
    print(f"当前背包使用：{current_slots}/5 格")
    
    # 尝试购买会超出容量的物品
    for i in range(10):
        player.inventory.add(f"test_item_{i}", 1)
    
    result = handler.handle_buy_command(player, 1, 1)
    print(f"背包满时购买：{result}")
    
    print("\n--- 测试9：灵石不足 ---")
    # 花光灵石
    player.spend_lingshi(player.get_total_lingshi() - 10)  # 只留10个下品灵石
    print(f"当前灵石：{player.get_lingshi_description()}")
    
    result = handler.handle_buy_command(player, 6, 1)  # 尝试买贵的东西
    print(f"灵石不足时购买：{result}")
    
    print("\n--- 测试10：特殊商店 ---")
    # 测试丹药专卖店
    result = handler.handle_shop_command(player, "lingdan")
    print("灵丹阁：")
    print(result[:200] + "...")  # 只显示部分
    
    print("\n=== 测试完成 ===")
    
    # 显示最终状态
    print(f"\n玩家最终状态：")
    print(f"  灵石：{player.get_lingshi_description()}")
    print(f"  背包物品：")
    for item_id, qty in player.inventory.list_items()[:10]:  # 只显示前10个
        item_info = trade_system.get_item_info(item_id)
        if item_info:
            print(f"    - {item_info['name']} x{qty}")
        else:
            print(f"    - {item_id} x{qty}")


def test_currency_system():
    """测试货币系统"""
    print("\n=== 货币系统测试 ===\n")
    
    player = Character(name="测试玩家")
    
    # 测试添加灵石
    print("--- 测试添加灵石 ---")
    player.add_lingshi(12345)
    print(f"添加12345下品灵石后：{player.get_lingshi_description()}")
    print(f"详细：{player.lingshi}")
    
    # 测试花费灵石
    print("\n--- 测试花费灵石 ---")
    success = player.spend_lingshi(150)
    print(f"花费150下品灵石：{'成功' if success else '失败'}")
    print(f"剩余：{player.get_lingshi_description()}")
    
    # 测试找零
    print("\n--- 测试找零机制 ---")
    player.lingshi = {"low": 0, "mid": 2, "high": 0, "supreme": 0}
    print(f"初始：{player.get_lingshi_description()}")
    success = player.spend_lingshi(150)
    print(f"花费150下品灵石：{'成功' if success else '失败'}")
    print(f"剩余：{player.get_lingshi_description()}")
    print(f"详细：{player.lingshi}")
    
    # 测试大额交易
    print("\n--- 测试大额交易 ---")
    player.add_lingshi(1234567)
    print(f"添加1234567下品灵石后：{player.get_lingshi_description()}")
    print(f"详细：{player.lingshi}")


if __name__ == "__main__":
    test_currency_system()
    print("\n" + "="*50 + "\n")
    test_trade_system()
