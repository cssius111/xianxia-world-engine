"""
基础设施测试脚本
验证服务容器和事件系统是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio

from xwe.core.events import Event, EventDispatcher, EventPriority
from xwe.core.services import IGameSystem, ServiceContainer


class TestService(IGameSystem):
    """测试服务"""

    def __init__(self, name: str = "TestService"):
        self._name = name
        self.initialized = False

    @property
    def name(self) -> str:
        return self._name

    def initialize(self) -> None:
        self.initialized = True
        print(f"{self.name} initialized")

    def shutdown(self) -> None:
        self.initialized = False
        print(f"{self.name} shutdown")

    def do_something(self) -> str:
        return f"{self.name} is working!"


class DependentService(IGameSystem):
    """依赖其他服务的测试服务"""

    def __init__(self, test_service: TestService):
        self.test_service = test_service
        self._name = "DependentService"

    @property
    def name(self) -> str:
        return self._name

    def initialize(self) -> None:
        print(f"{self.name} initialized with dependency: {self.test_service.name}")

    def shutdown(self) -> None:
        print(f"{self.name} shutdown")

    def use_dependency(self) -> str:
        return f"Using dependency: {self.test_service.do_something()}"


def test_service_container():
    """测试服务容器"""
    print("=== 测试服务容器 ===")

    # 创建容器
    container = ServiceContainer()

    # 注册服务
    container.register("test_service", lambda c: TestService("Service1"))
    container.register("dependent_service", lambda c: DependentService(c.get("test_service")))

    # 测试别名
    container.alias("test", "test_service")

    # 获取服务
    service1 = container.get("test_service")
    service2 = container.get("test")  # 通过别名获取
    dependent = container.get("dependent_service")

    # 验证单例
    assert service1 is service2, "单例服务应该返回相同实例"

    # 测试服务功能
    print(f"Service1: {service1.do_something()}")
    print(f"Dependent: {dependent.use_dependency()}")

    # 测试服务列表
    print("\n已注册的服务:")
    for name, status in container.get_all_services().items():
        print(f"  {name}: {status}")

    print("\n✅ 服务容器测试通过")


def test_event_dispatcher():
    """测试事件调度器"""
    print("\n=== 测试事件调度器 ===")

    # 创建调度器
    dispatcher = EventDispatcher()

    # 记录事件
    received_events = []

    # 注册事件处理器
    def on_test_event(event: Event):
        received_events.append(event)
        print(f"Received event: {event.name} with data: {event.data}")

    # 高优先级处理器
    def high_priority_handler(event: Event):
        print(f"[HIGH PRIORITY] Processing: {event.name}")

    # 一次性处理器
    @dispatcher.once("test.once")
    def once_handler(event: Event):
        print(f"[ONCE] This will only run once: {event.name}")

    # 注册处理器
    dispatcher.on("test.event", on_test_event)
    dispatcher.on("test.event", high_priority_handler, priority=EventPriority.HIGH)

    # 发布事件
    dispatcher.emit("test.event", {"value": 42})
    dispatcher.emit("test.once", {"message": "Hello"})
    dispatcher.emit("test.once", {"message": "World"})  # 这个不会被处理

    # 验证
    assert len(received_events) == 1
    assert received_events[0].data["value"] == 42

    # 测试通配符
    all_events = []
    dispatcher.on("*", lambda e: all_events.append(e))
    dispatcher.emit("any.event", {"test": True})

    print(f"\n接收到 {len(all_events)} 个通配符事件")

    print("\n✅ 事件调度器测试通过")


async def test_async_events():
    """测试异步事件"""
    print("\n=== 测试异步事件 ===")

    dispatcher = EventDispatcher()
    results = []

    # 异步处理器
    async def async_handler(event: Event):
        await asyncio.sleep(0.1)  # 模拟异步操作
        results.append(f"Async: {event.name}")
        print(f"[ASYNC] Processed: {event.name}")

    # 同步处理器
    def sync_handler(event: Event):
        results.append(f"Sync: {event.name}")
        print(f"[SYNC] Processed: {event.name}")

    # 注册处理器
    dispatcher.on("async.test", async_handler)
    dispatcher.on("async.test", sync_handler)

    # 发布异步事件
    await dispatcher.emit_async("async.test", {"async": True})

    # 测试延迟事件
    print("\n测试延迟事件...")
    task = dispatcher.emit_delayed("delayed.event", 0.2, {"delayed": True})
    print("等待延迟事件...")
    await task

    print(f"\n处理结果: {results}")
    print("✅ 异步事件测试通过")


def main():
    """运行所有测试"""
    print("🧪 开始测试基础设施\n")

    try:
        # 测试服务容器
        test_service_container()

        # 测试事件调度器
        test_event_dispatcher()

        # 测试异步事件
        asyncio.run(test_async_events())

        print("\n🎉 所有测试通过！基础设施工作正常。")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
