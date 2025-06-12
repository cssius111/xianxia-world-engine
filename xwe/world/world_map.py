# world/world_map.py
"""
世界地图系统

管理游戏世界的地理结构和区域关系。
"""

import logging
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class AreaType(Enum):
    """区域类型"""
    CITY = "city"              # 城市
    MARKET = "market"          # 坊市
    WILDERNESS = "wilderness"  # 荒野
    MOUNTAIN = "mountain"      # 山脉
    FOREST = "forest"         # 森林
    CAVE = "cave"             # 洞穴
    SECRET_REALM = "secret"   # 秘境
    SECT = "sect"             # 宗门
    VILLAGE = "village"       # 村庄
    RUINS = "ruins"           # 遗迹


@dataclass
class Area:
    """区域"""
    id: str
    name: str
    type: AreaType
    description: str
    parent_region: str
    danger_level: int = 1  # 1-10的危险等级
    min_level_requirement: int = 0  # 最低等级要求
    
    # 区域特性
    features: List[str] = field(default_factory=list)  # 特殊地点
    resources: Dict[str, str] = field(default_factory=dict)  # 资源类型和丰富度
    
    # 连接关系
    connected_areas: List[str] = field(default_factory=list)  # 相邻区域ID
    
    # 可用行动
    available_actions: List[str] = field(default_factory=list)
    
    # 区域状态
    is_discovered: bool = False
    is_accessible: bool = True
    
    # NPC和事件
    npcs: List[str] = field(default_factory=list)  # NPC ID列表
    events: List[str] = field(default_factory=list)  # 事件ID列表
    
    # 额外数据
    extra_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type.value,
            'description': self.description,
            'parent_region': self.parent_region,
            'danger_level': self.danger_level,
            'min_level_requirement': self.min_level_requirement,
            'features': self.features,
            'resources': self.resources,
            'connected_areas': self.connected_areas,
            'available_actions': self.available_actions,
            'is_discovered': self.is_discovered,
            'is_accessible': self.is_accessible,
            'npcs': self.npcs,
            'events': self.events,
            'extra_data': self.extra_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Area':
        """从字典创建"""
        area_type = AreaType(data.get('type', 'wilderness'))
        return cls(
            id=str(data['id']),
            name=data['name'],
            type=area_type,
            description=data.get('description', ''),
            parent_region=str(data.get('parent_region', '')),
            danger_level=data.get('danger_level', 1),
            min_level_requirement=data.get('min_level_requirement', 0),
            features=data.get('features', []),
            resources=data.get('resources', {}),
            connected_areas=[str(a) for a in data.get('connected_areas', [])],
            available_actions=data.get('available_actions', []),
            is_discovered=data.get('is_discovered', False),
            is_accessible=data.get('is_accessible', True),
            npcs=[str(n) for n in data.get('npcs', [])],
            events=[str(e) for e in data.get('events', [])],
            extra_data=data.get('extra_data', {})
        )


@dataclass
class Region:
    """大区域（包含多个Area）"""
    id: str
    name: str
    description: str
    controlling_force: str = ""  # 控制势力
    sub_areas: List[str] = field(default_factory=list)  # 包含的区域ID
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'controlling_force': self.controlling_force,
            'sub_areas': self.sub_areas
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Region':
        """从字典创建"""
        return cls(
            id=str(data['id']),
            name=data['name'],
            description=data.get('description', ''),
            controlling_force=data.get('controlling_force', ''),
            sub_areas=[str(a) for a in data.get('sub_areas', [])]
        )


class WorldMap:
    """
    世界地图
    
    管理所有区域和它们之间的关系。
    """
    
    def __init__(self) -> None:
        """初始化世界地图"""
        self.regions: Dict[str, Region] = {}
        self.areas: Dict[str, Area] = {}
        self.area_graph: Dict[str, Set[str]] = {}  # 邻接表表示的地图连接
        
        logger.info("世界地图系统初始化")
    
    def load_from_file(self, filepath: str) -> None:
        """从文件加载地图数据"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 加载大区域
            for region_data in data.get('regions', []):
                region = Region.from_dict(region_data)
                self.add_region(region)
            
            # 加载区域
            for area_data in data.get('areas', []):
                area = Area.from_dict(area_data)
                self.add_area(area)
            
            logger.info(f"加载地图数据: {len(self.regions)}个大区域, {len(self.areas)}个区域")
            
        except Exception as e:
            logger.error(f"加载地图数据失败: {e}")
    
    def add_region(self, region: Region) -> None:
        """添加大区域"""
        self.regions[region.id] = region
        logger.debug(f"添加大区域: {region.name}")
    
    def add_area(self, area: Area) -> None:
        """添加区域"""
        self.areas[area.id] = area
        
        # 更新邻接表
        if area.id not in self.area_graph:
            self.area_graph[area.id] = set()
        
        for connected_id in area.connected_areas:
            self.area_graph[area.id].add(connected_id)
            # 确保双向连接
            if connected_id not in self.area_graph:
                self.area_graph[connected_id] = set()
            self.area_graph[connected_id].add(area.id)
        
        # 将区域添加到所属大区域
        if area.parent_region and area.parent_region in self.regions:
            region = self.regions[area.parent_region]
            if area.id not in region.sub_areas:
                region.sub_areas.append(area.id)
        
        logger.debug(f"添加区域: {area.name}")
    
    def get_area(self, area_id: str) -> Optional[Area]:
        """获取区域"""
        return self.areas.get(area_id)
    
    def get_region(self, region_id: str) -> Optional[Region]:
        """获取大区域"""
        return self.regions.get(region_id)
    
    def get_connected_areas(self, area_id: str) -> List[Area]:
        """获取相邻区域"""
        connected_ids = self.area_graph.get(area_id, set())
        return [self.areas[aid] for aid in connected_ids if aid in self.areas]
    
    def can_move_to(self, from_area_id: str, to_area_id: str, player_level: int = 0) -> Tuple[bool, str]:
        """
        检查是否可以移动到目标区域
        
        Returns:
            (是否可以移动, 原因说明)
        """
        # 检查起始区域
        from_area = self.get_area(from_area_id)
        if not from_area:
            return False, "当前区域不存在"
        
        # 检查目标区域
        to_area = self.get_area(to_area_id)
        if not to_area:
            return False, "目标区域不存在"
        
        # 检查是否相邻
        if to_area_id not in self.area_graph.get(from_area_id, set()):
            return False, f"{to_area.name}不在附近，无法直接前往"
        
        # 检查是否可进入
        if not to_area.is_accessible:
            return False, f"{to_area.name}目前无法进入"
        
        # 检查等级要求
        if player_level < to_area.min_level_requirement:
            return False, f"需要达到{to_area.min_level_requirement}级才能进入{to_area.name}"
        
        # 检查是否已发现
        if not to_area.is_discovered:
            # 可以进入未发现的区域，但会有提示
            pass
        
        return True, ""
    
    def discover_area(self, area_id: str) -> None:
        """发现区域"""
        area = self.get_area(area_id)
        if area and not area.is_discovered:
            area.is_discovered = True
            logger.info(f"发现新区域: {area.name}")
            
            # 自动发现相邻区域的存在（但不是详细信息）
            for connected_id in area.connected_areas:
                connected = self.get_area(connected_id)
                if connected and not connected.is_discovered:
                    # 标记为"知道存在但未探索"
                    connected.extra_data['known_to_exist'] = True
    
    def get_area_info(self, area_id: str, detailed: bool = True) -> Dict[str, Any]:
        """
        获取区域信息
        
        Args:
            area_id: 区域ID
            detailed: 是否返回详细信息
        """
        area = self.get_area(area_id)
        if not area:
            return {}
        
        info: Dict[str, Any] = {
            'id': str(area.id),
            'name': area.name,
            'type': area.type.value,
            'description': area.description if area.is_discovered else "未知区域",
            'danger_level': area.danger_level,
            'is_discovered': area.is_discovered,
            'is_accessible': area.is_accessible
        }
        
        if detailed and area.is_discovered:
            # 已发现的区域显示详细信息
            info.update({
                'features': area.features,
                'resources': area.resources,
                'available_actions': area.available_actions,
                'connected_areas': [
                    {
                        'id': str(cid),
                        'name': self.areas[cid].name if cid in self.areas else "未知",
                        'discovered': self.areas[cid].is_discovered if cid in self.areas else False
                    }
                    for cid in area.connected_areas
                ]
            })
        
        return info
    
    def get_regions_info(self) -> List[Dict[str, Any]]:
        """获取所有大区域信息"""
        return [
            {
                'id': str(region.id),
                'name': region.name,
                'description': region.description,
                'controlling_force': region.controlling_force,
                'discovered_areas': sum(
                    1 for aid in region.sub_areas
                    if aid in self.areas and self.areas[aid].is_discovered
                ),
                'total_areas': len(region.sub_areas)
            }
            for region in self.regions.values()
        ]
    
    def find_path(self, from_area_id: str, to_area_id: str) -> Optional[List[str]]:
        """
        寻找两个区域之间的路径（BFS）
        
        Returns:
            路径列表（包含起点和终点），如果无法到达则返回None
        """
        if from_area_id not in self.areas or to_area_id not in self.areas:
            return None
        
        if from_area_id == to_area_id:
            return [from_area_id]
        
        # BFS寻路
        from collections import deque
        
        queue = deque([(from_area_id, [from_area_id])])
        visited = {from_area_id}
        
        while queue:
            current, path = queue.popleft()
            
            for neighbor in self.area_graph.get(current, set()):
                if neighbor == to_area_id:
                    return path + [neighbor]
                
                if neighbor not in visited and neighbor in self.areas:
                    area = self.areas[neighbor]
                    if area.is_accessible:  # 只通过可访问的区域
                        visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def get_distance(self, from_area_id: str, to_area_id: str) -> int:
        """获取两个区域之间的距离（最短路径长度）"""
        path = self.find_path(from_area_id, to_area_id)
        return len(path) - 1 if path else -1


# 预定义的测试地图数据
DEFAULT_MAP_DATA = {
    "regions": [
        {
            "id": "tiannan",
            "name": "天南州",
            "description": "修仙界南部重镇，灵气充沛，宗门林立",
            "controlling_force": "天南修仙联盟",
            "sub_areas": ["qingyun_city", "tiannan_market", "yellow_maple_valley", "sunset_mountains"]
        },
        {
            "id": "northern_wasteland",
            "name": "北域荒原",
            "description": "荒凉的北方大地，妖兽横行，但也蕴含着古老的机缘",
            "controlling_force": "",
            "sub_areas": ["wasteland_entrance", "demon_beast_valley", "ancient_ruins"]
        }
    ],
    "areas": [
        {
            "id": "qingyun_city",
            "name": "青云城",
            "type": "city",
            "description": "天南州最大的修仙者聚集地，繁华热闹，各种机缘汇聚",
            "parent_region": "tiannan",
            "danger_level": 1,
            "min_level_requirement": 0,
            "features": ["传送阵", "修仙者公会", "灵石银行", "万宝楼"],
            "resources": {"灵石": "丰富", "灵草": "普通", "炼器材料": "丰富"},
            "connected_areas": ["tiannan_market", "yellow_maple_valley", "wasteland_entrance"],
            "available_actions": ["explore", "rest", "trade", "teleport"],
            "is_discovered": True,
            "is_accessible": True
        },
        {
            "id": "tiannan_market",
            "name": "天南坊市",
            "type": "market",
            "description": "天南州最大的交易市场，各种珍稀物品应有尽有",
            "parent_region": "tiannan",
            "danger_level": 1,
            "min_level_requirement": 0,
            "features": ["拍卖行", "各类商铺", "黑市入口"],
            "resources": {"灵石": "极丰富", "各类物资": "极丰富"},
            "connected_areas": ["qingyun_city", "sunset_mountains"],
            "available_actions": ["trade", "auction", "gather_info"],
            "is_discovered": True,
            "is_accessible": True
        },
        {
            "id": "yellow_maple_valley",
            "name": "黄枫谷",
            "type": "forest",
            "description": "一片古老的枫树林，秋季时漫山遍野的金黄枫叶美不胜收",
            "parent_region": "tiannan",
            "danger_level": 2,
            "min_level_requirement": 0,
            "features": ["灵泉", "采药点", "隐藏洞穴"],
            "resources": {"灵草": "丰富", "灵木": "丰富"},
            "connected_areas": ["qingyun_city", "sunset_mountains"],
            "available_actions": ["explore", "gather", "hunt"],
            "is_discovered": False,
            "is_accessible": True
        },
        {
            "id": "sunset_mountains",
            "name": "落日山脉",
            "type": "mountain",
            "description": "连绵起伏的山脉，传说山中有上古遗迹",
            "parent_region": "tiannan",
            "danger_level": 4,
            "min_level_requirement": 5,
            "features": ["矿脉", "山洞群", "悬崖绝壁"],
            "resources": {"矿石": "丰富", "灵晶": "稀少"},
            "connected_areas": ["yellow_maple_valley", "tiannan_market"],
            "available_actions": ["explore", "mine", "climb"],
            "is_discovered": False,
            "is_accessible": True
        },
        {
            "id": "wasteland_entrance",
            "name": "荒原入口",
            "type": "wilderness",
            "description": "通往北域荒原的必经之地，寒风凛冽",
            "parent_region": "northern_wasteland",
            "danger_level": 3,
            "min_level_requirement": 3,
            "features": ["边境哨站", "补给点"],
            "resources": {"妖兽材料": "普通"},
            "connected_areas": ["qingyun_city", "demon_beast_valley"],
            "available_actions": ["explore", "hunt", "rest"],
            "is_discovered": False,
            "is_accessible": True
        },
        {
            "id": "demon_beast_valley",
            "name": "妖兽谷",
            "type": "wilderness",
            "description": "妖兽聚集之地，危险重重但妖丹、材料丰富",
            "parent_region": "northern_wasteland",
            "danger_level": 6,
            "min_level_requirement": 8,
            "features": ["妖兽巢穴", "血池", "兽王领地"],
            "resources": {"妖丹": "丰富", "妖兽材料": "极丰富"},
            "connected_areas": ["wasteland_entrance", "ancient_ruins"],
            "available_actions": ["hunt", "explore", "flee"],
            "is_discovered": False,
            "is_accessible": True
        },
        {
            "id": "ancient_ruins",
            "name": "上古遗迹",
            "type": "ruins",
            "description": "神秘的上古遗迹，蕴含着惊人的机缘和致命的危险",
            "parent_region": "northern_wasteland", 
            "danger_level": 8,
            "min_level_requirement": 15,
            "features": ["封印大殿", "藏经阁遗址", "试炼之地"],
            "resources": {"古籍": "稀有", "法宝": "稀有", "传承": "极稀有"},
            "connected_areas": ["demon_beast_valley"],
            "available_actions": ["explore", "search", "challenge"],
            "is_discovered": False,
            "is_accessible": False,
            "extra_data": {"unlock_condition": "需要特殊令牌"}
        }
    ]
}
