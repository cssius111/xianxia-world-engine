"""
游戏状态管理器 - 核心状态管理模块

负责管理游戏的所有状态，包括：
- 玩家状态
- 世界状态
- 游戏上下文栈（战斗/对话/探索等）
- 状态持久化
- 状态变化通知
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from xwe_v2.core.events import Event, EventBus
from xwe_v2.domain.character.models import Character

logger = logging.getLogger(__name__)


class GameContext(Enum):
    """游戏上下文类型"""

    EXPLORATION = auto()  # 探索模式
    COMBAT = auto()  # 战斗模式
    DIALOGUE = auto()  # 对话模式
    CULTIVATION = auto()  # 修炼模式
    TRADING = auto()  # 交易模式
    CRAFTING = auto()  # 炼制模式
    MENU = auto()  # 菜单界面
    CUTSCENE = auto()  # 剧情演出


@dataclass
class ContextInfo:
    """上下文信息"""

    context_type: GameContext
    data: Dict[str, Any] = field(default_factory=dict)
    entered_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "context_type": self.context_type.name,
            "data": self.data,
            "entered_at": self.entered_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContextInfo":
        """从字典创建"""
        return cls(
            context_type=GameContext[data["context_type"]],
            data=data.get("data", {}),
            entered_at=datetime.fromisoformat(data["entered_at"]),
        )


@dataclass
class GameState:
    """游戏状态数据类"""

    # 玩家相关
    player: Optional[Character] = None
    player_id: Optional[str] = None

    # 位置和时间
    current_location: str = "qingyun_city"
    game_time: int = 0  # 游戏时间（回合数）
    real_time_played: float = 0.0  # 实际游戏时长（秒）

    # 战斗相关
    current_combat: Optional[str] = None
    combat_history: List[Dict[str, Any]] = field(default_factory=list)

    # NPC相关
    npcs: Dict[str, Character] = field(default_factory=dict)
    npc_relationships: Dict[str, int] = field(default_factory=dict)

    # 游戏标记
    flags: Dict[str, Any] = field(default_factory=dict)
    quests: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    achievements: Set[str] = field(default_factory=set)

    # 统计数据
    statistics: Dict[str, Any] = field(default_factory=dict)

    # 游戏设置
    game_mode: str = "player"  # player, dev, tutorial
    difficulty: str = "normal"  # easy, normal, hard, nightmare

    def to_dict(self) -> Dict[str, Any]:
        """转换为可序列化的字典"""
        return {
            "player": self.player.to_dict() if self.player else None,
            "player_id": self.player_id,
            "current_location": self.current_location,
            "game_time": self.game_time,
            "real_time_played": self.real_time_played,
            "current_combat": self.current_combat,
            "combat_history": self.combat_history,
            "npcs": {npc_id: npc.to_dict() for npc_id, npc in self.npcs.items()},
            "npc_relationships": self.npc_relationships,
            "flags": self.flags,
            "quests": self.quests,
            "achievements": list(self.achievements),
            "statistics": self.statistics,
            "game_mode": self.game_mode,
            "difficulty": self.difficulty,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameState":
        """从字典创建游戏状态"""
        state = cls()

        if data.get("player"):
            state.player = Character.from_dict(data["player"])

        state.player_id = data.get("player_id")
        state.current_location = data.get("current_location", "qingyun_city")
        state.game_time = data.get("game_time", 0)
        state.real_time_played = data.get("real_time_played", 0.0)
        state.current_combat = data.get("current_combat")
        state.combat_history = data.get("combat_history", [])

        if "npcs" in data:
            state.npcs = {nid: Character.from_dict(nc) for nid, nc in data["npcs"].items()}

        state.npc_relationships = data.get("npc_relationships", {})
        state.flags = data.get("flags", {})
        state.quests = data.get("quests", {})
        state.achievements = set(data.get("achievements", []))
        state.statistics = data.get("statistics", {})
        state.game_mode = data.get("game_mode", "player")
        state.difficulty = data.get("difficulty", "normal")

        return state


class GameStateManager:
    """
    游戏状态管理器

    负责管理游戏的所有状态，包括上下文栈、状态持久化和状态变化通知
    """

    def __init__(self, event_bus: Optional[EventBus] = None):
        """
        初始化状态管理器

        Args:
            event_bus: 事件总线，用于发布状态变化事件
        """
        self.state = GameState()
        self.context_stack: List[ContextInfo] = []
        self.event_bus = event_bus or EventBus()

        # 状态变化监听器
        self._state_listeners: Dict[str, List[Callable]] = {}

        # 状态快照（用于撤销/重做）
        self._state_snapshots: List[Dict[str, Any]] = []
        self._max_snapshots = 10

        # 自动保存设置
        self._auto_save_enabled = True
        self._auto_save_interval = 300  # 5分钟
        self._last_auto_save = datetime.now()

        logger.info("游戏状态管理器初始化完成")

    # === 上下文管理 ===

    def push_context(
        self, context_type: GameContext, data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        推入新的游戏上下文

        Args:
            context_type: 上下文类型
            data: 上下文相关数据
        """
        context = ContextInfo(context_type, data or {})
        self.context_stack.append(context)

        logger.info(f"进入上下文: {context_type.name}")

        # 发布上下文变化事件
        self.event_bus.publish(
            Event(
                "context_changed",
                {
                    "action": "push",
                    "context": context_type.name,
                    "stack_size": len(self.context_stack),
                },
            )
        )

        # 触发监听器
        self._trigger_listeners("context_changed", {"context": context_type, "action": "enter"})

    def pop_context(self) -> Optional[ContextInfo]:
        """
        弹出当前上下文

        Returns:
            被弹出的上下文信息
        """
        if not self.context_stack:
            return None

        context = self.context_stack.pop()
        logger.info(f"退出上下文: {context.context_type.name}")

        # 发布上下文变化事件
        self.event_bus.publish(
            Event(
                "context_changed",
                {
                    "action": "pop",
                    "context": context.context_type.name,
                    "stack_size": len(self.context_stack),
                },
            )
        )

        # 触发监听器
        self._trigger_listeners(
            "context_changed", {"context": context.context_type, "action": "exit"}
        )

        return context

    def get_current_context(self) -> Optional[GameContext]:
        """
        获取当前上下文

        Returns:
            当前上下文类型，如果栈为空则返回None
        """
        if not self.context_stack:
            return None
        return self.context_stack[-1].context_type

    def get_context_data(self) -> Dict[str, Any]:
        """
        获取当前上下文的数据

        Returns:
            上下文数据
        """
        if not self.context_stack:
            return {}
        return self.context_stack[-1].data

    def update_context_data(self, updates: Dict[str, Any]) -> None:
        """
        更新当前上下文的数据

        Args:
            updates: 要更新的数据
        """
        if self.context_stack:
            self.context_stack[-1].data.update(updates)

    def is_in_context(self, context_type: GameContext) -> bool:
        """
        检查是否在指定的上下文中

        Args:
            context_type: 要检查的上下文类型

        Returns:
            是否在指定上下文中
        """
        return any(ctx.context_type == context_type for ctx in self.context_stack)

    def clear_context_stack(self) -> None:
        """清空上下文栈"""
        self.context_stack.clear()
        self.event_bus.publish(Event("context_cleared", {}))

    # === 状态访问和修改 ===

    def get_player(self) -> Optional[Character]:
        """获取玩家角色"""
        return self.state.player

    def set_player(self, player: Character) -> None:
        """设置玩家角色"""
        self.state.player = player
        self.state.player_id = player.id
        self._trigger_listeners("player_changed", {"player": player})

    def get_location(self) -> str:
        """获取当前位置"""
        return self.state.current_location

    def set_location(self, location: str) -> None:
        """设置当前位置"""
        old_location = self.state.current_location
        self.state.current_location = location
        self._trigger_listeners("location_changed", {"old": old_location, "new": location})

    def get_flag(self, key: str, default: Any = None) -> Any:
        """获取游戏标记"""
        return self.state.flags.get(key, default)

    def set_flag(self, key: str, value: Any) -> None:
        """设置游戏标记"""
        self.state.flags[key] = value
        self._trigger_listeners("flag_changed", {"key": key, "value": value})

    def update_statistics(self, stat: str, value: Any) -> None:
        """更新统计数据"""
        if stat not in self.state.statistics:
            self.state.statistics[stat] = 0

        if isinstance(value, (int, float)):
            self.state.statistics[stat] += value
        else:
            self.state.statistics[stat] = value

    def add_achievement(self, achievement_id: str) -> None:
        """添加成就"""
        if achievement_id not in self.state.achievements:
            self.state.achievements.add(achievement_id)
            self._trigger_listeners("achievement_unlocked", {"achievement": achievement_id})

    # === 战斗状态管理 ===

    def start_combat(self, combat_id: str) -> None:
        """开始战斗"""
        self.state.current_combat = combat_id
        self.push_context(GameContext.COMBAT, {"combat_id": combat_id})
        self._trigger_listeners("combat_started", {"combat_id": combat_id})

    def end_combat(self, result: Dict[str, Any]) -> None:
        """结束战斗"""
        if self.state.current_combat:
            # 记录战斗历史
            self.state.combat_history.append(
                {
                    "combat_id": self.state.current_combat,
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # 限制历史记录数量
            if len(self.state.combat_history) > 100:
                self.state.combat_history = self.state.combat_history[-100:]

            self.state.current_combat = None
            self.pop_context()
            self._trigger_listeners("combat_ended", result)

    def is_in_combat(self) -> bool:
        """检查是否在战斗中"""
        return self.state.current_combat is not None

    # === NPC管理 ===

    def add_npc(self, npc: Character) -> None:
        """添加NPC"""
        self.state.npcs[npc.id] = npc
        self._trigger_listeners("npc_added", {"npc": npc})

    def remove_npc(self, npc_id: str) -> None:
        """移除NPC"""
        if npc_id in self.state.npcs:
            npc = self.state.npcs.pop(npc_id)
            self._trigger_listeners("npc_removed", {"npc": npc})

    def get_npc(self, npc_id: str) -> Optional[Character]:
        """获取NPC"""
        return self.state.npcs.get(npc_id)

    def update_npc_relationship(self, npc_id: str, change: int) -> None:
        """更新NPC关系"""
        if npc_id not in self.state.npc_relationships:
            self.state.npc_relationships[npc_id] = 0

        old_value = self.state.npc_relationships[npc_id]
        self.state.npc_relationships[npc_id] += change

        self._trigger_listeners(
            "relationship_changed",
            {
                "npc_id": npc_id,
                "old_value": old_value,
                "new_value": self.state.npc_relationships[npc_id],
            },
        )

    # === 任务管理 ===

    def add_quest(self, quest_id: str, quest_data: Dict[str, Any]) -> None:
        """添加任务"""
        self.state.quests[quest_id] = quest_data
        self._trigger_listeners("quest_added", {"quest_id": quest_id, "data": quest_data})

    def update_quest(self, quest_id: str, updates: Dict[str, Any]) -> None:
        """更新任务"""
        if quest_id in self.state.quests:
            self.state.quests[quest_id].update(updates)
            self._trigger_listeners("quest_updated", {"quest_id": quest_id, "updates": updates})

    def complete_quest(self, quest_id: str) -> None:
        """完成任务"""
        if quest_id in self.state.quests:
            self.state.quests[quest_id]["completed"] = True
            self.state.quests[quest_id]["completed_at"] = datetime.now().isoformat()
            self._trigger_listeners("quest_completed", {"quest_id": quest_id})

    # === 状态监听器 ===

    def add_listener(self, event_type: str, callback: Callable) -> None:
        """
        添加状态变化监听器

        Args:
            event_type: 事件类型
            callback: 回调函数
        """
        if event_type not in self._state_listeners:
            self._state_listeners[event_type] = []
        self._state_listeners[event_type].append(callback)

    def remove_listener(self, event_type: str, callback: Callable) -> None:
        """
        移除状态变化监听器

        Args:
            event_type: 事件类型
            callback: 回调函数
        """
        if event_type in self._state_listeners:
            self._state_listeners[event_type].remove(callback)

    def _trigger_listeners(self, event_type: str, data: Dict[str, Any]) -> None:
        """触发监听器"""
        if event_type in self._state_listeners:
            for callback in self._state_listeners[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"监听器执行失败: {e}")

    # === 状态持久化 ===

    def save_state(self, filepath: Path) -> None:
        """
        保存游戏状态到文件

        Args:
            filepath: 保存路径
        """
        try:
            save_data = {
                "version": "2.0.0",
                "timestamp": datetime.now().isoformat(),
                "state": self.state.to_dict(),
                "context_stack": [ctx.to_dict() for ctx in self.context_stack],
            }

            filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            logger.info(f"游戏状态已保存: {filepath}")
            self._last_auto_save = datetime.now()

        except Exception as e:
            logger.error(f"保存游戏状态失败: {e}")
            raise

    def load_state(self, filepath: Path) -> None:
        """
        从文件加载游戏状态

        Args:
            filepath: 加载路径
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                save_data = json.load(f)

            # 加载游戏状态
            self.state = GameState.from_dict(save_data["state"])

            # 加载上下文栈
            self.context_stack = [
                ContextInfo.from_dict(ctx) for ctx in save_data.get("context_stack", [])
            ]

            logger.info(f"游戏状态已加载: {filepath}")

            # 触发状态加载事件
            self._trigger_listeners("state_loaded", {"filepath": str(filepath)})

        except Exception as e:
            logger.error(f"加载游戏状态失败: {e}")
            raise

    def create_snapshot(self) -> None:
        """创建状态快照"""
        snapshot = {
            "state": self.state.to_dict(),
            "context_stack": [ctx.to_dict() for ctx in self.context_stack],
            "timestamp": datetime.now().isoformat(),
        }

        self._state_snapshots.append(snapshot)

        # 限制快照数量
        if len(self._state_snapshots) > self._max_snapshots:
            self._state_snapshots.pop(0)

    def restore_snapshot(self, index: int = -1) -> bool:
        """
        恢复状态快照

        Args:
            index: 快照索引，默认为最新的快照

        Returns:
            是否成功恢复
        """
        if not self._state_snapshots:
            return False

        try:
            snapshot = self._state_snapshots[index]
            self.state = GameState.from_dict(snapshot["state"])
            self.context_stack = [ContextInfo.from_dict(ctx) for ctx in snapshot["context_stack"]]

            logger.info(f"已恢复到快照: {snapshot['timestamp']}")
            return True

        except Exception as e:
            logger.error(f"恢复快照失败: {e}")
            return False

    def check_auto_save(self) -> None:
        """检查是否需要自动保存"""
        if not self._auto_save_enabled:
            return

        now = datetime.now()
        if (now - self._last_auto_save).total_seconds() >= self._auto_save_interval:
            # 使用默认自动保存路径
            auto_save_path = Path("saves/auto/autosave.json")
            self.save_state(auto_save_path)

    # === 状态查询 ===

    def get_game_info(self) -> Dict[str, Any]:
        """获取游戏信息摘要"""
        return {
            "player_name": self.state.player.name if self.state.player else None,
            "location": self.state.current_location,
            "game_time": self.state.game_time,
            "real_time_played": self.state.real_time_played,
            "current_context": (
                self.get_current_context().name if self.get_current_context() else None
            ),
            "in_combat": self.is_in_combat(),
            "quest_count": len(self.state.quests),
            "achievement_count": len(self.state.achievements),
            "game_mode": self.state.game_mode,
            "difficulty": self.state.difficulty,
        }

    def validate_state(self) -> List[str]:
        """
        验证游戏状态的完整性

        Returns:
            错误信息列表
        """
        errors = []

        # 检查玩家
        if not self.state.player:
            errors.append("玩家角色未设置")

        # 检查位置
        if not self.state.current_location:
            errors.append("当前位置未设置")

        # 检查上下文栈一致性
        if self.is_in_context(GameContext.COMBAT) and not self.state.current_combat:
            errors.append("战斗上下文与战斗状态不一致")

        # 检查NPC引用
        for npc_id in self.state.npc_relationships:
            if npc_id not in self.state.npcs:
                errors.append(f"关系中引用了不存在的NPC: {npc_id}")

        return errors


# 导出主要类
__all__ = ["GameStateManager", "GameState", "GameContext", "ContextInfo"]
