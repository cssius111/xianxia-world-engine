"""
世界构建模块
管理游戏世界的生成和维护
"""

from typing import Dict, List, Optional, Any
import random


class Region:
    """地域"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.locations: List[str] = []
        self.danger_level = 1
        self.resources: List[str] = []


class WorldBuilder:
    """世界构建器"""
    
    def __init__(self):
        self.world_data: Dict[str, Any] = {}
        self.regions: Dict[str, Region] = {}
        self._init_default_world()
    
    def _init_default_world(self):
        """初始化默认世界"""
        # 创建基础地域
        regions = [
            ("青云山脉", "云雾缭绕的山脉，适合修炼"),
            ("落日平原", "广阔的平原，资源丰富"),
            ("幽冥谷", "危险的山谷，妖兽众多"),
            ("东海之滨", "靠近大海，灵气充沛")
        ]
        
        for name, desc in regions:
            region = Region(name, desc)
            region.danger_level = random.randint(1, 5)
            self.regions[name] = region
    
    def generate_world(self):
        """生成世界"""
        self.world_data = {
            "regions": {name: {
                "description": r.description,
                "danger_level": r.danger_level,
                "locations": r.locations
            } for name, r in self.regions.items()},
            "time": "dawn",
            "weather": "clear"
        }
        return self.world_data
    
    def load_world(self, data: Dict[str, Any]):
        """加载世界数据"""
        self.world_data = data
    
    def save_world(self) -> Dict[str, Any]:
        """保存世界数据"""
        return self.world_data
    
    def get_region(self, region_name: str) -> Optional[Region]:
        """获取地域"""
        return self.regions.get(region_name)
    
    def add_location(self, region_name: str, location: str):
        """添加地点"""
        region = self.regions.get(region_name)
        if region:
            region.locations.append(location)


# 全局实例
world_builder = WorldBuilder()
