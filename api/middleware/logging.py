"""
API日志中间件
记录所有API请求和响应
"""

import json
import logging
from datetime import datetime

from flask import Flask, g, request

# 设置日志格式
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("api")


def setup_logging(app: Flask):
    """
    设置API日志

    Args:
        app: Flask应用
    """

    @app.before_request
    def log_request():
        """记录请求信息"""
        # 获取请求信息
        request_data = {
            "request_id": getattr(g, "request_id", "unknown"),
            "method": request.method,
            "path": request.path,
            "query": dict(request.args),
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get("User-Agent"),
            "timestamp": datetime.now().isoformat(),
        }

        # 对于POST/PUT/PATCH请求，记录body
        if request.method in ["POST", "PUT", "PATCH"]:
            if request.is_json:
                try:
                    request_data["body"] = request.get_json()
                except:
                    request_data["body"] = "<invalid json>"
            else:
                request_data["body"] = "<non-json body>"

        # 记录日志
        logger.info(f"API Request: {json.dumps(request_data, ensure_ascii=False)}")

    @app.after_request
    def log_response(response):
        """记录响应信息"""
        # 获取响应信息
        response_data = {
            "request_id": getattr(g, "request_id", "unknown"),
            "status_code": response.status_code,
            "content_type": response.content_type,
            "timestamp": datetime.now().isoformat(),
        }

        # 记录处理时间
        if hasattr(g, "request_start_time"):
            import time

            duration = (time.time() - g.request_start_time) * 1000
            response_data["duration_ms"] = round(duration, 2)

        # 对于错误响应，记录响应体
        if response.status_code >= 400:
            try:
                response_data["body"] = response.get_json()
            except:
                pass

        # 根据状态码选择日志级别
        if response.status_code >= 500:
            logger.error(f"API Response: {json.dumps(response_data, ensure_ascii=False)}")
        elif response.status_code >= 400:
            logger.warning(f"API Response: {json.dumps(response_data, ensure_ascii=False)}")
        else:
            logger.info(f"API Response: {json.dumps(response_data, ensure_ascii=False)}")

        return response


def log_error(error: Exception, context: dict = None):
    """
    记录错误日志

    Args:
        error: 异常对象
        context: 额外的上下文信息
    """
    error_data = {
        "request_id": getattr(g, "request_id", "unknown"),
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.now().isoformat(),
    }

    if context:
        error_data["context"] = context

    logger.error(f"API Error: {json.dumps(error_data, ensure_ascii=False)}")
