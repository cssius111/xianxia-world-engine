"""
拍卖行命令处理器

处理拍卖相关的游戏命令
"""

from typing import Any, Dict, Optional
from xwe.features.auction_system import auction_system


class AuctionCommandHandler:
    """拍卖行命令处理器"""
    
    def __init__(self) -> None:
        self.auction_system = auction_system
        self.active_auction = False
        self.waiting_for_bid = False
        self.current_min_bid = 0
        
    def handle_auction_command(self, player, command: str, params: Optional[str] = None) -> str:
        """处理拍卖相关命令"""
        
        if command == "拍卖行" or command == "auction":
            # 进入拍卖行
            return self._enter_auction_house(player)
            
        elif command == "参加拍卖" or command == "join_auction":
            # 参加拍卖会
            if not self.active_auction:
                result = self.auction_system.start_auction(player, "regular")
                self.active_auction = True
                return result
            else:
                return "拍卖会正在进行中..."
                
        elif command == "出价" or command == "bid":
            # 出价
            if not self.active_auction:
                return "当前没有正在进行的拍卖会。"
                
            if not params:
                return "请指定出价金额，例如：出价 1000"
                
            try:
                amount = int(params)
                return self.auction_system.process_player_bid(player, amount)
            except ValueError:
                return "请输入有效的数字金额。"
                
        elif command == "放弃" or command == "pass":
            # 放弃当前物品
            if self.waiting_for_bid:
                self.waiting_for_bid = False
                return "您选择放弃竞拍当前物品。"
            else:
                return "当前没有需要您决定的竞拍。"
                
        elif command == "离开拍卖行" or command == "leave_auction":
            # 离开拍卖行
            if self.active_auction:
                self.active_auction = False
                self.waiting_for_bid = False
                return "您离开了拍卖行。"
            else:
                return "您不在拍卖行中。"
                
        elif command == "拍卖帮助" or command == "auction_help":
            # 显示拍卖帮助
            return self._show_auction_help()
            
        else:
            return "未知的拍卖命令。输入'拍卖帮助'查看可用命令。"
    
    def _enter_auction_house(self, player) -> str:
        """进入拍卖行"""
        output = []
        output.append("\n" + "="*60)
        output.append(f"欢迎来到{auction_system.config['name']}！")
        output.append("="*60)
        output.append("\n这里是玄苍界最大的拍卖行，每日都有珍稀宝物拍卖。")
        output.append(f"入场费：{auction_system.config['entry_requirements']['entry_fee']}灵石")
        output.append("\n可用命令：")
        output.append("- 参加拍卖：参加当前的拍卖会")
        output.append("- 离开拍卖行：离开此地")
        output.append("- 拍卖帮助：查看拍卖规则")
        
        # 检查是否有特殊拍卖会
        output.append("\n当前拍卖会：")
        output.append("【常规拍卖会】正在准备中...")
        output.append("预计拍品：丹药、法宝、功法等")
        
        return '\n'.join(output)
    
    def _show_auction_help(self) -> str:
        """显示拍卖帮助信息"""
        output = []
        output.append("\n" + "="*40)
        output.append("拍卖行使用指南")
        output.append("="*40)
        output.append("\n基本规则：")
        output.append(f"- 最小加价幅度：当前价格的{int(auction_system.config['auction_rules']['min_bid_increment']*100)}%")
        output.append(f"- 佣金率：成交价的{int(auction_system.config['auction_rules']['commission_rate']*100)}%")
        output.append("- 竞拍方式：英式拍卖（价高者得）")
        output.append("\n竞拍技巧：")
        output.append("- 仔细评估物品价值，避免冲动出价")
        output.append("- 注意其他竞拍者的出价模式")
        output.append("- 当心恶意抬价的对手")
        output.append("- 珍贵物品拍得后要小心离场")
        output.append("\nVIP特权：")
        output.append("- 匿名竞拍")
        output.append("- 专属包厢")
        output.append("- 优先座位")
        output.append("- 自动代理竞拍")
        
        return '\n'.join(output)
    
    def is_in_auction(self) -> bool:
        """检查是否在拍卖中"""
        return self.active_auction
    
    def get_auction_prompt(self) -> str:
        """获取拍卖提示信息"""
        if self.waiting_for_bid:
            return f"当前最低出价：{self.current_min_bid}灵石（输入'出价 金额'或'放弃'）"
        else:
            return ""


# 创建全局命令处理器实例
auction_command_handler = AuctionCommandHandler()
