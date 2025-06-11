"""
世界服务接口定义
负责游戏世界的管理，包括地图、位置、天气、时间和世界事件
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class LocationType(Enum):
    """位置类型"""
    CITY = "city"                    # 城市
    TOWN = "town"                    # 城镇
    VILLAGE = "village"              # 村庄
    WILDERNESS = "wilderness"        # 荒野
    DUNGEON = "dungeon"              # 地下城
    SECRET_REALM = "secret_realm"    # 秘境
    SECT = "sect"                    # 门派
    MOUNTAIN = "mountain"            # 山脉
    FOREST = "forest"                # 森林
    LAKE = "lake"                    # 湖泊
    DESERT = "desert"                # 沙漠


class Weather(Enum):
    """天气类型"""
    SUNNY = "sunny"          # 晴天
    CLOUDY = "cloudy"        # 多云
    RAINY = "rainy"          # 雨天
    STORMY = "stormy"        # 暴风雨
    SNOWY = "snowy"          # 雪天
    FOGGY = "foggy"          # 雾天
    WINDY = "windy"          # 大风
    

class TimeOfDay(Enum):
    """时段"""
    DAWN = "dawn"            # 黎明 (5:00-7:00)
    MORNING = "morning"      # 早晨 (7:00-11:00)
    NOON = "noon"            # 中午 (11:00-13:00)
    AFTERNOON = "afternoon"  # 下午 (13:00-17:00)
    DUSK = "dusk"            # 黄昏 (17:00-19:00)
    NIGHT = "night"          # 夜晚 (19:00-5:00)


@dataclass
class Location:
    """位置信息"""
    id: str
    name: str
    type: LocationType
    description: str
    
    # 坐标和区域
    coordinates: Tuple[int, int]  # (x, y)
    region: str  # 所属区域
    parent_location: Optional[str] = None  # 父位置ID
    
    # 连接和可达性
    connections: List[str] = field(default_factory=list)  # 连接的位置ID
    travel_time: Dict[str, float] = field(default_factory=dict)  # 到其他位置的旅行时间
    
    # 内容
    npcs: List[str] = field(default_factory=list)  # NPC ID列表
    shops: List[str] = field(default_factory=list)  # 商店ID列表
    quests: List[str] = field(default_factory=list)  # 任务ID列表
    resources: Dict[str, int] = field(default_factory=dict)  # 资源点
    
    # 属性
    danger_level: int = 1  # 危险等级 1-10
    spiritual_density: float = 1.0  # 灵气浓度倍率
    discovery_exp: int = 10  # 发现时获得的经验
    
    # 访问要求
    requirements: Dict[str, Any] = field(default_factory=dict)  # 进入要求
    is_discovered: bool = False  # 是否已发现
    is_accessible: bool = True  # 是否可访问
    
    # 特殊属性
    is_safe_zone: bool = False  # 是否安全区
    allow_pvp: bool = True  # 是否允许PVP
    respawn_point: bool = False  # 是否可作为重生点


@dataclass
class WorldEvent:
    """世界事件"""
    id: str
    name: str
    description: str
    event_type: str  # 'random', 'scheduled', 'triggered'
    
    # 发生条件
    locations: List[str] = field(default_factory=list)  # 可能发生的位置
    probability: float = 0.1  # 发生概率
    min_level: int = 1  # 最低等级要求
    
    # 时间相关
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: float = 0  # 持续时间（秒）
    
    # 效果
    effects: Dict[str, Any] = field(default_factory=dict)
    rewards: Dict[str, Any] = field(default_factory=dict)
    
    # 状态
    is_active: bool = False
    participants: List[str] = field(default_factory=list)  # 参与者ID


@dataclass
class ExplorationResult:
    """探索结果"""
    success: bool
    description: str
    discoveries: List[str] = field(default_factory=list)  # 发现的位置/物品/NPC
    encounters: List[Dict[str, Any]] = field(default_factory=list)  # 遭遇
    resources_found: Dict[str, int] = field(default_factory=dict)  # 找到的资源
    experience_gained: int = 0
    
    
class IWorldService(ABC):
    """
    世界服务接口
    
    主要职责：
    1. 地图和位置管理
    2. 移动和导航
    3. 探索系统
    4. 时间和天气系统
    5. 世界事件管理
    6. 资源点管理
    7. 区域控制
    """
    
    # ========== 位置管理 ==========
    
    @abstractmethod
    def get_location(self, location_id: str) -> Optional[Location]:
        """
        获取位置信息
        
        Args:
            location_id: 位置ID
            
        Returns:
            Location: 位置信息，不存在返回None
        """
        pass
        
    @abstractmethod
    def get_current_location(self) -> Location:
        """
        获取当前位置
        
        Returns:
            Location: 当前位置
        """
        pass
        
    @abstractmethod
    def list_locations(self, region: str = None, 
                      location_type: LocationType = None) -> List[Location]:
        """
        列出位置
        
        Args:
            region: 筛选区域
            location_type: 筛选类型
            
        Returns:
            List[Location]: 位置列表
        """
        pass
        
    @abstractmethod
    def discover_location(self, location_id: str) -> bool:
        """
        发现新位置
        
        Args:
            location_id: 位置ID
            
        Returns:
            bool: 是否成功发现
        """
        pass
        
    @abstractmethod
    def is_location_accessible(self, location_id: str) -> bool:
        """
        检查位置是否可访问
        
        Args:
            location_id: 位置ID
            
        Returns:
            bool: 是否可访问
        """
        pass
        
    # ========== 移动和导航 ==========
    
    @abstractmethod
    def move_to(self, location_id: str) -> Dict[str, Any]:
        """
        移动到指定位置
        
        Args:
            location_id: 目标位置ID
            
        Returns:
            Dict: 移动结果
                - success: 是否成功
                - travel_time: 旅行时间
                - events: 路上发生的事件
                - message: 结果消息
        """
        pass
        
    @abstractmethod
    def can_move_to(self, location_id: str) -> Tuple[bool, str]:
        """
        检查是否可以移动到指定位置
        
        Args:
            location_id: 目标位置ID
            
        Returns:
            Tuple[bool, str]: (是否可以移动, 原因说明)
        """
        pass
        
    @abstractmethod
    def get_connected_locations(self, location_id: str = None) -> List[Location]:
        """
        获取连接的位置
        
        Args:
            location_id: 位置ID，None表示当前位置
            
        Returns:
            List[Location]: 连接的位置列表
        """
        pass
        
    @abstractmethod
    def find_path(self, from_location: str, to_location: str) -> List[str]:
        """
        寻找路径
        
        Args:
            from_location: 起始位置ID
            to_location: 目标位置ID
            
        Returns:
            List[str]: 路径（位置ID列表），如果无法到达返回空列表
        """
        pass
        
    @abstractmethod
    def calculate_travel_time(self, from_location: str, to_location: str) -> float:
        """
        计算旅行时间
        
        Args:
            from_location: 起始位置ID
            to_location: 目标位置ID
            
        Returns:
            float: 旅行时间（秒）
        """
        pass
        
    # ========== 探索系统 ==========
    
    @abstractmethod
    def explore_current_location(self) -> ExplorationResult:
        """
        探索当前位置
        
        Returns:
            ExplorationResult: 探索结果
        """
        pass
        
    @abstractmethod
    def explore_location(self, location_id: str) -> ExplorationResult:
        """
        探索指定位置
        
        Args:
            location_id: 位置ID
            
        Returns:
            ExplorationResult: 探索结果
        """
        pass
        
    @abstractmethod
    def search_for_resources(self, resource_type: str = None) -> Dict[str, int]:
        """
        搜索资源
        
        Args:
            resource_type: 资源类型，None表示所有类型
            
        Returns:
            Dict[str, int]: 找到的资源及数量
        """
        pass
        
    @abstractmethod
    def gather_resource(self, resource_type: str, amount: int = 1) -> bool:
        """
        采集资源
        
        Args:
            resource_type: 资源类型
            amount: 采集数量
            
        Returns:
            bool: 是否成功采集
        """
        pass
        
    # ========== 时间系统 ==========
    
    @abstractmethod
    def get_world_time(self) -> Dict[str, Any]:
        """
        获取世界时间
        
        Returns:
            Dict: 时间信息
                - year: 年
                - month: 月
                - day: 日
                - hour: 时
                - minute: 分
                - time_of_day: 时段
                - total_seconds: 总秒数
        """
        pass
        
    @abstractmethod
    def advance_time(self, seconds: float) -> List[Dict[str, Any]]:
        """
        推进时间
        
        Args:
            seconds: 推进的秒数
            
        Returns:
            List[Dict]: 时间推进中发生的事件
        """
        pass
        
    @abstractmethod
    def get_time_of_day(self) -> TimeOfDay:
        """
        获取当前时段
        
        Returns:
            TimeOfDay: 当前时段
        """
        pass
        
    @abstractmethod
    def wait_until(self, target_time: TimeOfDay) -> float:
        """
        等待到指定时段
        
        Args:
            target_time: 目标时段
            
        Returns:
            float: 等待的时间（秒）
        """
        pass
        
    # ========== 天气系统 ==========
    
    @abstractmethod
    def get_weather(self, location_id: str = None) -> Weather:
        """
        获取天气
        
        Args:
            location_id: 位置ID，None表示当前位置
            
        Returns:
            Weather: 天气状况
        """
        pass
        
    @abstractmethod
    def forecast_weather(self, hours: int = 24) -> List[Tuple[float, Weather]]:
        """
        天气预报
        
        Args:
            hours: 预报时长（小时）
            
        Returns:
            List[Tuple[float, Weather]]: (时间, 天气) 列表
        """
        pass
        
    @abstractmethod
    def change_weather(self, weather: Weather, location_id: str = None) -> bool:
        """
        改变天气（GM功能）
        
        Args:
            weather: 新天气
            location_id: 位置ID，None表示当前位置
            
        Returns:
            bool: 是否成功改变
        """
        pass
        
    # ========== 世界事件 ==========
    
    @abstractmethod
    def get_active_events(self, location_id: str = None) -> List[WorldEvent]:
        """
        获取活跃的世界事件
        
        Args:
            location_id: 位置ID，None表示所有位置
            
        Returns:
            List[WorldEvent]: 活跃事件列表
        """
        pass
        
    @abstractmethod
    def trigger_event(self, event_id: str, location_id: str = None) -> bool:
        """
        触发世界事件
        
        Args:
            event_id: 事件ID
            location_id: 位置ID
            
        Returns:
            bool: 是否成功触发
        """
        pass
        
    @abstractmethod
    def participate_in_event(self, event_id: str) -> Dict[str, Any]:
        """
        参与世界事件
        
        Args:
            event_id: 事件ID
            
        Returns:
            Dict: 参与结果
        """
        pass
        
    @abstractmethod
    def schedule_event(self, event_id: str, start_time: float, 
                      location_id: str = None) -> bool:
        """
        预定世界事件
        
        Args:
            event_id: 事件ID
            start_time: 开始时间
            location_id: 位置ID
            
        Returns:
            bool: 是否成功预定
        """
        pass
        
    # ========== 区域控制 ==========
    
    @abstractmethod
    def get_region_info(self, region: str) -> Dict[str, Any]:
        """
        获取区域信息
        
        Args:
            region: 区域名称
            
        Returns:
            Dict: 区域信息
        """
        pass
        
    @abstractmethod
    def get_faction_territories(self, faction_id: str) -> List[str]:
        """
        获取门派领地
        
        Args:
            faction_id: 门派ID
            
        Returns:
            List[str]: 领地位置ID列表
        """
        pass
        
    @abstractmethod
    def claim_territory(self, location_id: str, faction_id: str) -> bool:
        """
        占领领地
        
        Args:
            location_id: 位置ID
            faction_id: 门派ID
            
        Returns:
            bool: 是否成功占领
        """
        pass
        
    # ========== 世界状态 ==========
    
    @abstractmethod
    def get_world_statistics(self) -> Dict[str, Any]:
        """
        获取世界统计信息
        
        Returns:
            Dict: 统计信息
                - total_locations: 总位置数
                - discovered_locations: 已发现位置数
                - active_events: 活跃事件数
                - total_resources: 资源总量
        """
        pass
        
    @abstractmethod
    def reset_world(self) -> bool:
        """
        重置世界（GM功能）
        
        Returns:
            bool: 是否成功重置
        """
        pass
        
    @abstractmethod
    def save_world_state(self) -> Dict[str, Any]:
        """
        保存世界状态
        
        Returns:
            Dict: 世界状态数据
        """
        pass
        
    @abstractmethod
    def load_world_state(self, state: Dict[str, Any]) -> bool:
        """
        加载世界状态
        
        Args:
            state: 世界状态数据
            
        Returns:
            bool: 是否成功加载
        """
        pass
