"""
经济系统模块
管理游戏内的经济活动
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import math


@dataclass
class Currency:
    """货币"""
    name: str
    symbol: str
    base_value: float  # 相对于基础货币的价值


class Market:
    """市场"""
    
    def __init__(self, name: str):
        self.name = name
        self.items: Dict[str, float] = {}  # 物品ID -> 价格
        self.supply: Dict[str, int] = {}   # 物品ID -> 供应量
        self.demand: Dict[str, float] = {} # 物品ID -> 需求系数
    
    def update_price(self, item_id: str):
        """根据供需更新价格"""
        if item_id not in self.items:
            return
            
        base_price = self.items[item_id]
        supply = self.supply.get(item_id, 1)
        demand = self.demand.get(item_id, 1.0)
        
        # 简单的供需公式
        price_modifier = demand / max(1, math.sqrt(supply))
        new_price = base_price * price_modifier
        
        self.items[item_id] = max(1, int(new_price))


class EconomySystem:
    """经济系统"""
    
    def __init__(self):
        self.currencies: Dict[str, Currency] = {}
        self.markets: Dict[str, Market] = {}
        self.exchange_rates: Dict[str, Dict[str, float]] = {}
        self._init_currencies()
        self._init_markets()
    
    def _init_currencies(self):
        """初始化货币"""
        self.currencies = {
            "gold": Currency("金币", "G", 1.0),
            "spirit_stone": Currency("灵石", "SS", 100.0),
            "contribution": Currency("贡献点", "CP", 10.0)
        }
        
        # 设置汇率
        self.exchange_rates = {
            "gold": {"spirit_stone": 0.01, "contribution": 0.1},
            "spirit_stone": {"gold": 100.0, "contribution": 10.0},
            "contribution": {"gold": 10.0, "spirit_stone": 0.1}
        }
    
    def _init_markets(self):
        """初始化市场"""
        # 创建主城市场
        main_market = Market("主城市场")
        main_market.items = {
            "healing_potion": 50,
            "mana_potion": 80,
            "iron_sword": 200,
            "wooden_staff": 150
        }
        self.markets["main_city"] = main_market
    
    def convert_currency(self, amount: float, from_type: str, to_type: str) -> float:
        """货币转换"""
        if from_type == to_type:
            return amount
            
        if from_type in self.exchange_rates and to_type in self.exchange_rates[from_type]:
            rate = self.exchange_rates[from_type][to_type]
            return amount * rate
            
        return 0.0
    
    def get_item_price(self, item_id: str, market_name: str = "main_city") -> Optional[float]:
        """获取物品价格"""
        market = self.markets.get(market_name)
        if market and item_id in market.items:
            return market.items[item_id]
        return None
    
    def buy_item(self, item_id: str, quantity: int, market_name: str = "main_city") -> Optional[float]:
        """购买物品"""
        market = self.markets.get(market_name)
        if not market or item_id not in market.items:
            return None
            
        price = market.items[item_id]
        total_cost = price * quantity
        
        # 更新供应量
        market.supply[item_id] = market.supply.get(item_id, 100) - quantity
        
        # 更新价格
        market.update_price(item_id)
        
        return total_cost
    
    def sell_item(self, item_id: str, quantity: int, market_name: str = "main_city") -> Optional[float]:
        """出售物品"""
        market = self.markets.get(market_name)
        if not market:
            return None
            
        # 如果市场没有这个物品，创建一个基础价格
        if item_id not in market.items:
            market.items[item_id] = 10  # 基础价格
            
        price = market.items[item_id] * 0.7  # 出售价格是购买价格的70%
        total_value = price * quantity
        
        # 更新供应量
        market.supply[item_id] = market.supply.get(item_id, 0) + quantity
        
        # 更新价格
        market.update_price(item_id)
        
        return total_value


# 全局实例
economy_system = EconomySystem()
