import json

from src.xwe.core.state.game_state_manager import GameStateManager
from src.xwe.core.game_core import GameState


def test_state_manager(tmp_path):
    mgr = GameStateManager(log_dir=tmp_path)

    state1 = GameState()
    mgr.set_state(state1, action="start")

    state2 = GameState(game_time=1.0)
    mgr.set_state(state2, action="progress")

    log_file = tmp_path / "state_transitions.log"
    assert log_file.exists()

    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2

    entry1 = json.loads(lines[0])
    assert entry1["action"] == "start"
    assert entry1["state"] == state1.to_dict()
    assert "timestamp" in entry1

    entry2 = json.loads(lines[1])
    assert entry2["action"] == "progress"
    assert entry2["state"] == state2.to_dict()
    assert "timestamp" in entry2

