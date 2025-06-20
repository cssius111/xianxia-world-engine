import sys
import xwe.core.data_loader as real_loader
import xwe.features.visual_enhancement as ve_mod
sys.modules.setdefault("xwe_v2.plugins.visual_enhancement", ve_mod)
sys.modules.setdefault("xwe_v2.core.data_loader", real_loader)
import types
import pytest

from xwe_v2.plugins.auction_system import AuctionSystem, AuctionItem


class DummyPlayer:
    def __init__(self, name="玩家", level=10, lingshi=1000):
        self.name = name
        self.level = level
        self._lingshi = lingshi
        self.inventory = types.SimpleNamespace(add=lambda item, qty: None)

    def get_total_lingshi(self) -> int:
        return self._lingshi

    def spend_lingshi(self, amount: int) -> bool:
        if self._lingshi >= amount:
            self._lingshi -= amount
            return True
        return False


@pytest.fixture()
def auction_system():
    return AuctionSystem()


def test_init_loads_config(auction_system):
    assert "name" in auction_system.config
    assert isinstance(auction_system.auction_items, dict)


def test_generate_bidders(auction_system):
    player = DummyPlayer()
    bidders = auction_system._generate_bidders(player, 3)
    assert bidders
    assert all(b.name for b in bidders)


def test_process_player_bid(auction_system):
    player = DummyPlayer(lingshi=500)
    auction_system.current_item = AuctionItem(
        id="test", name="测试物品", description="desc", tier="低阶", base_price=100, max_price=200
    )
    auction_system.current_item.current_bid = 100
    auction_system.current_item.current_bidder = "npc"

    msg = auction_system.process_player_bid(player, 105)
    assert "成功" in msg
    assert auction_system.current_item.current_bid == 105
    assert auction_system.current_item.current_bidder == player.name
