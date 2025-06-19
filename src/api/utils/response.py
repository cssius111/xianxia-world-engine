"""
API响应格式化工具
"""

from functools import wraps
from flask import jsonify, request, g
import time
from typing import Any, Dict, Optional, Callable
import traceback

from ..errors import APIError


def api_response(f: Callable) -> Callable:
    """
    统一API响应格式装饰器
    
    成功响应格式:
    {
        "success": true,
        "data": {...},
        "meta": {
            "timestamp": 1234567890,
            "version": "1.0.0",
            "request_id": "..."
        }
    }
    
    错误响应格式:
    {
        "success": false,
        "error": {
            "code": "ERROR_CODE",
            "message": "错误消息",
            "details": {...}
        },
        "meta": {...}
    }
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 记录请求开始时间
        start_time = time.time()
        
        try:
            # 执行原函数
            result = f(*args, **kwargs)
            
            # 如果返回的已经是Response对象，直接返回
            if hasattr(result, 'get_json'):
                return result
            
            # 构建成功响应
            response_data = {
                'success': True,
                'data': result,
                'meta': _build_meta(start_time)
            }
            
            return jsonify(response_data), 200
            
        except APIError as e:
            # 处理API错误
            response_data = {
                'success': False,
                'error': e.to_dict(),
                'meta': _build_meta(start_time)
            }
            
            return jsonify(response_data), e.status_code
            
        except Exception as e:
            # 处理未预期的错误
            print(f"未预期的错误: {str(e)}")
            print(traceback.format_exc())
            
            response_data = {
                'success': False,
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': '服务器内部错误',
                    'details': {
                        'error': str(e) if request.args.get('debug') else None
                    }
                },
                'meta': _build_meta(start_time)
            }
            
            return jsonify(response_data), 500
            
    return decorated_function


def paginated_response(f: Callable) -> Callable:
    """
    分页响应装饰器
    
    响应格式:
    {
        "success": true,
        "data": {
            "items": [...],
            "pagination": {
                "page": 1,
                "per_page": 20,
                "total": 100,
                "pages": 5
            }
        },
        "meta": {...}
    }
    """
    @wraps(f)
    @api_response
    def decorated_function(*args, **kwargs):
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 限制每页数量
        per_page = min(per_page, 100)
        
        # 调用原函数，传入分页参数
        items, total = f(*args, page=page, per_page=per_page, **kwargs)
        
        # 计算总页数
        pages = (total + per_page - 1) // per_page
        
        return {
            'items': items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': pages
            }
        }
        
    return decorated_function


def _build_meta(start_time: float) -> Dict[str, Any]:
    """构建响应元数据"""
    return {
        'timestamp': int(time.time()),
        'version': '1.0.0',
        'request_id': getattr(g, 'request_id', None),
        'duration': round((time.time() - start_time) * 1000, 2)  # 毫秒
    }


def success_response(data: Any = None, message: str = None) -> tuple:
    """
    快速创建成功响应
    
    Args:
        data: 响应数据
        message: 成功消息（可选）
        
    Returns:
        (response_dict, status_code)
    """
    response = {
        'success': True,
        'data': data,
        'meta': _build_meta(time.time())
    }
    
    if message:
        response['message'] = message
        
    return response, 200


def error_response(error: APIError) -> tuple:
    """
    快速创建错误响应
    
    Args:
        error: APIError实例
        
    Returns:
        (response_dict, status_code)
    """
    response = {
        'success': False,
        'error': error.to_dict(),
        'meta': _build_meta(time.time())
    }
    
    return response, error.status_code
