from run_web_ui import app as simple_app
from run_web_ui import app as enhanced_app


def test_simple_web_ui():
    with simple_app.test_client() as client:
        resp = client.get('/')
        assert resp.status_code == 200


def test_enhanced_web_ui():
    with enhanced_app.test_client() as client:
        resp = client.get('/status')
        assert resp.status_code == 200
