"""
CORS (跨域资源共享) 中间件
处理跨域请求的配置
"""

from flask import Flask
from flask_cors import CORS


def setup_cors(app: Flask) -> None:
    """
    配置CORS中间件
    
    Args:
        app: Flask应用实例
    """
    # 开发环境允许所有来源
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:*", "http://127.0.0.1:*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Request-ID"],
            "expose_headers": ["X-Request-ID"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })
