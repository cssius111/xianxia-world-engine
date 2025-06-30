from abc import ABC, abstractmethod
from typing import Any

from src.xwe.services import IService


class IWorldService(IService, ABC):
    """世界服务接口"""

    @abstractmethod
    def get_current_location(self) -> Any:
        """获取当前地点信息"""
        raise NotImplementedError
