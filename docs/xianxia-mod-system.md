# 修仙世界引擎 - MOD系统完整实现

## 一、MOD系统架构设计

### 1.1 MOD结构定义

```yaml
# MOD标准结构
mod_structure:
  mod_root/
    ├── mod.json              # MOD元数据
    ├── manifest.json         # 文件清单和版本信息
    ├── icon.png             # MOD图标
    ├── README.md            # MOD说明文档
    ├── data/                # 数据文件
    │   ├── items/          # 物品定义
    │   ├── skills/         # 技能定义
    │   ├── npcs/           # NPC定义
    │   ├── events/         # 事件定义
    │   ├── locations/      # 地点定义
    │   └── formulas/       # 公式定义
    ├── scripts/            # 脚本文件
    │   ├── init.py         # 初始化脚本
    │   ├── hooks.py        # 事件钩子
    │   └── commands.py     # 自定义命令
    ├── assets/             # 资源文件
    │   ├── images/         # 图片资源
    │   ├── sounds/         # 音效资源
    │   └── texts/          # 文本资源
    └── localization/       # 本地化文件
        ├── zh_CN.json      # 中文
        └── en_US.json      # 英文
```

### 1.2 MOD元数据格式

```json
{
  "id": "celestial_sword_sect",
  "name": "天剑宗扩展包",
  "version": "1.0.0",
  "game_version": "3.0.0",
  "author": "修仙爱好者",
  "description": "添加天剑宗门派及相关内容",
  "tags": ["门派", "剑修", "PvE"],
  "dependencies": [
    {
      "id": "core",
      "version": ">=3.0.0"
    }
  ],
  "conflicts": [
    {
      "id": "demon_sword_sect",
      "reason": "剑道理念冲突"
    }
  ],
  "load_order": 100,
  "permissions": {
    "modify_core_data": false,
    "add_new_realms": false,
    "modify_formulas": true,
    "add_commands": true
  },
  "entry_points": {
    "init": "scripts/init.py:initialize",
    "hooks": "scripts/hooks.py:register_hooks",
    "commands": "scripts/commands.py:register_commands"
  }
}
```

## 二、MOD加载器实现

### 2.1 核心加载器

```python
# xwe/mod_system/loader.py

import json
import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import zipfile
import shutil
import logging
import threading
from xwe.core.event_system import GameEvent

logger = logging.getLogger(__name__)


class ModStatus(Enum):
    """MOD状态"""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class ModInfo:
    """MOD信息"""
    id: str
    name: str
    version: str
    path: Path
    metadata: Dict
    status: ModStatus = ModStatus.UNLOADED
    error_message: Optional[str] = None
    loaded_modules: Dict = None
    
    def __post_init__(self):
        if self.loaded_modules is None:
            self.loaded_modules = {}


class ModDependencyResolver:
    """MOD依赖解析器"""
    
    def __init__(self):
        self.dependency_graph = {}
        
    def add_mod(self, mod_id: str, dependencies: List[Dict]):
        """添加MOD依赖信息"""
        self.dependency_graph[mod_id] = dependencies
        
    def resolve_load_order(self, available_mods: Dict[str, ModInfo]) -> List[str]:
        """解析加载顺序"""
        # 拓扑排序
        visited = set()
        stack = []
        
        def visit(mod_id: str):
            if mod_id in visited:
                return
                
            visited.add(mod_id)
            
            # 访问依赖
            if mod_id in self.dependency_graph:
                for dep in self.dependency_graph[mod_id]:
                    dep_id = dep['id']
                    if dep_id in available_mods:
                        visit(dep_id)
                        
            stack.append(mod_id)
            
        # 访问所有MOD
        for mod_id in available_mods:
            visit(mod_id)
            
        return stack
        
    def check_dependencies(self, mod_id: str, 
                          loaded_mods: Dict[str, ModInfo]) -> Tuple[bool, List[str]]:
        """检查依赖是否满足"""
        missing_deps = []
        
        if mod_id not in self.dependency_graph:
            return True, []
            
        for dep in self.dependency_graph[mod_id]:
            dep_id = dep['id']
            required_version = dep.get('version', '*')
            
            if dep_id not in loaded_mods:
                missing_deps.append(f"{dep_id} ({required_version})")
                continue
                
            # 检查版本
            if not self._check_version(loaded_mods[dep_id].version, required_version):
                missing_deps.append(
                    f"{dep_id} (需要: {required_version}, 当前: {loaded_mods[dep_id].version})"
                )
                
        return len(missing_deps) == 0, missing_deps
        
    def _check_version(self, current: str, required: str) -> bool:
        """检查版本是否满足要求"""
        if required == '*':
            return True
            
        # 简单的版本比较，实际应用可能需要更复杂的语义化版本比较
        if required.startswith('>='):
            return current >= required[2:]
        elif required.startswith('>'):
            return current > required[1:]
        elif required.startswith('<='):
            return current <= required[2:]
        elif required.startswith('<'):
            return current < required[1:]
        elif required.startswith('=='):
            return current == required[2:]
        else:
            return current == required


class ModLoader:
    """MOD加载器"""
    
    def __init__(self, engine):
        self.engine = engine
        self.mod_directory = Path('mods')
        self.loaded_mods = {}
        self.disabled_mods = set()
        self.dependency_resolver = ModDependencyResolver()
        self.mod_hooks = defaultdict(list)
        
        # 创建MOD目录
        self.mod_directory.mkdir(exist_ok=True)
        
    def discover_mods(self) -> Dict[str, ModInfo]:
        """发现所有MOD"""
        discovered_mods = {}
        
        # 扫描MOD目录
        for mod_path in self.mod_directory.iterdir():
            if mod_path.is_dir():
                mod_info = self._load_mod_info(mod_path)
                if mod_info:
                    discovered_mods[mod_info.id] = mod_info
                    
            elif mod_path.suffix == '.zip':
                # 支持压缩包MOD
                mod_info = self._load_mod_from_zip(mod_path)
                if mod_info:
                    discovered_mods[mod_info.id] = mod_info
                    
        logger.info(f"Discovered {len(discovered_mods)} mods")
        return discovered_mods
        
    def _load_mod_info(self, mod_path: Path) -> Optional[ModInfo]:
        """加载MOD信息"""
        metadata_path = mod_path / 'mod.json'
        
        if not metadata_path.exists():
            logger.warning(f"No mod.json found in {mod_path}")
            return None
            
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                
            # 验证必需字段
            required_fields = ['id', 'name', 'version']
            for field in required_fields:
                if field not in metadata:
                    logger.error(f"Missing required field '{field}' in {metadata_path}")
                    return None
                    
            # 添加依赖信息
            self.dependency_resolver.add_mod(
                metadata['id'],
                metadata.get('dependencies', [])
            )
            
            return ModInfo(
                id=metadata['id'],
                name=metadata['name'],
                version=metadata['version'],
                path=mod_path,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to load mod info from {mod_path}: {e}")
            return None
            
    def _load_mod_from_zip(self, zip_path: Path) -> Optional[ModInfo]:
        """从压缩包加载MOD"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                # 读取mod.json
                if 'mod.json' not in z.namelist():
                    logger.warning(f"No mod.json found in {zip_path}")
                    return None
                    
                metadata = json.loads(z.read('mod.json').decode('utf-8'))
                
                # 解压到临时目录
                extract_path = self.mod_directory / f".extracted/{metadata['id']}"
                extract_path.mkdir(parents=True, exist_ok=True)
                z.extractall(extract_path)
                
                return ModInfo(
                    id=metadata['id'],
                    name=metadata['name'],
                    version=metadata['version'],
                    path=extract_path,
                    metadata=metadata
                )
                
        except Exception as e:
            logger.error(f"Failed to load mod from {zip_path}: {e}")
            return None
            
    def load_all_mods(self, mods_to_load: Optional[List[str]] = None) -> None:
        """加载所有MOD"""
        # 发现MOD
        available_mods = self.discover_mods()
        
        # 过滤要加载的MOD
        if mods_to_load:
            available_mods = {
                mod_id: mod_info 
                for mod_id, mod_info in available_mods.items() 
                if mod_id in mods_to_load
            }
            
        # 解析加载顺序
        load_order = self.dependency_resolver.resolve_load_order(available_mods)
        
        # 按顺序加载
        for mod_id in load_order:
            if mod_id in available_mods and mod_id not in self.disabled_mods:
                self.load_mod(available_mods[mod_id])
                
    def load_mod(self, mod_info: ModInfo) -> bool:
        """加载单个MOD"""
        if mod_info.id in self.loaded_mods:
            logger.warning(f"Mod {mod_info.id} is already loaded")
            return True
            
        logger.info(f"Loading mod: {mod_info.name} v{mod_info.version}")
        mod_info.status = ModStatus.LOADING
        
        try:
            # 检查依赖
            deps_satisfied, missing_deps = self.dependency_resolver.check_dependencies(
                mod_info.id, 
                self.loaded_mods
            )
            
            if not deps_satisfied:
                raise ModError(f"Missing dependencies: {', '.join(missing_deps)}")
                
            # 检查冲突
            self._check_conflicts(mod_info)
            
            # 加载数据文件
            self._load_mod_data(mod_info)
            
            # 加载脚本
            self._load_mod_scripts(mod_info)
            
            # 注册到已加载列表
            self.loaded_mods[mod_info.id] = mod_info
            mod_info.status = ModStatus.LOADED
            
            logger.info(f"Successfully loaded mod: {mod_info.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load mod {mod_info.id}: {e}")
            mod_info.status = ModStatus.ERROR
            mod_info.error_message = str(e)
            return False
            
    def _check_conflicts(self, mod_info: ModInfo) -> None:
        """检查MOD冲突"""
        conflicts = mod_info.metadata.get('conflicts', [])
        
        for conflict in conflicts:
            conflict_id = conflict['id']
            if conflict_id in self.loaded_mods:
                reason = conflict.get('reason', 'Unknown conflict')
                raise ModError(
                    f"Mod {mod_info.id} conflicts with {conflict_id}: {reason}"
                )
                
    def _load_mod_data(self, mod_info: ModInfo) -> None:
        """加载MOD数据文件"""
        data_path = mod_info.path / 'data'
        
        if not data_path.exists():
            return
            
        # 定义数据类型和加载方法
        data_loaders = {
            'items': self._load_items,
            'skills': self._load_skills,
            'npcs': self._load_npcs,
            'events': self._load_events,
            'locations': self._load_locations,
            'formulas': self._load_formulas
        }
        
        for data_type, loader in data_loaders.items():
            type_path = data_path / data_type
            if type_path.exists():
                for file_path in type_path.glob('*.json'):
                    loader(mod_info.id, file_path)
                    
    def _load_items(self, mod_id: str, file_path: Path) -> None:
        """加载物品数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            items_data = json.load(f)
            
        for item_id, item_data in items_data.items():
            # 添加MOD前缀避免ID冲突
            full_id = f"{mod_id}:{item_id}"
            
            # 验证数据格式
            self._validate_item_data(item_data)
            
            # 注册到游戏数据
            self.engine.data.set(f'items.{full_id}', item_data)
            
            logger.debug(f"Loaded item: {full_id}")
            
    def _validate_item_data(self, item_data: Dict) -> None:
        """验证物品数据格式"""
        required_fields = ['name', 'type', 'quality']
        for field in required_fields:
            if field not in item_data:
                raise ValueError(f"Item missing required field: {field}")
                
    def _load_skills(self, mod_id: str, file_path: Path) -> None:
        """加载技能数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            skills_data = json.load(f)
            
        for skill_id, skill_data in skills_data.items():
            full_id = f"{mod_id}:{skill_id}"
            
            # 处理技能公式
            if 'damage' in skill_data and isinstance(skill_data['damage'], dict):
                if 'formula' in skill_data['damage']:
                    # 确保是结构化表达式
                    skill_data['damage']['formula'] = self._ensure_expression_format(
                        skill_data['damage']['formula']
                    )
                    
            self.engine.data.set(f'skills.{full_id}', skill_data)
            logger.debug(f"Loaded skill: {full_id}")
            
    def _ensure_expression_format(self, formula: Any) -> Dict:
        """确保公式是结构化表达式格式"""
        if isinstance(formula, str):
            # 如果是字符串，尝试解析
            from xwe.core.formula_parser import FormulaParser
            parser = FormulaParser()
            return parser.parse(formula)
        return formula
        
    def _load_npcs(self, mod_id: str, file_path: Path) -> None:
        """加载NPC数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            npcs_data = json.load(f)
            
        for npc_id, npc_data in npcs_data.items():
            full_id = f"{mod_id}:{npc_id}"
            
            # 处理NPC对话
            if 'dialogues' in npc_data:
                dialogue_id = f"{mod_id}:{npc_data['dialogues']}"
                npc_data['dialogues'] = dialogue_id
                
            self.engine.data.set(f'npcs.{full_id}', npc_data)
            logger.debug(f"Loaded NPC: {full_id}")
            
    def _load_events(self, mod_id: str, file_path: Path) -> None:
        """加载事件数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            events_data = json.load(f)
            
        for event_id, event_data in events_data.items():
            full_id = f"{mod_id}:{event_id}"
            
            # 注册事件触发器
            if 'trigger' in event_data:
                self._register_event_trigger(full_id, event_data['trigger'])
                
            self.engine.data.set(f'events.{full_id}', event_data)
            logger.debug(f"Loaded event: {full_id}")
            
    def _register_event_trigger(self, event_id: str, trigger_data: Dict) -> None:
        """注册事件触发器"""
        trigger_type = trigger_data.get('type')
        
        if trigger_type == 'location':
            # 位置触发
            location_id = trigger_data.get('location')
            self.engine.events.register(
                f'enter_location_{location_id}',
                lambda e: self._trigger_event(event_id, e)
            )
        elif trigger_type == 'time':
            # 时间触发
            interval = trigger_data.get('interval', 3600)  # 默认每小时触发
            def schedule_event():
                self._trigger_event(event_id, GameEvent(type='time', data={'interval': interval}))
                threading.Timer(interval, schedule_event).start()

            schedule_event()
            
    def _trigger_event(self, event_id: str, game_event) -> None:
        """触发MOD事件"""
        event_data = self.engine.data.get(f'events.{event_id}')
        if event_data:
            # 创建事件实例
            self.engine.events.emit('mod_event_triggered', {
                'event_id': event_id,
                'event_data': event_data,
                'trigger_context': game_event.data
            })
            
    def _load_locations(self, mod_id: str, file_path: Path) -> None:
        """加载地点数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            locations_data = json.load(f)
            
        for location_id, location_data in locations_data.items():
            full_id = f"{mod_id}:{location_id}"
            
            # 注册到世界地图
            if 'parent' in location_data:
                parent_id = location_data['parent']
                self.engine.world.add_location(full_id, location_data, parent_id)
                
            self.engine.data.set(f'locations.{full_id}', location_data)
            logger.debug(f"Loaded location: {full_id}")
            
    def _load_formulas(self, mod_id: str, file_path: Path) -> None:
        """加载公式数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            formulas_data = json.load(f)
            
        for formula_id, formula_data in formulas_data.items():
            full_id = f"{mod_id}:{formula_id}"
            
            # 确保是结构化表达式
            if isinstance(formula_data, str):
                formula_data = self._ensure_expression_format(formula_data)
                
            self.engine.data.set(f'formulas.{full_id}', formula_data)
            logger.debug(f"Loaded formula: {full_id}")
            
    def _load_mod_scripts(self, mod_info: ModInfo) -> None:
        """加载MOD脚本"""
        entry_points = mod_info.metadata.get('entry_points', {})
        
        # 加载初始化脚本
        if 'init' in entry_points:
            self._load_entry_point(mod_info, entry_points['init'], 'init')
            
        # 加载钩子脚本
        if 'hooks' in entry_points:
            self._load_entry_point(mod_info, entry_points['hooks'], 'hooks')
            
        # 加载命令脚本
        if 'commands' in entry_points:
            self._load_entry_point(mod_info, entry_points['commands'], 'commands')
            
    def _load_entry_point(self, mod_info: ModInfo, entry_point: str, 
                          entry_type: str) -> None:
        """加载入口点"""
        # 解析入口点格式: "path/to/module.py:function_name"
        parts = entry_point.split(':')
        if len(parts) != 2:
            raise ValueError(f"Invalid entry point format: {entry_point}")
            
        module_path, function_name = parts
        
        # 构建完整路径
        full_path = mod_info.path / module_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"Entry point file not found: {full_path}")
            
        # 动态加载模块
        module_name = f"mod_{mod_info.id}_{entry_type}"
        spec = importlib.util.spec_from_file_location(module_name, full_path)
        module = importlib.util.module_from_spec(spec)
        
        # 添加到系统模块
        sys.modules[module_name] = module
        mod_info.loaded_modules[entry_type] = module
        
        # 执行模块
        spec.loader.exec_module(module)
        
        # 调用入口函数
        if hasattr(module, function_name):
            entry_func = getattr(module, function_name)
            
            # 创建MOD API上下文
            mod_api = ModAPI(self.engine, mod_info.id)
            
            # 调用函数
            if entry_type == 'init':
                entry_func(mod_api)
            elif entry_type == 'hooks':
                hooks = entry_func(mod_api)
                self._register_hooks(mod_info.id, hooks)
            elif entry_type == 'commands':
                commands = entry_func(mod_api)
                self._register_commands(mod_info.id, commands)
        else:
            raise AttributeError(
                f"Entry point function '{function_name}' not found in {full_path}"
            )
            
    def _register_hooks(self, mod_id: str, hooks: Dict[str, callable]) -> None:
        """注册MOD钩子"""
        for event_name, handler in hooks.items():
            self.mod_hooks[event_name].append({
                'mod_id': mod_id,
                'handler': handler
            })
            
            # 注册到事件系统
            self.engine.events.register(
                event_name,
                lambda e, h=handler: self._execute_hook(h, e),
                priority=-100  # MOD钩子优先级较低
            )
            
    def _execute_hook(self, handler: callable, event) -> Any:
        """执行MOD钩子"""
        try:
            return handler(event)
        except Exception as e:
            logger.error(f"Error in mod hook: {e}")
            return None
            
    def _register_commands(self, mod_id: str, commands: Dict[str, callable]) -> None:
        """注册MOD命令"""
        for command_name, handler in commands.items():
            full_name = f"{mod_id}:{command_name}"
            
            # 注册到命令系统
            if hasattr(self.engine, 'commands'):
                self.engine.commands.register(full_name, handler)
                
            logger.debug(f"Registered command: {full_name}")
            
    def unload_mod(self, mod_id: str) -> bool:
        """卸载MOD"""
        if mod_id not in self.loaded_mods:
            logger.warning(f"Mod {mod_id} is not loaded")
            return False
            
        logger.info(f"Unloading mod: {mod_id}")
        
        try:
            mod_info = self.loaded_mods[mod_id]
            
            # 调用清理函数
            if 'cleanup' in mod_info.loaded_modules:
                cleanup_module = mod_info.loaded_modules['cleanup']
                if hasattr(cleanup_module, 'cleanup'):
                    cleanup_module.cleanup()
                    
            # 移除数据
            self._remove_mod_data(mod_id)
            
            # 移除钩子
            self._remove_mod_hooks(mod_id)
            
            # 移除命令
            self._remove_mod_commands(mod_id)
            
            # 从已加载列表中移除
            del self.loaded_mods[mod_id]
            
            # 清理系统模块
            for module_type, module in mod_info.loaded_modules.items():
                module_name = f"mod_{mod_id}_{module_type}"
                if module_name in sys.modules:
                    del sys.modules[module_name]
                    
            logger.info(f"Successfully unloaded mod: {mod_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload mod {mod_id}: {e}")
            return False
            
    def _remove_mod_data(self, mod_id: str) -> None:
        """移除MOD数据"""
        # 这里需要实现数据清理逻辑
        # 遍历所有数据类别，移除带有mod_id前缀的数据
        pass
        
    def _remove_mod_hooks(self, mod_id: str) -> None:
        """移除MOD钩子"""
        for event_name, hooks in self.mod_hooks.items():
            self.mod_hooks[event_name] = [
                h for h in hooks if h['mod_id'] != mod_id
            ]
            
    def _remove_mod_commands(self, mod_id: str) -> None:
        """移除MOD命令"""
        # 需要命令系统支持移除命令
        pass
        
    def get_mod_info(self, mod_id: str) -> Optional[ModInfo]:
        """获取MOD信息"""
        return self.loaded_mods.get(mod_id)
        
    def list_loaded_mods(self) -> List[ModInfo]:
        """列出已加载的MOD"""
        return list(self.loaded_mods.values())
        
    def enable_mod(self, mod_id: str) -> None:
        """启用MOD"""
        if mod_id in self.disabled_mods:
            self.disabled_mods.remove(mod_id)
            
    def disable_mod(self, mod_id: str) -> None:
        """禁用MOD"""
        self.disabled_mods.add(mod_id)
        if mod_id in self.loaded_mods:
            self.unload_mod(mod_id)


class ModError(Exception):
    """MOD错误"""
    pass
```

## 三、MOD API设计

### 3.1 MOD开发API

```python
# xwe/mod_system/api.py

from typing import Any, Dict, List, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class ModAPI:
    """MOD开发API"""
    
    def __init__(self, engine, mod_id: str):
        self.engine = engine
        self.mod_id = mod_id
        self._registered_items = []
        self._registered_handlers = []
        
    # ========== 数据API ==========
    
    def add_item(self, item_id: str, item_data: Dict[str, Any]) -> None:
        """添加物品"""
        full_id = f"{self.mod_id}:{item_id}"
        
        # 验证数据
        self._validate_item_data(item_data)
        
        # 注册物品
        self.engine.data.set(f'items.{full_id}', item_data)
        self._registered_items.append(full_id)
        
        logger.info(f"[{self.mod_id}] Added item: {item_id}")
        
    def add_skill(self, skill_id: str, skill_data: Dict[str, Any]) -> None:
        """添加技能"""
        full_id = f"{self.mod_id}:{skill_id}"
        
        # 处理技能公式
        if 'effects' in skill_data:
            for effect_type, effect_data in skill_data['effects'].items():
                if 'formula' in effect_data:
                    effect_data['formula'] = self._ensure_expression(effect_data['formula'])
                    
        self.engine.data.set(f'skills.{full_id}', skill_data)
        logger.info(f"[{self.mod_id}] Added skill: {skill_id}")
        
    def add_npc(self, npc_id: str, npc_data: Dict[str, Any]) -> None:
        """添加NPC"""
        full_id = f"{self.mod_id}:{npc_id}"
        
        # 处理NPC模板
        if 'template' in npc_data:
            template_data = self.engine.data.get(f"templates.npc.{npc_data['template']}")
            if template_data:
                # 合并模板数据
                merged_data = {**template_data, **npc_data}
                npc_data = merged_data
                
        self.engine.data.set(f'npcs.{full_id}', npc_data)
        
        # 如果有初始位置，添加到世界
        if 'initial_location' in npc_data:
            self.engine.world.spawn_npc(full_id, npc_data['initial_location'])
            
        logger.info(f"[{self.mod_id}] Added NPC: {npc_id}")
        
    def add_location(self, location_id: str, location_data: Dict[str, Any],
                     parent_location: Optional[str] = None) -> None:
        """添加地点"""
        full_id = f"{self.mod_id}:{location_id}"
        
        # 添加到世界地图
        self.engine.world.add_location(full_id, location_data, parent_location)
        
        # 保存数据
        self.engine.data.set(f'locations.{full_id}', location_data)
        
        logger.info(f"[{self.mod_id}] Added location: {location_id}")
        
    def modify_data(self, path: str, modifications: Dict[str, Any]) -> None:
        """修改现有数据"""
        # 检查权限
        if not self._check_permission('modify_core_data'):
            raise PermissionError(f"Mod {self.mod_id} does not have permission to modify core data")
            
        current_data = self.engine.data.get(path)
        if current_data is None:
            raise ValueError(f"Data path not found: {path}")
            
        # 应用修改
        if isinstance(current_data, dict):
            current_data.update(modifications)
        else:
            raise TypeError(f"Cannot modify non-dict data at {path}")
            
        # 记录修改
        logger.info(f"[{self.mod_id}] Modified data at: {path}")
        
    # ========== 事件API ==========
    
    def register_event_handler(self, event_type: str, handler: Callable,
                              priority: int = 0) -> None:
        """注册事件处理器"""
        wrapped_handler = self._wrap_handler(handler)
        
        self.engine.events.register(event_type, wrapped_handler, priority)
        self._registered_handlers.append((event_type, wrapped_handler))
        
        logger.debug(f"[{self.mod_id}] Registered handler for: {event_type}")
        
    def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """发送事件"""
        # 添加MOD标识
        data['_mod_id'] = self.mod_id
        
        self.engine.events.emit(event_type, data, source=f"mod:{self.mod_id}")
        
    def register_hook(self, hook_point: str, handler: Callable) -> None:
        """注册钩子"""
        # 钩子是特殊的事件处理器
        self.register_event_handler(f"hook:{hook_point}", handler, priority=-100)
        
    # ========== 命令API ==========
    
    def register_command(self, command_name: str, handler: Callable,
                        description: str = "") -> None:
        """注册命令"""
        full_name = f"{self.mod_id}:{command_name}"
        
        # 包装处理器
        wrapped_handler = self._wrap_command_handler(handler)
        
        # 注册到命令系统
        if hasattr(self.engine, 'commands'):
            self.engine.commands.register(full_name, wrapped_handler, description)
            
        logger.info(f"[{self.mod_id}] Registered command: {command_name}")
        
    # ========== 界面API ==========
    
    def add_menu_option(self, menu_id: str, option_data: Dict[str, Any]) -> None:
        """添加菜单选项"""
        if hasattr(self.engine, 'ui'):
            self.engine.ui.add_menu_option(menu_id, option_data)
            
    def show_dialog(self, title: str, content: str, 
                    options: List[Dict[str, Any]]) -> None:
        """显示对话框"""
        if hasattr(self.engine, 'ui'):
            self.engine.ui.show_dialog({
                'title': title,
                'content': content,
                'options': options,
                'source': f"mod:{self.mod_id}"
            })
            
    # ========== 工具函数 ==========
    
    def get_player(self) -> Any:
        """获取玩家对象"""
        return self.engine.player
        
    def get_current_location(self) -> str:
        """获取当前位置"""
        return self.engine.world.get_player_location()
        
    def get_game_time(self) -> float:
        """获取游戏时间"""
        return self.engine.total_time
        
    def save_mod_data(self, key: str, data: Any) -> None:
        """保存MOD数据"""
        save_path = f"mod_data.{self.mod_id}.{key}"
        self.engine.data.set(save_path, data)
        
    def load_mod_data(self, key: str, default: Any = None) -> Any:
        """加载MOD数据"""
        save_path = f"mod_data.{self.mod_id}.{key}"
        return self.engine.data.get(save_path, default)
        
    def log(self, message: str, level: str = "info") -> None:
        """记录日志"""
        log_func = getattr(logger, level, logger.info)
        log_func(f"[{self.mod_id}] {message}")
        
    # ========== 私有方法 ==========
    
    def _validate_item_data(self, item_data: Dict[str, Any]) -> None:
        """验证物品数据"""
        required_fields = ['name', 'type', 'quality', 'description']
        
        for field in required_fields:
            if field not in item_data:
                raise ValueError(f"Item missing required field: {field}")
                
        # 验证品质
        valid_qualities = ['common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic']
        if item_data['quality'] not in valid_qualities:
            raise ValueError(f"Invalid item quality: {item_data['quality']}")
            
    def _ensure_expression(self, formula: Any) -> Dict[str, Any]:
        """确保是表达式格式"""
        if isinstance(formula, str):
            # 解析字符串公式
            from xwe.core.formula_parser import FormulaParser
            parser = FormulaParser()
            return parser.parse(formula)
        return formula
        
    def _check_permission(self, permission: str) -> bool:
        """检查权限"""
        mod_info = self.engine.mod_loader.get_mod_info(self.mod_id)
        if mod_info:
            permissions = mod_info.metadata.get('permissions', {})
            return permissions.get(permission, False)
        return False
        
    def _wrap_handler(self, handler: Callable) -> Callable:
        """包装事件处理器"""
        def wrapped(event):
            try:
                return handler(self, event)
            except Exception as e:
                logger.error(f"[{self.mod_id}] Error in event handler: {e}")
                return None
        return wrapped
        
    def _wrap_command_handler(self, handler: Callable) -> Callable:
        """包装命令处理器"""
        def wrapped(player, args):
            try:
                return handler(self, player, args)
            except Exception as e:
                logger.error(f"[{self.mod_id}] Error in command handler: {e}")
                return f"命令执行出错: {e}"
        return wrapped
```

## 四、MOD开发示例

### 4.1 示例MOD：天剑宗

```python
# mods/celestial_sword_sect/scripts/init.py

def initialize(api):
    """初始化天剑宗MOD"""
    api.log("Initializing Celestial Sword Sect mod...")
    
    # 添加天剑宗地点
    api.add_location('celestial_sword_peak', {
        'name': '天剑峰',
        'description': '天剑宗的主峰，终年云雾缭绕，剑气冲天。',
        'type': 'sect_location',
        'requirements': {
            'reputation': 100,
            'realm': 'foundation_building'
        },
        'npcs': ['celestial_sword_sect:elder_li', 'celestial_sword_sect:sword_spirit'],
        'events': ['celestial_sword_sect:sword_enlightenment']
    }, parent_location='eastern_continent')
    
    # 添加剑道感悟事件
    api.register_event_handler('enter_location', handle_location_entry)
    
    api.log("Celestial Sword Sect mod initialized!")
    

def handle_location_entry(api, event):
    """处理进入地点事件"""
    location = event.data.get('location')
    
    if location == 'celestial_sword_sect:celestial_sword_peak':
        player = api.get_player()
        
        # 检查是否第一次访问
        first_visit = not api.load_mod_data('visited_peak', False)
        
        if first_visit:
            api.save_mod_data('visited_peak', True)
            
            # 触发特殊事件
            api.emit_event('special_encounter', {
                'type': 'sword_spirit_greeting',
                'message': '你感受到一股强大的剑意笼罩全身，仿佛有无数把剑在空中鸣响...'
            })
            
            # 增加剑道亲和
            if hasattr(player, 'add_affinity'):
                player.add_affinity('sword', 10)
```

```python
# mods/celestial_sword_sect/scripts/hooks.py

def register_hooks(api):
    """注册钩子"""
    return {
        'before_combat': before_combat_hook,
        'after_skill_use': after_skill_use_hook,
        'cultivation_complete': cultivation_hook
    }


def before_combat_hook(api, event):
    """战斗前钩子"""
    player = event.data.get('player')
    
    # 如果玩家是天剑宗弟子，增加剑系技能威力
    if player.faction == 'celestial_sword_sect':
        event.data['modifiers'] = event.data.get('modifiers', {})
        event.data['modifiers']['sword_damage_bonus'] = 1.2
        
        api.log("Celestial Sword Sect combat bonus applied")
        

def after_skill_use_hook(api, event):
    """技能使用后钩子"""
    skill_id = event.data.get('skill_id')
    
    # 统计剑系技能使用
    if 'sword' in skill_id:
        count = api.load_mod_data('sword_skill_count', 0)
        count += 1
        api.save_mod_data('sword_skill_count', count)
        
        # 每使用100次剑系技能，获得剑道感悟
        if count % 100 == 0:
            api.emit_event('gain_enlightenment', {
                'type': 'sword_dao',
                'level': count // 100
            })
            

def cultivation_hook(api, event):
    """修炼完成钩子"""
    player = api.get_player()
    location = api.get_current_location()
    
    # 在天剑峰修炼有额外加成
    if location == 'celestial_sword_sect:celestial_sword_peak':
        bonus_exp = event.data.get('exp_gained', 0) * 0.5
        
        api.emit_event('bonus_experience', {
            'amount': bonus_exp,
            'source': 'celestial_sword_peak_bonus'
        })
```

```python
# mods/celestial_sword_sect/scripts/commands.py

def register_commands(api):
    """注册命令"""
    return {
        'sword_dance': sword_dance_command,
        'summon_sword': summon_sword_command,
        'sword_meditation': sword_meditation_command
    }


def sword_dance_command(api, player, args):
    """剑舞命令 - 展示剑法并获得感悟"""
    # 检查是否在合适的地点
    location = api.get_current_location()
    
    if 'celestial_sword' not in location:
        return "这里的环境不适合施展剑舞。"
        
    # 检查体力
    if player.stamina < 30:
        return "你的体力不足，无法施展剑舞。"
        
    # 消耗体力
    player.stamina -= 30
    
    # 计算成功率
    import random
    skill_level = player.get_skill_level('sword_mastery')
    success_rate = 0.3 + skill_level * 0.1
    
    if random.random() < success_rate:
        # 成功获得感悟
        enlightenment = random.randint(5, 15)
        player.add_enlightenment('sword', enlightenment)
        
        # 记录成就
        api.emit_event('achievement_progress', {
            'achievement_id': 'sword_dancer',
            'progress': 1
        })
        
        return f"剑舞如行云流水，你获得了 {enlightenment} 点剑道感悟！"
    else:
        return "你施展了一套剑舞，但未能有所领悟。"
        

def summon_sword_command(api, player, args):
    """召唤飞剑命令"""
    # 检查是否学习了相关技能
    if not player.has_skill('celestial_sword_sect:flying_sword'):
        return "你还未掌握御剑之术。"
        
    # 检查法力
    mana_cost = 50
    if player.mana < mana_cost:
        return f"召唤飞剑需要 {mana_cost} 点法力，你的法力不足。"
        
    # 消耗法力
    player.mana -= mana_cost
    
    # 召唤飞剑
    api.emit_event('summon_entity', {
        'entity_type': 'flying_sword',
        'entity_id': 'celestial_sword_sect:summoned_sword',
        'duration': 300,  # 5分钟
        'owner': player.id
    })
    
    return "你掐诀念咒，一柄寒光闪闪的飞剑应声而出，环绕在你身边！"
    

def sword_meditation_command(api, player, args):
    """剑道冥想命令"""
    # 检查是否在战斗中
    if player.in_combat:
        return "战斗中无法进行剑道冥想。"
        
    # 开始冥想
    api.emit_event('start_meditation', {
        'type': 'sword_meditation',
        'duration': 60,  # 1分钟
        'effects': {
            'sword_comprehension': 2,
            'mana_regen': 1.5
        }
    })
    
    return "你盘膝而坐，神识沉入剑道感悟之中..."
```

### 4.2 MOD配置文件示例

```json
// mods/celestial_sword_sect/data/skills/sword_skills.json
{
  "basic_sword_slash": {
    "name": "基础剑斩",
    "type": "active",
    "category": "sword",
    "description": "天剑宗入门剑法第一式",
    "requirements": {
      "faction": "celestial_sword_sect",
      "skill_points": 1
    },
    "cost": {
      "mana": 10,
      "stamina": 5
    },
    "cooldown": 2,
    "effects": {
      "damage": {
        "type": "physical",
        "formula": {
          "operation": "*",
          "operands": [
            {"attribute": "player.attack"},
            {"constant": 1.5},
            {
              "operation": "+",
              "operands": [
                {"constant": 1},
                {
                  "operation": "*",
                  "operands": [
                    {"attribute": "skill.level"},
                    {"constant": 0.1}
                  ]
                }
              ]
            }
          ]
        }
      }
    }
  },
  "flying_sword": {
    "name": "御剑术",
    "type": "toggle",
    "category": "sword",
    "description": "天剑宗核心功法，可御剑飞行和战斗",
    "requirements": {
      "faction": "celestial_sword_sect",
      "realm": "golden_core",
      "prerequisite_skills": ["basic_sword_slash"],
      "skill_points": 5
    },
    "cost": {
      "mana_per_second": 5
    },
    "effects": {
      "movement_speed": {
        "formula": {
          "operation": "*",
          "operands": [
            {"attribute": "player.speed"},
            {"constant": 3}
          ]
        }
      },
      "flying": true,
      "sword_damage_bonus": {
        "formula": {
          "operation": "+",
          "operands": [
            {"constant": 0.5},
            {
              "operation": "*",
              "operands": [
                {"attribute": "skill.level"},
                {"constant": 0.1}
              ]
            }
          ]
        }
      }
    }
  }
}
```

## 五、MOD管理器UI

```python
# xwe/mod_system/manager_ui.py

from typing import List, Dict
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from pathlib import Path


class ModManagerUI:
    """MOD管理器界面"""
    
    def __init__(self, mod_loader):
        self.mod_loader = mod_loader
        self.window = tk.Tk()
        self.window.title("修仙世界引擎 - MOD管理器")
        self.window.geometry("800x600")
        
        self.setup_ui()
        self.refresh_mod_list()
        
    def setup_ui(self):
        """设置界面"""
        # 工具栏
        toolbar = ttk.Frame(self.window)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="刷新", command=self.refresh_mod_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="安装MOD", command=self.install_mod).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="创建MOD", command=self.create_mod).pack(side=tk.LEFT, padx=2)
        
        # 主框架
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # MOD列表
        list_frame = ttk.LabelFrame(main_frame, text="已安装的MOD")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 列表控件
        self.mod_tree = ttk.Treeview(list_frame, columns=(
            'version', 'author', 'status'
        ), show='tree headings')
        
        self.mod_tree.heading('#0', text='名称')
        self.mod_tree.heading('version', text='版本')
        self.mod_tree.heading('author', text='作者')
        self.mod_tree.heading('status', text='状态')
        
        self.mod_tree.column('#0', width=200)
        self.mod_tree.column('version', width=80)
        self.mod_tree.column('author', width=100)
        self.mod_tree.column('status', width=80)
        
        self.mod_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 绑定选择事件
        self.mod_tree.bind('<<TreeviewSelect>>', self.on_mod_select)
        
        # 详情面板
        detail_frame = ttk.LabelFrame(main_frame, text="MOD详情", width=300)
        detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        detail_frame.pack_propagate(False)
        
        # 详情文本
        self.detail_text = tk.Text(detail_frame, wrap=tk.WORD, width=40)
        self.detail_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 操作按钮
        button_frame = ttk.Frame(detail_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.enable_button = ttk.Button(
            button_frame, text="启用", 
            command=self.toggle_mod, state=tk.DISABLED
        )
        self.enable_button.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame, text="卸载", 
            command=self.uninstall_mod, state=tk.DISABLED
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame, text="配置", 
            command=self.configure_mod, state=tk.DISABLED
        ).pack(side=tk.LEFT, padx=2)
        
    def refresh_mod_list(self):
        """刷新MOD列表"""
        # 清空列表
        for item in self.mod_tree.get_children():
            self.mod_tree.delete(item)
            
        # 发现MOD
        discovered_mods = self.mod_loader.discover_mods()
        
        # 添加到列表
        for mod_id, mod_info in discovered_mods.items():
            status = "已加载" if mod_info.status == ModStatus.LOADED else "未加载"
            
            self.mod_tree.insert('', 'end', 
                text=mod_info.name,
                values=(
                    mod_info.version,
                    mod_info.metadata.get('author', '未知'),
                    status
                ),
                tags=(mod_id,)
            )
            
    def on_mod_select(self, event):
        """MOD选择事件"""
        selection = self.mod_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        mod_id = self.mod_tree.item(item, 'tags')[0]
        
        # 获取MOD信息
        mod_info = self.mod_loader.get_mod_info(mod_id)
        if not mod_info:
            # 未加载的MOD
            discovered = self.mod_loader.discover_mods()
            mod_info = discovered.get(mod_id)
            
        if mod_info:
            self.show_mod_details(mod_info)
            
    def show_mod_details(self, mod_info: ModInfo):
        """显示MOD详情"""
        self.detail_text.delete(1.0, tk.END)
        
        details = f"""名称: {mod_info.name}
ID: {mod_info.id}
版本: {mod_info.version}
作者: {mod_info.metadata.get('author', '未知')}
描述: {mod_info.metadata.get('description', '无描述')}

标签: {', '.join(mod_info.metadata.get('tags', []))}

依赖:
"""
        
        # 添加依赖信息
        dependencies = mod_info.metadata.get('dependencies', [])
        if dependencies:
            for dep in dependencies:
                details += f"  - {dep['id']} ({dep.get('version', '任意版本')})\n"
        else:
            details += "  无\n"
            
        # 添加权限信息
        details += "\n权限:\n"
        permissions = mod_info.metadata.get('permissions', {})
        for perm, value in permissions.items():
            status = "✓" if value else "✗"
            details += f"  {status} {perm}\n"
            
        self.detail_text.insert(1.0, details)
        
        # 更新按钮状态
        if mod_info.status == ModStatus.LOADED:
            self.enable_button.config(text="禁用", state=tk.NORMAL)
        else:
            self.enable_button.config(text="启用", state=tk.NORMAL)
            
    def toggle_mod(self):
        """切换MOD状态"""
        selection = self.mod_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        mod_id = self.mod_tree.item(item, 'tags')[0]
        
        mod_info = self.mod_loader.get_mod_info(mod_id)
        
        if mod_info and mod_info.status == ModStatus.LOADED:
            # 卸载MOD
            if self.mod_loader.unload_mod(mod_id):
                messagebox.showinfo("成功", f"MOD {mod_info.name} 已禁用")
                self.refresh_mod_list()
        else:
            # 加载MOD
            discovered = self.mod_loader.discover_mods()
            mod_info = discovered.get(mod_id)
            
            if mod_info and self.mod_loader.load_mod(mod_info):
                messagebox.showinfo("成功", f"MOD {mod_info.name} 已启用")
                self.refresh_mod_list()
            else:
                messagebox.showerror("错误", f"无法加载MOD: {mod_info.error_message}")
                
    def install_mod(self):
        """安装MOD"""
        # 选择MOD文件
        filename = filedialog.askopenfilename(
            title="选择MOD文件",
            filetypes=[("MOD文件", "*.zip"), ("所有文件", "*.*")]
        )
        
        if not filename:
            return
            
        try:
            # 复制到MOD目录
            import shutil
            mod_path = Path(filename)
            dest_path = self.mod_loader.mod_directory / mod_path.name
            
            shutil.copy2(mod_path, dest_path)
            
            messagebox.showinfo("成功", "MOD安装成功！")
            self.refresh_mod_list()
            
        except Exception as e:
            messagebox.showerror("错误", f"安装失败: {e}")
            
    def uninstall_mod(self):
        """卸载MOD"""
        selection = self.mod_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        mod_id = self.mod_tree.item(item, 'tags')[0]
        
        # 确认
        if not messagebox.askyesno("确认", f"确定要卸载MOD {mod_id} 吗？"):
            return
            
        # 卸载
        try:
            # 先禁用
            self.mod_loader.unload_mod(mod_id)
            
            # 删除文件
            discovered = self.mod_loader.discover_mods()
            mod_info = discovered.get(mod_id)
            
            if mod_info:
                import shutil
                shutil.rmtree(mod_info.path)
                
            messagebox.showinfo("成功", "MOD卸载成功！")
            self.refresh_mod_list()
            
        except Exception as e:
            messagebox.showerror("错误", f"卸载失败: {e}")
            
    def configure_mod(self):
        """配置MOD"""
        config_file = filedialog.askopenfilename(
            title="选择MOD配置文件", filetypes=[('JSON', '*.json')]
        )
        if not config_file:
            return
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        editor = ModConfigEditor(self.window, config)
        editor.run()
        
    def create_mod(self):
        """创建MOD"""
        # 打开MOD创建向导
        creator = ModCreatorWizard(self.window)
        creator.run()
        
    def run(self):
        """运行管理器"""
        self.window.mainloop()


class ModCreatorWizard:
    """MOD创建向导"""
    
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("创建新MOD")
        self.window.geometry("600x500")
        
        self.mod_data = {
            'id': '',
            'name': '',
            'version': '1.0.0',
            'author': '',
            'description': '',
            'tags': [],
            'dependencies': [],
            'permissions': {
                'modify_core_data': False,
                'add_new_realms': False,
                'modify_formulas': True,
                'add_commands': True
            }
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 基本信息页
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="基本信息")
        self.setup_basic_page(basic_frame)
        
        # 依赖设置页
        deps_frame = ttk.Frame(notebook)
        notebook.add(deps_frame, text="依赖设置")
        self.setup_deps_page(deps_frame)
        
        # 权限设置页
        perms_frame = ttk.Frame(notebook)
        notebook.add(perms_frame, text="权限设置")
        self.setup_perms_page(perms_frame)
        
        # 按钮
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="创建", command=self.create).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.window.destroy).pack(side=tk.RIGHT)
        
    def setup_basic_page(self, parent):
        """设置基本信息页"""
        # ID
        ttk.Label(parent, text="MOD ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.id_entry = ttk.Entry(parent, width=40)
        self.id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 名称
        ttk.Label(parent, text="名称:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(parent, width=40)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # 版本
        ttk.Label(parent, text="版本:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.version_entry = ttk.Entry(parent, width=40)
        self.version_entry.insert(0, "1.0.0")
        self.version_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # 作者
        ttk.Label(parent, text="作者:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.author_entry = ttk.Entry(parent, width=40)
        self.author_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # 描述
        ttk.Label(parent, text="描述:").grid(row=4, column=0, sticky=tk.NW, padx=5, pady=5)
        self.desc_text = tk.Text(parent, width=40, height=5)
        self.desc_text.grid(row=4, column=1, padx=5, pady=5)
        
        # 标签
        ttk.Label(parent, text="标签:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.tags_entry = ttk.Entry(parent, width=40)
        self.tags_entry.insert(0, "用逗号分隔")
        self.tags_entry.grid(row=5, column=1, padx=5, pady=5)
        
    def setup_deps_page(self, parent):
        """设置依赖页"""
        ttk.Label(parent, text="依赖MOD列表:").pack(anchor=tk.W, padx=5, pady=5)
        self.deps_list = tk.Listbox(parent, height=6)
        self.deps_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        control = ttk.Frame(parent)
        control.pack(fill=tk.X, padx=5, pady=5)
        self.new_dep = tk.StringVar()
        ttk.Entry(control, textvariable=self.new_dep, width=20).pack(side=tk.LEFT)
        ttk.Button(control, text="添加", command=self.add_dependency).pack(side=tk.LEFT, padx=5)
        ttk.Button(control, text="移除选中", command=self.remove_dependency).pack(side=tk.LEFT)

    def add_dependency(self):
        dep = self.new_dep.get().strip()
        if dep:
            self.deps_list.insert(tk.END, dep)
            self.new_dep.set('')

    def remove_dependency(self):
        for i in reversed(self.deps_list.curselection()):
            self.deps_list.delete(i)
        
    def setup_perms_page(self, parent):
        """设置权限页"""
        self.perm_vars = {}
        
        perms = [
            ('modify_core_data', '修改核心数据'),
            ('add_new_realms', '添加新境界'),
            ('modify_formulas', '修改公式'),
            ('add_commands', '添加命令')
        ]
        
        for i, (key, label) in enumerate(perms):
            var = tk.BooleanVar(value=self.mod_data['permissions'].get(key, False))
            self.perm_vars[key] = var
            
            ttk.Checkbutton(parent, text=label, variable=var).grid(
                row=i, column=0, sticky=tk.W, padx=20, pady=5
            )
            
    def create(self):
        """创建MOD"""
        # 收集数据
        self.mod_data['id'] = self.id_entry.get()
        self.mod_data['name'] = self.name_entry.get()
        self.mod_data['version'] = self.version_entry.get()
        self.mod_data['author'] = self.author_entry.get()
        self.mod_data['description'] = self.desc_text.get(1.0, tk.END).strip()
        
        # 处理标签
        tags_text = self.tags_entry.get()
        if tags_text and tags_text != "用逗号分隔":
            self.mod_data['tags'] = [t.strip() for t in tags_text.split(',')]
            
        # 收集权限
        for key, var in self.perm_vars.items():
            self.mod_data['permissions'][key] = var.get()
            
        # 验证
        if not self.mod_data['id'] or not self.mod_data['name']:
            messagebox.showerror("错误", "MOD ID和名称不能为空！")
            return
            
        # 创建MOD结构
        try:
            self.create_mod_structure()
            messagebox.showinfo("成功", f"MOD {self.mod_data['name']} 创建成功！")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"创建失败: {e}")
            
    def create_mod_structure(self):
        """创建MOD目录结构"""
        mod_path = Path('mods') / self.mod_data['id']
        
        # 创建目录
        mod_path.mkdir(parents=True, exist_ok=True)
        (mod_path / 'data').mkdir(exist_ok=True)
        (mod_path / 'scripts').mkdir(exist_ok=True)
        (mod_path / 'assets').mkdir(exist_ok=True)
        (mod_path / 'localization').mkdir(exist_ok=True)
        
        # 创建子目录
        for subdir in ['items', 'skills', 'npcs', 'events', 'locations']:
            (mod_path / 'data' / subdir).mkdir(exist_ok=True)
            
        # 创建mod.json
        with open(mod_path / 'mod.json', 'w', encoding='utf-8') as f:
            json.dump(self.mod_data, f, indent=2, ensure_ascii=False)
            
        # 创建README.md
        readme_content = f"""# {self.mod_data['name']}

{self.mod_data['description']}

## 安装方法

1. 将MOD文件夹复制到游戏的 `mods` 目录
2. 在MOD管理器中启用此MOD
3. 重启游戏

## 功能特性

- 待添加...

## 作者

{self.mod_data['author']}

## 版本历史

### v{self.mod_data['version']}
- 初始版本
"""
        
        with open(mod_path / 'README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
            
        # 创建示例脚本
        init_script = '''def initialize(api):
    """初始化MOD"""
    api.log("MOD initialized!")
'''
        
        with open(mod_path / 'scripts' / 'init.py', 'w', encoding='utf-8') as f:
            f.write(init_script)
            
    def run(self):
        """运行向导"""
        self.window.transient(self.parent)
        self.window.grab_set()
        self.parent.wait_window(self.window)
```

## 六、MOD系统集成

### 6.1 引擎集成

```python
# xwe/core/engine.py 添加MOD支持

class GameEngine:
    """游戏引擎核心（支持MOD）"""
    
    def __init__(self):
        # ... 原有代码 ...
        
        # MOD系统
        self.mod_loader = ModLoader(self)
        
    def initialize(self, config_path: str, load_mods: bool = True) -> None:
        """初始化引擎"""
        # ... 原有初始化代码 ...
        
        # 加载MOD
        if load_mods:
            self.mod_loader.load_all_mods()
            
    def register_mod_api_extensions(self):
        """注册MOD API扩展"""
        # 允许MOD扩展引擎功能
        self.mod_extensions = {}
        
    def add_mod_extension(self, name: str, extension: Any) -> None:
        """添加MOD扩展"""
        self.mod_extensions[name] = extension
        
    def get_mod_extension(self, name: str) -> Any:
        """获取MOD扩展"""
        return self.mod_extensions.get(name)
```

## 总结

这个完整的MOD系统实现提供了：

1. **灵活的MOD结构** - 支持数据、脚本、资源的模块化组织
2. **强大的API** - 允许MOD开发者扩展游戏的各个方面
3. **依赖管理** - 自动处理MOD之间的依赖关系
4. **权限控制** - 限制MOD的权限，保护核心系统
5. **可视化管理** - 提供友好的MOD管理界面
6. **开发工具** - MOD创建向导简化开发流程

通过这个系统，玩家和开发者可以轻松地为修仙世界引擎创建和分享各种扩展内容，大大增强了游戏的可玩性和生命力。