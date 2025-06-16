# world/__init__.py
"""
世界系统模块

管理游戏世界的地图、区域、事件等。
"""

from .world_map import WorldMap, Area, Region, AreaType
from .location_manager import LocationManager
from .event_system import EventSystem, WorldEvent

__all__ = [
    'WorldMap', 'Area', 'Region', 'AreaType',
    'LocationManager',
    'EventSystem', 'WorldEvent'
]
