"""
请求ID中间件
为每个请求生成唯一ID用于追踪
"""

import uuid
from flask import Flask, g, request


def setup_request_id(app: Flask) -> None:
    """
    设置请求ID中间件
    
    Args:
        app: Flask应用实例
    """
    
    @app.before_request
    def add_request_id():
        """为每个请求添加唯一ID"""
        # 检查是否已有请求ID（从客户端传来）
        request_id = request.headers.get('X-Request-ID')
        
        if not request_id:
            # 生成新的请求ID
            request_id = str(uuid.uuid4())
        
        # 存储在g对象中，供后续使用
        g.request_id = request_id
    
    @app.after_request
    def add_request_id_header(response):
        """在响应头中添加请求ID"""
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        
        return response
