"""
统一异常处理器
"""

import logging
import traceback
from typing import Any, Callable, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class GameException(Exception):
    """游戏相关异常基类"""
    pass


class APIException(GameException):
    """API调用异常"""
    pass


class ConfigurationException(GameException):
    """配置异常"""
    pass


def handle_exceptions(
    default_return: Any = None,
    raise_on_error: bool = False,
    log_error: bool = True
):
    """异常处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(
                        f"函数 {func.__name__} 执行出错: {e}\n"
                        f"错误详情: {traceback.format_exc()}"
                    )
                
                if raise_on_error:
                    raise
                
                return default_return
        
        return wrapper
    return decorator


def safe_api_call(func: Callable, *args, **kwargs) -> tuple[bool, Any]:
    """安全的API调用"""
    try:
        result = func(*args, **kwargs)
        return True, result
    except Exception as e:
        logger.error(f"API调用失败: {e}")
        return False, None


def safe_file_operation(func: Callable, *args, **kwargs) -> tuple[bool, Any]:
    """安全的文件操作"""
    try:
        result = func(*args, **kwargs)
        return True, result
    except (IOError, OSError, UnicodeDecodeError) as e:
        logger.error(f"文件操作失败: {e}")
        return False, None


def handle_game_exception(exception: Exception, context: str = "") -> str:
    """处理游戏异常并返回用户友好的错误信息"""
    logger.error(f"游戏异常[{context}]: {exception}")
    
    if isinstance(exception, APIException):
        return "网络连接或API调用出现问题，请稍后重试。"
    elif isinstance(exception, ConfigurationException):
        return "游戏配置文件有问题，请检查设置。"
    elif isinstance(exception, FileNotFoundError):
        return "找不到必要的游戏文件，请检查安装是否完整。"
    elif isinstance(exception, MemoryError):
        return "内存不足，请关闭其他程序后重试。"
    else:
        return f"发生了未知错误: {str(exception)[:100]}..."
