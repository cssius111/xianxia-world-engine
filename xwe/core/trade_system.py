# core/trade_system.py
"""
交易系统模块

实现商店、市集、讨价还价等交易功能。
支持灵石货币系统（下品、中品、上品、极品）。
"""

from typing import Any, Dict, List, Optional, Tuple
from random import uniform, random
from dataclasses import dataclass
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ShopItem:
    """商店物品"""
    item_id: str
    item_data: Dict[str, Any]
    quantity: int
    sell_price: int  # 卖出价（商家卖给玩家）
    buy_price: int   # 收购价（商家从玩家收购）
    
    def __str__(self) -> Any:
        return f"{self.item_data['name']} x{self.quantity}"


class TradeSystem:
    """交易系统主类"""
    
    def __init__(self) -> None:
        self.items_data = self._load_items_data()
        self.shopkeepers = {}
        
    def _load_items_data(self) -> Dict[str, Dict]:
        """加载物品数据"""
        items_path = Path(__file__).parent.parent / "data" / "items" / "items.json"
        try:
            with open(items_path, 'r', encoding='utf-8') as f:
                items_list = json.load(f)
                return {item['id']: item for item in items_list}
        except Exception as e:
            logger.error(f"加载物品数据失败: {e}")
            return {}
    
    def get_item_info(self, item_id: str) -> Optional[Dict]:
        """获取物品信息"""
        return self.items_data.get(item_id)
    
    def convert_currency(self, lingshi: Dict[str, int]) -> int:
        """
        将灵石转换为下品灵石数量
        
        Args:
            lingshi: {"low": 0, "mid": 0, "high": 0, "supreme": 0}
            
        Returns:
            下品灵石总数
        """
        return (lingshi.get('low', 0) + 
                lingshi.get('mid', 0) * 100 + 
                lingshi.get('high', 0) * 10000 +
                lingshi.get('supreme', 0) * 1000000)
    
    def make_change(self, amount: int) -> Dict[str, int]:
        """
        将下品灵石数量转换为各种灵石组合（找零）
        
        Args:
            amount: 下品灵石数量
            
        Returns:
            灵石组合
        """
        result = {"low": 0, "mid": 0, "high": 0, "supreme": 0}
        
        # 极品灵石（100万下品）
        if amount >= 1000000:
            result["supreme"] = amount // 1000000
            amount %= 1000000
        
        # 上品灵石（1万下品）
        if amount >= 10000:
            result["high"] = amount // 10000
            amount %= 10000
        
        # 中品灵石（100下品）
        if amount >= 100:
            result["mid"] = amount // 100
            amount %= 100
        
        # 下品灵石
        result["low"] = amount
        
        return result


class Shopkeeper:
    """商店掌柜NPC"""
    
    def __init__(self, name: str, shop_type: str = "general", 
                 markup: float = 1.2, min_price_factor: float = 0.9):
        """
        初始化商店掌柜
        
        Args:
            name: 掌柜名字
            shop_type: 商店类型（general/pills/weapons/materials等）
            markup: 加价倍率（相对于基础价）
            min_price_factor: 心理底价系数（最低接受价格 = 售价 * min_price_factor）
        """
        self.name = name
        self.shop_type = shop_type
        self.markup = markup
        self.min_price_factor = min_price_factor
        self.inventory: Dict[str, ShopItem] = {}
        self.trade_history: List[Dict] = []
        self.player_reputation = 0  # 玩家在此商店的声望
        
    def add_goods(self, item_id: str, quantity: int, item_data: Dict[str, Any]) -> None:
        """添加商品到商店"""
        base_price = item_data.get('base_price', 100)
        variance = item_data.get('variance', 0)
        
        # 计算动态价格
        price_variation = uniform(-variance, variance) if variance > 0 else 0
        sell_price = int((base_price + price_variation) * self.markup)
        buy_price = int(sell_price * 0.5)  # 收购价是售价的50%
        
        self.inventory[item_id] = ShopItem(
            item_id=item_id,
            item_data=item_data,
            quantity=quantity,
            sell_price=sell_price,
            buy_price=buy_price
        )
    
    def list_goods(self) -> List[ShopItem]:
        """列出所有在售商品"""
        return [item for item in self.inventory.values() if item.quantity > 0]
    
    def get_item_details(self, item_id: str) -> Optional[Dict]:
        """获取商品详情"""
        if item_id in self.inventory:
            item = self.inventory[item_id]
            return {
                'name': item.item_data['name'],
                'type': item.item_data['type'],
                'grade': item.item_data['grade'],
                'description': item.item_data['description'],
                'effect': item.item_data.get('effect', {}),
                'sell_price': item.sell_price,
                'buy_price': item.buy_price,
                'quantity': item.quantity
            }
        return None
    
    def bargain(self, item_id: str, offered_price: int, player_charisma: int) -> Tuple[int, str]:
        """
        讨价还价
        
        Args:
            item_id: 物品ID
            offered_price: 玩家出价（下品灵石）
            player_charisma: 玩家魅力值
            
        Returns:
            (结果代码, 消息)
            结果代码: 0=拒绝, 1=成交, -1=还价
        """
        if item_id not in self.inventory:
            return (0, "掌柜疑惑地说：「我们店里没有这个东西啊。」")
        
        item = self.inventory[item_id]
        
        # 玩家出价高于标价，直接成交
        if offered_price >= item.sell_price:
            return (1, f"掌柜喜笑颜开：「成交！{item.item_data['name']}是您的了！」")
        
        # 计算心理底价
        floor_price = int(item.sell_price * self.min_price_factor)
        
        # 魅力加成：每10点魅力可以再降价2%
        charisma_discount = max(0, (player_charisma - 50) // 10) * 0.02
        floor_price = int(floor_price * (1 - charisma_discount))
        
        # 声望加成
        if self.player_reputation > 50:
            floor_price = int(floor_price * 0.95)
        
        # 出价低于底价，拒绝
        if offered_price < floor_price:
            if offered_price < floor_price * 0.8:
                return (0, "掌柜脸色一变：「道友莫要开玩笑，这个价格太离谱了！」")
            else:
                return (0, "掌柜摇了摇头：「这个价格实在太低了，小本生意，还请理解。」")
        
        # 在底价和标价之间，根据概率决定
        price_ratio = (offered_price - floor_price) / (item.sell_price - floor_price)
        
        # 成功率 = 基础成功率 + 价格比例加成 + 魅力加成
        base_success_rate = 0.3
        charisma_bonus = min(0.3, player_charisma / 200)  # 最多30%加成
        success_rate = base_success_rate + price_ratio * 0.5 + charisma_bonus
        
        if random() < success_rate:
            # 成交
            return (1, f"掌柜犹豫了一下：「罢了，看在道友诚心的份上，{offered_price}就{offered_price}吧！」")
        else:
            # 还价
            counter_price = int(offered_price + (item.sell_price - offered_price) * 0.3)
            return (-1, f"掌柜搓了搓手：「这样吧，{counter_price}灵石，不能再少了！」")
    
    def attempt_leave_discount(self, item_id: str, last_offer: int) -> Optional[Tuple[int, str]]:
        """
        假装离开时的挽留机制
        
        Args:
            item_id: 物品ID
            last_offer: 玩家最后的出价
            
        Returns:
            如果触发挽留，返回(新价格, 消息)，否则返回None
        """
        if item_id not in self.inventory:
            return None
        
        item = self.inventory[item_id]
        floor_price = int(item.sell_price * self.min_price_factor)
        
        # 只有当玩家出价接近底价时才可能触发挽留
        if last_offer >= floor_price * 0.95:
            # 50%概率触发挽留
            if random() < 0.5:
                # 给出一个略高于玩家出价的新价格
                new_price = int(last_offer * 1.05)
                # 但不能低于底价
                new_price = max(new_price, floor_price)
                
                messages = [
                    f"掌柜急忙喊道：「道友且慢！{new_price}灵石如何？就当交个朋友！」",
                    f"掌柜连忙招手：「别走别走！{new_price}灵石，这是最低价了！」",
                    f"掌柜叹了口气：「唉，{new_price}灵石拿走吧，就当给道友个面子。」"
                ]
                
                from random import choice
                return (new_price, choice(messages))
        
        return None
    
    def complete_purchase(self, item_id: str, quantity: int, final_price: int) -> None:
        """
        完成购买
        
        Args:
            item_id: 物品ID
            quantity: 购买数量
            final_price: 最终成交价（单价）
        """
        if item_id in self.inventory:
            self.inventory[item_id].quantity -= quantity
            
            # 记录交易历史
            self.trade_history.append({
                'type': 'sell',
                'item_id': item_id,
                'quantity': quantity,
                'price': final_price,
                'markup': final_price / self.inventory[item_id].item_data['base_price']
            })
            
            # 提升声望
            self.player_reputation += 1
    
    def complete_sale(self, item_id: str, quantity: int, item_data: Dict[str, Any]) -> None:
        """
        完成出售（玩家卖给商店）
        
        Args:
            item_id: 物品ID
            quantity: 出售数量
            item_data: 物品数据
        """
        # 如果商店没有这个物品，添加到库存
        if item_id not in self.inventory:
            self.add_goods(item_id, 0, item_data)
        
        self.inventory[item_id].quantity += quantity
        
        # 记录交易历史
        self.trade_history.append({
            'type': 'buy',
            'item_id': item_id,
            'quantity': quantity,
            'price': self.inventory[item_id].buy_price
        })
        
        # 提升声望
        self.player_reputation += 1


class MarketStall(Shopkeeper):
    """集市摊贩（流动商贩）"""
    
    def __init__(self, name: str, stall_type: str = "random") -> None:
        # 集市摊贩价格波动更大，砍价空间也更大
        super().__init__(
            name=name,
            shop_type=stall_type,
            markup=uniform(0.9, 1.5),  # 价格在90%-150%之间浮动
            min_price_factor=0.8  # 心理底价更低，可以砍价到80%
        )
        self.is_special_vendor = random() < 0.1  # 10%概率是特殊商贩
        
    def refresh_inventory(self) -> None:
        """刷新摊位商品（每日刷新）"""
        self.inventory.clear()
        self.markup = uniform(0.9, 1.5)
        
        # TODO: 根据摊位类型随机生成商品
        
    def has_rare_items(self) -> bool:
        """是否有稀有物品"""
        return self.is_special_vendor


class BlackMarket(Shopkeeper):
    """黑市商人"""
    
    def __init__(self, name: str = "神秘商人") -> None:
        super().__init__(
            name=name,
            shop_type="black_market",
            markup=uniform(2.0, 3.0),  # 黑市价格是正常的2-3倍
            min_price_factor=0.7  # 但可以砍价到70%
        )
        self.trust_level = 0  # 信任等级
        
    def is_accessible(self, player_reputation: int) -> bool:
        """
        是否可以访问黑市
        
        Args:
            player_reputation: 玩家声望
            
        Returns:
            是否可访问
        """
        # 需要一定声望或特殊条件才能访问黑市
        return player_reputation >= 100 or self.trust_level > 0
