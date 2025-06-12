"""
API错误定义和处理
"""

from typing import Optional, Dict, Any, List


class APIError(Exception):
    """API错误基类"""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {"code": self.code, "message": self.message, "details": self.details}


class ErrorCodes:
    """错误代码常量"""

    # 通用错误 (1000-1999)
    INVALID_REQUEST = "INVALID_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"

    # 游戏错误 (2000-2999)
    INVALID_COMMAND = "INVALID_COMMAND"
    PLAYER_DEAD = "PLAYER_DEAD"
    NOT_ENOUGH_MANA = "NOT_ENOUGH_MANA"
    NOT_ENOUGH_HEALTH = "NOT_ENOUGH_HEALTH"
    INVALID_TARGET = "INVALID_TARGET"
    NOT_IN_COMBAT = "NOT_IN_COMBAT"
    ALREADY_IN_COMBAT = "ALREADY_IN_COMBAT"

    # 存档错误 (3000-3999)
    SAVE_NOT_FOUND = "SAVE_NOT_FOUND"
    SAVE_CORRUPTED = "SAVE_CORRUPTED"
    SAVE_LIMIT_EXCEEDED = "SAVE_LIMIT_EXCEEDED"
    SAVE_NAME_EXISTS = "SAVE_NAME_EXISTS"

    # 玩家错误 (4000-4999)
    PLAYER_NOT_FOUND = "PLAYER_NOT_FOUND"
    INVALID_PLAYER_DATA = "INVALID_PLAYER_DATA"
    SKILL_NOT_FOUND = "SKILL_NOT_FOUND"
    ITEM_NOT_FOUND = "ITEM_NOT_FOUND"


# 预定义的错误实例
class InvalidRequestError(APIError):
    """无效请求错误"""

    def __init__(self, message: str = "无效的请求", details: Optional[Dict] = None):
        super().__init__(
            code=ErrorCodes.INVALID_REQUEST,
            message=message,
            status_code=400,
            details=details,
        )


class NotFoundError(APIError):
    """资源未找到错误"""

    def __init__(self, resource: str, resource_id: Any = None):
        message = f"{resource}未找到"
        details = {"resource": resource}
        if resource_id:
            details["id"] = str(resource_id)

        super().__init__(
            code=ErrorCodes.NOT_FOUND, message=message, status_code=404, details=details
        )


class InvalidCommandError(APIError):
    """无效命令错误"""

    def __init__(self, command: str, suggestions: Optional[List[str]] = None):
        details: Dict[str, Any] = {"command": command}
        if suggestions:
            details["suggestions"] = suggestions

        super().__init__(
            code=ErrorCodes.INVALID_COMMAND,
            message=f"无效的命令: {command}",
            status_code=400,
            details=details,
        )


class PlayerDeadError(APIError):
    """玩家已死亡错误"""

    def __init__(self):
        super().__init__(
            code=ErrorCodes.PLAYER_DEAD,
            message="玩家已死亡，无法执行此操作",
            status_code=400,
        )


class InsufficientResourceError(APIError):
    """资源不足错误"""

    def __init__(self, resource: str, required: int, current: int):
        super().__init__(
            code=f"NOT_ENOUGH_{resource.upper()}",
            message=f"{resource}不足",
            status_code=400,
            details={"resource": resource, "required": required, "current": current},
        )


class SaveNotFoundError(APIError):
    """存档未找到错误"""

    def __init__(self, save_id: str):
        super().__init__(
            code=ErrorCodes.SAVE_NOT_FOUND,
            message="存档未找到",
            status_code=404,
            details={"save_id": save_id},
        )


class SaveLimitExceededError(APIError):
    """存档数量超限错误"""

    def __init__(self, limit: int):
        super().__init__(
            code=ErrorCodes.SAVE_LIMIT_EXCEEDED,
            message=f"存档数量已达上限({limit}个)",
            status_code=400,
            details={"limit": limit},
        )


class GameNotInitializedError(APIError):
    """游戏未初始化错误"""

    def __init__(self):
        super().__init__(
            code="GAME_NOT_INITIALIZED",
            message="游戏尚未初始化，请先开始游戏",
            status_code=400,
            details={"suggestions": ["开始游戏", "创建角色"]},
        )
