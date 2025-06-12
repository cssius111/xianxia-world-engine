"""
OpenAPI 文档生成器
用于配置 Swagger UI 前端页面及 JSON 文档返回
"""

from flask_swagger_ui import get_swaggerui_blueprint
from flask import jsonify

# OpenAPI 规范主体结构
openapi_spec = {
    "openapi": "3.0.0",
    "info": {
        "title": "修仙世界引擎 API",
        "version": "1.0.0"
    },
    "paths": {}  # 接口路径可在此处追加
}

# 返回 OpenAPI JSON 格式文档
def openapi_json():
    return jsonify(openapi_spec)

# 设置 Swagger UI 到 Flask 应用
def setup_swagger_ui(app):
    swagger_ui = get_swaggerui_blueprint(
        '/api/docs',           # 文档前端访问路径
        '/api/openapi.json',   # 文档 JSON 数据源
        config={ 'app_name': "修仙世界引擎 API" }
    )
    app.register_blueprint(swagger_ui, url_prefix='/api/docs')
    app.add_url_rule("/api/openapi.json", "openapi_json", openapi_json)
