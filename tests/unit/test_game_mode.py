
from xwe.core.game_core import GameCore


def test_game_mode_default():
    game = GameCore()
    assert game.game_state.game_mode == "player"


def test_game_mode_dev():
    game = GameCore(game_mode="dev")
    assert game.game_state.game_mode == "dev"
