# core/trade_commands.py
"""
交易系统命令处理器

处理商店、交易、讨价还价等相关命令。
"""

from typing import Any, Dict, List, Optional, Tuple
import logging
from .trade_system import TradeSystem, Shopkeeper, MarketStall, BlackMarket
from .character import Character

logger = logging.getLogger(__name__)


class TradeCommandHandler:
    """交易命令处理器"""
    
    def __init__(self, trade_system: TradeSystem) -> None:
        self.trade_system = trade_system
        self.current_shop: Optional[Shopkeeper] = None
        self.bargaining_state: Dict[str, Any] = {}  # 记录讨价还价状态
        self._init_shops()
    
    def _init_shops(self) -> None:
        """初始化默认商店"""
        # 万宝楼 - 综合商店
        wanbao_shop = Shopkeeper("万宝楼掌柜", "general", markup=1.2)
        wanbao_shop.add_goods("hui_qi_dan", 25, self.trade_system.get_item_info("hui_qi_dan"))
        wanbao_shop.add_goods("xiao_huan_dan", 20, self.trade_system.get_item_info("xiao_huan_dan"))
        wanbao_shop.add_goods("bi_gu_dan", 10, self.trade_system.get_item_info("bi_gu_dan"))
        wanbao_shop.add_goods("huo_ball_fu", 15, self.trade_system.get_item_info("huo_ball_fu"))
        wanbao_shop.add_goods("shen_xing_fu", 10, self.trade_system.get_item_info("shen_xing_fu"))
        wanbao_shop.add_goods("fei_feng_jian", 2, self.trade_system.get_item_info("fei_feng_jian"))
        self.trade_system.shopkeepers["wanbao"] = wanbao_shop
        
        # 灵丹阁 - 丹药专卖
        lingdan_shop = Shopkeeper("灵丹阁老板", "pills", markup=1.15)
        lingdan_shop.add_goods("hui_qi_dan", 50, self.trade_system.get_item_info("hui_qi_dan"))
        lingdan_shop.add_goods("xiao_huan_dan", 30, self.trade_system.get_item_info("xiao_huan_dan"))
        lingdan_shop.add_goods("da_huan_dan", 10, self.trade_system.get_item_info("da_huan_dan"))
        lingdan_shop.add_goods("qing_xin_dan", 5, self.trade_system.get_item_info("qing_xin_dan"))
        lingdan_shop.add_goods("bi_gu_dan", 20, self.trade_system.get_item_info("bi_gu_dan"))
        lingdan_shop.add_goods("zhu_ji_dan", 1, self.trade_system.get_item_info("zhu_ji_dan"))
        self.trade_system.shopkeepers["lingdan"] = lingdan_shop
        
        # 炼器坊 - 法器装备
        lianqi_shop = Shopkeeper("炼器坊主人", "weapons", markup=1.25)
        lianqi_shop.add_goods("fei_feng_jian", 5, self.trade_system.get_item_info("fei_feng_jian"))
        lianqi_shop.add_goods("mu_shield", 3, self.trade_system.get_item_info("mu_shield"))
        lianqi_shop.add_goods("qing_feng_dao_pao", 2, self.trade_system.get_item_info("qing_feng_dao_pao"))
        lianqi_shop.add_goods("yi_jie_ju_ling_pan", 1, self.trade_system.get_item_info("yi_jie_ju_ling_pan"))
        self.trade_system.shopkeepers["lianqi"] = lianqi_shop
    
    def handle_shop_command(self, player: Character, shop_name: str = "wanbao") -> str:
        """处理进入商店命令"""
        if shop_name not in self.trade_system.shopkeepers:
            return f"找不到名为'{shop_name}'的商店。"
        
        self.current_shop = self.trade_system.shopkeepers[shop_name]
        self.bargaining_state.clear()
        
        return self._display_shop_inventory()
    
    def _display_shop_inventory(self) -> str:
        """显示商店物品列表"""
        if not self.current_shop:
            return "你还没有进入任何商店。"
        
        output = [f"\n【{self.current_shop.name}】欢迎光临！\n"]
        output.append("┌─────商品─────────────────────────┬─库存─┬─售价(下品)─┐")
        
        goods = self.current_shop.list_goods()
        for i, item in enumerate(goods, 1):
            name = item.item_data['name'].ljust(20)
            qty = str(item.quantity).center(6)
            price = str(item.sell_price).center(12)
            output.append(f"│ {i}. {name} │{qty}│{price}│")
        
        output.append("└──────────────────────────────────┴──────┴────────────┘")
        output.append("\n可用命令：")
        output.append("  购买 [编号] [数量] - 购买商品")
        output.append("  出售 [物品名] [数量] - 出售物品")
        output.append("  详情 [编号] - 查看商品详情")
        output.append("  还价 [编号] [价格] - 讨价还价")
        output.append("  离开 - 离开商店")
        
        return "\n".join(output)
    
    def handle_buy_command(self, player: Character, item_index: int, quantity: int = 1) -> str:
        """处理购买命令"""
        if not self.current_shop:
            return "你还没有进入任何商店。"
        
        goods = self.current_shop.list_goods()
        if item_index < 1 or item_index > len(goods):
            return "无效的商品编号。"
        
        item = goods[item_index - 1]
        
        if quantity > item.quantity:
            return f"库存不足！当前只有 {item.quantity} 个。"
        
        # 检查是否有讨价还价的价格
        final_price = self.bargaining_state.get(item.item_id, item.sell_price)
        total_cost = final_price * quantity
        
        # 检查玩家灵石
        if player.get_total_lingshi() < total_cost:
            return f"灵石不足！需要 {total_cost} 下品灵石。你只有 {player.get_lingshi_description()}。"
        
        # 检查背包空间
        if not player.inventory.add(item.item_id, quantity):
            player.inventory.remove(item.item_id, quantity)  # 回滚
            return "背包空间不足！"
        
        # 扣除灵石
        if not player.spend_lingshi(total_cost):
            player.inventory.remove(item.item_id, quantity)  # 回滚
            return "支付失败！"
        
        # 更新商店库存
        self.current_shop.complete_purchase(item.item_id, quantity, final_price)
        
        # 清除讨价还价状态
        if item.item_id in self.bargaining_state:
            del self.bargaining_state[item.item_id]
        
        return f"成功购买 {item.item_data['name']} x{quantity}，花费 {total_cost} 下品灵石。"
    
    def handle_sell_command(self, player: Character, item_name: str, quantity: int = 1) -> str:
        """处理出售命令"""
        if not self.current_shop:
            return "你还没有进入任何商店。"
        
        # 查找物品ID
        item_id = None
        for iid, idata in self.trade_system.items_data.items():
            if idata['name'] == item_name:
                item_id = iid
                break
        
        if not item_id:
            return f"未知的物品：{item_name}"
        
        # 检查玩家是否有该物品
        if not player.inventory.has(item_id, quantity):
            return f"你没有足够的 {item_name}。"
        
        # 获取收购价
        if item_id in self.current_shop.inventory:
            buy_price = self.current_shop.inventory[item_id].buy_price
        else:
            # 如果商店没有这个物品，按基础价的40%收购
            base_price = self.trade_system.items_data[item_id].get('base_price', 10)
            buy_price = int(base_price * 0.4)
        
        total_income = buy_price * quantity
        
        # 移除物品
        if not player.inventory.remove(item_id, quantity):
            return "出售失败！"
        
        # 添加灵石
        player.add_lingshi(total_income)
        
        # 更新商店库存
        self.current_shop.complete_sale(item_id, quantity, self.trade_system.items_data[item_id])
        
        return f"成功出售 {item_name} x{quantity}，获得 {total_income} 下品灵石。"
    
    def handle_item_detail_command(self, item_index: int) -> str:
        """处理查看商品详情命令"""
        if not self.current_shop:
            return "你还没有进入任何商店。"
        
        goods = self.current_shop.list_goods()
        if item_index < 1 or item_index > len(goods):
            return "无效的商品编号。"
        
        item = goods[item_index - 1]
        details = self.current_shop.get_item_details(item.item_id)
        
        output = [f"\n【{details['name']}】"]
        output.append(f"类型：{details['type']}")
        output.append(f"品级：{details['grade']}")
        output.append(f"售价：{details['sell_price']} 下品灵石")
        output.append(f"收购价：{details['buy_price']} 下品灵石")
        output.append(f"库存：{details['quantity']}")
        output.append(f"\n描述：{details['description']}")
        
        if details['effect']:
            output.append("\n效果：")
            for key, value in details['effect'].items():
                # 转换效果键名为中文
                effect_name = self._translate_effect_key(key)
                output.append(f"  {effect_name}：{value}")
        
        return "\n".join(output)
    
    def _translate_effect_key(self, key: str) -> str:
        """将效果键名转换为中文"""
        translations = {
            'mana_restore': '灵力恢复',
            'mana_regen_buff': '灵力回复加成',
            'health_restore': '气血恢复',
            'heal_pct': '气血恢复百分比',
            'breakthrough_bonus': '突破成功率加成',
            'suppress_hunger_hours': '辟谷时长(小时)',
            'cultivation_speed_mul': '修炼速度倍率',
            'duration': '持续时间(秒)',
            'attack_bonus': '攻击力加成',
            'defense_bonus': '防御力加成',
            'fire_damage': '火焰伤害',
            'single_use': '一次性使用',
            'clear_mind': '清心净神',
            'cultivation_bonus': '修炼效率加成',
            'detoxify': '解毒',
            'ice_resistance': '冰系抗性',
            'mana_bonus': '灵力上限加成',
            'mana_regen': '灵力恢复速度',
            'speed_boost': '速度提升倍率',
            'invincible_duration': '无敌时长(秒)',
            'trap_duration': '困敌时长(秒)',
            'defense_formation': '防御阵法',
            'accuracy_bonus': '命中加成',
            'wood_resistance': '木系抗性',
            'heal_injuries': '治疗内伤',
            'cultivation_exp': '修为值'
        }
        return translations.get(key, key)
    
    def handle_bargain_command(self, player: Character, item_index: int, offered_price: int) -> str:
        """处理讨价还价命令"""
        if not self.current_shop:
            return "你还没有进入任何商店。"
        
        goods = self.current_shop.list_goods()
        if item_index < 1 or item_index > len(goods):
            return "无效的商品编号。"
        
        item = goods[item_index - 1]
        
        # 计算玩家的有效魅力值（基础魅力 + 讨价还价技能）
        effective_charisma = player.charisma + player.bargain_skill * 5
        
        result, message = self.current_shop.bargain(
            item.item_id, 
            offered_price, 
            effective_charisma
        )
        
        if result == 1:
            # 成交，记录价格
            self.bargaining_state[item.item_id] = offered_price
            return message + f"\n（商品价格已更新为 {offered_price} 下品灵石）"
        elif result == -1:
            # 还价，记录掌柜的还价
            counter_price = int(offered_price + (item.sell_price - offered_price) * 0.3)
            self.bargaining_state[item.item_id] = counter_price
            return message
        else:
            # 拒绝
            return message
    
    def handle_leave_shop_command(self, player: Character) -> str:
        """处理离开商店命令"""
        if not self.current_shop:
            return "你还没有进入任何商店。"
        
        # 检查是否有正在讨价还价的商品
        if self.bargaining_state:
            # 尝试触发挽留机制
            for item_id, last_offer in self.bargaining_state.items():
                result = self.current_shop.attempt_leave_discount(item_id, last_offer)
                if result:
                    new_price, message = result
                    self.bargaining_state[item_id] = new_price
                    return message + f"\n\n是否接受？（输入'接受'或'拒绝'）"
        
        self.current_shop = None
        self.bargaining_state.clear()
        return "你离开了商店。"
    
    def handle_accept_offer_command(self, player: Character) -> str:
        """处理接受掌柜报价"""
        if not self.current_shop or not self.bargaining_state:
            return "没有待处理的报价。"
        
        # 找到最新的报价商品
        item_id = list(self.bargaining_state.keys())[-1]
        return f"成交！请使用'购买'命令完成交易。"
    
    def handle_reject_offer_command(self, player: Character) -> str:
        """处理拒绝掌柜报价"""
        if not self.current_shop:
            return "你还没有进入任何商店。"
        
        self.current_shop = None
        self.bargaining_state.clear()
        return "你摇了摇头，离开了商店。"
