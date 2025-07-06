import pytest


@pytest.mark.parametrize(
    "endpoint,key",
    [
        ("/api/cultivation/status", "realm"),  # 返回的是{realm, progress, ...}而不是{data: ...}
        ("/api/achievements", "achievements"),
        ("/api/map", "data"),
        ("/api/quests", "quests"),
        ("/api/intel", "data"),
        ("/api/player/stats/detailed", "data"),
    ],
)
def test_get_endpoints(client, endpoint, key):
    resp = client.get(endpoint)
    assert resp.status_code == 200
    data = resp.get_json()
    # Some endpoints return {success: true, data: ...}, others return data directly
    if 'success' in data:
        assert data.get("success") is True
    assert key in data


def test_cultivation_start(client):
    resp = client.post("/api/cultivation/start", json={"hours": 2})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("success") is True
    assert "result" in data


def _setup_mock_game(app, mana=30, comprehension=15, progress=0):
    """Helper to create a mocked game instance for cultivation."""
    from types import SimpleNamespace
    from src.xwe.core.attributes import CharacterAttributes
    from unittest.mock import MagicMock

    attrs = CharacterAttributes()
    attrs.current_mana = mana
    attrs.comprehension = comprehension
    attrs.realm_progress = progress
    attrs.cultivation_exp = 0
    attrs.realm_name = "炼气期"
    player = SimpleNamespace(attributes=attrs)

    game = SimpleNamespace()
    game.game_state = SimpleNamespace(player=player, current_location="qingyun_city")
    game.time_system = MagicMock()
    game.world_map = MagicMock()
    game.world_map.get_area.return_value = SimpleNamespace(danger_level=2, name="青云城")
    game.cultivation_system = MagicMock()
    game.cultivation_system.calculate_cultivation_exp.return_value = 20
    game.cultivation_system.realm_breakthroughs = {"炼气期": {"exp_required": 100}}
    game.narrative_system = MagicMock()
    game.narrative_system.generate_story_event.return_value = {"id": "ev"}

    app.game_instances = {"test_session": {"game": game}}
    return game, player


def test_start_cultivation_success(client, app):
    game, player = _setup_mock_game(app)
    with client.session_transaction() as sess:
        sess["session_id"] = "test_session"

    resp = client.post("/api/cultivation/start", json={"hours": 2})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["exp_gained"] == 20
    assert player.attributes.current_mana == 20
    assert game.time_system.advance_time.called


def test_start_cultivation_insufficient_mana(client, app):
    _setup_mock_game(app, mana=3)
    with client.session_transaction() as sess:
        sess["session_id"] = "test_session"

    resp = client.post("/api/cultivation/start", json={"hours": 2})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["success"] is False
    assert "confirm" in data


def test_start_cultivation_continue(client, app):
    game, player = _setup_mock_game(app)
    with client.session_transaction() as sess:
        sess["session_id"] = "test_session"

    resp1 = client.post("/api/cultivation/start", json={"hours": 2})
    assert resp1.status_code == 200
    assert player.attributes.current_mana == 20

    resp2 = client.post("/api/cultivation/start", json={"hours": 1})
    assert resp2.status_code == 200
    assert player.attributes.current_mana == 15
    # ensure time advanced twice
    assert game.time_system.advance_time.call_count == 2
