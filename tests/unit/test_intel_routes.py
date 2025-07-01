import sys
from pathlib import Path

# Ensure src is in sys.path so run.py can import config and other modules
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))

import run


def test_intel_tips_endpoint():
    with run.app.test_client() as client:
        resp = client.get('/intel/tips')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'tips' in data
        assert isinstance(data['tips'], list)
