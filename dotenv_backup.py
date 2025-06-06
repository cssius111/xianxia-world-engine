import os
from pathlib import Path

def load_dotenv(dotenv_path=None):
    """Simple dotenv loader for tests."""
    path = Path(dotenv_path) if dotenv_path else Path(__file__).resolve().parent / '.env'
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            os.environ.setdefault(key, value)
