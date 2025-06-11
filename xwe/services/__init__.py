"""
服务层基础架构
提供服务的基类、接口和生命周期管理
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Type, Optional, TypeVar, Generic
import logging

logger = logging.getLogger(__name__)


class ServiceLifetime(Enum):
    """服务生命周期"""
    TRANSIENT = "transient"      # 每次请求创建新实例
    SCOPED = "scoped"            # 每个作用域一个实例
    SINGLETON = "singleton"      # 全局单例


class IService(ABC):
    """服务基础接口"""
    
    @abstractmethod
    def initialize(self) -> None:
        """初始化服务"""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """关闭服务"""
        pass


T = TypeVar('T')


class ServiceBase(IService, Generic[T]):
    """服务基类"""
    
    def __init__(self, container: 'ServiceContainer'):
        self.container = container
        self.logger = logger.getChild(self.__class__.__name__)
        self._initialized = False
        
    def initialize(self) -> None:
        """初始化服务"""
        if self._initialized:
            return
            
        self.logger.info(f"Initializing {self.__class__.__name__}")
        self._do_initialize()
        self._initialized = True
        
    def shutdown(self) -> None:
        """关闭服务"""
        if not self._initialized:
            return
            
        self.logger.info(f"Shutting down {self.__class__.__name__}")
        self._do_shutdown()
        self._initialized = False
        
    def _do_initialize(self) -> None:
        """子类实现的初始化逻辑"""
        pass
        
    def _do_shutdown(self) -> None:
        """子类实现的关闭逻辑"""
        pass
        
    def get_service(self, service_type: Type[T]) -> T:
        """获取其他服务"""
        return self.container.resolve(service_type)


class ServiceDescriptor:
    """服务描述符"""
    
    def __init__(self, 
                 service_type: Type,
                 implementation: Type,
                 lifetime: ServiceLifetime,
                 factory: Optional[callable] = None):
        self.service_type = service_type
        self.implementation = implementation
        self.lifetime = lifetime
        self.factory = factory
        
    def __repr__(self):
        return (f"ServiceDescriptor("
                f"type={self.service_type.__name__}, "
                f"impl={self.implementation.__name__}, "
                f"lifetime={self.lifetime.value})")


class ServiceNotFoundError(Exception):
    """服务未找到异常"""
    pass


class ServiceContainer:
    """服务容器 - 依赖注入容器"""
    
    def __init__(self):
        self._descriptors: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._scoped_instances: Dict[Type, Any] = {}
        self.logger = logger.getChild('ServiceContainer')
        
    def register(self,
                 service_type: Type,
                 implementation: Type = None,
                 lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
                 factory: callable = None) -> 'ServiceContainer':
        """
        注册服务
        
        Args:
            service_type: 服务接口类型
            implementation: 实现类型（如果为None，则使用service_type）
            lifetime: 服务生命周期
            factory: 自定义工厂函数
            
        Returns:
            self，支持链式调用
        """
        if implementation is None:
            implementation = service_type
            
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation=implementation,
            lifetime=lifetime,
            factory=factory
        )
        
        self._descriptors[service_type] = descriptor
        self.logger.debug(f"Registered service: {descriptor}")
        
        return self
        
    def register_singleton(self, 
                          service_type: Type,
                          instance: Any) -> 'ServiceContainer':
        """
        注册单例实例
        
        Args:
            service_type: 服务类型
            instance: 服务实例
            
        Returns:
            self
        """
        self._singletons[service_type] = instance
        self._descriptors[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation=type(instance),
            lifetime=ServiceLifetime.SINGLETON
        )
        self.logger.debug(f"Registered singleton instance: {service_type.__name__}")
        
        return self
        
    def resolve(self, service_type: Type[T]) -> T:
        """
        解析服务
        
        Args:
            service_type: 要解析的服务类型
            
        Returns:
            服务实例
            
        Raises:
            ServiceNotFoundError: 服务未注册
        """
        # 检查是否已注册
        if service_type not in self._descriptors:
            raise ServiceNotFoundError(
                f"Service {service_type.__name__} is not registered"
            )
            
        descriptor = self._descriptors[service_type]
        
        # 根据生命周期返回实例
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            return self._resolve_singleton(descriptor)
        elif descriptor.lifetime == ServiceLifetime.SCOPED:
            return self._resolve_scoped(descriptor)
        else:  # TRANSIENT
            return self._create_instance(descriptor)
            
    def _resolve_singleton(self, descriptor: ServiceDescriptor) -> Any:
        """解析单例服务"""
        if descriptor.service_type not in self._singletons:
            instance = self._create_instance(descriptor)
            self._singletons[descriptor.service_type] = instance
            
        return self._singletons[descriptor.service_type]
        
    def _resolve_scoped(self, descriptor: ServiceDescriptor) -> Any:
        """解析作用域服务"""
        if descriptor.service_type not in self._scoped_instances:
            instance = self._create_instance(descriptor)
            self._scoped_instances[descriptor.service_type] = instance
            
        return self._scoped_instances[descriptor.service_type]
        
    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """创建服务实例"""
        if descriptor.factory:
            # 使用自定义工厂
            instance = descriptor.factory(self)
        else:
            # 使用构造函数注入
            instance = self._construct_instance(descriptor.implementation)
            
        # 如果是服务基类，初始化
        if isinstance(instance, IService):
            instance.initialize()
            
        return instance
        
    def _construct_instance(self, implementation: Type) -> Any:
        """
        通过构造函数创建实例
        自动注入依赖
        """
        # 获取构造函数参数
        import inspect
        sig = inspect.signature(implementation.__init__)
        params = sig.parameters
        
        # 准备参数
        kwargs = {}
        for param_name, param in params.items():
            if param_name == 'self':
                continue
                
            # 如果参数是container类型，注入自己
            if param.annotation == ServiceContainer or param.annotation == 'ServiceContainer':
                kwargs[param_name] = self
            # 尝试从容器解析参数类型
            elif param.annotation != param.empty:
                try:
                    kwargs[param_name] = self.resolve(param.annotation)
                except ServiceNotFoundError:
                    # 如果有默认值，跳过
                    if param.default == param.empty:
                        raise
                        
        return implementation(**kwargs)
        
    def create_scope(self) -> 'ServiceScope':
        """创建新的服务作用域"""
        return ServiceScope(self)
        
    def clear_scoped(self) -> None:
        """清理作用域实例"""
        self._scoped_instances.clear()
        
    def shutdown_all(self) -> None:
        """关闭所有服务"""
        # 先关闭作用域服务
        for service in self._scoped_instances.values():
            if isinstance(service, IService):
                service.shutdown()
                
        # 再关闭单例服务
        for service in self._singletons.values():
            if isinstance(service, IService):
                service.shutdown()
                
        self.clear_scoped()


class ServiceScope:
    """服务作用域"""
    
    def __init__(self, container: ServiceContainer):
        self.container = container
        self._original_scoped = dict(container._scoped_instances)
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 恢复原始作用域实例
        self.container._scoped_instances = self._original_scoped


# 全局服务容器实例
_global_container = ServiceContainer()


def get_service_container() -> ServiceContainer:
    """获取全局服务容器"""
    return _global_container


def register_services(container: ServiceContainer) -> None:
    """
    注册所有服务
    这个函数应该在应用启动时调用
    """
    from .game_service import GameService, IGameService
    from .player_service import PlayerService, IPlayerService
    from .combat_service import CombatService, ICombatService
    from .save_service import SaveService, ISaveService
    from .world_service import WorldService, IWorldService
    from .cultivation_service import CultivationService, ICultivationService
    from .command_engine import CommandEngine, ICommandEngine
    from .event_dispatcher import EventDispatcher, IEventDispatcher
    from .log_service import LogService, ILogService
    
    # 注册核心服务
    container.register(IGameService, GameService, ServiceLifetime.SINGLETON)
    container.register(IPlayerService, PlayerService, ServiceLifetime.SINGLETON)
    container.register(ICombatService, CombatService, ServiceLifetime.SINGLETON)
    container.register(ISaveService, SaveService, ServiceLifetime.SINGLETON)
    container.register(IWorldService, WorldService, ServiceLifetime.SINGLETON)
    container.register(ICultivationService, CultivationService, ServiceLifetime.SINGLETON)
    container.register(ICommandEngine, CommandEngine, ServiceLifetime.SINGLETON)
    container.register(IEventDispatcher, EventDispatcher, ServiceLifetime.SINGLETON)
    container.register(ILogService, LogService, ServiceLifetime.SINGLETON)
    
    logger.info("All services registered")
