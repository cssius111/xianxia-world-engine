import os
from types import SimpleNamespace
from unittest.mock import MagicMock

os.environ['ENABLE_PROMETHEUS'] = 'false'
from src.app import create_app, game_instances

app = create_app()


def test_continue_game_redirects_if_autosave_missing():
    """When autosave is missing, /continue should redirect to /intro."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["session_id"] = "test_session"

        game = SimpleNamespace(game_state=SimpleNamespace())
        game.technical_ops = MagicMock()
        game.technical_ops.load_game.return_value = None
        game_instances["test_session"] = {"game": game, "last_update": 0, "need_refresh": False}

        resp = client.get("/continue")
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/intro")
