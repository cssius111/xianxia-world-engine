"""
交互式拍卖系统
提供更加生动和互动的拍卖体验
"""

import random
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple


class BidderPersonality(Enum):
    """竞拍者性格"""
    AGGRESSIVE = "aggressive"      # 激进型
    CONSERVATIVE = "conservative"  # 保守型
    STRATEGIC = "strategic"        # 策略型
    IMPULSIVE = "impulsive"       # 冲动型
    COLLECTOR = "collector"        # 收藏家型


@dataclass
class AuctioneerStyle:
    """拍卖师风格"""
    name: str
    greeting: str
    bid_prompts: List[str]
    closing_words: List[str]
    personality: str


class InteractiveAuctioneer:
    """交互式拍卖师"""
    
    def __init__(self):
        self.styles = {
            "elegant": AuctioneerStyle(
                name="风雅先生",
                greeting="诸位道友，今日拍卖会即将开始，请各位准备好灵石。",
                bid_prompts=[
                    "有道友出价{price}灵石，还有更高的吗？",
                    "{price}灵石一次，这等宝物可不多见。",
                    "目前最高价{price}灵石，机会难得！"
                ],
                closing_words=[
                    "{price}灵石三次，成交！恭喜这位道友。",
                    "成交！{winner}道友慧眼识珠。"
                ],
                personality="优雅从容"
            ),
            "energetic": AuctioneerStyle(
                name="火爆道人",
                greeting="各位！激动人心的时刻到了！宝物即将登场！",
                bid_prompts=[
                    "哇！{price}灵石！还有谁？还有谁要出价？",
                    "太精彩了！{price}灵石！这可是千载难逢的机会！",
                    "{price}灵石！快快快！不要错过！"
                ],
                closing_words=[
                    "砰！成交！{price}灵石归{winner}道友所有！",
                    "太棒了！{winner}道友以{price}灵石拿下此宝！"
                ],
                personality="热情激昂"
            ),
            "mysterious": AuctioneerStyle(
                name="玄机老人",
                greeting="缘分到此，宝物自现。有缘者得之...",
                bid_prompts=[
                    "已有人出{price}灵石，缘分未尽否？",
                    "{price}灵石...此物与谁有缘？",
                    "命数已显，{price}灵石，可还有变数？"
                ],
                closing_words=[
                    "缘定于此，{price}灵石，{winner}道友请收好。",
                    "天意如此，此宝归{winner}道友，{price}灵石。"
                ],
                personality="神秘莫测"
            )
        }
        self.current_style = self.styles["elegant"]
    
    def set_style(self, style: str):
        """设置拍卖师风格"""
        if style in self.styles:
            self.current_style = self.styles[style]
    
    def greet(self) -> str:
        """开场白"""
        return f"【{self.current_style.name}】{self.current_style.greeting}"
    
    def announce_item(self, item_name: str, description: str, starting_price: int) -> str:
        """介绍拍卖品"""
        return f"\n【{self.current_style.name}】接下来要拍卖的是：{item_name}\n{description}\n起拍价：{starting_price}灵石"
    
    def prompt_bid(self, current_price: int) -> str:
        """催促出价"""
        prompt = random.choice(self.current_style.bid_prompts)
        return f"【{self.current_style.name}】{prompt.format(price=current_price)}"
    
    def announce_winner(self, winner: str, final_price: int) -> str:
        """宣布获胜者"""
        closing = random.choice(self.current_style.closing_words)
        return f"【{self.current_style.name}】{closing.format(winner=winner, price=final_price)}"


class VirtualBidder:
    """虚拟竞拍者"""
    
    def __init__(self, name: str, wealth: int, personality: BidderPersonality):
        self.name = name
        self.wealth = wealth
        self.personality = personality
        self.current_bid = 0
        self.interest_level = 0.0
        self.bid_history: List[int] = []
    
    def evaluate_item(self, item_value: int, item_type: str) -> float:
        """评估物品兴趣度"""
        base_interest = random.uniform(0.3, 0.9)
        
        # 根据性格调整
        if self.personality == BidderPersonality.COLLECTOR:
            base_interest += 0.2
        elif self.personality == BidderPersonality.CONSERVATIVE:
            base_interest -= 0.1
        
        # 根据财富调整
        if item_value < self.wealth * 0.1:
            base_interest += 0.1
        elif item_value > self.wealth * 0.5:
            base_interest -= 0.3
        
        self.interest_level = max(0.0, min(1.0, base_interest))
        return self.interest_level
    
    def decide_bid(self, current_price: int, min_increment: int) -> Optional[int]:
        """决定是否出价及出价金额"""
        # 超出承受能力
        if current_price >= self.wealth * 0.7:
            return None
        
        # 根据兴趣度和性格决定
        bid_probability = self.interest_level
        
        if self.personality == BidderPersonality.AGGRESSIVE:
            bid_probability += 0.2
            increment = random.randint(min_increment, min_increment * 3)
        elif self.personality == BidderPersonality.IMPULSIVE:
            bid_probability += 0.15
            increment = random.randint(min_increment, min_increment * 5)
        elif self.personality == BidderPersonality.STRATEGIC:
            # 策略型会在早期观望
            if len(self.bid_history) < 3:
                bid_probability -= 0.3
            increment = min_increment
        else:
            increment = min_increment
        
        # 已经连续出价多次，降低概率
        if len(self.bid_history) > 0 and self.bid_history[-1] == current_price - min_increment:
            bid_probability -= 0.2
        
        if random.random() < bid_probability:
            new_bid = current_price + increment
            if new_bid <= self.wealth * 0.7:
                self.current_bid = new_bid
                self.bid_history.append(new_bid)
                return new_bid
        
        return None
    
    def react_to_bid(self, bidder: str, amount: int) -> Optional[str]:
        """对其他人出价的反应"""
        reactions = {
            BidderPersonality.AGGRESSIVE: [
                f"{bidder}道友好魄力！",
                "哼，这点灵石算什么！",
                "有意思，继续！"
            ],
            BidderPersonality.CONSERVATIVE: [
                "这个价格有些高了...",
                f"{bidder}道友似乎志在必得。",
                "需要慎重考虑..."
            ],
            BidderPersonality.IMPULSIVE: [
                "我也要！我也要！",
                "不行，这宝物必须是我的！",
                f"可恶，{bidder}道友抢先了！"
            ]
        }
        
        if self.personality in reactions and random.random() < 0.3:
            return f"【{self.name}】{random.choice(reactions[self.personality])}"
        return None


class InteractiveAuction:
    """交互式拍卖"""
    
    def __init__(self):
        self.auctioneer = InteractiveAuctioneer()
        self.bidders: List[VirtualBidder] = []
        self.current_item = None
        self.current_price = 0
        self.min_increment = 100
        self.bid_history: List[Tuple[str, int, datetime]] = []
        self.is_active = False
        
        # 初始化一些虚拟竞拍者
        self._init_virtual_bidders()
    
    def _init_virtual_bidders(self):
        """初始化虚拟竞拍者"""
        bidder_templates = [
            ("富贵公子", 50000, BidderPersonality.IMPULSIVE),
            ("精明商人", 30000, BidderPersonality.STRATEGIC),
            ("藏宝阁主", 80000, BidderPersonality.COLLECTOR),
            ("谨慎散修", 20000, BidderPersonality.CONSERVATIVE),
            ("霸道宗主", 100000, BidderPersonality.AGGRESSIVE)
        ]
        
        for name, wealth, personality in bidder_templates:
            if random.random() < 0.7:  # 70%概率参与
                self.bidders.append(VirtualBidder(name, wealth, personality))
    
    def start_auction(self, item_name: str, description: str, 
                     starting_price: int, min_increment: int = 100) -> str:
        """开始拍卖"""
        self.current_item = item_name
        self.current_price = starting_price
        self.min_increment = min_increment
        self.bid_history = []
        self.is_active = True
        
        # 让竞拍者评估物品
        for bidder in self.bidders:
            bidder.evaluate_item(starting_price * random.randint(3, 10), "treasure")
            bidder.bid_history = []
        
        output = self.auctioneer.greet()
        output += "\n" + self.auctioneer.announce_item(item_name, description, starting_price)
        
        # 可能有竞拍者立即出价
        eager_bidder = random.choice(self.bidders) if self.bidders else None
        if eager_bidder and eager_bidder.interest_level > 0.7:
            bid = eager_bidder.decide_bid(self.current_price, self.min_increment)
            if bid:
                self.current_price = bid
                self.bid_history.append((eager_bidder.name, bid, datetime.now()))
                output += f"\n\n【{eager_bidder.name}】抢先出价{bid}灵石！"
        
        return output
    
    def player_bid(self, amount: int) -> Tuple[bool, str]:
        """玩家出价"""
        if not self.is_active:
            return False, "当前没有正在进行的拍卖。"
        
        if amount <= self.current_price:
            return False, f"出价必须高于当前价格{self.current_price}灵石。"
        
        if amount < self.current_price + self.min_increment:
            return False, f"最低加价幅度为{self.min_increment}灵石。"
        
        self.current_price = amount
        self.bid_history.append(("玩家", amount, datetime.now()))
        
        output = f"你出价{amount}灵石。"
        
        # 其他竞拍者的反应
        reactions = []
        for bidder in self.bidders:
            reaction = bidder.react_to_bid("阁下", amount)
            if reaction:
                reactions.append(reaction)
        
        if reactions:
            output += "\n\n" + "\n".join(reactions[:2])  # 最多显示2个反应
        
        # 触发其他竞拍者出价
        output += self._trigger_npc_bids()
        
        return True, output
    
    def _trigger_npc_bids(self) -> str:
        """触发NPC竞拍"""
        output = ""
        bid_made = False
        
        # 随机顺序，更真实
        bidders = self.bidders.copy()
        random.shuffle(bidders)
        
        for bidder in bidders:
            if random.random() < 0.6:  # 60%概率考虑出价
                bid = bidder.decide_bid(self.current_price, self.min_increment)
                if bid:
                    self.current_price = bid
                    self.bid_history.append((bidder.name, bid, datetime.now()))
                    output += f"\n\n【{bidder.name}】出价{bid}灵石！"
                    
                    # 偶尔添加拍卖师的评论
                    if random.random() < 0.4:
                        output += "\n" + self.auctioneer.prompt_bid(self.current_price)
                    
                    bid_made = True
                    break  # 一次只有一个NPC出价
        
        if not bid_made and random.random() < 0.3:
            # 没人出价时，拍卖师催促
            output += "\n\n" + self.auctioneer.prompt_bid(self.current_price)
        
        return output
    
    def check_auction_status(self) -> Tuple[bool, str]:
        """检查拍卖状态"""
        if not self.is_active:
            return False, "没有正在进行的拍卖。"
        
        # 检查是否有人继续出价
        last_bid_time = self.bid_history[-1][2] if self.bid_history else datetime.now()
        time_passed = (datetime.now() - last_bid_time).seconds
        
        if time_passed > 30:  # 30秒无人出价
            # 结束拍卖
            if self.bid_history:
                winner = self.bid_history[-1][0]
                final_price = self.bid_history[-1][1]
                self.is_active = False
                return True, self.auctioneer.announce_winner(winner, final_price)
            else:
                self.is_active = False
                return True, "【拍卖师】很遗憾，无人出价，流拍。"
        
        # 拍卖继续
        output = self._trigger_npc_bids()
        if not output:
            output = f"当前最高价：{self.current_price}灵石"
            if self.bid_history:
                output += f"（{self.bid_history[-1][0]}）"
        
        return False, output
    
    def end_auction(self) -> str:
        """强制结束拍卖"""
        if not self.is_active:
            return "没有正在进行的拍卖。"
        
        self.is_active = False
        if self.bid_history:
            winner = self.bid_history[-1][0]
            final_price = self.bid_history[-1][1]
            return self.auctioneer.announce_winner(winner, final_price)
        else:
            return "【拍卖师】拍卖结束，无人出价。"
