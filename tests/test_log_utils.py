import logging
from logging.handlers import RotatingFileHandler

from xwe.utils.log import configure_logging


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

