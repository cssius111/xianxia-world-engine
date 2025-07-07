import os

import pytest

from scripts.run import app, get_game_instance

pytestmark = pytest.mark.skipif(
    not os.getenv("DEEPSEEK_API_KEY"), reason="DeepSeek API key not set"
)


def test_status_uses_game_session():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["player_id"] = "player_test"
            sess["player_name"] = "Tester"
            sess["session_id"] = "session_test"

        instance = get_game_instance("session_test")
        game = instance["game"]
        player = game.game_state.player
        player.name = "Tester"
        player.attributes.current_health = 80
        player.attributes.max_health = 120
        player.attributes.current_mana = 40
        player.attributes.max_mana = 60
        player.extra_data["destiny"] = {"name": "天命测试"}
        player.extra_data["talents"] = [{"name": "剑修"}]
        game.game_state.current_location = "TestTown"

        resp = client.get("/status")
        assert resp.status_code == 200
        data = resp.get_json()
        attrs = data["player"]["attributes"]
        assert attrs["current_health"] == 80
        assert attrs["max_health"] == 120
        assert attrs["current_mana"] == 40
        assert attrs["max_mana"] == 60
        assert data["player"]["name"] == "Tester"
        assert data["location"] == "TestTown"
        assert data["destiny"]["name"] == "天命测试"
        assert data["talents"][0]["name"] == "剑修"
