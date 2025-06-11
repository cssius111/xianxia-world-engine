"""
CORS（跨域资源共享）中间件
"""

from flask import Flask, make_response, request
from typing import Optional


def setup_cors(app: Flask, 
               origins: Optional[str] = None,
               methods: Optional[str] = None,
               headers: Optional[str] = None):
    """
    设置CORS支持
    
    Args:
        app: Flask应用
        origins: 允许的来源，默认为 '*'
        methods: 允许的方法，默认为常见方法
        headers: 允许的头部，默认为常见头部
    """
    if origins is None:
        origins = '*'
    
    if methods is None:
        methods = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        
    if headers is None:
        headers = 'Content-Type, Authorization, X-Requested-With'
    
    @app.after_request
    def after_request(response):
        """添加CORS头部"""
        # 允许的来源
        response.headers['Access-Control-Allow-Origin'] = origins
        
        # 允许的方法
        response.headers['Access-Control-Allow-Methods'] = methods
        
        # 允许的头部
        response.headers['Access-Control-Allow-Headers'] = headers
        
        # 允许发送凭证
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        
        # 预检请求的缓存时间
        response.headers['Access-Control-Max-Age'] = '3600'
        
        return response
    
    @app.before_request
    def handle_preflight():
        """处理预检请求"""
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers['Access-Control-Allow-Origin'] = origins
            response.headers['Access-Control-Allow-Methods'] = methods
            response.headers['Access-Control-Allow-Headers'] = headers
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '3600'
            return response
