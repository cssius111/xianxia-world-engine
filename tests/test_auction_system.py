import pytest
from xwe.core.character import Character, CharacterType
from xwe.features.auction_system import auction_system


def test_auction_system_basic():
    player = Character(name="测试玩家", character_type=CharacterType.PLAYER, level=20)
    player.add_lingshi(100000)

    result = auction_system.start_auction(player, "regular")

    assert "拍卖会圆满结束" in result
    assert len(auction_system.bidders) > 0
