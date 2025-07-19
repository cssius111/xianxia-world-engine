# world/__init__.py
"""
世界系统模块

管理游戏世界的地图、区域、事件等。
"""

from .event_system import EventSystem, WorldEvent
from .location_manager import LocationManager
from .time_system import TimeSystem
from .world_map import Area, AreaType, Region, WorldMap
from .laws import WorldLaw, load_world_laws

__all__ = [
    "WorldMap",
    "Area",
    "Region",
    "AreaType",
    "LocationManager",
    "EventSystem",
    "WorldEvent",
    "TimeSystem",
    "WorldLaw",
    "load_world_laws",
]
