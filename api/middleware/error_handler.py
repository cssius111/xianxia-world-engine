"""
全局错误处理中间件
"""

from flask import Flask, jsonify
import traceback
from ..errors import APIError
from ..utils.response import _build_meta
import time


def setup_error_handlers(app: Flask):
    """
    设置全局错误处理器
    
    Args:
        app: Flask应用
    """
    
    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        """处理API错误"""
        response = {
            'success': False,
            'error': error.to_dict(),
            'meta': _build_meta(time.time())
        }
        return jsonify(response), error.status_code
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """处理404错误"""
        response = {
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': '请求的资源不存在',
                'details': {
                    'path': error.description
                }
            },
            'meta': _build_meta(time.time())
        }
        return jsonify(response), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """处理405错误"""
        response = {
            'success': False,
            'error': {
                'code': 'METHOD_NOT_ALLOWED',
                'message': '不支持该HTTP方法',
                'details': {
                    'method': error.description
                }
            },
            'meta': _build_meta(time.time())
        }
        return jsonify(response), 405
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """处理500错误"""
        # 记录详细错误信息
        print(f"内部服务器错误: {str(error)}")
        print(traceback.format_exc())
        
        response = {
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '服务器内部错误',
                'details': {}
            },
            'meta': _build_meta(time.time())
        }
        return jsonify(response), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """处理未预期的错误"""
        # 记录详细错误信息
        print(f"未预期的错误: {type(error).__name__}: {str(error)}")
        print(traceback.format_exc())
        
        response = {
            'success': False,
            'error': {
                'code': 'UNEXPECTED_ERROR',
                'message': '发生了未预期的错误',
                'details': {
                    'type': type(error).__name__
                }
            },
            'meta': _build_meta(time.time())
        }
        return jsonify(response), 500
