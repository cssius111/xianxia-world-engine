"""
核心服务模块
提供依赖注入容器和接口定义
"""
from .container import ServiceContainer, ServiceNotFoundError, CircularDependencyError
from .interfaces import (
    # 数据模型接口
    ICharacter, IAttributes, IInventory,
    
    # 系统接口
    IGameSystem, ICombatSystem, ISkillSystem, INPCManager,
    IEventSystem, ITimeSystem, ISaveSystem, IDataLoader,
    
    # 游戏流程接口
    ICommandHandler, IOutputChannel, IGameOrchestrator,
    
    # 数据传输对象
    ICommandResult, IGameContext, IOutputMessage, IGameTime,
    
    # 战斗相关
    CombatActionType, ICombatAction, ICombatResult, ICombatState,
    
    # 技能相关
    SkillTargetType, ISkill, ISkillResult,
    
    # 事件相关
    EventType, IEventResult
)

__all__ = [
    # 容器
    'ServiceContainer', 'ServiceNotFoundError', 'CircularDependencyError',
    
    # 接口
    'ICharacter', 'IAttributes', 'IInventory',
    'IGameSystem', 'ICombatSystem', 'ISkillSystem', 'INPCManager',
    'IEventSystem', 'ITimeSystem', 'ISaveSystem', 'IDataLoader',
    'ICommandHandler', 'IOutputChannel', 'IGameOrchestrator',
    'ICommandResult', 'IGameContext', 'IOutputMessage', 'IGameTime',
    'CombatActionType', 'ICombatAction', 'ICombatResult', 'ICombatState',
    'SkillTargetType', 'ISkill', 'ISkillResult',
    'EventType', 'IEventResult'
]
