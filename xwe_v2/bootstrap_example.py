"""
游戏引导程序示例
展示如何使用新的架构启动游戏
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging

from xwe_v2.core.events import Event, EventDispatcher
from xwe_v2.core.services import ServiceContainer

# 配置日志
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_game_container() -> ServiceContainer:
    """
    创建并配置游戏服务容器

    这是游戏启动的核心函数，所有服务都在这里注册
    """
    logger.info("创建游戏服务容器...")
    container = ServiceContainer()

    # ========== 注册核心服务 ==========

    # 事件调度器（单例）
    container.register("event_dispatcher", lambda c: EventDispatcher(), singleton=True)

    # TODO: 注册其他核心服务
    # container.register('state_manager',
    #                   lambda c: GameStateManager(),
    #                   singleton=True)

    # container.register('output_manager',
    #                   lambda c: OutputManager(),
    #                   singleton=True)

    # container.register('command_processor',
    #                   lambda c: CommandProcessor(c.get('command_parser')),
    #                   singleton=True)

    # ========== 注册系统服务 ==========

    # TODO: 注册游戏系统
    # container.register('combat_manager',
    #                   lambda c: CombatManager(c.get('event_dispatcher')),
    #                   singleton=True)

    # container.register('time_manager',
    #                   lambda c: TimeManager(c.get('event_dispatcher')),
    #                   singleton=True)

    # container.register('save_manager',
    #                   lambda c: SaveLoadManager(Path('saves')),
    #                   singleton=True)

    # container.register('data_repository',
    #                   lambda c: DataRepository(Path('xwe/data')),
    #                   singleton=True)

    # ========== 注册主协调器 ==========

    # TODO: 注册游戏协调器
    # container.register('game_orchestrator',
    #                   lambda c: GameOrchestrator(c),
    #                   singleton=True)

    logger.info("服务容器配置完成")
    return container


def setup_event_handlers(container: ServiceContainer):
    """
    设置全局事件处理器
    """
    logger.info("设置事件处理器...")

    dispatcher = container.get("event_dispatcher")

    # 游戏生命周期事件
    @dispatcher.on("game.initializing")
    def on_game_initializing(event: Event):
        logger.info("游戏正在初始化...")

    @dispatcher.on("game.initialized")
    def on_game_initialized(event: Event):
        logger.info("游戏初始化完成！")

    @dispatcher.on("game.shutting_down")
    def on_game_shutting_down(event: Event):
        logger.info("游戏正在关闭...")

    # 系统事件
    @dispatcher.on("system.error")
    def on_system_error(event: Event):
        logger.error(f"系统错误: {event.data.get('error', 'Unknown error')}")

    # 调试事件（监听所有事件）
    if logger.level <= logging.DEBUG:

        @dispatcher.on("*")
        def on_any_event(event: Event):
            logger.debug(f"Event: {event.name} | Data: {event.data}")


def main():
    """
    主函数 - 游戏启动入口
    """
    print("=== 修仙世界引擎 - 新架构示例 ===\n")

    try:
        # 创建服务容器
        container = create_game_container()

        # 设置事件处理器
        setup_event_handlers(container)

        # 获取事件调度器
        dispatcher = container.get("event_dispatcher")

        # 发布初始化事件
        dispatcher.emit("game.initializing")

        # TODO: 初始化游戏
        # orchestrator = container.get('game_orchestrator')
        # orchestrator.initialize()

        # 模拟一些游戏事件
        print("\n模拟游戏事件:")
        dispatcher.emit("player.login", {"player_id": "player_001"})
        dispatcher.emit("game.started", {"mode": "adventure"})

        # 发布初始化完成事件
        dispatcher.emit("game.initialized")

        print("\n当前已注册的服务:")
        for name, status in container.get_all_services().items():
            print(f"  - {name}: {status}")

        print("\n🎮 游戏已准备就绪（演示模式）")
        print("下一步：实现具体的游戏系统模块")

    except Exception as e:
        logger.error(f"启动失败: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
