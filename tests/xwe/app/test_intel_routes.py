import sys
from pathlib import Path

# Ensure project root and src are on the path so the entrypoint can import
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from scripts import run


def test_intel_tips_endpoint():
    with run.app.test_client() as client:
        resp = client.get('/api/intel/tips')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'tips' in data
        assert isinstance(data['tips'], list)
