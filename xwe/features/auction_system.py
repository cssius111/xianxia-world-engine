"""
拍卖行系统模块

实现了完整的拍卖行功能，包括：
- 多种拍卖模式（英式、荷兰式）
- NPC智能竞价系统
- 动态事件触发
- VIP特权系统
- 拍后事件链
"""

import json
import random
import time
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from enum import Enum
from dataclasses import dataclass

from xwe.core.data_loader import DataLoader
from xwe.features.visual_enhancement import VisualEnhancement


class AuctionMode(Enum):
    """拍卖模式"""
    ENGLISH = "english"  # 英式拍卖（递增）
    DUTCH = "dutch"      # 荷兰式拍卖（递减）
    SEALED = "sealed"    # 密封投标


class BidderType(Enum):
    """竞拍者类型"""
    PLAYER = "player"
    NPC = "npc"
    GRUDGE = "grudge"    # 仇敌
    VIP = "vip"          # VIP贵宾


@dataclass
class AuctionItem:
    """拍卖物品"""
    id: str
    name: str
    description: str
    tier: str
    base_price: int
    max_price: int
    current_bid: int = 0
    current_bidder: Optional[str] = None
    bid_history: List[Tuple[str, int]] = None
    
    def __post_init__(self):
        if self.bid_history is None:
            self.bid_history = []


@dataclass
class Bidder:
    """竞拍者"""
    name: str
    type: BidderType
    archetype: str
    wealth: int
    max_price: int
    personality: Dict[str, float]
    grudge_target: Optional[str] = None
    bid_count: int = 0
    items_won: List[str] = None
    
    def __post_init__(self):
        if self.items_won is None:
            self.items_won = []


class AuctionSystem:
    """拍卖行系统"""
    
    def __init__(self):
        """初始化拍卖系统"""
        self.data_loader = DataLoader()
        self.visual = VisualEnhancement()
        
        # 加载配置数据
        self._load_auction_data()
        
        # 当前拍卖状态
        self.current_auction = None
        self.current_item = None
        self.bidders = []
        self.player_vip = False
        self.auction_log = []
        
    def _load_auction_data(self):
        """加载拍卖行数据"""
        try:
            # 加载拍卖配置
            config_path = Path("xwe/data/auction/auction_config.json")
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)['auction_house_config']
            
            # 加载拍卖物品
            items_path = Path("xwe/data/auction/auction_items.json")
            with open(items_path, 'r', encoding='utf-8') as f:
                self.auction_items = json.load(f)['auction_items']
            
            # 加载NPC数据
            npcs_path = Path("xwe/data/auction/auction_npcs.json")
            with open(npcs_path, 'r', encoding='utf-8') as f:
                npc_data = json.load(f)
                self.auctioneer = npc_data['auctioneer']
                self.bidder_archetypes = npc_data['bidder_archetypes']
                self.grudge_npcs = npc_data['grudge_npcs']
                self.auction_events = npc_data['auction_events']
        except Exception as e:
            print(f"加载拍卖数据失败: {e}")
            # 使用默认数据
            self.config = self._get_default_config()
            self.auction_items = self._get_default_items()
            
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "name": "天宝拍卖行",
            "auction_rules": {
                "min_bid_increment": 0.05,
                "commission_rate": 0.1
            }
        }
    
    def _get_default_items(self) -> Dict:
        """获取默认物品"""
        return {
            "low_tier": [{
                "id": "basic_pill",
                "name": "聚气丹",
                "description": "基础修炼丹药",
                "tier": "低阶",
                "base_price": 100,
                "max_price": 300
            }]
        }
    
    def start_auction(self, player, auction_type: str = "regular") -> str:
        """开始拍卖会"""
        self.auction_log = []
        
        # 检查进入条件
        entry_fee = self.config.get('entry_requirements', {}).get('entry_fee', 100)
        if player.get_total_lingshi() < entry_fee:
            return f"进入{self.config['name']}需要{entry_fee}灵石入场费，您的灵石不足。"
        
        # 扣除入场费
        player.spend_lingshi(entry_fee)
        
        # 检查VIP资格
        self.player_vip = self._check_vip_status(player)
        
        # 生成拍卖物品列表
        items = self._generate_auction_items(auction_type)
        
        # 生成NPC竞拍者
        self.bidders = self._generate_bidders(player, len(items))
        
        # 开始拍卖流程
        output = []
        output.append(self.visual.get_colored_text(
            f"\n{'='*60}\n欢迎来到{self.config['name']}！\n{'='*60}\n",
            'YELLOW'
        ))
        
        if self.player_vip:
            output.append(self.visual.get_colored_text(
                "【VIP】您被引导至贵宾包厢，享受匿名竞拍特权。\n",
                'GOLD'
            ))
        
        output.append(f"\n拍卖师{self.auctioneer['name']}登场：")
        output.append(f"「{random.choice(self.auctioneer['catchphrases'])}」\n")
        output.append(f"本场拍卖会共有{len(items)}件拍品，祝各位满载而归！\n")
        
        # 逐个拍卖物品
        for i, item in enumerate(items):
            output.append(f"\n{'-'*50}")
            output.append(f"第{i+1}件拍品：")
            result = self._auction_item(player, item, i+1, len(items))
            output.extend(result)
            
            # 随机触发特殊事件
            if random.random() < 0.1:
                event = self._trigger_auction_event()
                if event:
                    output.append(f"\n{event}")
        
        # 拍卖会结束
        output.append(f"\n{'='*60}")
        output.append("拍卖会圆满结束！")
        
        # 结算和后续事件
        post_events = self._handle_post_auction_events(player)
        if post_events:
            output.extend(post_events)
        
        return '\n'.join(output)
    
    def _check_vip_status(self, player) -> bool:
        """检查VIP资格"""
        # 这里简化处理，实际应该基于消费记录等
        return player.level >= 30 or player.get_total_lingshi() > 50000
    
    def _generate_auction_items(self, auction_type: str) -> List[AuctionItem]:
        """生成拍卖物品列表"""
        items = []
        auction_config = self.config['auction_types'].get(auction_type, self.config['auction_types']['regular'])
        item_count = auction_config['item_count']
        tier_dist = auction_config['tier_distribution']
        
        # 按层级分配物品
        for tier, ratio in tier_dist.items():
            count = int(item_count * ratio)
            tier_key = f"{tier}_tier"
            
            if tier_key in self.auction_items:
                tier_items = random.sample(
                    self.auction_items[tier_key],
                    min(count, len(self.auction_items[tier_key]))
                )
                
                for item_data in tier_items:
                    items.append(AuctionItem(
                        id=item_data['id'],
                        name=item_data['name'],
                        description=item_data['description'],
                        tier=item_data['tier'],
                        base_price=item_data['base_price'],
                        max_price=item_data['max_price']
                    ))
        
        return items
    
    def _generate_bidders(self, player, item_count: int) -> List[Bidder]:
        """生成NPC竞拍者"""
        bidders = []
        
        # 基础竞拍者数量
        base_count = min(10 + item_count // 2, 20)
        
        # 生成普通竞拍者
        for _ in range(base_count):
            archetype = random.choice(self.bidder_archetypes)
            name = random.choice(archetype['name_pool'])
            
            bidder = Bidder(
                name=name,
                type=BidderType.NPC,
                archetype=archetype['type'],
                wealth=random.randint(5000, 50000),
                max_price=0,  # 将在竞拍时动态计算
                personality=archetype['personality_traits']
            )
            bidders.append(bidder)
        
        # 添加仇敌（如果有）
        if hasattr(player, 'grudges') and player.grudges:
            for grudge_data in self.grudge_npcs[:2]:  # 最多2个仇敌
                bidder = Bidder(
                    name=grudge_data['name'],
                    type=BidderType.GRUDGE,
                    archetype='aggressive',
                    wealth=random.randint(20000, 100000),
                    max_price=0,
                    personality={'patience': 0.3, 'aggression': 0.9, 'wealth': 0.8},
                    grudge_target=player.name
                )
                bidders.append(bidder)
        
        return bidders
    
    def _auction_item(self, player, item: AuctionItem, item_num: int, total_items: int) -> List[str]:
        """拍卖单个物品"""
        output = []
        self.current_item = item
        item.current_bid = item.base_price
        
        # 展示物品信息
        output.append(self.visual.get_colored_text(
            f"\n【{item.name}】",
            'CYAN'
        ))
        output.append(f"品阶：{item.tier}")
        output.append(f"描述：{item.description}")
        output.append(self.visual.get_colored_text(
            f"起拍价：{item.base_price}下品灵石",
            'YELLOW'
        ))
        
        # 拍卖师开场
        if item.tier == "压轴":
            output.append(f"\n拍卖师激动地说：「{item.name}！此乃本场压轴之宝！」")
        else:
            output.append(f"\n拍卖师：「{item.name}，起拍价{item.base_price}灵石！」")
        
        # 竞价循环
        consecutive_passes = 0
        round_num = 0
        player_won = False
        
        while consecutive_passes < 3 and round_num < 20:  # 最多20轮
            round_num += 1
            bid_made = False
            
            # NPC竞价
            npc_bids = self._generate_npc_bids(item, player)
            if npc_bids:
                for bid in npc_bids:
                    output.append(bid['text'])
                    item.current_bid = bid['amount']
                    item.current_bidder = bid['bidder']
                    item.bid_history.append((bid['bidder'], bid['amount']))
                    bid_made = True
                    consecutive_passes = 0
            
            # 玩家竞价机会
            if item.current_bidder != player.name:
                min_increment = int(item.current_bid * self.config['auction_rules']['min_bid_increment'])
                next_bid = item.current_bid + min_increment
                
                output.append(f"\n当前最高价：{item.current_bid}灵石（{item.current_bidder}）")
                output.append(f"您需要至少出价：{next_bid}灵石")
                
                # 获取玩家输入
                player_bid = self._get_player_bid(player, item, next_bid)
                
                if player_bid > 0:
                    # 玩家出价
                    if player.get_total_lingshi() >= player_bid:
                        item.current_bid = player_bid
                        item.current_bidder = player.name
                        item.bid_history.append((player.name, player_bid))
                        
                        if self.player_vip:
                            output.append(f"*神秘贵客出价*：{player_bid}灵石！")
                        else:
                            output.append(f"您出价：{player_bid}灵石！")
                        
                        bid_made = True
                        consecutive_passes = 0
                        
                        # 仇敌反应
                        grudge_response = self._handle_grudge_bidding(player, item, player_bid)
                        if grudge_response:
                            output.extend(grudge_response)
                    else:
                        output.append("您的灵石不足！")
                else:
                    # 玩家放弃
                    consecutive_passes += 1
                    if consecutive_passes == 1:
                        output.append("您选择观望...")
            else:
                # 玩家领先，其他人可能继续出价
                consecutive_passes += 1
            
            # 拍卖师倒计时
            if bid_made:
                if consecutive_passes == 0:
                    output.append(f"拍卖师：「{item.current_bid}灵石！还有更高的吗？」")
                elif consecutive_passes == 1:
                    output.append(f"拍卖师：「{item.current_bid}灵石一次！」")
                elif consecutive_passes == 2:
                    output.append(f"拍卖师：「{item.current_bid}灵石两次！」")
        
        # 成交
        if item.current_bidder:
            output.append(self.visual.get_colored_text(
                f"\n拍卖师：「{item.current_bid}灵石三次！成交！」",
                'GREEN'
            ))
            
            if item.current_bidder == player.name:
                # 玩家获得物品
                player.spend_lingshi(item.current_bid)
                # TODO: 将物品加入玩家背包
                output.append(self.visual.get_colored_text(
                    f"恭喜您以{item.current_bid}灵石拍得{item.name}！",
                    'GREEN'
                ))
                player_won = True
                
                # 记录日志
                self.auction_log.append({
                    'item': item.name,
                    'price': item.current_bid,
                    'won': True
                })
            else:
                output.append(f"{item.current_bidder}以{item.current_bid}灵石拍得此物。")
                self.auction_log.append({
                    'item': item.name,
                    'price': item.current_bid,
                    'won': False,
                    'winner': item.current_bidder
                })
        else:
            output.append("拍卖师：「很遗憾，此物流拍。」")
        
        return output
    
    def _generate_npc_bids(self, item: AuctionItem, player) -> List[Dict]:
        """生成NPC竞价"""
        bids = []
        
        # 计算物品吸引力
        item_value = item.base_price
        if item.tier == "高阶":
            item_value *= 1.5
        elif item.tier == "压轴":
            item_value *= 2.0
        
        # 每个NPC决定是否竞价
        for bidder in self.bidders:
            # 计算NPC的最高承受价格
            if bidder.max_price == 0:
                variance = self.config['bidding_strategies']['npc_behavior']['value_assessment_variance']
                bidder.max_price = int(item_value * (1 + random.uniform(-variance, variance)))
                
                # 根据性格调整
                if bidder.personality['wealth'] > 0.8:
                    bidder.max_price *= 1.2
                if bidder.personality['aggression'] > 0.7:
                    bidder.max_price *= 1.1
            
            # 决定是否出价
            if item.current_bid < bidder.max_price * 0.9:  # 还有10%余地
                # 计算出价
                min_increment = int(item.current_bid * self.config['auction_rules']['min_bid_increment'])
                max_increment = int(item.current_bid * 0.2)  # 最多加价20%
                
                if bidder.type == BidderType.GRUDGE and item.current_bidder == player.name:
                    # 仇敌恶意抬价
                    increment = int(max_increment * 1.5)
                else:
                    # 正常竞价
                    increment = random.randint(min_increment, max_increment)
                
                new_bid = item.current_bid + increment
                
                # 检查是否超过承受能力
                if new_bid <= bidder.max_price and new_bid <= bidder.wealth:
                    # 根据性格决定是否出价
                    bid_chance = bidder.personality['aggression'] * 0.5 + bidder.personality['patience'] * 0.3
                    
                    if random.random() < bid_chance:
                        # 生成竞价文本
                        archetype = next((a for a in self.bidder_archetypes if a['type'] == bidder.archetype), None)
                        if archetype:
                            speech = random.choice(archetype['speech_patterns'])
                            speech = speech.replace('{price}', str(new_bid))
                        else:
                            speech = f"{new_bid}灵石！"
                        
                        bids.append({
                            'bidder': bidder.name,
                            'amount': new_bid,
                            'text': f"{bidder.name}：「{speech}」"
                        })
                        
                        bidder.bid_count += 1
                        
                        # 限制每轮出价人数
                        if len(bids) >= 3:
                            break
        
        return bids
    
    def _get_player_bid(self, player, item: AuctionItem, min_bid: int) -> int:
        """获取玩家竞价（简化版，实际应该等待玩家输入）"""
        # 这里简化处理，实际游戏中应该等待玩家输入
        # 返回0表示放弃，返回正数表示出价
        
        # 模拟玩家决策
        if player.get_total_lingshi() < min_bid:
            return 0  # 没钱了
        
        # 这里应该是等待玩家输入的地方
        # 暂时返回一个模拟值
        if random.random() < 0.6:  # 60%概率出价
            return min_bid + random.randint(0, int(min_bid * 0.1))
        else:
            return 0
    
    def _handle_grudge_bidding(self, player, item: AuctionItem, player_bid: int) -> List[str]:
        """处理仇敌竞价"""
        output = []
        
        grudge_bidders = [b for b in self.bidders if b.type == BidderType.GRUDGE]
        if not grudge_bidders:
            return output
        
        for grudge in grudge_bidders:
            if random.random() < 0.7:  # 70%概率回应
                # 从grudge_npcs中找到对应的特殊对话
                grudge_data = next((g for g in self.grudge_npcs if g['name'] == grudge.name), None)
                if grudge_data:
                    dialogue = random.choice(grudge_data['special_dialogue'])
                    output.append(f"\n{grudge.name}冷笑：「{dialogue}」")
                    
                    # 恶意抬价
                    spite_bid = int(player_bid * self.config['bidding_strategies']['npc_behavior']['spite_bidding_multiplier'])
                    if spite_bid <= grudge.wealth:
                        item.current_bid = spite_bid
                        item.current_bidder = grudge.name
                        item.bid_history.append((grudge.name, spite_bid))
                        output.append(f"{grudge.name}恶意抬价至：{spite_bid}灵石！")
        
        return output
    
    def _trigger_auction_event(self) -> Optional[str]:
        """触发拍卖特殊事件"""
        for event_id, event_data in self.auction_events.items():
            if random.random() < event_data['probability']:
                output = []
                output.append(self.visual.get_colored_text(
                    f"\n【特殊事件：{event_data['description']}】",
                    'RED'
                ))
                for dialogue in event_data['dialogues']:
                    output.append(dialogue)
                return '\n'.join(output)
        
        return None
    
    def _handle_post_auction_events(self, player) -> List[str]:
        """处理拍后事件"""
        output = []
        
        # 检查是否触发劫杀事件
        won_items = [log for log in self.auction_log if log.get('won', False)]
        if won_items:
            total_value = sum(item['price'] for item in won_items)
            
            # 计算劫杀概率
            ambush_config = self.config['post_auction_events']['ambush']
            ambush_prob = ambush_config['base_probability']
            ambush_prob += total_value * ambush_config['factors']['item_value']
            
            # 根据玩家属性调整
            if hasattr(player, 'stealth'):
                ambush_prob += player.stealth * ambush_config['factors']['player_stealth']
            
            if random.random() < ambush_prob:
                output.append(self.visual.get_colored_text(
                    "\n【危险！】离开拍卖行时，您感到有人在跟踪...",
                    'RED'
                ))
                output.append("几个蒙面人突然出现：「把拍卖品交出来！」")
                output.append("（触发战斗事件）")
                # TODO: 触发战斗
        
        # 检查是否有人想要结交
        if player.get_total_lingshi() > 10000:
            alliance_config = self.config['post_auction_events']['alliance_offer']
            alliance_prob = alliance_config['base_probability']
            
            if random.random() < alliance_prob:
                output.append(self.visual.get_colored_text(
                    "\n【机遇】一位神秘修士走近...",
                    'GREEN'
                ))
                output.append("神秘修士：「道友财力不凡，可否交个朋友？」")
                # TODO: 触发社交事件
        
        return output
    
    def process_player_bid(self, player, amount: int) -> str:
        """处理玩家出价（供外部调用）"""
        if not self.current_item:
            return "当前没有正在拍卖的物品。"
        
        min_increment = int(self.current_item.current_bid * self.config['auction_rules']['min_bid_increment'])
        min_bid = self.current_item.current_bid + min_increment
        
        if amount < min_bid:
            return f"出价必须至少为{min_bid}灵石。"
        
        if player.get_total_lingshi() < amount:
            return "您的灵石不足！"
        
        # 更新竞价
        self.current_item.current_bid = amount
        self.current_item.current_bidder = player.name
        self.current_item.bid_history.append((player.name, amount))
        
        return f"您成功出价{amount}灵石！"


# 创建全局拍卖系统实例
auction_system = AuctionSystem()
