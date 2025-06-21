"""
拍卖行系统
管理游戏内的物品拍卖功能
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class AuctionMode(Enum):
    """拍卖模式"""
    NORMAL = "normal"       # 普通拍卖
    TIMED = "timed"         # 限时拍卖
    SECRET = "secret"       # 暗拍

class BidderType(Enum):
    """竞拍者类型"""
    PLAYER = "player"
    NPC = "npc"

@dataclass
class AuctionItem:
    """拍卖物品"""
    id: str
    name: str
    description: str
    seller_id: str
    starting_price: int
    current_price: int
    buyout_price: Optional[int] = None
    mode: AuctionMode = AuctionMode.NORMAL
    end_time: Optional[datetime] = None
    bids: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.bids is None:
            self.bids = []

@dataclass
class Bidder:
    """竞拍者"""
    id: str
    name: str
    bidder_type: BidderType
    max_budget: int

class AuctionSystem:
    """拍卖系统"""
    
    def __init__(self):
        self.active_auctions: Dict[str, AuctionItem] = {}
        self.completed_auctions: List[AuctionItem] = []
        self.bidders: Dict[str, Bidder] = {}
        self.auction_id_counter = 0
    
    def create_auction(self, item_name: str, seller_id: str, 
                      starting_price: int, **kwargs) -> str:
        """创建拍卖"""
        self.auction_id_counter += 1
        auction_id = f"auction_{self.auction_id_counter}"
        
        auction = AuctionItem(
            id=auction_id,
            name=item_name,
            description=kwargs.get("description", ""),
            seller_id=seller_id,
            starting_price=starting_price,
            current_price=starting_price,
            buyout_price=kwargs.get("buyout_price"),
            mode=kwargs.get("mode", AuctionMode.NORMAL)
        )
        
        self.active_auctions[auction_id] = auction
        return auction_id
    
    def place_bid(self, auction_id: str, bidder_id: str, amount: int) -> Dict[str, Any]:
        """竞价"""
        if auction_id not in self.active_auctions:
            return {"success": False, "message": "拍卖不存在"}
        
        auction = self.active_auctions[auction_id]
        
        if amount <= auction.current_price:
            return {"success": False, "message": "出价必须高于当前价格"}
        
        # 记录竞价
        auction.bids.append({
            "bidder_id": bidder_id,
            "amount": amount,
            "timestamp": datetime.now()
        })
        auction.current_price = amount
        
        # 检查是否达到一口价
        if auction.buyout_price and amount >= auction.buyout_price:
            self._complete_auction(auction_id, bidder_id)
            return {"success": True, "message": "恭喜！您以一口价获得了物品"}
        
        return {"success": True, "message": f"竞价成功！当前价格：{amount}"}
    
    def _complete_auction(self, auction_id: str, winner_id: str):
        """完成拍卖"""
        auction = self.active_auctions.pop(auction_id)
        auction.winner_id = winner_id
        self.completed_auctions.append(auction)
    
    def get_active_auctions(self) -> List[AuctionItem]:
        """获取活跃拍卖列表"""
        return list(self.active_auctions.values())

# 创建全局实例
auction_system = AuctionSystem()

__all__ = [
    "AuctionSystem", "AuctionItem", "AuctionMode", 
    "Bidder", "BidderType", "auction_system"
]
