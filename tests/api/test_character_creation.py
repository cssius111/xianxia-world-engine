import pytest


@pytest.fixture
def app_instance():
    from src.app import create_app
    app = create_app()
    app.config.update(TESTING=True)
    return app


def test_api_roll_returns_complete_character(app_instance):
    with app_instance.test_client() as client:
        resp = client.post('/api/roll', json={'mode': 'random'})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True

        character = data.get("character")
        assert isinstance(character, dict)
        for field in ["name", "gender", "background", "attributes", "destiny", "talents"]:
            assert field in character

        attrs = character["attributes"]
        assert isinstance(attrs, dict)
        for attr in ["constitution", "comprehension", "spirit", "luck"]:
            assert isinstance(attrs.get(attr), (int, float))

        destiny = data.get("destiny")
        assert isinstance(destiny, dict)
        assert isinstance(destiny.get("name"), str)


def test_create_character_writes_session(app_instance):
    with app_instance.test_client() as client:
        resp = client.post('/create_character', json={'name': 'Tester'})
        assert resp.status_code == 200
        with client.session_transaction() as sess:
            assert sess.get('player_name') == 'Tester'
            assert 'player_id' in sess
            assert 'session_id' in sess
            assert sess.get('player_created') is True

