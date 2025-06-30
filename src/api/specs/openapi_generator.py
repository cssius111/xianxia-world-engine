"""
OpenAPI文档生成器
生成符合OpenAPI 3.0规范的API文档
"""

from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint


def generate_openapi_spec():
    """生成OpenAPI规范文档"""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "仙侠世界引擎 API",
            "version": "1.0.0",
            "description": "一个基于文本的仙侠世界模拟器API",
            "contact": {
                "name": "XWE Team",
                "email": "support@xwe.com"
            }
        },
        "servers": [
            {
                "url": "http://localhost:5001/api",
                "description": "开发服务器"
            }
        ],
        "paths": {
            "/v1/game/status": {
                "get": {
                    "tags": ["游戏"],
                    "summary": "获取游戏状态",
                    "responses": {
                        "200": {
                            "description": "成功",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "version": {"type": "string"},
                                            "players_online": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/v1/player/info": {
                "get": {
                    "tags": ["玩家"],
                    "summary": "获取玩家信息",
                    "responses": {
                        "200": {
                            "description": "成功",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Player"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "Player": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "level": {"type": "integer"},
                        "realm": {"type": "string"},
                        "attributes": {
                            "type": "object",
                            "properties": {
                                "health": {"type": "integer"},
                                "mana": {"type": "integer"},
                                "stamina": {"type": "integer"},
                                "attack": {"type": "integer"},
                                "defense": {"type": "integer"}
                            }
                        }
                    }
                }
            }
        },
        "tags": [
            {
                "name": "游戏",
                "description": "游戏核心功能"
            },
            {
                "name": "玩家",
                "description": "玩家相关操作"
            },
            {
                "name": "存档",
                "description": "游戏存档管理"
            },
            {
                "name": "系统",
                "description": "系统设置和信息"
            }
        ]
    }


def setup_swagger_ui(app: Flask):
    """配置Swagger UI"""
    SWAGGER_URL = '/api/docs'
    API_URL = '/api/openapi.json'
    
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "仙侠世界引擎 API",
            'docExpansion': 'none',
            'defaultModelsExpandDepth': -1
        }
    )
    
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    @app.route('/api/openapi.json')
    def openapi_spec():
        return jsonify(generate_openapi_spec())
    
    print(f"✅ API文档已启用: http://localhost:5001{SWAGGER_URL}")
