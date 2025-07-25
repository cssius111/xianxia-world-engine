import pytest
from src.app import create_app

@pytest.fixture
def app_instance():
    app = create_app()
    app.config.update(TESTING=True, DEV_PASSWORD='test')
    return app


def test_root_contains_welcome_modal(app_instance):
    with app_instance.test_client() as client:
        resp = client.get('/')
        assert resp.status_code == 200
        data = resp.data.decode('utf-8')
        assert 'welcomeModal' in data
        assert '诊断工具' not in data
