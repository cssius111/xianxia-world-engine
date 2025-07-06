"""
拍卖行命令处理
处理拍卖相关的游戏命令
"""

from dataclasses import dataclass, asdict
import uuid
from typing import Dict, Any, Optional, List


@dataclass
class Auction:
    """简单的拍卖数据结构"""

    id: str
    item_name: str
    seller_id: str
    starting_price: int
    highest_bid: int
    highest_bidder: Optional[str] = None


class AuctionSystem:
    """内存中的拍卖系统"""

    def __init__(self) -> None:
        self.auctions: Dict[str, Auction] = {}

    def create_auction(self, seller_id: str, item_name: str, starting_price: int) -> Auction:
        auction_id = str(uuid.uuid4())[:8]
        auction = Auction(
            id=auction_id,
            item_name=item_name,
            seller_id=seller_id,
            starting_price=starting_price,
            highest_bid=starting_price,
        )
        self.auctions[auction_id] = auction
        return auction

    def place_bid(self, auction_id: str, bidder_id: str, price: int) -> bool:
        auction = self.auctions.get(auction_id)
        if not auction or price <= auction.highest_bid:
            return False
        auction.highest_bid = price
        auction.highest_bidder = bidder_id
        return True

    def list_auctions(self) -> List[Dict[str, Any]]:
        return [asdict(a) for a in self.auctions.values()]

    def list_player_auctions(self, player_id: str) -> List[Dict[str, Any]]:
        return [asdict(a) for a in self.auctions.values() if a.seller_id == player_id]

class AuctionCommandHandler:
    """拍卖行命令处理器"""
    
    def __init__(self, auction_system: Optional[AuctionSystem] = None):
        self.auction_system = auction_system or AuctionSystem()
        self.commands = {
            "拍卖": self.handle_auction,
            "竞价": self.handle_bid,
            "查看拍卖": self.handle_list_auctions,
            "我的拍卖": self.handle_my_auctions
        }
    
    def handle_command(self, command: str, args: list, player_id: str) -> Dict[str, Any]:
        """处理拍卖命令"""
        if command in self.commands:
            return self.commands[command](args, player_id)
        return {"success": False, "message": "未知的拍卖命令"}
    
    def handle_auction(self, args: list, player_id: str) -> Dict[str, Any]:
        """处理拍卖物品命令"""
        if len(args) < 2:
            return {"success": False, "message": "用法: 拍卖 <物品> <起拍价>"}
        
        item_name = args[0]
        try:
            starting_price = int(args[1])
        except ValueError:
            return {"success": False, "message": "起拍价必须是数字"}
        
        auction = self.auction_system.create_auction(player_id, item_name, starting_price)
        return {
            "success": True,
            "message": f"已将{item_name}以{starting_price}金币起拍 (ID:{auction.id})",
            "auction_id": auction.id,
        }
    
    def handle_bid(self, args: list, player_id: str) -> Dict[str, Any]:
        """处理竞价命令"""
        if len(args) < 2:
            return {"success": False, "message": "用法: 竞价 <拍卖ID> <价格>"}
        auction_id = args[0]
        try:
            price = int(args[1])
        except ValueError:
            return {"success": False, "message": "价格必须是数字"}

        if self.auction_system.place_bid(auction_id, player_id, price):
            return {"success": True, "message": "竞价成功"}
        return {"success": False, "message": "竞价失败，可能出价过低或拍卖不存在"}
    
    def handle_list_auctions(self, args: list, player_id: str) -> Dict[str, Any]:
        """查看当前拍卖"""
        auctions = self.auction_system.list_auctions()
        return {
            "success": True,
            "message": "当前拍卖列表:",
            "auctions": auctions,
        }
    
    def handle_my_auctions(self, args: list, player_id: str) -> Dict[str, Any]:
        """查看我的拍卖"""
        auctions = self.auction_system.list_player_auctions(player_id)
        return {
            "success": True,
            "message": "我的拍卖:",
            "auctions": auctions,
        }

# 创建全局实例
auction_command_handler = AuctionCommandHandler()

__all__ = ["AuctionCommandHandler", "auction_command_handler"]
