# API错误定义和处理
from flask import jsonify, current_app
from typing import Dict, Any, Optional
import time


class APIError(Exception):
    """API错误基类"""
    status_code = 400
    code = "UNKNOWN_ERROR"
    message = "未知错误"
    
    def __init__(self, message: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None,
                 status_code: Optional[int] = None):
        super().__init__()
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.details = details or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为响应字典"""
        return {
            'code': self.code,
            'message': self.message,
            'details': self.details
        }


class InvalidRequest(APIError):
    """无效请求"""
    status_code = 400
    code = "INVALID_REQUEST"
    message = "无效的请求"


class NotFound(APIError):
    """资源未找到"""
    status_code = 404
    code = "NOT_FOUND"
    message = "资源未找到"


class Unauthorized(APIError):
    """未授权"""
    status_code = 401
    code = "UNAUTHORIZED"
    message = "未授权访问"


class Forbidden(APIError):
    """禁止访问"""
    status_code = 403
    code = "FORBIDDEN"
    message = "禁止访问"


class InternalError(APIError):
    """内部错误"""
    status_code = 500
    code = "INTERNAL_ERROR"
    message = "服务器内部错误"


# 游戏相关错误
class InvalidCommand(APIError):
    """无效命令"""
    status_code = 400
    code = "INVALID_COMMAND"
    message = "无效的命令"
    
    def __init__(self, command: str, suggestions: Optional[list] = None):
        super().__init__(
            message=f"无效的命令: {command}",
            details={
                'command': command,
                'suggestions': suggestions or []
            }
        )


class PlayerDead(APIError):
    """玩家已死亡"""
    status_code = 400
    code = "PLAYER_DEAD"
    message = "玩家已死亡，无法执行操作"


class NotEnoughResource(APIError):
    """资源不足"""
    status_code = 400
    code = "NOT_ENOUGH_RESOURCE"
    message = "资源不足"
    
    def __init__(self, resource: str, required: int, current: int):
        super().__init__(
            message=f"{resource}不足",
            details={
                'resource': resource,
                'required': required,
                'current': current,
                'lacking': required - current
            }
        )


class InvalidTarget(APIError):
    """无效目标"""
    status_code = 400
    code = "INVALID_TARGET"
    message = "无效的目标"


# 存档相关错误
class SaveNotFound(APIError):
    """存档未找到"""
    status_code = 404
    code = "SAVE_NOT_FOUND"
    message = "存档未找到"


class SaveCorrupted(APIError):
    """存档损坏"""
    status_code = 400
    code = "SAVE_CORRUPTED"
    message = "存档文件已损坏"


class SaveLimitExceeded(APIError):
    """存档数量超限"""
    status_code = 400
    code = "SAVE_LIMIT_EXCEEDED"
    message = "存档数量已达上限"


def create_error_response(error: APIError) -> tuple:
    """创建错误响应"""
    response = {
        'success': False,
        'error': error.to_dict(),
        'meta': {
            'timestamp': int(time.time()),
            'version': current_app.config.get('API_VERSION', '1.0.0')
        }
    }
    return jsonify(response), error.status_code


def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """处理API错误"""
        return create_error_response(error)
    
    @app.errorhandler(404)
    def handle_404(error):
        """处理404错误"""
        api_error = NotFound("请求的资源不存在")
        return create_error_response(api_error)
    
    @app.errorhandler(500)
    def handle_500(error):
        """处理500错误"""
        api_error = InternalError("服务器内部错误，请稍后重试")
        # 记录错误日志
        current_app.logger.error(f"Internal error: {error}")
        return create_error_response(api_error)
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """处理未预期的异常"""
        # 记录错误日志
        current_app.logger.error(f"Unhandled exception: {error}", exc_info=True)
        
        # 在开发环境显示详细错误
        if current_app.debug:
            api_error = InternalError(
                message=str(error),
                details={'type': type(error).__name__}
            )
        else:
            api_error = InternalError()
            
        return create_error_response(api_error)
