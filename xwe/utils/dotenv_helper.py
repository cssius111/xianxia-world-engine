from typing import Optional


def load_dotenv(dotenv_path: Optional[str] = None) -> None:
    """Load environment variables from a .env file.

    Tries to use ``python-dotenv`` if available; otherwise falls back to the
    simplified implementation in ``dotenv_backup.py``.
    """
    try:
        from dotenv import load_dotenv as _load
    except Exception:
        from dotenv_backup import load_dotenv as _load  # type: ignore
    _load(dotenv_path)
