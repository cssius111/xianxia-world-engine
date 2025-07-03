import logging
import os
from logging import Handler
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Dict

LOG_FMT = "%(asctime)s [%(levelname).1s] %(name)s: %(message)s"


class ThrottleFilter(logging.Filter):
    """Filter that limits log output frequency per logger."""

    def __init__(self, interval: float = 10.0) -> None:
        super().__init__()
        self.interval = interval
        self.last_emit: Dict[str, float] = {}

    def filter(self, record: logging.LogRecord) -> bool:
        last = self.last_emit.get(record.name)
        if last is None or record.created - last >= self.interval:
            self.last_emit[record.name] = record.created
            return True
        return False


class ChangeOnlyFilter(logging.Filter):
    """Filter that emits logs only when the message changes."""

    def __init__(self) -> None:
        super().__init__()
        self.last_message: Dict[str, str] = {}

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        last = self.last_message.get(record.name)
        if last != msg:
            self.last_message[record.name] = msg
            return True
        return False


def _add_handler(logger: logging.Logger, handler: Handler) -> None:
    logger.addHandler(handler)


def setup_logging() -> None:
    """Configure root logger for the application."""

    level = logging.DEBUG if os.getenv("DEBUG_LOG") in {"1", "true", "True"} else logging.INFO
    root = logging.getLogger()
    root.setLevel(level)

    # Remove existing handlers to avoid duplicate logs
    for h in list(root.handlers):
        root.removeHandler(h)

    formatter = logging.Formatter(LOG_FMT, "%H:%M:%S")

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    console.addFilter(ChangeOnlyFilter())
    console.addFilter(ThrottleFilter())
    _add_handler(root, console)

    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    debug_file = TimedRotatingFileHandler(log_dir / "app_debug.log", when="D", backupCount=7, encoding="utf-8")
    debug_file.setLevel(logging.DEBUG)
    debug_file.setFormatter(formatter)
    _add_handler(root, debug_file)

    info_file = TimedRotatingFileHandler(log_dir / "app.log", when="D", backupCount=7, encoding="utf-8")
    info_file.setLevel(logging.INFO)
    info_file.setFormatter(formatter)
    _add_handler(root, info_file)

