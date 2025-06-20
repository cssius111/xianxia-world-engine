"""
游戏服务接口定义
负责游戏的整体流程控制、状态管理和协调各个子系统
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class GameState:
    """游戏状态数据"""

    initialized: bool
    in_combat: bool
    current_location: str
    game_time: float
    player_id: Optional[str] = None
    active_events: List[str] = field(default_factory=list)
    paused: bool = False


@dataclass
class CommandResult:
    """命令执行结果"""

    success: bool
    output: str
    state_changed: bool = False
    events: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    require_confirmation: bool = False
    confirmation_data: Dict[str, Any] = field(default_factory=dict)


class IGameService(ABC):
    """
    游戏服务接口

    主要职责：
    1. 游戏生命周期管理（初始化、暂停、恢复、结束）
    2. 命令处理和路由
    3. 游戏状态查询和管理
    4. 事件协调和日志管理
    5. 存档的保存和加载
    """

    # ========== 生命周期管理 ==========

    @abstractmethod
    def initialize_game(self, player_name: Optional[str] = None, **options) -> bool:
        """
        初始化新游戏

        Args:
            player_name: 玩家名称（可选，如果不提供则需要后续创建）
            **options: 游戏初始化选项
                - difficulty: 游戏难度 ('easy', 'normal', 'hard')
                - mode: 游戏模式 ('standard', 'hardcore', 'creative')
                - seed: 随机种子

        Returns:
            bool: 初始化是否成功

        Example:
            >>> game_service.initialize_game("张三", difficulty="normal")
            True
        """
        pass

    @abstractmethod
    def start_game(self) -> bool:
        """
        开始游戏（从暂停状态恢复）

        Returns:
            bool: 是否成功开始
        """
        pass

    @abstractmethod
    def pause_game(self) -> bool:
        """
        暂停游戏

        Returns:
            bool: 是否成功暂停
        """
        pass

    @abstractmethod
    def end_game(self, reason: str = "player_quit") -> bool:
        """
        结束游戏

        Args:
            reason: 结束原因 ('player_quit', 'player_death', 'victory', 'error')

        Returns:
            bool: 是否成功结束
        """
        pass

    # ========== 命令处理 ==========

    @abstractmethod
    def process_command(self, command: str, **context) -> CommandResult:
        """
        处理游戏命令

        Args:
            command: 命令字符串
            **context: 命令上下文
                - source: 命令来源 ('player', 'system', 'ai')
                - priority: 优先级

        Returns:
            CommandResult: 命令执行结果

        Example:
            >>> result = game_service.process_command("攻击 妖兽")
            >>> print(result.output)
            "你对妖兽发起了攻击，造成了50点伤害！"
        """
        pass

    @abstractmethod
    def can_execute_command(self, command: str) -> bool:
        """
        检查命令是否可以执行

        Args:
            command: 命令字符串

        Returns:
            bool: 是否可以执行
        """
        pass

    # ========== 状态管理 ==========

    @abstractmethod
    def get_game_state(self) -> GameState:
        """
        获取当前游戏状态

        Returns:
            GameState: 游戏状态对象
        """
        pass

    @abstractmethod
    def get_game_time(self) -> float:
        """
        获取游戏时间（秒）

        Returns:
            float: 游戏时间
        """
        pass

    @abstractmethod
    def get_real_time(self) -> float:
        """
        获取实际游戏时长（秒）

        Returns:
            float: 实际时长
        """
        pass

    @abstractmethod
    def is_game_over(self) -> bool:
        """
        检查游戏是否结束

        Returns:
            bool: 游戏是否结束
        """
        pass

    # ========== 存档管理 ==========

    @abstractmethod
    def save_game(self, save_name: str, description: str = "") -> bool:
        """
        保存游戏

        Args:
            save_name: 存档名称
            description: 存档描述

        Returns:
            bool: 是否保存成功
        """
        pass

    @abstractmethod
    def load_game(self, save_id: str) -> bool:
        """
        加载游戏

        Args:
            save_id: 存档ID

        Returns:
            bool: 是否加载成功
        """
        pass

    @abstractmethod
    def quick_save(self) -> bool:
        """
        快速保存

        Returns:
            bool: 是否保存成功
        """
        pass

    @abstractmethod
    def quick_load(self) -> bool:
        """
        快速加载

        Returns:
            bool: 是否加载成功
        """
        pass

    # ========== 日志和事件 ==========

    @abstractmethod
    def get_logs(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取游戏日志

        Args:
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            List[Dict]: 日志列表
        """
        pass

    @abstractmethod
    def get_recent_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取最近的游戏事件

        Args:
            limit: 返回数量限制

        Returns:
            List[Dict]: 事件列表
        """
        pass

    @abstractmethod
    def clear_logs(self) -> bool:
        """
        清空日志

        Returns:
            bool: 是否成功清空
        """
        pass

    # ========== 系统交互 ==========

    @abstractmethod
    def get_system_info(self) -> Dict[str, Any]:
        """
        获取系统信息

        Returns:
            Dict: 系统信息
                - version: 游戏版本
                - modules: 已加载模块
                - performance: 性能指标
        """
        pass

    @abstractmethod
    def set_game_speed(self, speed: float) -> bool:
        """
        设置游戏速度

        Args:
            speed: 速度倍率 (0.5 = 半速, 1.0 = 正常, 2.0 = 双倍速)

        Returns:
            bool: 是否设置成功
        """
        pass

    @abstractmethod
    def toggle_debug_mode(self) -> bool:
        """
        切换调试模式

        Returns:
            bool: 当前调试模式状态
        """
        pass
