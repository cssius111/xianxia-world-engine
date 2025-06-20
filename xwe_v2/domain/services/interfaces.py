"""
核心接口定义
定义游戏中各个系统的接口规范
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

# ========== 数据模型接口 ==========


@runtime_checkable
class ICharacter(Protocol):
    """角色接口"""

    id: str
    name: str
    character_type: Any  # CharacterType enum
    attributes: "IAttributes"

    def is_alive(self) -> bool: ...
    def take_damage(self, damage: float) -> None: ...
    def heal(self, amount: float) -> None: ...
    def has_skill(self, skill_id: str) -> bool: ...
    def learn_skill(self, skill_id: str) -> bool: ...


@runtime_checkable
class IAttributes(Protocol):
    """属性接口"""

    # 基础属性
    current_health: float
    max_health: float
    current_mana: float
    max_mana: float
    current_stamina: float
    max_stamina: float

    # 修炼相关
    cultivation_level: int
    realm_name: str
    realm_level: int

    def get(self, attr_name: str) -> float: ...
    def set(self, attr_name: str, value: float) -> None: ...
    def modify(self, attr_name: str, delta: float) -> None: ...
    def calculate_derived_attributes(self) -> None: ...


@runtime_checkable
class IInventory(Protocol):
    """背包接口"""

    def add(self, item_id: str, quantity: int) -> bool: ...
    def remove(self, item_id: str, quantity: int) -> bool: ...
    def has(self, item_id: str, quantity: int = 1) -> bool: ...
    def get_quantity(self, item_id: str) -> int: ...
    def list_items(self) -> List[tuple[str, int]]: ...


# ========== 系统接口 ==========


class IGameSystem(ABC):
    """游戏系统基础接口"""

    @abstractmethod
    def initialize(self) -> None:
        """初始化系统"""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """关闭系统"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """系统名称"""
        pass


class ICombatSystem(IGameSystem):
    """战斗系统接口"""

    @abstractmethod
    def create_combat(self, combat_id: str) -> "ICombatState":
        """创建战斗"""
        pass

    @abstractmethod
    def execute_action(self, combat_id: str, action: "ICombatAction") -> "ICombatResult":
        """执行战斗动作"""
        pass

    @abstractmethod
    def end_combat(self, combat_id: str) -> None:
        """结束战斗"""
        pass

    @abstractmethod
    def get_combat(self, combat_id: str) -> Optional["ICombatState"]:
        """获取战斗状态"""
        pass


class ISkillSystem(IGameSystem):
    """技能系统接口"""

    @abstractmethod
    def get_skill(self, skill_id: str) -> Optional["ISkill"]:
        """获取技能"""
        pass

    @abstractmethod
    def can_use_skill(self, character: ICharacter, skill_id: str) -> bool:
        """检查是否可以使用技能"""
        pass

    @abstractmethod
    def use_skill(
        self, character: ICharacter, skill_id: str, targets: List[ICharacter]
    ) -> "ISkillResult":
        """使用技能"""
        pass


class INPCManager(IGameSystem):
    """NPC管理器接口"""

    @abstractmethod
    def get_npc(self, npc_id: str) -> Optional[ICharacter]:
        """获取NPC"""
        pass

    @abstractmethod
    def get_npcs_at_location(self, location_id: str) -> List[ICharacter]:
        """获取某位置的所有NPC"""
        pass

    @abstractmethod
    def create_npc(self, template_id: str, location_id: str) -> ICharacter:
        """创建NPC"""
        pass

    @abstractmethod
    def remove_npc(self, npc_id: str) -> bool:
        """移除NPC"""
        pass


class IEventSystem(IGameSystem):
    """事件系统接口"""

    @abstractmethod
    def trigger_event(self, event_id: str, context: Dict[str, Any]) -> "IEventResult":
        """触发事件"""
        pass

    @abstractmethod
    def register_event_handler(self, event_type: str, handler: Any) -> None:
        """注册事件处理器"""
        pass

    @abstractmethod
    def check_triggers(self, context: Dict[str, Any]) -> List[str]:
        """检查可触发的事件"""
        pass


class ITimeSystem(IGameSystem):
    """时间系统接口"""

    @abstractmethod
    def get_current_time(self) -> "IGameTime":
        """获取当前游戏时间"""
        pass

    @abstractmethod
    def advance_time(self, hours: int) -> None:
        """推进时间"""
        pass

    @abstractmethod
    def schedule_event(
        self, hours_from_now: int, event_name: str, event_data: Dict[str, Any]
    ) -> None:
        """安排定时事件"""
        pass


class ISaveSystem(IGameSystem):
    """存档系统接口"""

    @abstractmethod
    def save_game(self, save_name: str, game_data: Dict[str, Any]) -> bool:
        """保存游戏"""
        pass

    @abstractmethod
    def load_game(self, save_name: str) -> Optional[Dict[str, Any]]:
        """加载游戏"""
        pass

    @abstractmethod
    def list_saves(self) -> List[Dict[str, Any]]:
        """列出所有存档"""
        pass

    @abstractmethod
    def delete_save(self, save_name: str) -> bool:
        """删除存档"""
        pass


class IDataLoader(IGameSystem):
    """数据加载器接口"""

    @abstractmethod
    def load_json(self, file_path: str) -> Dict[str, Any]:
        """加载JSON文件"""
        pass

    @abstractmethod
    def get_template(self, template_type: str, template_id: str) -> Optional[Dict[str, Any]]:
        """获取模板数据"""
        pass

    @abstractmethod
    def reload_data(self) -> None:
        """重新加载所有数据"""
        pass


# ========== 游戏流程接口 ==========


class ICommandHandler(ABC):
    """命令处理器接口"""

    @abstractmethod
    def can_handle(self, command: str, context: "IGameContext") -> bool:
        """判断是否可以处理该命令"""
        pass

    @abstractmethod
    def handle(
        self, command: str, args: Dict[str, Any], context: "IGameContext"
    ) -> "ICommandResult":
        """处理命令"""
        pass

    @property
    @abstractmethod
    def command_type(self) -> str:
        """命令类型"""
        pass


class IOutputChannel(Protocol):
    """输出通道接口"""

    def send(self, message: "IOutputMessage") -> None:
        """发送消息到输出通道"""
        ...

    def flush(self) -> None:
        """刷新输出缓冲"""
        ...


class IGameOrchestrator(ABC):
    """游戏协调器接口"""

    @abstractmethod
    def initialize(self) -> None:
        """初始化游戏"""
        pass

    @abstractmethod
    def run_game_loop(self) -> None:
        """运行游戏主循环"""
        pass

    @abstractmethod
    def process_input(self, input_text: str) -> None:
        """处理输入"""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """关闭游戏"""
        pass


# ========== 数据传输对象 ==========


@dataclass
class ICommandResult:
    """命令执行结果"""

    success: bool
    message: Optional[str] = None
    data: Dict[str, Any] = None
    side_effects: List[str] = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.side_effects is None:
            self.side_effects = []


@dataclass
class IGameContext:
    """游戏上下文"""

    context_type: str
    data: Dict[str, Any] = None
    parent: Optional["IGameContext"] = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}


@dataclass
class IOutputMessage:
    """输出消息"""

    text: str
    category: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class IGameTime:
    """游戏时间"""

    year: int
    month: int
    day: int
    hour: int

    def total_hours(self) -> int:
        """转换为总小时数"""
        return (self.year - 1) * 8760 + (self.month - 1) * 720 + (self.day - 1) * 24 + self.hour


# ========== 战斗相关接口 ==========


class CombatActionType(Enum):
    """战斗动作类型"""

    ATTACK = "attack"
    SKILL = "skill"
    DEFEND = "defend"
    ITEM = "item"
    FLEE = "flee"
    WAIT = "wait"


@dataclass
class ICombatAction:
    """战斗动作"""

    action_type: CombatActionType
    actor_id: str
    target_ids: List[str] = None
    skill_id: Optional[str] = None
    item_id: Optional[str] = None

    def __post_init__(self):
        if self.target_ids is None:
            self.target_ids = []


@dataclass
class ICombatResult:
    """战斗结果"""

    success: bool
    damage_dealt: Dict[str, float] = None
    healing_done: Dict[str, float] = None
    effects_applied: List[str] = None
    message: str = ""

    def __post_init__(self):
        if self.damage_dealt is None:
            self.damage_dealt = {}
        if self.healing_done is None:
            self.healing_done = {}
        if self.effects_applied is None:
            self.effects_applied = []


@runtime_checkable
class ICombatState(Protocol):
    """战斗状态接口"""

    combat_id: str
    participants: Dict[str, ICharacter]
    turn_order: List[str]
    current_turn: int
    round_count: int

    def is_combat_over(self) -> bool: ...
    def get_winning_team(self) -> Optional[str]: ...
    def get_enemies(self, character: ICharacter) -> List[ICharacter]: ...
    def get_allies(self, character: ICharacter) -> List[ICharacter]: ...


# ========== 技能相关接口 ==========


class SkillTargetType(Enum):
    """技能目标类型"""

    SELF = "self"
    SINGLE_ENEMY = "single_enemy"
    SINGLE_ALLY = "single_ally"
    ALL_ENEMIES = "all_enemies"
    ALL_ALLIES = "all_allies"
    ALL = "all"


@runtime_checkable
class ISkill(Protocol):
    """技能接口"""

    id: str
    name: str
    description: str
    mana_cost: int
    stamina_cost: int
    cooldown: int
    target_type: SkillTargetType
    max_targets: int

    def can_use(self, user: ICharacter) -> bool: ...
    def get_valid_targets(
        self, user: ICharacter, all_characters: List[ICharacter]
    ) -> List[ICharacter]: ...


@dataclass
class ISkillResult:
    """技能使用结果"""

    success: bool
    targets_affected: Dict[str, Dict[str, Any]] = None
    message: str = ""

    def __post_init__(self):
        if self.targets_affected is None:
            self.targets_affected = {}


# ========== 事件相关接口 ==========


class EventType(Enum):
    """事件类型"""

    RANDOM = "random"
    STORY = "story"
    COMBAT = "combat"
    SOCIAL = "social"
    EXPLORATION = "exploration"
    CULTIVATION = "cultivation"


@dataclass
class IEventResult:
    """事件结果"""

    success: bool
    outcomes: List[str] = None
    rewards: Dict[str, Any] = None
    consequences: Dict[str, Any] = None

    def __post_init__(self):
        if self.outcomes is None:
            self.outcomes = []
        if self.rewards is None:
            self.rewards = {}
        if self.consequences is None:
            self.consequences = {}
