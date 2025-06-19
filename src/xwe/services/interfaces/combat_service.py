from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class ICombatService(ABC):
    """战斗服务接口"""

    @abstractmethod
    def start_combat(self, enemy_data: Dict[str, Any]) -> bool:
        """开始战斗"""
        pass

    @abstractmethod
    def execute_attack(self, target: Optional[str] = None) -> Dict[str, Any]:
        """执行攻击"""
        pass

    @abstractmethod
    def execute_defend(self) -> Dict[str, Any]:
        """执行防御"""
        pass

    @abstractmethod
    def attempt_flee(self) -> Dict[str, Any]:
        """尝试逃跑"""
        pass

    @abstractmethod
    def is_in_combat(self) -> bool:
        """是否在战斗中"""
        pass

    @abstractmethod
    def get_combat_state(self) -> Dict[str, Any]:
        """获取战斗状态"""
        pass
