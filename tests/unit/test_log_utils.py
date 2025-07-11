import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

from src.xwe.utils.log import configure_logging


def test_log_handler_namer(tmp_path):
    logger = logging.getLogger()
    old_handlers = list(logger.handlers)
    try:
        configure_logging(str(tmp_path), "test.log")
        handler = next(
            h for h in logger.handlers if isinstance(h, RotatingFileHandler)
        )
        assert handler.namer("foo") == "foo.gz"
    finally:
        logger.handlers = old_handlers


def test_no_duplicate_handlers(tmp_path):
    logger = logging.getLogger()
    old_handlers = list(logger.handlers)
    try:
        configure_logging(str(tmp_path), "test.log")
        configure_logging(str(tmp_path), "test.log")

        log_path = tmp_path / "test.log"
        handlers = [
            h
            for h in logger.handlers
            if isinstance(h, RotatingFileHandler)
            and Path(h.baseFilename) == log_path
        ]
        assert len(handlers) == 1
    finally:
        logger.handlers = old_handlers


def test_configure_logging_debug_level(tmp_path):
    logger = logging.getLogger()
    old_handlers = list(logger.handlers)
    old_level = logger.level
    logger.handlers = []
    logger.setLevel(logging.NOTSET)
    try:
        configure_logging(str(tmp_path), "debug.log", level=logging.DEBUG)
        assert logger.level == logging.DEBUG
    finally:
        logger.handlers = old_handlers
        logger.setLevel(old_level)


def test_configure_logging_info_level(tmp_path):
    logger = logging.getLogger()
    old_handlers = list(logger.handlers)
    old_level = logger.level
    logger.handlers = []
    logger.setLevel(logging.NOTSET)
    try:
        configure_logging(str(tmp_path), "info.log", level=logging.INFO)
        assert logger.level == logging.INFO
    finally:
        logger.handlers = old_handlers
        logger.setLevel(old_level)

