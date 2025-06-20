"""
服务层测试脚本
测试新创建的服务层组件
"""

import time

from xwe.events import GameEvent, PlayerEvent
from xwe.services import (
    ICommandEngine,
    IEventDispatcher,
    IGameService,
    ILogService,
    IPlayerService,
    ServiceContainer,
    ServiceLifetime,
    register_services,
)
from xwe.services.command_engine import CommandContext, CommandHandler, CommandResult

# 添加项目根目录到Python路径


def test_service_container():
    """测试服务容器"""
    print("\n=== 测试服务容器 ===")

    # 创建容器
    container = ServiceContainer()

    # 注册所有服务
    register_services(container)

    # 解析服务
    game_service = container.resolve(IGameService)
    player_service = container.resolve(IPlayerService)

    print(f"✓ 成功解析 GameService: {game_service}")
    print(f"✓ 成功解析 PlayerService: {player_service}")

    # 测试单例
    game_service2 = container.resolve(IGameService)
    assert game_service is game_service2, "服务应该是单例"
    print("✓ 单例模式工作正常")


def test_command_engine():
    """测试命令引擎"""
    print("\n=== 测试命令引擎 ===")

    container = ServiceContainer()
    register_services(container)

    command_engine = container.resolve(ICommandEngine)

    # 注册自定义命令处理器
    class TestCommandHandler(CommandHandler):
        def __init__(self):
            super().__init__(
                commands=["测试"], aliases=["test"], description="测试命令", usage="测试 [参数]"
            )

        def _do_handle(self, context: CommandContext) -> CommandResult:
            return CommandResult(success=True, output=f"测试成功！参数: {context.args}")

    test_handler = TestCommandHandler()
    command_engine.register_handler(test_handler)

    # 测试命令执行
    result = command_engine.process_command("测试 参数1 参数2")
    print(f"✓ 命令执行结果: {result.output}")

    # 测试自然语言
    result = command_engine.process_command("我想看看帮助")
    print(f"✓ 自然语言处理: {result.output[:50]}...")

    # 测试命令建议
    suggestions = command_engine.get_suggestions("帮")
    print(f"✓ 命令建议: {suggestions}")


def test_event_dispatcher():
    """测试事件分发器"""
    print("\n=== 测试事件分发器 ===")

    container = ServiceContainer()
    register_services(container)

    event_dispatcher = container.resolve(IEventDispatcher)

    # 记录接收到的事件
    received_events = []

    def event_handler(event):
        received_events.append(event)
        print(f"  收到事件: {event.type}")

    # 订阅事件
    event_dispatcher.subscribe("test_event", event_handler)
    event_dispatcher.subscribe("player_level_up", event_handler)

    # 分发事件
    event_dispatcher.dispatch_game_event("test_event", {"message": "Hello"})
    event_dispatcher.dispatch_player_event(
        "player_level_up", {"new_level": 10}, player_id="test_player"
    )

    # 等待异步处理
    time.sleep(0.1)

    print(f"✓ 成功接收 {len(received_events)} 个事件")

    # 获取事件历史
    history = event_dispatcher.get_event_history(limit=10)
    print(f"✓ 事件历史记录: {len(history)} 条")

    # 获取统计信息
    stats = event_dispatcher.get_statistics()
    print(f"✓ 事件统计: 总数={stats.total_events}, 每分钟={stats.events_per_minute:.2f}")


def test_log_service():
    """测试日志服务"""
    print("\n=== 测试日志服务 ===")

    container = ServiceContainer()
    register_services(container)

    log_service = container.resolve(ILogService)

    # 记录各种日志
    log_service.log_info("游戏启动", category="system")
    log_service.log_debug("调试信息", category="debug")
    log_service.log_warning("警告信息", category="warning")
    log_service.log_error("错误信息", category="error")
    log_service.log_combat("战斗开始", player_id="test_player")
    log_service.log_achievement("获得成就：初心者", player_id="test_player")

    # 获取最近日志
    recent_logs = log_service.get_recent_logs(limit=10)
    print(f"✓ 最近日志数量: {len(recent_logs)}")

    for log in recent_logs[:3]:
        print(f"  [{log.level.value}] {log.message}")

    # 获取统计信息
    stats = log_service.get_log_statistics()
    print(f"✓ 日志统计: 总数={stats['total_logs']}")
    print(f"  按级别: {stats['logs_by_level']}")
    print(f"  按类别: {stats['logs_by_category']}")


def test_integration():
    """测试服务集成"""
    print("\n=== 测试服务集成 ===")

    container = ServiceContainer()
    register_services(container)

    # 获取所有服务
    game_service = container.resolve(IGameService)
    player_service = container.resolve(IPlayerService)
    command_engine = container.resolve(ICommandEngine)
    event_dispatcher = container.resolve(IEventDispatcher)
    log_service = container.resolve(ILogService)

    # 初始化游戏
    success = game_service.initialize_game("测试玩家")
    print(f"✓ 游戏初始化: {'成功' if success else '失败'}")

    # 处理命令
    result = game_service.process_command("状态")
    print(f"✓ 执行命令'状态': {result.output[:100]}...")

    # 检查日志
    logs = log_service.get_recent_logs(5)
    print(f"✓ 生成了 {len(logs)} 条日志")

    # 检查事件
    events = event_dispatcher.get_event_history(limit=5)
    print(f"✓ 记录了 {len(events)} 个事件")

    # 获取游戏状态
    state = game_service.get_game_state()
    print(f"✓ 游戏状态: 已初始化={state.initialized}, 位置={state.current_location}")


def main():
    """主测试函数"""
    print("=" * 50)
    print("服务层测试")
    print("=" * 50)

    try:
        test_service_container()
        test_command_engine()
        test_event_dispatcher()
        test_log_service()
        test_integration()

        print("\n" + "=" * 50)
        print("✅ 所有测试通过！")
        print("=" * 50)

    except Exception as e:
        print("\n" + "=" * 50)
        print(f"❌ 测试失败: {e}")
        print("=" * 50)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
