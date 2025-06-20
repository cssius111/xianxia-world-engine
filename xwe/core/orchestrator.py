"""
游戏协调器 - 整合所有核心模块的中央控制器

负责协调和管理游戏的所有核心模块，提供统一的游戏接口。
"""

import asyncio
import json
import logging
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from xwe.core.character import Character, CharacterType
from xwe.core.command import CombatCommandHandler  # 中间件; 处理器
from xwe.core.command import (
    CommandProcessor,
    CooldownMiddleware,
    CultivationCommandHandler,
    InfoHandler,
    InteractionCommandHandler,
    LoggingMiddleware,
    MovementHandler,
    RateLimitMiddleware,
    SystemCommandHandler,
    ValidationMiddleware,
)
from xwe.core.output import (
    ConsoleChannel,
    FileChannel,
    HTMLChannel,
    MessagePriority,
    MessageType,
    OutputManager,
)
from xwe.core.state import GameContext, GameStateManager
from xwe.core.world import Location, World

logger = logging.getLogger(__name__)


class GameMode(Enum):
    """游戏模式"""

    PLAYER = "player"  # 玩家模式
    DEV = "dev"  # 开发模式
    TEST = "test"  # 测试模式
    SCRIPT = "script"  # 脚本模式
    SERVER = "server"  # 服务器模式


class GameStatus(Enum):
    """游戏状态"""

    INITIALIZING = auto()  # 初始化中
    READY = auto()  # 就绪
    RUNNING = auto()  # 运行中
    PAUSED = auto()  # 暂停
    SAVING = auto()  # 保存中
    LOADING = auto()  # 加载中
    SHUTTING_DOWN = auto()  # 关闭中
    ERROR = auto()  # 错误状态


@dataclass
class GameConfig:
    """游戏配置"""

    # 基础配置
    game_mode: GameMode = GameMode.PLAYER
    game_name: str = "仙侠世界"
    version: str = "1.0.0"

    # 路径配置
    save_dir: Path = field(default_factory=lambda: Path("saves"))
    log_dir: Path = field(default_factory=lambda: Path("logs"))
    data_dir: Path = field(default_factory=lambda: Path("data"))

    # 输出配置
    enable_console: bool = True
    enable_file_log: bool = True
    enable_html: bool = False
    console_colored: bool = True
    html_refresh_interval: int = 2

    # 命令配置
    enable_command_log: bool = True
    enable_validation: bool = True
    enable_cooldown: bool = True
    enable_rate_limit: bool = True
    rate_limit_max: int = 30
    rate_limit_window: float = 60.0

    # 自动保存配置
    auto_save_enabled: bool = True
    auto_save_interval: float = 300.0  # 5分钟

    # 性能配置
    max_command_history: int = 100
    max_output_history: int = 1000

    # 调试配置
    debug_mode: bool = False
    show_traceback: bool = False

    @classmethod
    def from_file(cls, filepath: Path) -> "GameConfig":
        """从文件加载配置"""
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 转换路径字符串为Path对象
                for key in ["save_dir", "log_dir", "data_dir"]:
                    if key in data:
                        data[key] = Path(data[key])
                # 转换枚举
                if "game_mode" in data:
                    data["game_mode"] = GameMode(data["game_mode"])
                return cls(**data)
        return cls()

    def save_to_file(self, filepath: Path) -> None:
        """保存配置到文件"""
        data = {
            "game_mode": self.game_mode.value,
            "game_name": self.game_name,
            "version": self.version,
            "save_dir": str(self.save_dir),
            "log_dir": str(self.log_dir),
            "data_dir": str(self.data_dir),
            "enable_console": self.enable_console,
            "enable_file_log": self.enable_file_log,
            "enable_html": self.enable_html,
            "console_colored": self.console_colored,
            "html_refresh_interval": self.html_refresh_interval,
            "enable_command_log": self.enable_command_log,
            "enable_validation": self.enable_validation,
            "enable_cooldown": self.enable_cooldown,
            "enable_rate_limit": self.enable_rate_limit,
            "rate_limit_max": self.rate_limit_max,
            "rate_limit_window": self.rate_limit_window,
            "auto_save_enabled": self.auto_save_enabled,
            "auto_save_interval": self.auto_save_interval,
            "max_command_history": self.max_command_history,
            "max_output_history": self.max_output_history,
            "debug_mode": self.debug_mode,
            "show_traceback": self.show_traceback,
        }

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


class GameOrchestrator:
    """
    游戏协调器

    整合和协调所有游戏核心模块，提供统一的游戏管理接口。
    """

    def __init__(self, config: Optional[GameConfig] = None):
        """
        初始化游戏协调器

        Args:
            config: 游戏配置，None则使用默认配置
        """
        self.config = config or GameConfig()
        self.status = GameStatus.INITIALIZING

        # 核心模块
        self.state_manager: Optional[GameStateManager] = None
        self.output_manager: Optional[OutputManager] = None
        self.command_processor: Optional[CommandProcessor] = None

        # 游戏世界
        self.world: Optional[World] = None

        # 运行控制
        self.running = False
        self.paused = False
        self._shutdown_requested = False

        # 自动保存
        self._auto_save_task: Optional[asyncio.Task] = None
        self._last_save_time = datetime.now()

        # 钩子函数
        self._startup_hooks: List[Callable] = []
        self._shutdown_hooks: List[Callable] = []
        self._pre_command_hooks: List[Callable] = []
        self._post_command_hooks: List[Callable] = []

        logger.info(f"游戏协调器初始化: 模式={self.config.game_mode.value}")

    async def initialize(self) -> None:
        """初始化游戏系统"""
        try:
            self.status = GameStatus.INITIALIZING

            # 创建必要的目录
            self._create_directories()

            # 初始化核心模块
            await self._init_state_manager()
            await self._init_output_manager()
            await self._init_command_processor()

            # 初始化游戏世界
            await self._init_world()

            # 设置模块间连接
            self._setup_module_connections()

            # 运行启动钩子
            await self._run_startup_hooks()

            self.status = GameStatus.READY
            self.output_manager.success(f"{self.config.game_name} 初始化完成！")

            logger.info("游戏系统初始化成功")

        except Exception as e:
            self.status = GameStatus.ERROR
            logger.error(f"游戏初始化失败: {e}")
            if self.output_manager:
                self.output_manager.error(f"初始化失败: {str(e)}")
            raise

    def _create_directories(self) -> None:
        """创建必要的目录"""
        for dir_path in [self.config.save_dir, self.config.log_dir, self.config.data_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    async def _init_state_manager(self) -> None:
        """初始化状态管理器"""
        self.state_manager = GameStateManager()
        self.state_manager.state.game_mode = self.config.game_mode.value
        self.state_manager.state.version = self.config.version

        # 设置状态监听器
        self._setup_state_listeners()

        logger.info("状态管理器初始化完成")

    async def _init_output_manager(self) -> None:
        """初始化输出管理器"""
        self.output_manager = OutputManager()

        # 添加输出通道
        if self.config.enable_console:
            console = ConsoleChannel(colored=self.config.console_colored)
            self.output_manager.add_channel(console)

        if self.config.enable_file_log:
            log_file = self.config.log_dir / f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            file_channel = FileChannel(log_file)
            self.output_manager.add_channel(file_channel)

        if self.config.enable_html:
            html_file = Path("game_output.html")
            html_channel = HTMLChannel(
                html_file,
                title=self.config.game_name,
                auto_refresh=self.config.html_refresh_interval,
            )
            self.output_manager.add_channel(html_channel)

        # 设置输出过滤器（开发模式显示调试信息）
        if self.config.game_mode != GameMode.DEV:
            console = self.output_manager.get_channel("console")
            if console:
                console.add_filter(lambda msg: msg.type != MessageType.DEBUG)

        logger.info("输出管理器初始化完成")

    async def _init_command_processor(self) -> None:
        """初始化命令处理器"""
        self.command_processor = CommandProcessor(self.state_manager, self.output_manager)

        # 添加中间件
        if self.config.enable_command_log:
            self.command_processor.add_middleware(LoggingMiddleware())

        if self.config.enable_validation:
            self.command_processor.add_middleware(ValidationMiddleware())

        if self.config.enable_cooldown:
            self.command_processor.add_middleware(CooldownMiddleware())

        if self.config.enable_rate_limit:
            self.command_processor.add_middleware(
                RateLimitMiddleware(
                    max_commands=self.config.rate_limit_max, window=self.config.rate_limit_window
                )
            )

        # 注册命令处理器
        self._register_command_handlers()

        # 设置命令别名
        self._setup_command_aliases()

        logger.info("命令处理器初始化完成")

    async def _init_world(self) -> None:
        """初始化游戏世界"""
        # TODO: 实际的世界初始化
        self.world = World()

        # 创建初始位置
        starting_location = Location(
            id="qingyun_main", name="青云山主峰", description="青云门的主峰，云雾缭绕，仙气飘渺。"
        )
        self.world.add_location(starting_location)

        logger.info("游戏世界初始化完成")

    def _register_command_handlers(self) -> None:
        """注册命令处理器"""
        handlers = [
            CombatCommandHandler(),
            InteractionCommandHandler(),
            SystemCommandHandler(),
            CultivationCommandHandler(),
            MovementHandler(),
            InfoHandler(),
        ]

        for handler in handlers:
            self.command_processor.register_handler(handler)

        # 开发模式额外命令
        if self.config.game_mode == GameMode.DEV:
            # TODO: 注册开发命令处理器
            pass

    def _setup_command_aliases(self) -> None:
        """设置命令别名"""
        aliases = {
            # 战斗
            "杀": "攻击",
            "打": "攻击",
            "k": "攻击",
            "a": "攻击",
            "逃": "逃跑",
            "跑": "逃跑",
            "f": "逃跑",
            # 移动
            "走": "去",
            "g": "去",
            "l": "探索",
            # 交互
            "说": "和",
            "t": "和",
            "买": "交易",
            "捡": "拾取",
            "拿": "拾取",
            # 修炼
            "练": "修炼",
            "c": "修炼",
            "学": "学习",
            # 系统
            "s": "保存",
            "存": "保存",
            "读": "加载",
            "退": "退出",
            "q": "退出",
            "?": "帮助",
            "h": "帮助",
            # 信息
            "i": "背包",
            "包": "背包",
            "st": "状态",
            "属性": "状态",
            "m": "地图",
        }

        for alias, command in aliases.items():
            self.command_processor.add_alias(alias, command)

    def _setup_state_listeners(self) -> None:
        """设置状态监听器"""
        # 监听重要状态变化
        self.state_manager.add_listener("player_death", self._on_player_death)

        self.state_manager.add_listener("level_up", self._on_level_up)

        self.state_manager.add_listener("achievement_unlocked", self._on_achievement_unlocked)

    def _setup_module_connections(self) -> None:
        """设置模块间连接"""
        # 命令处理器的系统处理器需要访问协调器
        system_handler = self.command_processor.handler_registry.get("system_commands")
        if system_handler:
            # TODO: 设置退出命令的回调
            pass

    async def _run_startup_hooks(self) -> None:
        """运行启动钩子"""
        for hook in self._startup_hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(self)
                else:
                    hook(self)
            except Exception as e:
                logger.error(f"启动钩子执行失败: {e}")

    async def _run_shutdown_hooks(self) -> None:
        """运行关闭钩子"""
        for hook in self._shutdown_hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(self)
                else:
                    hook(self)
            except Exception as e:
                logger.error(f"关闭钩子执行失败: {e}")

    # === 游戏运行 ===

    async def run(self) -> None:
        """运行游戏主循环"""
        if self.status != GameStatus.READY:
            raise RuntimeError("游戏未初始化或状态异常")

        self.running = True
        self.status = GameStatus.RUNNING

        # 显示欢迎信息
        self._show_welcome()

        # 启动自动保存
        if self.config.auto_save_enabled:
            self._auto_save_task = asyncio.create_task(self._auto_save_loop())

        try:
            # 主循环
            while self.running and not self._shutdown_requested:
                try:
                    # 暂停检查
                    if self.paused:
                        await asyncio.sleep(0.1)
                        continue

                    # 获取用户输入
                    user_input = await self._get_user_input()

                    if user_input is None:  # EOF或中断
                        break

                    # 处理输入
                    await self._process_input(user_input)

                except KeyboardInterrupt:
                    self.output_manager.warning("\n检测到中断信号")
                    break

                except Exception as e:
                    self._handle_error(e)

        finally:
            await self.shutdown()

    def run_sync(self) -> None:
        """同步运行游戏（便捷方法）"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # 初始化
            loop.run_until_complete(self.initialize())

            # 运行主循环
            loop.run_until_complete(self.run())

        finally:
            loop.close()

    async def _get_user_input(self) -> Optional[str]:
        """获取用户输入（异步）"""
        # 在实际实现中，这里可以是异步的输入
        # 现在使用同步输入的包装
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, input, "> ")

    async def _process_input(self, user_input: str) -> None:
        """处理用户输入"""
        if not user_input.strip():
            return

        # 运行前置钩子
        for hook in self._pre_command_hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(self, user_input)
                else:
                    hook(self, user_input)
            except Exception as e:
                logger.error(f"前置命令钩子失败: {e}")

        # 处理命令
        result = await self.command_processor.process_command_async(user_input)

        # 检查特殊结果
        if result.data.get("should_quit"):
            self._shutdown_requested = True

        if result.data.get("redirect"):
            # 处理命令重定向
            await self._process_input(result.data["redirect"])

        # 运行后置钩子
        for hook in self._post_command_hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(self, user_input, result)
                else:
                    hook(self, user_input, result)
            except Exception as e:
                logger.error(f"后置命令钩子失败: {e}")

    def _handle_error(self, error: Exception) -> None:
        """处理错误"""
        error_msg = f"游戏错误: {str(error)}"
        logger.error(error_msg, exc_info=True)

        self.output_manager.error(error_msg)

        if self.config.show_traceback:
            self.output_manager.debug(traceback.format_exc())

    # === 游戏控制 ===

    def pause(self) -> None:
        """暂停游戏"""
        if self.status == GameStatus.RUNNING:
            self.paused = True
            self.status = GameStatus.PAUSED
            self.output_manager.system("游戏已暂停")

    def resume(self) -> None:
        """恢复游戏"""
        if self.status == GameStatus.PAUSED:
            self.paused = False
            self.status = GameStatus.RUNNING
            self.output_manager.system("游戏已恢复")

    async def shutdown(self) -> None:
        """关闭游戏"""
        if self.status == GameStatus.SHUTTING_DOWN:
            return

        self.status = GameStatus.SHUTTING_DOWN
        self.running = False

        self.output_manager.system("正在关闭游戏...")

        # 取消自动保存任务
        if self._auto_save_task:
            self._auto_save_task.cancel()
            try:
                await self._auto_save_task
            except asyncio.CancelledError:
                pass

        # 保存游戏
        if self.state_manager and self.state_manager.has_unsaved_changes():
            await self.save_game("autosave_exit")

        # 运行关闭钩子
        await self._run_shutdown_hooks()

        # 刷新输出
        if self.output_manager:
            self.output_manager.flush_all()

        self.output_manager.system("游戏已关闭，欢迎下次再来！")
        logger.info("游戏正常关闭")

    # === 游戏功能 ===

    async def new_game(self, player_name: str, **kwargs) -> None:
        """开始新游戏"""
        self.output_manager.system("创建新游戏...")

        # 创建玩家角色
        player = Character(name=player_name, character_type=CharacterType.PLAYER)

        # 设置初始属性
        for key, value in kwargs.items():
            if hasattr(player.attributes, key):
                setattr(player.attributes, key, value)

        # 设置到状态管理器
        self.state_manager.set_player(player)

        # 设置初始位置
        starting_location = "qingyun_main"
        self.state_manager.set_location(starting_location)

        # 初始化游戏数据
        self._init_game_data()

        # 显示开场
        self._show_intro(player_name)

        self.output_manager.success("新游戏创建成功！")

    async def save_game(self, save_name: Optional[str] = None) -> bool:
        """保存游戏"""
        if self.status == GameStatus.SAVING:
            self.output_manager.warning("正在保存中，请稍候...")
            return False

        original_status = self.status
        self.status = GameStatus.SAVING

        try:
            # 生成存档名
            if not save_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_name = f"save_{timestamp}"

            # 创建存档数据
            save_data = self.state_manager.create_save_data()

            # 添加额外信息
            save_data["orchestrator"] = {
                "version": self.config.version,
                "game_mode": self.config.game_mode.value,
                "save_time": datetime.now().isoformat(),
            }

            # 保存到文件
            save_path = self.config.save_dir / f"{save_name}.json"
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            self._last_save_time = datetime.now()
            self.output_manager.success(f"游戏已保存: {save_name}")

            return True

        except Exception as e:
            self.output_manager.error(f"保存失败: {str(e)}")
            logger.error(f"保存游戏失败: {e}", exc_info=True)
            return False

        finally:
            self.status = original_status

    async def load_game(self, save_name: str) -> bool:
        """加载游戏"""
        if self.status == GameStatus.LOADING:
            self.output_manager.warning("正在加载中，请稍候...")
            return False

        original_status = self.status
        self.status = GameStatus.LOADING

        try:
            # 加载存档文件
            save_path = self.config.save_dir / f"{save_name}.json"

            if not save_path.exists():
                self.output_manager.error(f"存档不存在: {save_name}")
                return False

            with open(save_path, "r", encoding="utf-8") as f:
                save_data = json.load(f)

            # 检查版本兼容性
            save_version = save_data.get("orchestrator", {}).get("version", "0.0.0")
            if not self._check_save_compatibility(save_version):
                self.output_manager.warning(f"存档版本({save_version})可能不兼容")

            # 加载游戏状态
            self.state_manager.load_save_data(save_data)

            # 恢复游戏世界
            # TODO: 恢复世界状态

            self.output_manager.success(f"游戏已加载: {save_name}")

            # 显示当前状态
            self.command_processor.process_command("状态")

            return True

        except Exception as e:
            self.output_manager.error(f"加载失败: {str(e)}")
            logger.error(f"加载游戏失败: {e}", exc_info=True)
            return False

        finally:
            self.status = original_status

    async def _auto_save_loop(self) -> None:
        """自动保存循环"""
        while self.running:
            try:
                await asyncio.sleep(self.config.auto_save_interval)

                if self.running and not self.paused:
                    # 检查是否有未保存的更改
                    if self.state_manager.has_unsaved_changes():
                        await self.save_game("autosave")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"自动保存失败: {e}")

    def _check_save_compatibility(self, save_version: str) -> bool:
        """检查存档兼容性"""
        # 简单的版本比较
        current_parts = self.config.version.split(".")
        save_parts = save_version.split(".")

        # 主版本号必须相同
        return current_parts[0] == save_parts[0]

    def _init_game_data(self) -> None:
        """初始化游戏数据"""
        # 设置初始标记
        self.state_manager.set_flag("game_started", True)
        self.state_manager.set_flag("tutorial_completed", False)

        # 初始化统计
        self.state_manager.state.statistics["game_start_time"] = datetime.now().isoformat()

    def _show_welcome(self) -> None:
        """显示欢迎信息"""
        self.output_manager.system("=" * 60)
        self.output_manager.system(f"欢迎来到 {self.config.game_name} v{self.config.version}")
        self.output_manager.system("=" * 60)
        self.output_manager.info("输入 '帮助' 查看可用命令")
        self.output_manager.info("输入 '新游戏' 开始游戏")
        self.output_manager.info("输入 '加载' 继续之前的游戏")
        self.output_manager.system("=" * 60)

    def _show_intro(self, player_name: str) -> None:
        """显示游戏开场"""
        intro_text = f"""
天地初开，混沌始分。
修仙之路，艰难而漫长。

{player_name}，你是一个刚刚踏入修仙之路的凡人。
在这个充满机遇与危险的世界中，
你将经历无数的磨难，追求那虚无缥缈的长生之道。

你的修仙之旅，从青云山开始...
"""

        self.output_manager.narrative(intro_text)

    # === 事件处理 ===

    def _on_player_death(self, data: Dict[str, Any]) -> None:
        """处理玩家死亡"""
        self.output_manager.error("你已经死亡！")

        # 显示死亡信息
        cause = data.get("cause", "未知原因")
        self.output_manager.narrative(f"死因: {cause}")

        # 显示游戏统计
        stats = self.state_manager.state.statistics
        play_time = stats.get("play_time", 0)
        self.output_manager.info(f"游戏时长: {play_time:.1f} 小时")

        # 选项
        self.output_manager.menu(["读取存档", "重新开始", "退出游戏"], "请选择")

    def _on_level_up(self, data: Dict[str, Any]) -> None:
        """处理升级"""
        old_level = data.get("old_level", 0)
        new_level = data.get("new_level", 0)

        self.output_manager.achievement(f"恭喜！你从 {old_level} 级升到了 {new_level} 级！")

        # 显示属性提升
        self.output_manager.success("属性提升：")
        self.output_manager.info("生命上限 +10")
        self.output_manager.info("法力上限 +5")
        self.output_manager.info("获得 1 个技能点")

    def _on_achievement_unlocked(self, data: Dict[str, Any]) -> None:
        """处理成就解锁"""
        achievement_id = data.get("achievement")

        # 成就描述映射
        achievement_map = {
            "first_kill": "初战告捷 - 第一次击败敌人",
            "first_cultivation": "踏入仙途 - 第一次修炼",
            "explorer_10": "初级探索者 - 探索10个区域",
            "level_10": "小有所成 - 达到10级",
            "money_1000": "小财主 - 拥有1000灵石",
        }

        desc = achievement_map.get(achievement_id, achievement_id)
        self.output_manager.achievement(f"🏆 成就解锁: {desc}")

    # === 钩子管理 ===

    def add_startup_hook(self, hook: Callable) -> None:
        """添加启动钩子"""
        self._startup_hooks.append(hook)

    def add_shutdown_hook(self, hook: Callable) -> None:
        """添加关闭钩子"""
        self._shutdown_hooks.append(hook)

    def add_pre_command_hook(self, hook: Callable) -> None:
        """添加命令前置钩子"""
        self._pre_command_hooks.append(hook)

    def add_post_command_hook(self, hook: Callable) -> None:
        """添加命令后置钩子"""
        self._post_command_hooks.append(hook)

    # === 辅助方法 ===

    def get_player(self) -> Optional[Character]:
        """获取玩家角色"""
        return self.state_manager.get_player() if self.state_manager else None

    def get_location(self) -> Optional[str]:
        """获取当前位置"""
        return self.state_manager.get_location() if self.state_manager else None

    def get_game_time(self) -> float:
        """获取游戏时长（小时）"""
        return self.state_manager.get_play_time() if self.state_manager else 0.0


# 便捷函数
def create_game(config: Optional[GameConfig] = None) -> GameOrchestrator:
    """创建游戏实例"""
    return GameOrchestrator(config)


def run_game(config: Optional[GameConfig] = None) -> None:
    """运行游戏（同步）"""
    game = create_game(config)
    game.run_sync()


async def run_game_async(config: Optional[GameConfig] = None) -> None:
    """运行游戏（异步）"""
    game = create_game(config)
    await game.initialize()
    await game.run()


# 导出主要类和函数
__all__ = [
    "GameOrchestrator",
    "GameConfig",
    "GameMode",
    "GameStatus",
    "create_game",
    "run_game",
    "run_game_async",
]
