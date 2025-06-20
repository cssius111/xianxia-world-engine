from typing import Optional


def load_dotenv(dotenv_path: Optional[str] = None) -> None:
    """Load environment variables from a .env file using ``python-dotenv``."""
    try:
        from dotenv import load_dotenv as _load
    except ImportError as exc:
        raise RuntimeError(
            "The 'python-dotenv' package must be installed to load '.env' files."
        ) from exc
    _load(dotenv_path)
