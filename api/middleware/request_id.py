"""
请求ID中间件
为每个请求生成唯一ID，方便追踪和调试
"""

import time
import uuid

from flask import Flask, g, request


def setup_request_id(app: Flask):
    """
    设置请求ID中间件

    Args:
        app: Flask应用
    """

    @app.before_request
    def before_request():
        """在请求开始时生成请求ID"""
        # 尝试从请求头获取请求ID
        request_id = request.headers.get("X-Request-ID")

        # 如果没有，生成新的请求ID
        if not request_id:
            request_id = generate_request_id()

        # 存储到g对象中
        g.request_id = request_id
        g.request_start_time = time.time()

    @app.after_request
    def after_request(response):
        """在响应中添加请求ID"""
        if hasattr(g, "request_id"):
            response.headers["X-Request-ID"] = g.request_id

        # 添加处理时间
        if hasattr(g, "request_start_time"):
            duration = (time.time() - g.request_start_time) * 1000  # 毫秒
            response.headers["X-Response-Time"] = f"{duration:.2f}ms"

        return response


def generate_request_id() -> str:
    """
    生成请求ID
    格式: 时间戳-随机UUID前8位
    """
    timestamp = int(time.time())
    uuid_part = str(uuid.uuid4())[:8]
    return f"{timestamp}-{uuid_part}"


def get_request_id() -> str:
    """
    获取当前请求的ID

    Returns:
        请求ID，如果不存在则返回 'unknown'
    """
    return getattr(g, "request_id", "unknown")
