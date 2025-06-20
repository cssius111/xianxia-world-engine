from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PlayerData:
    id: str
    name: str
    level: int = 1
    experience: int = 0
    realm: str = "炼气期"
    health: int = 100
    max_health: int = 100
    mana: int = 50
    max_mana: int = 50
    attack: int = 10
    defense: int = 5
    speed: int = 10
    spiritual_root: str = "普通"
    talent: str = "平凡"
    fate: str = "普通"
    skills: List[str] = field(default_factory=list)
    inventory: Dict[str, int] = field(default_factory=dict)
    equipment: Dict[str, str] = field(default_factory=dict)
    total_battles: int = 0
    victories: int = 0
    defeats: int = 0

    @property
    def experience_to_next(self) -> int:
        """计算升级所需经验"""
        return self.level * 100 + 50


class IPlayerService(ABC):
    """玩家服务接口"""

    @abstractmethod
    def create_player(self, name: str, **kwargs: Any) -> str:
        """创建新玩家"""
        pass

    @abstractmethod
    def get_player(self, player_id: str) -> Optional[PlayerData]:
        """根据ID获取玩家"""
        pass

    @abstractmethod
    def get_current_player(self) -> Optional[PlayerData]:
        """获取当前玩家"""
        pass

    @abstractmethod
    def update_player(self, player_id: str, updates: Dict[str, Any]) -> bool:
        """更新玩家数据"""
        pass

    @abstractmethod
    def add_experience(self, amount: int) -> Dict[str, Any]:
        """添加经验值"""
        pass

    @abstractmethod
    def level_up(self) -> bool:
        """玩家升级"""
        pass

    @abstractmethod
    def heal(self, amount: int) -> int:
        """治疗玩家"""
        pass

    @abstractmethod
    def damage(self, amount: int) -> int:
        """对玩家造成伤害"""
        pass

    @abstractmethod
    def use_mana(self, amount: int) -> bool:
        """消耗灵力"""
        pass

    @abstractmethod
    def restore_mana(self, amount: int) -> int:
        """恢复灵力"""
        pass

    @abstractmethod
    def add_skill(self, skill_id: str) -> bool:
        """学习技能"""
        pass

    @abstractmethod
    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """添加物品"""
        pass

    @abstractmethod
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """移除物品"""
        pass

    @abstractmethod
    def equip_item(self, item_id: str, slot: str) -> bool:
        """装备物品"""
        pass

    @abstractmethod
    def get_current_player_data(self) -> Dict[str, Any]:
        """获取当前玩家数据（用于存档）"""
        pass

    @abstractmethod
    def load_player_data(self, data: Dict[str, Any]) -> bool:
        """加载玩家数据（从存档）"""
        pass
