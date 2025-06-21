"""
错误处理中间件
统一处理API错误响应
"""

import logging
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def setup_error_handlers(app: Flask) -> None:
    """
    设置全局错误处理器
    
    Args:
        app: Flask应用实例
    """
    
    @app.errorhandler(404)
    def not_found_error(error):
        """处理404错误"""
        return jsonify({
            "error": "Not Found",
            "message": "请求的资源不存在",
            "status": 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """处理500错误"""
        logger.error(f"Internal error: {error}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "服务器内部错误",
            "status": 500
        }), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """处理所有HTTP异常"""
        return jsonify({
            "error": e.name,
            "message": e.description,
            "status": e.code
        }), e.code
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        """处理未预期的错误"""
        logger.exception("Unexpected error occurred")
        return jsonify({
            "error": "Unexpected Error",
            "message": "发生了未预期的错误",
            "status": 500
        }), 500
