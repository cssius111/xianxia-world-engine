"""
服务容器 - 依赖注入实现
用于管理游戏中所有服务的创建和依赖关系
"""

import inspect
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Type, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ServiceNotFoundError(Exception):
    """服务未找到异常"""

    pass


class CircularDependencyError(Exception):
    """循环依赖异常"""

    pass


class ServiceContainer:
    """
    服务容器 - 依赖注入容器

    特性：
    - 支持单例和工厂模式
    - 自动依赖注入
    - 循环依赖检测
    - 服务别名
    """

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._aliases: Dict[str, str] = {}
        self._resolving: set = set()  # 用于检测循环依赖

    def register(self, name: str, factory: Callable, singleton: bool = True) -> "ServiceContainer":
        """
        注册服务

        Args:
            name: 服务名称
            factory: 服务工厂函数
            singleton: 是否为单例

        Returns:
            self，支持链式调用
        """
        self._factories[name] = factory
        if not singleton:
            self._services[name] = None  # 标记为非单例

        logger.debug(f"Registered service: {name} (singleton={singleton})")
        return self

    def register_instance(self, name: str, instance: Any) -> "ServiceContainer":
        """
        注册已创建的实例

        Args:
            name: 服务名称
            instance: 服务实例

        Returns:
            self，支持链式调用
        """
        self._singletons[name] = instance
        logger.debug(f"Registered instance: {name}")
        return self

    def alias(self, alias: str, service: str) -> "ServiceContainer":
        """
        创建服务别名

        Args:
            alias: 别名
            service: 实际服务名

        Returns:
            self，支持链式调用
        """
        self._aliases[alias] = service
        logger.debug(f"Created alias: {alias} -> {service}")
        return self

    def get(self, name: str) -> Any:
        """
        获取服务实例

        Args:
            name: 服务名或别名

        Returns:
            服务实例

        Raises:
            ServiceNotFoundError: 服务未注册
            CircularDependencyError: 检测到循环依赖
        """
        # 解析别名
        actual_name = self._aliases.get(name, name)

        # 检测循环依赖
        if actual_name in self._resolving:
            raise CircularDependencyError(
                f"Circular dependency detected for service: {actual_name}"
            )

        # 返回已存在的单例
        if actual_name in self._singletons:
            return self._singletons[actual_name]

        # 创建新实例
        if actual_name in self._factories:
            self._resolving.add(actual_name)
            try:
                factory = self._factories[actual_name]

                # 注入依赖
                instance = self._create_with_dependencies(factory)

                # 如果是单例，缓存起来
                if actual_name not in self._services:
                    self._singletons[actual_name] = instance

                return instance
            finally:
                self._resolving.remove(actual_name)

        raise ServiceNotFoundError(f"Service '{name}' not registered")

    def _create_with_dependencies(self, factory: Callable) -> Any:
        """
        创建实例并注入依赖

        Args:
            factory: 工厂函数

        Returns:
            创建的实例
        """
        # 获取构造函数参数
        sig = inspect.signature(factory)
        kwargs = {}

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            # 特殊处理：如果参数名是 'container' 或简称 'c'，则注入容器本身
            if param_name in ("container", "c"):

                kwargs[param_name] = self
                continue

            # 尝试从容器获取依赖
            if param.annotation != param.empty:
                # 使用类型注解作为服务名
                if hasattr(param.annotation, "__name__"):
                    service_name = param.annotation.__name__.lower()
                    if self.has(service_name):
                        kwargs[param_name] = self.get(service_name)
                        continue

            # 使用参数名作为服务名
            if self.has(param_name):
                kwargs[param_name] = self.get(param_name)
            elif param.default != param.empty:
                # 使用默认值
                kwargs[param_name] = param.default

        return factory(**kwargs)

    def has(self, name: str) -> bool:
        """
        检查服务是否已注册

        Args:
            name: 服务名或别名

        Returns:
            是否已注册
        """
        actual_name = self._aliases.get(name, name)
        return actual_name in self._factories or actual_name in self._singletons

    def reset(self) -> None:
        """重置容器，清除所有服务"""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._aliases.clear()
        self._resolving.clear()
        logger.info("Service container reset")

    def get_all_services(self) -> Dict[str, str]:
        """
        获取所有已注册服务的信息

        Returns:
            服务名到状态的映射
        """
        services = {}

        # 添加工厂服务
        for name in self._factories:
            if name in self._singletons:
                services[name] = "singleton (created)"
            elif name in self._services:
                services[name] = "factory"
            else:
                services[name] = "singleton (not created)"

        # 添加直接注册的实例
        for name in self._singletons:
            if name not in services:
                services[name] = "instance"

        # 添加别名
        for alias, actual in self._aliases.items():
            services[f"{alias} (alias)"] = f"-> {actual}"

        return services
