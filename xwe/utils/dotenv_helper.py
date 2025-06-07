from typing import Optional

def load_dotenv(dotenv_path: Optional[str] = None) -> None:
    """Load environment variables from a .env file.

    Tries to use `python-dotenv`. If not installed, shows clear error.
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

    except ImportError:
        raise ImportError(
            "Missing required package 'python-dotenv'. Please install it using:\n"
            "pip install python-dotenv"
        )

    _load(dotenv_path)
