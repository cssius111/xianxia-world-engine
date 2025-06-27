from xwe.core.state.game_state_manager import GameStateManager
from xwe.core.game_core import GameState


def test_state_manager(tmp_path):
    mgr = GameStateManager(log_dir=tmp_path)
    state = GameState()
    mgr.set_state(state, action="start")
    log_file = tmp_path / "state_transitions.log"
    assert log_file.exists()

