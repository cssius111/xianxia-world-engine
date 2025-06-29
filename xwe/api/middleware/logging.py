"""
日志中间件
记录API请求和响应
"""

import logging
import time
from flask import Flask, g, request

logger = logging.getLogger(__name__)


def setup_logging(app: Flask) -> None:
    """
    设置请求日志中间件
    
    Args:
        app: Flask应用实例
    """
    
    @app.before_request
    def log_request_start():
        """记录请求开始"""
        g.start_time = time.time()
        
        # 记录请求信息
        logger.info(
            f"Request started: {request.method} {request.path} "
            f"from {request.remote_addr}"
        )
        
        # 开发模式下记录请求体
        if app.debug and request.data:
            logger.debug(f"Request body: {request.data.decode('utf-8', errors='ignore')}")
    
    @app.after_request
    def log_request_end(response):
        """记录请求结束"""
        if hasattr(g, 'start_time'):
            elapsed = (time.time() - g.start_time) * 1000  # 转换为毫秒
            
            logger.info(
                f"Request completed: {request.method} {request.path} "
                f"- Status: {response.status_code} "
                f"- Duration: {elapsed:.2f}ms"
            )
        
        return response
    
    # 设置日志格式
    if not app.debug:
        # 生产环境使用更简洁的日志
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        ))
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
