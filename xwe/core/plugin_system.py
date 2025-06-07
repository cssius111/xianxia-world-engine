# xwe/core/plugin_system.py

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Type, Optional, Callable
import importlib
import importlib.util
import inspect
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class Plugin(ABC):
    """插件基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称"""
        pass
        
    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass
        
    @property
    @abstractmethod
    def dependencies(self) -> List[str]:
        """依赖的其他插件"""
        pass
        
    @abstractmethod
    async def initialize(self, engine) -> None:
        """初始化插件"""
        pass
        
    @abstractmethod
    async def shutdown(self) -> None:
        """关闭插件"""
        pass
        
    def register_commands(self) -> Dict[str, Callable]:
        """注册命令"""
        return {}
        
    def register_events(self) -> Dict[str, List[Callable]]:
        """注册事件处理器"""
        return {}
        
    def register_api_endpoints(self) -> List[Dict]:
        """注册API端点"""
        return []
        
    def get_config_schema(self) -> Dict:
        """获取配置架构"""
        return {}
        
    def on_config_change(self, config: Dict) -> None:
        """配置变更回调"""
        pass
        

class PluginError(Exception):
    """插件错误"""
    pass


class PluginManager:
    """插件管理器"""
    
    def __init__(self, engine):
        self.engine = engine
        self.plugins: Dict[str, Plugin] = {}
        self.load_order: List[str] = []
        self.plugin_configs: Dict[str, Dict] = {}
        self.plugin_paths: List[Path] = [
            Path('plugins'),  # 默认插件目录
            Path('xwe/plugins')  # 内置插件目录
        ]
        
    async def load_plugin(self, plugin_class: Type[Plugin], 
                         config: Optional[Dict] = None) -> None:
        """加载插件"""
        
        plugin = plugin_class()
        
        # 检查依赖
        for dep in plugin.dependencies:
            if dep not in self.plugins:
                raise PluginError(f"Missing dependency: {dep}")
                
        # 保存配置
        if config:
            self.plugin_configs[plugin.name] = config
            plugin.on_config_change(config)
            
        # 初始化插件
        await plugin.initialize(self.engine)
        
        # 注册命令
        commands = plugin.register_commands()
        for cmd_name, handler in commands.items():
            self._register_command(plugin.name, cmd_name, handler)
            
        # 注册事件
        events = plugin.register_events()
        for event_type, handlers in events.items():
            for handler in handlers:
                self._register_event_handler(plugin.name, event_type, handler)
                
        # 注册API
        endpoints = plugin.register_api_endpoints()
        for endpoint in endpoints:
            self._register_api_endpoint(plugin.name, endpoint)
            
        # 保存插件
        self.plugins[plugin.name] = plugin
        self.load_order.append(plugin.name)
        
        logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
        
    async def unload_plugin(self, plugin_name: str) -> None:
        """卸载插件"""
        
        if plugin_name not in self.plugins:
            return
            
        plugin = self.plugins[plugin_name]
        
        # 检查是否有其他插件依赖此插件
        for other_name, other_plugin in self.plugins.items():
            if plugin_name in other_plugin.dependencies:
                raise PluginError(
                    f"Cannot unload {plugin_name}: "
                    f"{other_name} depends on it"
                )
                
        # 关闭插件
        await plugin.shutdown()
        
        # 注销命令、事件等
        self._unregister_plugin_resources(plugin_name)
        
        # 移除插件
        del self.plugins[plugin_name]
        self.load_order.remove(plugin_name)
        
        logger.info(f"Unloaded plugin: {plugin_name}")
        
    async def reload_plugin(self, plugin_name: str) -> None:
        """重载插件"""
        
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            plugin_class = type(plugin)
            config = self.plugin_configs.get(plugin_name)
            
            # 卸载
            await self.unload_plugin(plugin_name)
            
            # 重新加载模块
            module = importlib.import_module(plugin_class.__module__)
            importlib.reload(module)
            
            # 重新获取类
            plugin_class = getattr(module, plugin_class.__name__)
            
            # 重新加载
            await self.load_plugin(plugin_class, config)
            
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """获取插件实例"""
        return self.plugins.get(plugin_name)
        
    def list_plugins(self) -> List[Dict[str, Any]]:
        """列出所有插件"""
        return [
            {
                'name': plugin.name,
                'version': plugin.version,
                'dependencies': plugin.dependencies,
                'loaded': True
            }
            for plugin in self.plugins.values()
        ]
        
    async def discover_plugins(self) -> List[Dict[str, Any]]:
        """发现可用插件"""
        discovered = []
        
        for plugin_path in self.plugin_paths:
            if not plugin_path.exists():
                continue
                
            for item in plugin_path.iterdir():
                if item.is_dir() and (item / '__init__.py').exists():
                    # 尝试加载插件信息
                    plugin_info = self._load_plugin_info(item)
                    if plugin_info:
                        plugin_info['path'] = str(item)
                        plugin_info['loaded'] = plugin_info['name'] in self.plugins
                        discovered.append(plugin_info)
                        
        return discovered
        
    def _load_plugin_info(self, plugin_path: Path) -> Optional[Dict[str, Any]]:
        """加载插件信息"""
        info_file = plugin_path / 'plugin.json'
        
        if info_file.exists():
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load plugin info from {info_file}: {e}")
                
        # 尝试从Python模块加载
        try:
            module_name = plugin_path.name
            spec = importlib.util.spec_from_file_location(
                module_name, 
                plugin_path / '__init__.py'
            )
            
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 查找Plugin子类
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, Plugin) and 
                        obj != Plugin):
                        
                        instance = obj()
                        return {
                            'name': instance.name,
                            'version': instance.version,
                            'dependencies': instance.dependencies,
                            'class_name': name,
                            'module': module_name
                        }
                        
        except Exception as e:
            logger.error(f"Failed to load plugin from {plugin_path}: {e}")
            
        return None
        
    async def load_plugin_from_path(self, plugin_path: Path, 
                                   config: Optional[Dict] = None) -> None:
        """从路径加载插件"""
        plugin_info = self._load_plugin_info(plugin_path)
        
        if not plugin_info:
            raise PluginError(f"Cannot load plugin from {plugin_path}")
            
        # 动态导入模块
        module_name = plugin_info['module']
        spec = importlib.util.spec_from_file_location(
            module_name,
            plugin_path / '__init__.py'
        )
        
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 获取插件类
            plugin_class = getattr(module, plugin_info['class_name'])
            
            # 加载插件
            await self.load_plugin(plugin_class, config)
            
    def _register_command(self, plugin_name: str, cmd_name: str, 
                         handler: Callable) -> None:
        """注册命令"""
        full_name = f"{plugin_name}:{cmd_name}"
        
        if hasattr(self.engine, 'commands'):
            self.engine.commands.register(full_name, handler)
            
    def _register_event_handler(self, plugin_name: str, event_type: str,
                               handler: Callable) -> None:
        """注册事件处理器"""
        # 包装处理器以添加插件上下文
        def wrapped_handler(event):
            event['_plugin'] = plugin_name
            return handler(event)
            
        if hasattr(self.engine, 'events'):
            self.engine.events.register(event_type, wrapped_handler)
            
    def _register_api_endpoint(self, plugin_name: str, endpoint: Dict) -> None:
        """注册API端点"""
        # 添加插件前缀
        endpoint['path'] = f"/plugins/{plugin_name}{endpoint['path']}"
        
        if hasattr(self.engine, 'api'):
            self.engine.api.register_endpoint(endpoint)
            
    def _unregister_plugin_resources(self, plugin_name: str) -> None:
        """注销插件资源"""
        # 注销命令
        if hasattr(self.engine, 'commands'):
            # 移除所有以插件名开头的命令
            commands_to_remove = [
                cmd for cmd in self.engine.commands.list_commands()
                if cmd.startswith(f"{plugin_name}:")
            ]
            
            for cmd in commands_to_remove:
                self.engine.commands.unregister(cmd)
                
        # 注销API端点
        if hasattr(self.engine, 'api'):
            # 移除插件的API端点
            self.engine.api.unregister_by_prefix(f"/plugins/{plugin_name}")
            
    def update_config(self, plugin_name: str, config: Dict) -> None:
        """更新插件配置"""
        if plugin_name not in self.plugins:
            raise PluginError(f"Plugin {plugin_name} not loaded")
            
        self.plugin_configs[plugin_name] = config
        self.plugins[plugin_name].on_config_change(config)
        
    def get_config(self, plugin_name: str) -> Optional[Dict]:
        """获取插件配置"""
        return self.plugin_configs.get(plugin_name)
        
    async def enable_all_plugins(self) -> None:
        """启用所有发现的插件"""
        discovered = await self.discover_plugins()
        
        # 按依赖关系排序
        sorted_plugins = self._topological_sort(discovered)
        
        for plugin_info in sorted_plugins:
            if not plugin_info['loaded']:
                try:
                    plugin_path = Path(plugin_info['path'])
                    await self.load_plugin_from_path(plugin_path)
                except Exception as e:
                    logger.error(f"Failed to load plugin {plugin_info['name']}: {e}")
                    
    def _topological_sort(self, plugins: List[Dict]) -> List[Dict]:
        """拓扑排序插件（处理依赖关系）"""
        # 构建依赖图
        graph = {}
        for plugin in plugins:
            graph[plugin['name']] = plugin['dependencies']
            
        # 拓扑排序
        sorted_names = []
        visited = set()
        
        def visit(name: str):
            if name in visited:
                return
                
            visited.add(name)
            
            # 访问依赖
            for dep in graph.get(name, []):
                if dep in graph:
                    visit(dep)
                    
            sorted_names.append(name)
            
        for name in graph:
            visit(name)
            
        # 按排序顺序返回插件
        name_to_plugin = {p['name']: p for p in plugins}
        return [name_to_plugin[name] for name in sorted_names if name in name_to_plugin]


# 示例插件
class ExamplePlugin(Plugin):
    """示例插件"""
    
    @property
    def name(self) -> str:
        return "example"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def dependencies(self) -> List[str]:
        return []
        
    async def initialize(self, engine) -> None:
        """初始化插件"""
        self.engine = engine
        logger.info(f"{self.name} plugin initialized")
        
    async def shutdown(self) -> None:
        """关闭插件"""
        logger.info(f"{self.name} plugin shutdown")
        
    def register_commands(self) -> Dict[str, Callable]:
        """注册命令"""
        return {
            'hello': self._hello_command
        }
        
    def _hello_command(self, player, args):
        """示例命令"""
        return f"Hello from {self.name} plugin!"
