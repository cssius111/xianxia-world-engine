"""
API中间件模块
"""

from flask import Flask

from .cors import setup_cors
from .error_handler import setup_error_handlers
from .logging import setup_logging
from .request_id import setup_request_id


def register_middleware(app: Flask):
    """
    注册所有中间件

    Args:
        app: Flask应用实例
    """
    # CORS支持
    setup_cors(app)

    # 请求ID
    setup_request_id(app)

    # 日志
    setup_logging(app)

    # 错误处理
    setup_error_handlers(app)

    print("✅ API中间件已注册")


__all__ = ["register_middleware"]
