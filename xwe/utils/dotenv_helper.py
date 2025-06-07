from typing import Optional

def load_dotenv(dotenv_path: Optional[str] = None) -> None:
    """Load environment variables from a .env file.

    Tries to use `python-dotenv`. If not installed, shows clear error.
    """
    try:
        from dotenv import load_dotenv as _load
    except ImportError:
        raise ImportError(
            "Missing required package 'python-dotenv'. Please install it using:\n"
            "pip install python-dotenv"
        )
    _load(dotenv_path)
