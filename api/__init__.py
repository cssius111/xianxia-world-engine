"""
修仙世界引擎 - API模块
负责注册和管理所有API端点
"""

from flask import Flask
from .v1 import game_bp, player_bp, save_bp, system_bp
from .middleware import register_middleware


def register_api(app: Flask, url_prefix: str = '/api'):
    """
    注册所有API蓝图到Flask应用
    
    Args:
        app: Flask应用实例
        url_prefix: API的URL前缀，默认为 '/api'
    """
    # 注册中间件
    register_middleware(app)
    
    # 注册v1版本的API
    v1_prefix = f"{url_prefix}/v1"
    
    # 游戏相关API
    app.register_blueprint(game_bp, url_prefix=f"{v1_prefix}/game")
    
    # 玩家相关API
    app.register_blueprint(player_bp, url_prefix=f"{v1_prefix}/player")
    
    # 存档相关API
    app.register_blueprint(save_bp, url_prefix=f"{v1_prefix}/save")
    
    # 系统相关API
    app.register_blueprint(system_bp, url_prefix=f"{v1_prefix}/system")
    
    print(f"✅ API v1 已注册到: {v1_prefix}")


__all__ = ['register_api']
