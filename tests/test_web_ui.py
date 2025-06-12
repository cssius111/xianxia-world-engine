"""Web UI 测试"""

from run_web_ui_optimized import app


def test_simple_web_ui():
    with app.test_client() as client:
        resp = client.get('/')
        assert resp.status_code == 200


def test_enhanced_web_ui():
    with app.test_client() as client:
        resp = client.get('/status')
        assert resp.status_code == 200
