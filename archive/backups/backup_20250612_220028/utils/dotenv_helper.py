from typing import Any, Optional

def load_dotenv(dotenv_path: Optional[str] = None) -> None:
    """Load environment variables from a .env file.

    Tries to use `python-dotenv`. If not installed, falls back to dotenv_backup or archive fallback.
    """
    try:
        from dotenv import load_dotenv as _load
    except ImportError:
        try:
            from dotenv_backup import load_dotenv as _load  # type: ignore
        except ImportError:
            import sys
            from pathlib import Path

            # 尝试从项目的 _archive 目录中加载备用模块
            backup_dir = Path(__file__).resolve().parent.parent.parent / "_archive"
            sys.path.append(str(backup_dir))
            try:
                from dotenv_backup import load_dotenv as _load  # type: ignore
            except ImportError:
                raise ImportError(
                    "Cannot find 'python-dotenv' or 'dotenv_backup'. "
                    "Please install 'python-dotenv' using:\n"
                    "pip install python-dotenv"
                )
    _load(dotenv_path)
