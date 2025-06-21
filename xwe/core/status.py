"""
状态效果系统
管理角色的各种状态效果（增益、减益等）
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import time
import logging

logger = logging.getLogger(__name__)


class StatusType(Enum):
    """状态类型"""
    BUFF = "buff"      # 增益
    DEBUFF = "debuff"  # 减益
    NEUTRAL = "neutral" # 中性


@dataclass
class StatusEffect:
    """状态效果"""
    id: str
    name: str
    description: str
    status_type: StatusType
    duration: float  # 持续时间（秒），-1表示永久
    stack_count: int = 1
    max_stacks: int = 1
    modifiers: Dict[str, float] = field(default_factory=dict)  # 属性修改
    start_time: float = field(default_factory=time.time)
    
    def is_expired(self) -> bool:
        """检查是否已过期"""
        if self.duration < 0:  # 永久效果
            return False
        return time.time() - self.start_time >= self.duration
        
    def get_remaining_time(self) -> float:
        """获取剩余时间"""
        if self.duration < 0:
            return -1
        remaining = self.duration - (time.time() - self.start_time)
        return max(0, remaining)


class StatusEffectManager:
    """
    状态效果管理器
    
    管理角色的所有状态效果
    """
    
    def __init__(self):
        self.effects: Dict[str, StatusEffect] = {}
        
    def add_effect(self, effect: StatusEffect) -> None:
        """
        添加状态效果
        
        Args:
            effect: 状态效果
        """
        if effect.id in self.effects:
            # 如果已存在，尝试叠加
            existing = self.effects[effect.id]
            if existing.stack_count < existing.max_stacks:
                existing.stack_count += 1
                existing.start_time = time.time()  # 刷新时间
                logger.info(f"状态效果 {effect.name} 叠加至 {existing.stack_count} 层")
            else:
                # 达到最大层数，刷新持续时间
                existing.start_time = time.time()
                logger.info(f"状态效果 {effect.name} 已达最大层数，刷新持续时间")
        else:
            # 添加新效果
            self.effects[effect.id] = effect
            logger.info(f"添加状态效果: {effect.name}")
            
    def remove_effect(self, effect_id: str) -> bool:
        """
        移除状态效果
        
        Args:
            effect_id: 效果ID
            
        Returns:
            是否成功移除
        """
        if effect_id in self.effects:
            effect = self.effects[effect_id]
            del self.effects[effect_id]
            logger.info(f"移除状态效果: {effect.name}")
            return True
        return False
        
    def has_effect(self, effect_id: str) -> bool:
        """检查是否有某个效果"""
        return effect_id in self.effects and not self.effects[effect_id].is_expired()
        
    def get_effect(self, effect_id: str) -> Optional[StatusEffect]:
        """获取状态效果"""
        effect = self.effects.get(effect_id)
        if effect and not effect.is_expired():
            return effect
        return None
        
    def update(self) -> List[str]:
        """
        更新所有状态效果
        
        Returns:
            过期的效果ID列表
        """
        expired = []
        for effect_id, effect in list(self.effects.items()):
            if effect.is_expired():
                expired.append(effect_id)
                del self.effects[effect_id]
                logger.info(f"状态效果 {effect.name} 已过期")
                
        return expired
        
    def get_total_modifiers(self) -> Dict[str, float]:
        """
        获取所有效果的总属性修改
        
        Returns:
            属性名 -> 修改值
        """
        total_modifiers = {}
        
        for effect in self.effects.values():
            if effect.is_expired():
                continue
                
            for attr, value in effect.modifiers.items():
                if attr not in total_modifiers:
                    total_modifiers[attr] = 0
                # 考虑叠加层数
                total_modifiers[attr] += value * effect.stack_count
                
        return total_modifiers
        
    def get_status_summary(self) -> List[str]:
        """
        获取状态摘要
        
        Returns:
            状态描述列表
        """
        summary = []
        
        for effect in self.effects.values():
            if effect.is_expired():
                continue
                
            remaining = effect.get_remaining_time()
            if remaining < 0:
                time_str = "永久"
            else:
                time_str = f"{int(remaining)}秒"
                
            if effect.stack_count > 1:
                summary.append(f"{effect.name} x{effect.stack_count} ({time_str})")
            else:
                summary.append(f"{effect.name} ({time_str})")
                
        return summary
        
    def clear_all(self) -> None:
        """清除所有状态效果"""
        self.effects.clear()
        logger.info("清除所有状态效果")
        
    def clear_debuffs(self) -> None:
        """清除所有减益效果"""
        to_remove = []
        for effect_id, effect in self.effects.items():
            if effect.status_type == StatusType.DEBUFF:
                to_remove.append(effect_id)
                
        for effect_id in to_remove:
            self.remove_effect(effect_id)
            
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            effect_id: {
                "id": effect.id,
                "name": effect.name,
                "description": effect.description,
                "status_type": effect.status_type.value,
                "duration": effect.duration,
                "stack_count": effect.stack_count,
                "max_stacks": effect.max_stacks,
                "modifiers": effect.modifiers,
                "start_time": effect.start_time
            }
            for effect_id, effect in self.effects.items()
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StatusEffectManager":
        """从字典创建"""
        manager = cls()
        
        for effect_id, effect_data in data.items():
            effect = StatusEffect(
                id=effect_data["id"],
                name=effect_data["name"],
                description=effect_data["description"],
                status_type=StatusType(effect_data["status_type"]),
                duration=effect_data["duration"],
                stack_count=effect_data.get("stack_count", 1),
                max_stacks=effect_data.get("max_stacks", 1),
                modifiers=effect_data.get("modifiers", {}),
                start_time=effect_data.get("start_time", time.time())
            )
            manager.effects[effect_id] = effect
            
        return manager
