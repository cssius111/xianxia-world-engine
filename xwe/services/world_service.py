"""
世界服务
负责游戏世界的管理，包括地图、位置、探索等
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Set
import random

from . import ServiceBase, ServiceContainer


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


class WorldService(ServiceBase[IWorldService], IWorldService):
    """世界服务实现"""
    
    def __init__(self, container: ServiceContainer):
        super().__init__(container)
        self._locations: Dict[str, Dict[str, Any]] = {}
        self._connections: Dict[str, List[str]] = {}
        self._discovered_locations: Set[str] = set()
 
        
    def _do_initialize(self) -> None:
        """初始化服务"""
        self.initialize_world()
        
    def initialize_world(self) -> bool:
        """初始化世界"""
        # 创建基础位置
        self._locations = {
            '天南镇': {
                'id': '天南镇',
                'name': '天南镇',
                'description': '一个繁华的修仙小镇，各种修士来来往往',
                'type': 'town',
                'npcs': ['王老板', '李铁匠', '云梦儿'],
                'shops': ['杂货铺', '铁匠铺'],
                'level_range': (1, 10)
            },
            '青云山': {
                'id': '青云山',
                'name': '青云山',
                'description': '云雾缭绕的山峰，据说山上有修仙门派',
                'type': 'mountain',
                'enemies': ['野狼', '山贼'],
                'resources': ['灵草', '矿石'],
                'level_range': (5, 15)
            },
            '幽暗森林': {
                'id': '幽暗森林',
                'name': '幽暗森林',
                'description': '阴森恐怖的森林，充满了未知的危险',
                'type': 'forest',
                'enemies': ['妖兽', '毒蛇'],
                'resources': ['灵木', '妖丹'],
                'level_range': (10, 20)
            },
            '荒漠戈壁': {
                'id': '荒漠戈壁',
                'name': '荒漠戈壁',
                'description': '一望无际的沙漠，传说中有古老的遗迹',
                'type': 'desert',
                'enemies': ['沙虫', '沙盗'],
                'resources': ['沙晶', '古物'],
                'level_range': (15, 25)
            }
        }
        
        # 创建位置连接
        self._connections = {
            '天南镇': ['青云山', '幽暗森林', '荒漠戈壁'],
            '青云山': ['天南镇', '幽暗森林'],
            '幽暗森林': ['天南镇', '青云山', '荒漠戈壁'],
            '荒漠戈壁': ['天南镇', '幽暗森林']
        }
        
        # 初始发现天南镇
        self._discovered_locations.add('天南镇')
        
        self.logger.info("World initialized with %d locations", len(self._locations))
        return True
        
    def get_location_info(self, location_id: str) -> Dict[str, Any]:
        """获取位置信息"""
        return self._locations.get(location_id, {})
        
    def get_map_info(self, location_id: str) -> Dict[str, Any]:
        """获取地图信息"""
        location = self._locations.get(location_id)
        if not location:
            return {
                'error': '未知位置',
                'description': '你不知道这个地方'
            }
            
        connections = self._connections.get(location_id, [])
        discovered_connections = [
            loc for loc in connections 
            if loc in self._discovered_locations
        ]
        
        return {
            'location': location,
            'description': location['description'],
            'connections': discovered_connections,
            'discovered_count': len(self._discovered_locations),
            'total_locations': len(self._locations)
        }
        
    def explore_location(self, location_id: str) -> Dict[str, Any]:
        """探索位置"""
        location = self._locations.get(location_id)
        if not location:
            return {
                'success': False,
                'description': '未知位置'
            }
            
        # 随机事件
        event_roll = random.random()
        
        if event_roll < 0.3 and location.get('enemies'):
            # 遭遇敌人
            enemy_name = random.choice(location['enemies'])
            return {
                'success': True,
                'description': f'你在{location["name"]}探索时遭遇了{enemy_name}！',
                'encounter': {
                    'type': 'combat',
                    'enemy': {
                        'name': enemy_name,
                        'level': random.randint(*location['level_range']),
                        'health': 100,
                        'attack': 10
                    }
                }
            }
            
        elif event_roll < 0.5 and location.get('resources'):
            # 发现资源
            resource = random.choice(location['resources'])
            quantity = random.randint(1, 3)
            return {
                'success': True,
                'description': f'你在{location["name"]}发现了{quantity}个{resource}！',
                'encounter': {
                    'type': 'resource',
                    'item': resource,
                    'quantity': quantity
                }
            }
            
        elif event_roll < 0.6:
            # 发现新位置
            connections = self._connections.get(location_id, [])
            undiscovered = [
                loc for loc in connections 
                if loc not in self._discovered_locations
            ]
            
            if undiscovered:
                new_location = random.choice(undiscovered)
                self._discovered_locations.add(new_location)
                return {
                    'success': True,
                    'description': f'你发现了通往{new_location}的道路！',
                    'encounter': {
                        'type': 'discovery',
                        'location': new_location
                    }
                }
                
        # 普通探索
        descriptions = [
            f'你在{location["name"]}四处查看，但没有发现什么特别的',
            f'{location["name"]}今天很平静',
            f'你仔细探索了{location["name"]}的每个角落',
            f'微风吹过{location["name"]}，一切都很安宁'
        ]
        
        return {
            'success': True,
            'description': random.choice(descriptions),
            'encounter': None
        }
        
    def move_to_location(self, from_location: str, to_location: str) -> bool:
        """移动到新位置"""
        # 检查连接
        connections = self._connections.get(from_location, [])
        if to_location not in connections:
            return False
            
        # 自动发现新位置
        if to_location not in self._discovered_locations:
            self._discovered_locations.add(to_location)
            
        return True
        
    def get_world_data(self) -> Dict[str, Any]:
        """获取世界数据（用于存档）"""
        return {
            'discovered_locations': list(self._discovered_locations),
            'custom_data': {}  # 预留给未来的自定义数据
        }
        
    def load_world_data(self, data: Dict[str, Any]) -> bool:
        """加载世界数据（从存档）"""
        if 'discovered_locations' in data:
            self._discovered_locations = set(data['discovered_locations'])
            
        self.logger.info("World data loaded, %d locations discovered", 
                        len(self._discovered_locations))
        
        return True
