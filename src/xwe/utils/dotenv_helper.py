from pathlib import Path
from dotenv import load_dotenv as _load_dotenv


def load_dotenv(path: str | None = None) -> None:
    """Load environment variables from a .env file if it exists."""
    env_path = Path(path or '.env')
    if env_path.exists():
        _load_dotenv(env_path)
