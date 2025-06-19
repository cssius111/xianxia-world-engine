"""
OpenAPI/Swagger文档生成器
自动生成API文档
"""

from flask import Flask, Blueprint, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from typing import Dict, Any, List
import inspect
import re


class OpenAPIGenerator:
    """OpenAPI规范生成器"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "修仙世界引擎 API",
                "description": "XianXia World Engine RESTful API Documentation",
                "version": "1.0.0",
                "contact": {
                    "name": "XWE Team",
                    "email": "support@xwe.example.com"
                }
            },
            "servers": [
                {
                    "url": "http://localhost:5001/api/v1",
                    "description": "Development server"
                }
            ],
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {}
            },
            "tags": []
        }
        
    def generate_from_app(self, app: Flask) -> Dict[str, Any]:
        """从Flask应用生成OpenAPI规范"""
        self.app = app
        
        # 收集所有路由
        for rule in app.url_map.iter_rules():
            if rule.endpoint == 'static':
                continue
                
            # 获取视图函数
            view_func = app.view_functions.get(rule.endpoint)
            if not view_func:
                continue
                
            # 生成路径规范
            self._add_path_spec(rule, view_func)
            
        # 添加通用响应模式
        self._add_common_schemas()
        
        # 添加标签
        self._add_tags()
        
        return self.spec
        
    def _add_path_spec(self, rule, view_func):
        """添加路径规范"""
        # 转换Flask路径到OpenAPI格式
        path = self._convert_path(rule.rule)
        
        # 跳过非API路径
        if not path.startswith('/api/'):
            return
            
        if path not in self.spec["paths"]:
            self.spec["paths"][path] = {}
            
        # 处理每个HTTP方法
        for method in rule.methods:
            if method in ['HEAD', 'OPTIONS']:
                continue
                
            method_lower = method.lower()
            
            # 从函数文档字符串提取描述
            doc = inspect.getdoc(view_func) or ""
            summary, description = self._parse_docstring(doc)
            
            # 构建操作规范
            operation = {
                "summary": summary or f"{method} {path}",
                "description": description,
                "operationId": f"{rule.endpoint}_{method_lower}",
                "tags": [self._get_tag_from_path(path)],
                "responses": self._get_responses_spec(view_func, doc)
            }
            
            # 添加请求体规范（POST/PUT）
            if method in ['POST', 'PUT', 'PATCH']:
                operation["requestBody"] = self._get_request_body_spec(view_func, doc)
                
            # 添加参数规范
            parameters = self._get_parameters_spec(rule, doc)
            if parameters:
                operation["parameters"] = parameters
                
            self.spec["paths"][path][method_lower] = operation
            
    def _convert_path(self, flask_path: str) -> str:
        """转换Flask路径到OpenAPI格式"""
        # 转换 <param> 到 {param}
        return re.sub(r'<(?:.*?:)?(.+?)>', r'{\1}', flask_path)
        
    def _parse_docstring(self, doc: str) -> tuple:
        """解析文档字符串"""
        lines = doc.strip().split('\n')
        if not lines:
            return "", ""
            
        summary = lines[0].strip()
        description = ""
        
        if len(lines) > 2:
            # 跳过空行
            desc_lines = []
            for line in lines[2:]:
                line = line.strip()
                if line and not line.startswith(('参数：', '返回：', 'Args:', 'Returns:')):
                    desc_lines.append(line)
                elif line.startswith(('参数：', '返回：', 'Args:', 'Returns:')):
                    break
            description = '\n'.join(desc_lines)
            
        return summary, description
        
    def _get_tag_from_path(self, path: str) -> str:
        """从路径获取标签"""
        parts = path.split('/')
        if len(parts) >= 4 and parts[1] == 'api':
            return parts[3]  # /api/v1/game -> game
        return "default"
        
    def _get_responses_spec(self, view_func, doc: str) -> Dict[str, Any]:
        """获取响应规范"""
        responses = {
            "200": {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/SuccessResponse"
                        }
                    }
                }
            },
            "400": {
                "description": "Bad request",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/ErrorResponse"
                        }
                    }
                }
            },
            "500": {
                "description": "Internal server error",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/ErrorResponse"
                        }
                    }
                }
            }
        }
        
        return responses
        
    def _get_request_body_spec(self, view_func, doc: str) -> Dict[str, Any]:
        """获取请求体规范"""
        return {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        }
        
    def _get_parameters_spec(self, rule, doc: str) -> List[Dict[str, Any]]:
        """获取参数规范"""
        parameters = []
        
        # 路径参数
        for param in re.findall(r'<(?:.*?:)?(.+?)>', rule.rule):
            parameters.append({
                "name": param,
                "in": "path",
                "required": True,
                "schema": {
                    "type": "string"
                }
            })
            
        return parameters
        
    def _add_common_schemas(self):
        """添加通用模式"""
        self.spec["components"]["schemas"].update({
            "SuccessResponse": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": True
                    },
                    "data": {
                        "type": "object",
                        "description": "Response data"
                    },
                    "message": {
                        "type": "string",
                        "example": "Operation successful"
                    },
                    "timestamp": {
                        "type": "number",
                        "example": 1623456789.123
                    }
                }
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": False
                    },
                    "error": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "example": "VALIDATION_ERROR"
                            },
                            "message": {
                                "type": "string",
                                "example": "Invalid input data"
                            },
                            "details": {
                                "type": "object"
                            }
                        }
                    },
                    "timestamp": {
                        "type": "number",
                        "example": 1623456789.123
                    }
                }
            }
        })
        
    def _add_tags(self):
        """添加标签定义"""
        self.spec["tags"] = [
            {
                "name": "game",
                "description": "游戏核心功能"
            },
            {
                "name": "player",
                "description": "玩家信息管理"
            },
            {
                "name": "save",
                "description": "存档管理"
            },
            {
                "name": "system",
                "description": "系统信息"
            },
            {
                "name": "dev",
                "description": "开发调试工具"
            }
        ]


def setup_swagger_ui(app: Flask):
    """设置Swagger UI"""
    # Swagger UI配置
    SWAGGER_URL = '/api/docs'
    API_URL = '/api/openapi.json'
    
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "修仙世界引擎 API",
            'docExpansion': 'none',
            'defaultModelsExpandDepth': -1
        }
    )
    
    app.register_blueprint(swaggerui_blueprint)
    
    # 添加OpenAPI规范端点
    @app.route('/api/openapi.json')
    def openapi_spec():
        generator = OpenAPIGenerator()
        spec = generator.generate_from_app(app)
        return jsonify(spec)
        
    return app
