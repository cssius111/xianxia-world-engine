# npc/trading_system.py
"""
交易系统

实现NPC商店和交易功能。
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ItemType(Enum):
    """物品类型"""
    CONSUMABLE = "consumable"    # 消耗品
    EQUIPMENT = "equipment"      # 装备
    MATERIAL = "material"        # 材料
    SKILL_BOOK = "skill_book"    # 技能书
    QUEST_ITEM = "quest_item"    # 任务物品
    MISC = "misc"               # 杂物


@dataclass
class ItemData:
    """物品数据"""
    id: str
    name: str
    type: ItemType
    description: str
    
    # 价格
    buy_price: int = 0       # 购买价格（灵石）
    sell_price: int = 0      # 出售价格
    
    # 使用效果
    effects: Dict[str, Any] = field(default_factory=dict)
    
    # 装备属性
    equipment_slot: Optional[str] = None
    equipment_stats: Dict[str, int] = field(default_factory=dict)
    
    # 其他属性
    stackable: bool = True
    max_stack: int = 99
    level_requirement: int = 0
    
    # 额外数据
    extra_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ShopItem:
    """商店物品"""
    item_id: str
    quantity: int = -1  # -1表示无限
    discount: float = 1.0  # 折扣率
    requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Shop:
    """商店"""
    id: str
    name: str
    owner_npc: str
    
    # 商品列表
    items: List[ShopItem] = field(default_factory=list)
    
    # 商店属性
    buy_rate: float = 1.0   # 购买价格倍率
    sell_rate: float = 0.5  # 出售价格倍率
    
    # 刷新设置
    refresh_interval: int = 0  # 刷新间隔（0表示不刷新）
    last_refresh: int = 0
    
    # 额外数据
    extra_data: Dict[str, Any] = field(default_factory=dict)


class TradingSystem:
    """
    交易系统
    
    管理商店和物品交易。
    """
    
    def __init__(self):
        """初始化交易系统"""
        self.items: Dict[str, ItemData] = {}
        self.shops: Dict[str, Shop] = {}
        
        # 初始化默认物品和商店
        self._init_default_items()
        self._init_default_shops()
        
        logger.info("交易系统初始化")
    
    def _init_default_items(self):
        """初始化默认物品"""
        # 消耗品
        items = [
            ItemData(
                id="healing_pill_low",
                name="低阶疗伤丹",
                type=ItemType.CONSUMABLE,
                description="最基础的疗伤丹药，可以恢复少量生命值。",
                buy_price=50,
                sell_price=20,
                effects={"heal_hp": 50}
            ),
            ItemData(
                id="mana_pill_low",
                name="低阶回灵丹",
                type=ItemType.CONSUMABLE,
                description="恢复少量法力的丹药。",
                buy_price=80,
                sell_price=30,
                effects={"restore_mana": 30}
            ),
            ItemData(
                id="stamina_pill_low",
                name="低阶活力丹",
                type=ItemType.CONSUMABLE,
                description="恢复体力的丹药。",
                buy_price=40,
                sell_price=15,
                effects={"restore_stamina": 40}
            ),
            
            # 装备
            ItemData(
                id="iron_sword",
                name="精铁剑",
                type=ItemType.EQUIPMENT,
                description="用精铁打造的长剑，适合初学者使用。",
                buy_price=200,
                sell_price=80,
                equipment_slot="weapon",
                equipment_stats={"attack_power": 10},
                stackable=False
            ),
            ItemData(
                id="cloth_armor",
                name="布衣",
                type=ItemType.EQUIPMENT,
                description="普通的布制衣物，提供基础防护。",
                buy_price=150,
                sell_price=60,
                equipment_slot="armor",
                equipment_stats={"defense": 5},
                stackable=False
            ),
            
            # 材料
            ItemData(
                id="spirit_stone_low",
                name="下品灵石",
                type=ItemType.MATERIAL,
                description="修仙界的通用货币，蕴含少量灵气。",
                buy_price=1,
                sell_price=1,
                max_stack=9999
            ),
            ItemData(
                id="iron_ore",
                name="铁矿石",
                type=ItemType.MATERIAL,
                description="炼器的基础材料。",
                buy_price=20,
                sell_price=8
            ),
            
            # 技能书
            ItemData(
                id="skill_book_basic_meditation",
                name="基础吐纳法",
                type=ItemType.SKILL_BOOK,
                description="记载着基础修炼方法的书籍。",
                buy_price=500,
                sell_price=200,
                effects={"learn_skill": "basic_meditation"},
                stackable=False,
                level_requirement=1
            )
        ]
        
        for item in items:
            self.register_item(item)
    
    def _init_default_shops(self):
        """初始化默认商店"""
        # 王老板的基础商店
        wang_shop = Shop(
            id="wang_basic_shop",
            name="王记杂货铺",
            owner_npc="npc_wang_boss",
            items=[
                ShopItem("healing_pill_low", quantity=10),
                ShopItem("mana_pill_low", quantity=5),
                ShopItem("stamina_pill_low", quantity=10),
                ShopItem("iron_sword", quantity=2),
                ShopItem("cloth_armor", quantity=3),
                ShopItem("skill_book_basic_meditation", quantity=1,
                        requirements={"min_relationship": 10})
            ]
        )
        self.register_shop(wang_shop)
    
    def register_item(self, item: ItemData):
        """注册物品"""
        self.items[item.id] = item
        logger.debug(f"注册物品: {item.name}")
    
    def register_shop(self, shop: Shop):
        """注册商店"""
        self.shops[shop.id] = shop
        logger.debug(f"注册商店: {shop.name}")
    
    def get_item(self, item_id: str) -> Optional[ItemData]:
        """获取物品数据"""
        return self.items.get(item_id)
    
    def get_shop(self, shop_id: str) -> Optional[Shop]:
        """获取商店"""
        return self.shops.get(shop_id)
    
    def get_shop_items(self, shop_id: str, player_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        获取商店物品列表
        
        Args:
            shop_id: 商店ID
            player_context: 玩家上下文（用于检查购买条件）
            
        Returns:
            可购买的物品列表
        """
        shop = self.get_shop(shop_id)
        if not shop:
            return []
        
        available_items = []
        
        for shop_item in shop.items:
            # 检查物品是否满足购买条件
            if not self._check_requirements(shop_item.requirements, player_context):
                continue
            
            item_data = self.get_item(shop_item.item_id)
            if not item_data:
                continue
            
            # 计算实际价格
            actual_price = int(item_data.buy_price * shop.buy_rate * shop_item.discount)
            
            item_info = {
                'id': item_data.id,
                'name': item_data.name,
                'type': item_data.type.value,
                'description': item_data.description,
                'price': actual_price,
                'quantity': shop_item.quantity,
                'level_requirement': item_data.level_requirement
            }
            
            available_items.append(item_info)
        
        return available_items
    
    def buy_item(self, shop_id: str, item_id: str, quantity: int,
                 player_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        购买物品
        
        Args:
            shop_id: 商店ID
            item_id: 物品ID
            quantity: 购买数量
            player_context: 玩家上下文
            
        Returns:
            交易结果
        """
        result = {
            'success': False,
            'message': '',
            'cost': 0,
            'items': []
        }
        
        # 获取商店
        shop = self.get_shop(shop_id)
        if not shop:
            result['message'] = '商店不存在'
            return result
        
        # 查找商品
        shop_item = None
        for item in shop.items:
            if item.item_id == item_id:
                shop_item = item
                break
        
        if not shop_item:
            result['message'] = '商店没有这个物品'
            return result
        
        # 检查购买条件
        if not self._check_requirements(shop_item.requirements, player_context):
            result['message'] = '不满足购买条件'
            return result
        
        # 获取物品数据
        item_data = self.get_item(item_id)
        if not item_data:
            result['message'] = '物品数据不存在'
            return result
        
        # 检查等级要求
        player_level = player_context.get('player_level', 0)
        if player_level < item_data.level_requirement:
            result['message'] = f'需要达到{item_data.level_requirement}级才能购买'
            return result
        
        # 检查库存
        if shop_item.quantity != -1:
            if quantity > shop_item.quantity:
                result['message'] = '商店库存不足'
                return result
        
        # 计算价格
        unit_price = int(item_data.buy_price * shop.buy_rate * shop_item.discount)
        total_cost = unit_price * quantity
        
        # 检查玩家灵石
        player_money = player_context.get('spirit_stones', 0)
        if player_money < total_cost:
            result['message'] = '灵石不足'
            return result
        
        # 交易成功
        result['success'] = True
        result['message'] = f'成功购买{item_data.name} x{quantity}'
        result['cost'] = total_cost
        result['items'] = [{
            'id': item_id,
            'name': item_data.name,
            'quantity': quantity
        }]
        
        # 更新商店库存
        if shop_item.quantity != -1:
            shop_item.quantity -= quantity
        
        return result
    
    def sell_item(self, shop_id: str, item_id: str, quantity: int) -> Dict[str, Any]:
        """
        出售物品
        
        Args:
            shop_id: 商店ID
            item_id: 物品ID
            quantity: 出售数量
            
        Returns:
            交易结果
        """
        result = {
            'success': False,
            'message': '',
            'income': 0
        }
        
        # 获取商店
        shop = self.get_shop(shop_id)
        if not shop:
            result['message'] = '商店不存在'
            return result
        
        # 获取物品数据
        item_data = self.get_item(item_id)
        if not item_data:
            result['message'] = '物品不存在'
            return result
        
        # 某些物品不能出售
        if item_data.type == ItemType.QUEST_ITEM:
            result['message'] = '任务物品不能出售'
            return result
        
        # 计算价格
        unit_price = int(item_data.sell_price * shop.sell_rate)
        total_income = unit_price * quantity
        
        # 交易成功
        result['success'] = True
        result['message'] = f'成功出售{item_data.name} x{quantity}'
        result['income'] = total_income
        
        return result
    
    def _check_requirements(self, requirements: Dict[str, Any], 
                           context: Dict[str, Any]) -> bool:
        """检查需求条件"""
        for req_type, req_value in requirements.items():
            if req_type == 'min_level':
                if context.get('player_level', 0) < req_value:
                    return False
                    
            elif req_type == 'min_relationship':
                if context.get('npc_relationship', 0) < req_value:
                    return False
                    
            elif req_type == 'has_flag':
                flags = context.get('flags', {})
                if not flags.get(req_value, False):
                    return False
        
        return True
    
    def refresh_shop(self, shop_id: str, game_time: int):
        """
        刷新商店
        
        Args:
            shop_id: 商店ID
            game_time: 游戏时间
        """
        shop = self.get_shop(shop_id)
        if not shop or shop.refresh_interval <= 0:
            return
        
        if game_time - shop.last_refresh >= shop.refresh_interval:
            # TODO: 实现商店刷新逻辑
            shop.last_refresh = game_time
            logger.info(f"商店 {shop.name} 已刷新")


# 物品数据模板
ITEM_TEMPLATES = {
    "consumables": {
        "healing_pill_mid": {
            "name": "中阶疗伤丹",
            "type": "consumable",
            "description": "品质不错的疗伤丹药，可以恢复大量生命值。",
            "buy_price": 200,
            "sell_price": 80,
            "effects": {"heal_hp": 200},
            "level_requirement": 5
        },
        "breakthrough_pill": {
            "name": "破境丹",
            "type": "consumable",
            "description": "辅助突破境界的珍贵丹药。",
            "buy_price": 1000,
            "sell_price": 400,
            "effects": {"breakthrough_chance": 0.2},
            "level_requirement": 9,
            "stackable": False
        }
    },
    "equipment": {
        "spirit_sword_low": {
            "name": "下品灵剑",
            "type": "equipment",
            "description": "蕴含微弱灵气的法剑。",
            "buy_price": 800,
            "sell_price": 320,
            "equipment_slot": "weapon",
            "equipment_stats": {"attack_power": 25, "spell_power": 10},
            "level_requirement": 5,
            "stackable": False
        }
    }
}
