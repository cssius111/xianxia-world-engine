from typing import Optional


def load_dotenv(dotenv_path: Optional[str] = None) -> None:
    """Load environment variables from a .env file.

    Tries to use ``python-dotenv`` if available; otherwise falls back to the
    simplified implementation in ``dotenv_backup.py``.
    """
    try:
        from dotenv import load_dotenv as _load
    except Exception:
        try:
            from dotenv_backup import load_dotenv as _load  # type: ignore
        except Exception:
            import sys
            from pathlib import Path

            backup_dir = Path(__file__).resolve().parent.parent.parent / "_archive"
            sys.path.append(str(backup_dir))
            from dotenv_backup import load_dotenv as _load  # type: ignore
    _load(dotenv_path)
