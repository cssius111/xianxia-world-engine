"""
OpenAPI 文档生成器
用于配置 Swagger UI 前端页面及 JSON 文档返回
"""

from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint

from .middleware import register_middleware
from .specs.openapi_generator import setup_swagger_ui as setup_openapi_ui
from .v1 import game_bp, player_bp, save_bp, system_bp
from .v1.dev import dev_bp

# OpenAPI 规范主体结构
openapi_spec = {
    "openapi": "3.0.0",
    "info": {"title": "修仙世界引擎 API", "version": "1.0.0"},
    "paths": {},  # 接口路径可在此处追加
}


# 返回 OpenAPI JSON 格式文档
def openapi_json():
    return jsonify(openapi_spec)


# 设置 Swagger UI 到 Flask 应用
def setup_swagger_ui(app):
    swagger_ui = get_swaggerui_blueprint(
        "/api/docs",  # 文档前端访问路径
        "/api/openapi.json",  # 文档 JSON 数据源
        config={"app_name": "修仙世界引擎 API"},
    )
    app.register_blueprint(swagger_ui, url_prefix="/api/docs")
    app.add_url_rule("/api/openapi.json", "openapi_json", openapi_json)


def register_api(app: Flask, url_prefix: str = "/api"):
    """注册所有API蓝图并配置文档"""
    # 注册通用中间件
    register_middleware(app)

    v1_prefix = f"{url_prefix}/v1"

    # 注册各模块蓝图
    app.register_blueprint(game_bp, url_prefix=f"{v1_prefix}/game")
    app.register_blueprint(player_bp, url_prefix=f"{v1_prefix}/player")
    app.register_blueprint(save_bp, url_prefix=f"{v1_prefix}/save")
    app.register_blueprint(system_bp, url_prefix=f"{v1_prefix}/system")

    # 可选：开发调试API
    try:
        from game_config import config

        if config.ENABLE_DEV_API:
            if dev_bp is not None:
                app.register_blueprint(dev_bp, url_prefix=f"{v1_prefix}/dev")
            else:
                print("⚠️  dev_bp is None, skipping dev API registration")
    except Exception:
        pass

    # 设置Swagger文档
    try:
        setup_openapi_ui(app)
    except Exception:
        setup_swagger_ui(app)

    print(f"✅ API v1 已注册到: {v1_prefix}")

    return app


__all__ = ["register_api"]
