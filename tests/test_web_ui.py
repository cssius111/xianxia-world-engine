
"""Web UI 测试"""

from entrypoints.run_web_ui_optimized import app

from entrypoints.run_web_ui_optimized import app as simple_app
from entrypoints.run_web_ui_optimized import app as enhanced_app



def test_simple_web_ui():
    with app.test_client() as client:
        resp = client.get('/')
        assert resp.status_code == 200


def test_enhanced_web_ui():
    with app.test_client() as client:
        resp = client.get('/status')
        assert resp.status_code == 200


def test_intel_api():
    with app.test_client() as client:
        resp = client.get('/api/intel')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'global' in data and 'personal' in data
