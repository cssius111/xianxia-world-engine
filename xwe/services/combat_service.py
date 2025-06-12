"""
战斗服务
负责战斗系统的逻辑处理
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from . import ServiceBase, ServiceContainer
from .game_service import CommandResult


class ICombatService(ABC):
    """战斗服务接口"""
    
    @abstractmethod
    def start_combat(self, enemy_data: Dict[str, Any]) -> bool:
        """开始战斗"""
        pass
        
    @abstractmethod
    def execute_attack(self, target: Optional[str] = None) -> CommandResult:
        """执行攻击"""
        pass
        
    @abstractmethod
    def execute_defend(self) -> CommandResult:
        """执行防御"""
        pass
        
    @abstractmethod
    def attempt_flee(self) -> CommandResult:
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


class CombatService(ServiceBase[ICombatService], ICombatService):
    """战斗服务实现"""
    
    def __init__(self, container: ServiceContainer):
        super().__init__(container)
        self._in_combat = False
        self._current_enemy = None

        self._combat_log: List[str] = []

        
    def start_combat(self, enemy_data: Dict[str, Any]) -> bool:
        """开始战斗"""
        self._in_combat = True
        self._current_enemy = enemy_data
        self._combat_log.clear()
        
        self.logger.info(f"Combat started with {enemy_data.get('name', 'Unknown')}")
        return True
        
    def execute_attack(self, target: Optional[str] = None) -> CommandResult:
        """执行攻击"""
        if not self._in_combat:
            return CommandResult(
                success=False,
                output="当前不在战斗中"
            )
            
        # 简化的战斗逻辑
        enemy_name = self._current_enemy.get('name', '敌人')
        damage = 10  # 简化伤害计算
        
        output = f"你对{enemy_name}造成了{damage}点伤害！"
        self._combat_log.append(output)
        
        return CommandResult(
            success=True,
            output=output,
            state_changed=True
        )
        
    def execute_defend(self) -> CommandResult:
        """执行防御"""
        if not self._in_combat:
            return CommandResult(
                success=False,
                output="当前不在战斗中"
            )
            
        output = "你进入防御姿态，减少受到的伤害"
        self._combat_log.append(output)
        
        return CommandResult(
            success=True,
            output=output
        )
        
    def attempt_flee(self) -> CommandResult:
        """尝试逃跑"""
        if not self._in_combat:
            return CommandResult(
                success=False,
                output="当前不在战斗中"
            )
            
        # 简化的逃跑逻辑
        import random
        if random.random() > 0.5:
            self._in_combat = False
            return CommandResult(
                success=True,
                output="你成功逃离了战斗！",
                state_changed=True
            )
        else:
            return CommandResult(
                success=False,
                output="逃跑失败！"
            )
            
    def is_in_combat(self) -> bool:
        """是否在战斗中"""
        return self._in_combat
        
    def get_combat_state(self) -> Dict[str, Any]:
        """获取战斗状态"""
        return {
            'in_combat': self._in_combat,
            'enemy': self._current_enemy,
            'combat_log': self._combat_log[-10:]  # 最近10条日志
        }
