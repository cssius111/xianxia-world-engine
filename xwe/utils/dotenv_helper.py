from typing import Optional
from dotenv import load_dotenv as _load


def load_dotenv(dotenv_path: Optional[str] = None) -> None:
    """Load environment variables from a .env file using python-dotenv."""
    _load(dotenv_path)
