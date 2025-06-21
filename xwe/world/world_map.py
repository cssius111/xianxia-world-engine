# world/world_map.py
"""简易世界地图实现"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class AreaType(Enum):
    """区域类型枚举"""

    CITY = "city"
    MARKET = "market"
    WILDERNESS = "wilderness"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    CAVE = "cave"
    RUINS = "ruins"


@dataclass
class Region:
    """大区域"""

    id: str
    name: str
    description: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Region":
        return cls(
            id=str(data.get("id", "")),
            name=data.get("name", ""),
            description=data.get("description", ""),
        )


@dataclass
class Area:
    """地图区域"""

    id: str
    name: str
    type: AreaType
    description: str = ""
    connected_areas: List[str] = field(default_factory=list)
    level_requirement: int = 0
    danger_level: int = 0
    features: List[str] = field(default_factory=list)
    resources: Dict[str, int] = field(default_factory=dict)
    region_id: Optional[str] = None
    is_discovered: bool = False
    is_accessible: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> "Area":
        return cls(
            id=str(data.get("id", "")),
            name=data.get("name", ""),
            type=AreaType(data.get("type", "city")),
            description=data.get("description", ""),
            connected_areas=list(data.get("connections", [])),
            level_requirement=int(data.get("level_requirement", 0)),
            danger_level=int(data.get("danger_level", 0)),
            features=list(data.get("features", [])),
            resources=dict(data.get("resources", {})),
            region_id=data.get("region"),
        )


class WorldMap:
    """世界地图管理器"""

    def __init__(self) -> None:
        self.areas: Dict[str, Area] = {}
        self.regions: Dict[str, Region] = {}

    # 基本增删查
    def add_region(self, region: Region) -> None:
        self.regions[region.id] = region

    def add_area(self, area: Area) -> None:
        self.areas[area.id] = area

    def get_area(self, area_id: str) -> Optional[Area]:
        return self.areas.get(area_id)

    def get_connected_areas(self, area_id: str) -> List[Area]:
        area = self.get_area(area_id)
        if not area:
            return []
        return [self.areas[a] for a in area.connected_areas if a in self.areas]

    # 路径查找 - 简单广度优先
    def find_path(self, start_id: str, end_id: str) -> Optional[List[str]]:
        if start_id == end_id:
            return [start_id]
        if start_id not in self.areas or end_id not in self.areas:
            return None
        from collections import deque

        queue = deque([[start_id]])
        visited = {start_id}
        while queue:
            path = queue.popleft()
            current = path[-1]
            if current == end_id:
                return path
            for nxt in self.areas[current].connected_areas:
                if nxt not in visited and nxt in self.areas:
                    visited.add(nxt)
                    queue.append(path + [nxt])
        return None

    def can_move_to(self, current_area_id: str, target_area_id: str, player_level: int) -> tuple[bool, str]:
        current = self.get_area(current_area_id)
        target = self.get_area(target_area_id)
        if not current or not target:
            return False, "区域不存在"
        if target_area_id not in current.connected_areas:
            return False, "无法直接到达该区域"
        if not target.is_accessible:
            return False, "该区域暂时无法进入"
        if player_level < target.level_requirement:
            return False, "修为不足，无法进入该区域"
        return True, ""

    def discover_area(self, area_id: str) -> None:
        area = self.get_area(area_id)
        if area:
            area.is_discovered = True

    def get_regions_info(self) -> List[Dict[str, any]]:
        info: List[Dict[str, any]] = []
        for region in self.regions.values():
            areas = [a for a in self.areas.values() if a.region_id == region.id]
            discovered = sum(1 for a in areas if a.is_discovered)
            info.append(
                {
                    "id": region.id,
                    "name": region.name,
                    "discovered_areas": discovered,
                    "total_areas": len(areas),
                }
            )
        return info


# 一些默认地图数据供测试和示例使用
DEFAULT_MAP_DATA = {
    "regions": [
        {
            "id": "central_plains",
            "name": "中原",
            "description": "广阔的中原地区",
        }
    ],
    "areas": [
        {
            "id": "qingyun_city",
            "name": "青云城",
            "type": "city",
            "description": "修仙者聚集的繁华城池",
            "connections": ["wild_forest"],
            "region": "central_plains",
            "danger_level": 1,
        },
        {
            "id": "wild_forest",
            "name": "荒野森林",
            "type": "forest",
            "description": "充满妖兽的森林",
            "connections": ["qingyun_city"],
            "region": "central_plains",
            "danger_level": 2,
        },
    ],
}
