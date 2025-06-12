"""
拍卖行系统 - 交互式竞拍处理器

实现真正的交互式竞拍体验
"""

import time
import random
from typing import Any, Any as AnyType, Dict, List, Optional, Type
from xwe.features.auction_system import AuctionSystem, AuctionItem, BidderType

VEClass: Type[AnyType]
try:
    from xwe.features.visual_enhancement import VisualEnhancement
except Exception:  # pragma: no cover - fallback
    from xwe.features.visual_enhancement import visual_effects

    class _FallbackVisualEnhancement:
        def __init__(self) -> None:
            self._effects = visual_effects

        def get_colored_text(self, text: str, color: str) -> str:
            return self._effects.text_renderer.colorize(text, color.lower())

    VEClass = _FallbackVisualEnhancement
else:
    VEClass = VisualEnhancement


class InteractiveAuction:
    """交互式拍卖处理器"""
    
    def __init__(self, auction_system: AuctionSystem):
        self.auction_system = auction_system
        self.visual = VEClass()
        self.current_item = None
        self.bidding_active = False
        self.countdown_active = False
        
    def start_interactive_auction(self, player, items: List[AuctionItem]) -> Dict:
        """开始交互式拍卖"""
        results = {
            'items_won': [],
            'total_spent': 0,
            'events_triggered': []
        }
        
        print(self.visual.get_colored_text(
            f"\n{'='*60}\n拍卖会正式开始！\n{'='*60}\n",
            'YELLOW'
        ))
        
        for i, item in enumerate(items):
            print(f"\n{'-'*50}")
            print(f"第{i+1}/{len(items)}件拍品")
            
            # 拍卖单个物品
            won, final_price = self._auction_single_item(player, item, i == len(items)-1)
            
            if won:
                results['items_won'].append(item)
                results['total_spent'] += final_price
            
            # 休息一下
            if i < len(items) - 1:
                print("\n拍卖师：「请稍候，我们准备下一件拍品...」")
                time.sleep(1)
        
        return results
    
    def _auction_single_item(self, player, item: AuctionItem, is_final: bool) -> tuple:
        """拍卖单个物品的交互式流程"""
        self.current_item = item
        item.current_bid = item.base_price
        
        # 展示物品
        self._display_item(item, is_final)
        
        # 初始NPC竞价
        time.sleep(2)
        self._initial_npc_bids(item)
        
        # 主竞价循环
        player_won = False
        final_price = item.current_bid
        rounds = 0
        max_rounds = 15
        
        while rounds < max_rounds:
            rounds += 1
            
            # 显示当前状态
            self._display_current_status(item)
            
            # 玩家决策
            if item.current_bidder != player.name:
                player_action = self._get_player_decision(player, item)
                
                if player_action == 'bid':
                    bid_amount = self._get_bid_amount(player, item)
                    if bid_amount > 0:
                        success = self._process_player_bid(player, item, bid_amount)
                        if success:
                            # NPC反应
                            time.sleep(1)
                            npc_response = self._npc_respond_to_player_bid(item, bid_amount)
                            if not npc_response:
                                # 没有NPC继续竞价
                                if self._final_countdown(item):
                                    player_won = True
                                    final_price = item.current_bid
                                    break
                    else:
                        print("出价取消。")
                        
                elif player_action == 'pass':
                    print("\n您选择继续观望...")
                    # NPC之间可能继续竞价
                    if not self._npc_bidding_round(item):
                        # 无人继续出价
                        if self._final_countdown(item):
                            break
                            
                elif player_action == 'quit':
                    print("\n您决定放弃这件拍品。")
                    # 继续NPC竞价直到结束
                    while self._npc_bidding_round(item):
                        time.sleep(1)
                    self._final_countdown(item)
                    break
            else:
                # 玩家当前最高价
                print(self.visual.get_colored_text(
                    f"\n您目前是最高出价者！({item.current_bid}灵石)",
                    'GREEN'
                ))
                
                # 其他NPC可能继续出价
                if not self._npc_respond_to_player_lead(item):
                    # 无人超过玩家
                    if self._final_countdown(item):
                        player_won = True
                        final_price = item.current_bid
                        break
            
            # 防止死循环
            if rounds >= max_rounds:
                print("\n拍卖师：「竞价时间已到，按当前最高价成交！」")
                if item.current_bidder == player.name:
                    player_won = True
                    final_price = item.current_bid
                break
        
        # 宣布结果
        self._announce_result(item, player_won, final_price)
        
        return player_won, final_price
    
    def _display_item(self, item: AuctionItem, is_final: bool) -> None:
        """展示拍品信息"""
        if is_final:
            print(self.visual.get_colored_text(
                "\n【压轴拍品登场！】",
                'GOLD'
            ))
            print("*全场哗然，所有人都将目光投向展台*")
        
        print(self.visual.get_colored_text(
            f"\n物品：{item.name}",
            'CYAN'
        ))
        print(f"品阶：{item.tier}")
        print(f"描述：{item.description}")
        print(self.visual.get_colored_text(
            f"起拍价：{item.base_price}下品灵石",
            'YELLOW'
        ))
        
        # 拍卖师介绍
        if item.tier == "压轴":
            print(f"\n拍卖师激动地说：「诸位道友！这{item.name}乃是本场压轴重宝！」")
            print("「据说此物..." + self._generate_item_story(item) + "」")
        else:
            print(f"\n拍卖师：「{item.name}，起拍价{item.base_price}灵石，请出价！」")
    
    def _generate_item_story(self, item: AuctionItem) -> str:
        """生成物品背景故事"""
        stories = {
            "渡劫法宝": "曾助三位大能成功渡过九九天劫",
            "万年雪莲": "采自北域极寒之地的万载玄冰之中",
            "上古功法": "出自上古遗迹，虽有残缺但威力依然惊人",
            "龙纹炼丹炉": "以真龙之鳞炼制，丹成有龙吟之声"
        }
        
        for key, story in stories.items():
            if key in item.name:
                return story
        
        return "来历神秘，威力非凡"
    
    def _initial_npc_bids(self, item: AuctionItem) -> None:
        """初始NPC竞价"""
        print("\n*竞价开始*")
        
        # 生成2-4个初始出价
        num_bids = random.randint(2, 4)
        for i in range(num_bids):
            bidder = random.choice(self.auction_system.bidders)
            increment = int(item.current_bid * random.uniform(0.05, 0.15))
            new_bid = item.current_bid + increment
            
            # 检查是否在承受范围内
            if new_bid <= bidder.wealth * 0.1:  # 初始阶段保守
                item.current_bid = new_bid
                item.current_bidder = bidder.name
                
                # 生成竞价文本
                archetype = next((a for a in self.auction_system.bidder_archetypes 
                                if a['type'] == bidder.archetype), None)
                if archetype:
                    speech = random.choice(archetype['speech_patterns']).replace('{price}', str(new_bid))
                    print(f"{bidder.name}：「{speech}」")
                else:
                    print(f"{bidder.name}出价：{new_bid}灵石")
                
                time.sleep(0.8)
    
    def _display_current_status(self, item: AuctionItem) -> None:
        """显示当前竞价状态"""
        print(f"\n当前最高出价：{self.visual.get_colored_text(str(item.current_bid) + '灵石', 'YELLOW')}")
        print(f"出价者：{item.current_bidder}")
        
        # 显示竞价历史（最近3次）
        if len(item.bid_history) > 1:
            print("最近出价记录：")
            for bidder, amount in item.bid_history[-3:]:
                print(f"  - {bidder}: {amount}灵石")
    
    def _get_player_decision(self, player, item: AuctionItem) -> str:
        """获取玩家决策"""
        min_increment = int(item.current_bid * self.auction_system.config['auction_rules']['min_bid_increment'])
        min_bid = item.current_bid + min_increment
        
        print(f"\n您的灵石：{player.get_lingshi_description()}")
        print(f"最低出价：{min_bid}灵石")
        print("\n请选择：")
        print("1. 出价竞拍")
        print("2. 继续观望")
        print("3. 放弃此物")
        
        while True:
            choice = input("\n您的选择 (1/2/3): ").strip()
            if choice == '1':
                return 'bid'
            elif choice == '2':
                return 'pass'
            elif choice == '3':
                return 'quit'
            else:
                print("无效选择，请输入 1、2 或 3")
    
    def _get_bid_amount(self, player, item: AuctionItem) -> int:
        """获取玩家出价金额"""
        min_increment = int(item.current_bid * self.auction_system.config['auction_rules']['min_bid_increment'])
        min_bid = item.current_bid + min_increment
        
        print(f"\n当前价格：{item.current_bid}灵石")
        print(f"最低出价：{min_bid}灵石")
        print("(输入 0 取消出价)")
        
        while True:
            try:
                amount = input("\n您的出价: ").strip()
                if not amount:
                    return 0
                    
                amount = int(amount)
                
                if amount == 0:
                    return 0
                elif amount < min_bid:
                    print(f"出价必须至少为{min_bid}灵石！")
                elif amount > player.get_total_lingshi():
                    print(f"您的灵石不足！(当前：{player.get_total_lingshi()})")
                else:
                    return amount
                    
            except ValueError:
                print("请输入有效的数字！")
    
    def _process_player_bid(self, player, item: AuctionItem, amount: int) -> bool:
        """处理玩家出价"""
        item.current_bid = amount
        item.current_bidder = player.name
        item.bid_history.append((player.name, amount))
        
        print(self.visual.get_colored_text(
            f"\n您出价：{amount}灵石！",
            'GREEN'
        ))
        
        # 检查是否有仇敌
        grudge_response = self._check_grudge_response(player, item, amount)
        if grudge_response:
            print(grudge_response)
        
        return True
    
    def _check_grudge_response(self, player, item: AuctionItem, player_bid: int) -> Optional[str]:
        """检查仇敌反应"""
        grudge_bidders = [b for b in self.auction_system.bidders if b.type == BidderType.GRUDGE]
        
        for grudge in grudge_bidders:
            if random.random() < 0.6:  # 60%概率触发
                grudge_data = next((g for g in self.auction_system.grudge_npcs 
                                  if g['name'] == grudge.name), None)
                if grudge_data:
                    return f"\n{grudge.name}冷笑道：「{random.choice(grudge_data['special_dialogue'])}」"
        
        return None
    
    def _npc_respond_to_player_bid(self, item: AuctionItem, player_bid: int) -> bool:
        """NPC响应玩家出价"""
        responded = False
        
        # 随机1-3个NPC可能响应
        potential_bidders = [b for b in self.auction_system.bidders 
                           if b.wealth > player_bid and b.name != item.current_bidder]
        
        if potential_bidders:
            num_responses = min(random.randint(0, 2), len(potential_bidders))
            
            for _ in range(num_responses):
                bidder = random.choice(potential_bidders)
                
                # 决定是否出价
                if self._npc_decides_to_bid(bidder, item, player_bid):
                    increment = int(player_bid * random.uniform(0.05, 0.2))
                    new_bid = player_bid + increment
                    
                    if new_bid <= bidder.wealth:
                        item.current_bid = new_bid
                        item.current_bidder = bidder.name
                        item.bid_history.append((bidder.name, new_bid))
                        
                        # 生成对话
                        self._generate_npc_bid_dialogue(bidder, new_bid, is_response=True)
                        responded = True
                        time.sleep(1)
                        break
        
        return responded
    
    def _npc_decides_to_bid(self, bidder, item: AuctionItem, current_price: int) -> bool:
        """NPC决定是否竞价"""
        # 基于物品价值和NPC性格决定
        value_ratio = current_price / item.base_price
        
        if value_ratio > 3.0:  # 已经是起拍价的3倍
            return random.random() < 0.1
        elif value_ratio > 2.0:
            return random.random() < 0.3
        elif value_ratio > 1.5:
            return random.random() < 0.5
        else:
            return random.random() < 0.7
    
    def _generate_npc_bid_dialogue(self, bidder, amount: int, is_response: bool = False) -> None:
        """生成NPC竞价对话"""
        archetype = next((a for a in self.auction_system.bidder_archetypes 
                        if a['type'] == bidder.archetype), None)
        
        if archetype:
            if is_response and bidder.archetype == 'aggressive':
                speeches = [
                    f"哼！区区{amount}灵石！",
                    f"想跟我抢？{amount}！",
                    f"我出{amount}！看谁敢再加！"
                ]
            else:
                speeches = archetype['speech_patterns']
            
            speech = random.choice(speeches).replace('{price}', str(amount))
            print(f"\n{bidder.name}：「{speech}」")
        else:
            print(f"\n{bidder.name}出价：{amount}灵石")
    
    def _npc_respond_to_player_lead(self, item: AuctionItem) -> bool:
        """当玩家领先时NPC的反应"""
        # 20-50%概率有NPC继续出价
        if random.random() < random.uniform(0.2, 0.5):
            return self._npc_bidding_round(item)
        return False
    
    def _npc_bidding_round(self, item: AuctionItem) -> bool:
        """NPC之间的竞价回合"""
        bidded = False
        
        # 随机选择1-2个NPC出价
        active_bidders = [b for b in self.auction_system.bidders 
                         if b.wealth > item.current_bid * 1.1]
        
        if active_bidders:
            num_bids = min(random.randint(1, 2), len(active_bidders))
            
            for _ in range(num_bids):
                bidder = random.choice(active_bidders)
                increment = int(item.current_bid * random.uniform(0.05, 0.15))
                new_bid = item.current_bid + increment
                
                if new_bid <= bidder.wealth * 0.8:  # 不会用尽全部财富
                    item.current_bid = new_bid
                    item.current_bidder = bidder.name
                    item.bid_history.append((bidder.name, new_bid))
                    
                    self._generate_npc_bid_dialogue(bidder, new_bid)
                    bidded = True
                    time.sleep(1)
        
        return bidded
    
    def _final_countdown(self, item: AuctionItem) -> bool:
        """最终倒计时"""
        print(f"\n拍卖师举起木槌：「{item.current_bid}灵石一次！」")
        time.sleep(1.5)
        
        # 10%概率有人最后时刻出价
        if random.random() < 0.1 and item.current_bidder != "您":
            last_bidder = random.choice(self.auction_system.bidders)
            last_bid = int(item.current_bid * 1.1)
            if last_bid <= last_bidder.wealth:
                print(f"\n*突然* {last_bidder.name}：「等等！{last_bid}灵石！」")
                item.current_bid = last_bid
                item.current_bidder = last_bidder.name
                return False
        
        print(f"拍卖师：「{item.current_bid}灵石两次！」")
        time.sleep(1.5)
        
        print(f"拍卖师：「{item.current_bid}灵石三次！」")
        time.sleep(1)
        
        print("*木槌落下*")
        print(self.visual.get_colored_text("成交！", 'GREEN'))
        
        return True
    
    def _announce_result(self, item: AuctionItem, player_won: bool, final_price: int) -> None:
        """宣布拍卖结果"""
        if player_won:
            print(self.visual.get_colored_text(
                f"\n恭喜您以{final_price}灵石成功拍得{item.name}！",
                'GREEN'
            ))
            print("拍卖师：「恭喜这位道友，请到后台交割。」")
        else:
            print(f"\n{item.current_bidder}以{final_price}灵石拍得{item.name}。")
            print("拍卖师：「恭喜" + item.current_bidder + "道友！」")
