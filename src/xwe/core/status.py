# core/status.py
"""
状态效果系统模块

管理游戏中的各种状态效果（Buff/Debuff）。
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)


class StatusEffectType(Enum):
    """状态效果类型"""
    BUFF = "buff"              # 增益
    DEBUFF = "debuff"          # 减益
    DOT = "dot"                # 持续伤害
    HOT = "hot"                # 持续治疗
    CONTROL = "control"        # 控制
    SPECIAL = "special"        # 特殊


class StatusEffectStackType(Enum):
    """状态效果叠加类型"""
    NO_STACK = "no_stack"              # 不可叠加
    REFRESH_DURATION = "refresh"       # 刷新持续时间
    STACK_INTENSITY = "intensity"      # 叠加强度
    STACK_INDEPENDENT = "independent"  # 独立叠加


@dataclass
class StatusEffect:
    """
    状态效果类
    
    表示一个作用在角色身上的状态效果。
    """
    
    # 基础信息
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "未命名效果"
    description: str = ""
    effect_type: StatusEffectType = StatusEffectType.BUFF
    
    # 持续时间
    duration: int = 1              # 持续回合数，-1表示永久
    remaining_duration: int = 1    # 剩余回合数
    
    # 效果参数
    modifier_type: str = ""        # 修改的属性类型
    modifier_value: float = 0      # 修改值
    modifier_formula: str = ""     # 计算公式
    
    # 叠加规则
    stack_type: StatusEffectStackType = StatusEffectStackType.NO_STACK
    max_stack: int = 1             # 最大叠加层数
    current_stack: int = 1         # 当前叠加层数
    
    # 触发条件
    trigger_on: str = ""           # 触发时机
    trigger_chance: float = 1.0    # 触发概率
    
    # 来源信息
    source_id: str = ""            # 施加者ID
    source_skill: str = ""         # 来源技能
    
    # 其他数据
    tags: List[str] = field(default_factory=list)
    extra_data: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """是否已过期"""
        return self.duration != -1 and self.remaining_duration <= 0
    
    def tick(self) -> None:
        """经过一回合"""
        if self.duration != -1 and self.remaining_duration > 0:
            self.remaining_duration -= 1
    
    def refresh(self) -> None:
        """刷新持续时间"""
        self.remaining_duration = self.duration
    
    def stack(self, amount: int = 1) -> None:
        """
        叠加层数
        
        Args:
            amount: 叠加数量
        """
        if self.stack_type == StatusEffectStackType.NO_STACK:
            return
        
        self.current_stack = min(self.current_stack + amount, self.max_stack)
    
    def get_actual_value(self) -> float:
        """获取实际效果值（考虑叠加）"""
        if self.stack_type == StatusEffectStackType.STACK_INTENSITY:
            return self.modifier_value * self.current_stack
        return self.modifier_value
    
    def can_dispel(self) -> bool:
        """是否可以被驱散"""
        return "undispellable" not in self.tags
    
    def is_control_effect(self) -> bool:
        """是否是控制效果"""
        return self.effect_type == StatusEffectType.CONTROL or "control" in self.tags


class StatusEffectManager:
    """
    状态效果管理器
    
    管理角色身上的所有状态效果。
    """
    
    def __init__(self) -> None:
        """初始化状态效果管理器"""
        self.effects: List[StatusEffect] = []
        self.effect_callbacks: Dict[str, List[Callable]] = {}
    
    def add_effect(self, effect: StatusEffect) -> bool:
        """
        添加状态效果
        
        Args:
            effect: 状态效果
            
        Returns:
            是否成功添加
        """
        # 检查叠加规则
        existing = self.get_effect_by_name(effect.name)
        
        if existing:
            if effect.stack_type == StatusEffectStackType.NO_STACK:
                # 不可叠加，检查是否可以覆盖
                if effect.modifier_value > existing.modifier_value:
                    self.remove_effect(existing.id)
                else:
                    return False
                    
            elif effect.stack_type == StatusEffectStackType.REFRESH_DURATION:
                # 刷新持续时间
                existing.refresh()
                return True
                
            elif effect.stack_type == StatusEffectStackType.STACK_INTENSITY:
                # 叠加强度
                existing.stack()
                return True
        
        # 添加新效果
        self.effects.append(effect)
        self._trigger_callback('on_effect_added', effect=effect)
        
        logger.info(f"添加状态效果: {effect.name}")
        return True
    
    def remove_effect(self, effect_id: str) -> bool:
        """
        移除状态效果
        
        Args:
            effect_id: 效果ID
            
        Returns:
            是否成功移除
        """
        for i, effect in enumerate(self.effects):
            if effect.id == effect_id:
                removed = self.effects.pop(i)
                self._trigger_callback('on_effect_removed', effect=removed)
                logger.info(f"移除状态效果: {removed.name}")
                return True
        
        return False
    
    def get_effect_by_name(self, name: str) -> Optional[StatusEffect]:
        """
        通过名称获取效果
        
        Args:
            name: 效果名称
            
        Returns:
            状态效果对象
        """
        for effect in self.effects:
            if effect.name == name:
                return effect
        return None
    
    def get_effects_by_type(self, effect_type: StatusEffectType) -> List[StatusEffect]:
        """
        获取指定类型的所有效果
        
        Args:
            effect_type: 效果类型
            
        Returns:
            效果列表
        """
        return [e for e in self.effects if e.effect_type == effect_type]
    
    def get_effects_by_tag(self, tag: str) -> List[StatusEffect]:
        """
        获取带有指定标签的效果
        
        Args:
            tag: 标签
            
        Returns:
            效果列表
        """
        return [e for e in self.effects if tag in e.tags]
    
    def has_effect(self, name: str) -> bool:
        """
        是否有指定效果
        
        Args:
            name: 效果名称
            
        Returns:
            是否存在
        """
        return self.get_effect_by_name(name) is not None
    
    def has_control_effect(self) -> bool:
        """是否有控制效果"""
        return any(e.is_control_effect() for e in self.effects)
    
    def update(self) -> None:
        """更新所有效果（每回合调用）"""
        # 触发回合开始回调
        self._trigger_callback('on_turn_start')
        
        # 更新所有效果
        expired_effects = []
        
        for effect in self.effects:
            # 处理每回合效果
            if effect.trigger_on == 'turn_start':
                self._trigger_callback('on_effect_trigger', effect=effect)
            
            # 减少持续时间
            effect.tick()
            
            # 检查是否过期
            if effect.is_expired():
                expired_effects.append(effect)
        
        # 移除过期效果
        for effect in expired_effects:
            self.remove_effect(effect.id)
        
        # 触发回合结束回调
        self._trigger_callback('on_turn_end')
    
    def clear_debuffs(self) -> None:
        """清除所有可驱散的减益效果"""
        to_remove = []
        
        for effect in self.effects:
            if effect.effect_type == StatusEffectType.DEBUFF and effect.can_dispel():
                to_remove.append(effect.id)
        
        for effect_id in to_remove:
            self.remove_effect(effect_id)
    
    def clear_all(self) -> None:
        """清除所有效果"""
        self.effects.clear()
        logger.info("清除所有状态效果")
    
    def get_attribute_modifier(self, attribute: str) -> float:
        """
        获取属性修正值
        
        Args:
            attribute: 属性名称
            
        Returns:
            总修正值
        """
        total = 0
        
        for effect in self.effects:
            if effect.modifier_type == attribute:
                total += effect.get_actual_value()
        
        return total
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """
        注册事件回调
        
        Args:
            event: 事件名称
            callback: 回调函数
        """
        if event not in self.effect_callbacks:
            self.effect_callbacks[event] = []
        
        self.effect_callbacks[event].append(callback)
    
    def _trigger_callback(self, event: str, **kwargs) -> None:
        """
        触发事件回调
        
        Args:
            event: 事件名称
            **kwargs: 传递给回调的参数
        """
        if event in self.effect_callbacks:
            for callback in self.effect_callbacks[event]:
                try:
                    callback(**kwargs)
                except Exception as e:
                    logger.error(f"状态效果回调执行失败: {e}")
    
    def get_status_summary(self) -> List[str]:
        """
        获取状态概要
        
        Returns:
            状态描述列表
        """
        summary = []
        
        for effect in self.effects:
            if effect.duration == -1:
                duration_text = "永久"
            else:
                duration_text = f"{effect.remaining_duration}回合"
            
            if effect.current_stack > 1:
                stack_text = f" x{effect.current_stack}"
            else:
                stack_text = ""
            
            summary.append(f"{effect.name}{stack_text} ({duration_text})")
        
        return summary
