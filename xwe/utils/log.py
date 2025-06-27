"""日志配置工具"""

from __future__ import annotations

import gzip
import logging
import shutil
from pathlib import Path
from logging.handlers import RotatingFileHandler


def configure_logging(log_dir: str, filename: str = "app.log") -> None:
    """配置日志轮转并自动压缩"""

    Path(log_dir).mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    handler = RotatingFileHandler(Path(log_dir) / filename, maxBytes=1024 * 1024, backupCount=5)

    def _rotator(source: str, dest: str) -> None:  # pragma: no cover - IO utility
        with open(source, "rb") as sf, gzip.open(dest + ".gz", "wb") as df:
            shutil.copyfileobj(sf, df)
        Path(source).unlink()

    handler.rotator = _rotator

    def _namer(dest: str) -> str:  # pragma: no cover - file renaming
        """添加 .gz 后缀用于轮转文件"""
        return dest + ".gz"

    handler.namer = _namer
    logging.getLogger().addHandler(handler)

