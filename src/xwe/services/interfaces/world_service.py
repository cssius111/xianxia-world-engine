from abc import ABC, abstractmethod
from typing import Any, Dict

class IWorldService(ABC):
    """世界服务接口"""

    @abstractmethod
    def initialize_world(self) -> bool:
        """初始化世界"""
        pass

    @abstractmethod
    def get_location_info(self, location_id: str) -> Dict[str, Any]:
        """获取位置信息"""
        pass

    @abstractmethod
    def get_map_info(self, location_id: str) -> Dict[str, Any]:
        """获取地图信息"""
        pass

    @abstractmethod
    def explore_location(self, location_id: str) -> Dict[str, Any]:
        """探索位置"""
        pass

    @abstractmethod
    def move_to_location(self, from_location: str, to_location: str) -> bool:
        """移动到新位置"""
        pass

    @abstractmethod
    def get_world_data(self) -> Dict[str, Any]:
        """获取世界数据（用于存档）"""
        pass

    @abstractmethod
    def load_world_data(self, data: Dict[str, Any]) -> bool:
        """加载世界数据（从存档）"""
        pass
