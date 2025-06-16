"""
可持续进化的内容生态系统
- MOD加载器
- 热更新支持
- 内容注册表
- 社区内容管理
"""

import os
import json
import importlib
import importlib.util
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import logging
import time
from enum import Enum

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """内容类型"""
    NPC = "npc"
    ITEM = "item"
    SKILL = "skill"
    LOCATION = "location"
    EVENT = "event"
    QUEST = "quest"
    DIALOGUE = "dialogue"
    MONSTER = "monster"
    SYSTEM = "system"


@dataclass
class ModInfo:
    """MOD信息"""
    id: str
    name: str
    version: str
    author: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    content_types: List[ContentType] = field(default_factory=list)
    enabled: bool = True
    load_order: int = 0
    path: str = ""
    checksum: str = ""


@dataclass
class ContentEntry:
    """内容条目"""
    id: str
    type: ContentType
    mod_id: str
    data: Dict[str, Any]
    version: str
    tags: List[str] = field(default_factory=list)
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        return self.data.get("name", self.id)


class ModLoader:
    """MOD加载器"""
    
    def __init__(self, mods_directory: str = "mods"):
        self.mods_directory = Path(mods_directory)
        self.loaded_mods: Dict[str, ModInfo] = {}
        self.mod_contents: Dict[str, List[ContentEntry]] = {}
        self.load_callbacks: List[Callable] = []
        self.error_callbacks: List[Callable] = []
        
        # 确保MOD目录存在
        self.mods_directory.mkdir(exist_ok=True)
        
        # 创建示例MOD目录结构
        self._create_mod_template()
    
    def _create_mod_template(self) -> None:
        """创建MOD模板"""
        template_path = self.mods_directory / "template_mod"
        if not template_path.exists():
            template_path.mkdir()
            
            # MOD信息文件
            mod_info = {
                "id": "template_mod",
                "name": "模板MOD",
                "version": "1.0.0",
                "author": "作者名",
                "description": "这是一个MOD模板",
                "dependencies": [],
                "content_types": ["npc", "item", "event"]
            }
            
            with open(template_path / "mod.json", "w", encoding="utf-8") as f:
                json.dump(mod_info, f, ensure_ascii=False, indent=2)
            
            # 创建内容目录
            for content_type in ["npcs", "items", "events"]:
                (template_path / content_type).mkdir(exist_ok=True)
            
            # 示例NPC
            example_npc = {
                "id": "mysterious_merchant",
                "name": "神秘商人",
                "description": "一位来历不明的商人",
                "dialogue": {
                    "greeting": "欢迎光临，我这里有些特别的东西...",
                    "farewell": "期待下次见面。"
                },
                "inventory": ["special_sword", "rare_potion"],
                "tags": ["merchant", "mysterious"]
            }
            
            with open(template_path / "npcs" / "mysterious_merchant.json", "w", encoding="utf-8") as f:
                json.dump(example_npc, f, ensure_ascii=False, indent=2)
    
    def scan_mods(self) -> List[ModInfo]:
        """扫描MOD目录"""
        discovered_mods = []
        
        for mod_dir in self.mods_directory.iterdir():
            if mod_dir.is_dir() and (mod_dir / "mod.json").exists():
                try:
                    mod_info = self._load_mod_info(mod_dir)
                    if mod_info:
                        discovered_mods.append(mod_info)
                except Exception as e:
                    logger.error(f"加载MOD失败 {mod_dir.name}: {e}")
                    for callback in self.error_callbacks:
                        callback(mod_dir.name, str(e))
        
        return discovered_mods
    
    def _load_mod_info(self, mod_path: Path) -> Optional[ModInfo]:
        """加载MOD信息"""
        info_file = mod_path / "mod.json"
        
        try:
            with open(info_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 计算校验和
            checksum = self._calculate_checksum(mod_path)
            
            return ModInfo(
                id=data["id"],
                name=data["name"],
                version=data["version"],
                author=data.get("author", "Unknown"),
                description=data.get("description", ""),
                dependencies=data.get("dependencies", []),
                content_types=[ContentType(t) for t in data.get("content_types", [])],
                path=str(mod_path),
                checksum=checksum
            )
        except Exception as e:
            logger.error(f"解析MOD信息失败: {e}")
            return None
    
    def _calculate_checksum(self, mod_path: Path) -> str:
        """计算MOD校验和"""
        hasher = hashlib.md5()
        
        for file_path in mod_path.rglob("*.json"):
            with open(file_path, "rb") as f:
                hasher.update(f.read())
        
        return hasher.hexdigest()
    
    def load_mod(self, mod_info: ModInfo) -> bool:
        """加载单个MOD"""
        if mod_info.id in self.loaded_mods:
            logger.warning(f"MOD {mod_info.id} 已加载")
            return False
        
        try:
            # 检查依赖
            for dep in mod_info.dependencies:
                if dep not in self.loaded_mods:
                    logger.error(f"MOD {mod_info.id} 缺少依赖: {dep}")
                    return False
            
            # 加载内容
            mod_path = Path(mod_info.path)
            contents = []
            
            # 加载各类内容
            content_loaders = {
                ContentType.NPC: ("npcs", self._load_npc),
                ContentType.ITEM: ("items", self._load_item),
                ContentType.SKILL: ("skills", self._load_skill),
                ContentType.LOCATION: ("locations", self._load_location),
                ContentType.EVENT: ("events", self._load_event),
                ContentType.QUEST: ("quests", self._load_quest),
                ContentType.DIALOGUE: ("dialogues", self._load_dialogue),
                ContentType.MONSTER: ("monsters", self._load_monster)
            }
            
            for content_type, (subdir, loader) in content_loaders.items():
                if content_type in mod_info.content_types:
                    content_dir = mod_path / subdir
                    if content_dir.exists():
                        for file_path in content_dir.glob("*.json"):
                            content = loader(file_path, mod_info.id)
                            if content:
                                contents.append(content)
            
            # 保存MOD信息
            self.loaded_mods[mod_info.id] = mod_info
            self.mod_contents[mod_info.id] = contents
            
            # 触发加载回调
            for callback in self.load_callbacks:
                callback(mod_info, contents)
            
            logger.info(f"成功加载MOD: {mod_info.name} v{mod_info.version}")
            return True
            
        except Exception as e:
            logger.error(f"加载MOD {mod_info.id} 失败: {e}")
            for callback in self.error_callbacks:
                callback(mod_info.id, str(e))
            return False
    
    def _load_npc(self, file_path: Path, mod_id: str) -> Optional[ContentEntry]:
        """加载NPC数据"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return ContentEntry(
                id=data["id"],
                type=ContentType.NPC,
                mod_id=mod_id,
                data=data,
                version="1.0",
                tags=data.get("tags", [])
            )
        except Exception as e:
            logger.error(f"加载NPC失败 {file_path}: {e}")
            return None
    
    def _load_item(self, file_path: Path, mod_id: str) -> Optional[ContentEntry]:
        """加载物品数据"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return ContentEntry(
                id=data["id"],
                type=ContentType.ITEM,
                mod_id=mod_id,
                data=data,
                version="1.0",
                tags=data.get("tags", [])
            )
        except Exception as e:
            logger.error(f"加载物品失败 {file_path}: {e}")
            return None
    
    def _load_skill(self, file_path: Path, mod_id: str) -> Optional[ContentEntry]:
        """加载技能数据"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return ContentEntry(
                id=data["id"],
                type=ContentType.SKILL,
                mod_id=mod_id,
                data=data,
                version="1.0",
                tags=data.get("tags", [])
            )
        except Exception as e:
            logger.error(f"加载技能失败 {file_path}: {e}")
            return None
    
    def _load_location(self, file_path: Path, mod_id: str) -> Optional[ContentEntry]:
        """加载地点数据"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return ContentEntry(
                id=data["id"],
                type=ContentType.LOCATION,
                mod_id=mod_id,
                data=data,
                version="1.0",
                tags=data.get("tags", [])
            )
        except Exception as e:
            logger.error(f"加载地点失败 {file_path}: {e}")
            return None
    
    def _load_event(self, file_path: Path, mod_id: str) -> Optional[ContentEntry]:
        """加载事件数据"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return ContentEntry(
                id=data["id"],
                type=ContentType.EVENT,
                mod_id=mod_id,
                data=data,
                version="1.0",
                tags=data.get("tags", [])
            )
        except Exception as e:
            logger.error(f"加载事件失败 {file_path}: {e}")
            return None
    
    def _load_quest(self, file_path: Path, mod_id: str) -> Optional[ContentEntry]:
        """加载任务数据"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return ContentEntry(
                id=data["id"],
                type=ContentType.QUEST,
                mod_id=mod_id,
                data=data,
                version="1.0",
                tags=data.get("tags", [])
            )
        except Exception as e:
            logger.error(f"加载任务失败 {file_path}: {e}")
            return None
    
    def _load_dialogue(self, file_path: Path, mod_id: str) -> Optional[ContentEntry]:
        """加载对话数据"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return ContentEntry(
                id=data["id"],
                type=ContentType.DIALOGUE,
                mod_id=mod_id,
                data=data,
                version="1.0",
                tags=data.get("tags", [])
            )
        except Exception as e:
            logger.error(f"加载对话失败 {file_path}: {e}")
            return None
    
    def _load_monster(self, file_path: Path, mod_id: str) -> Optional[ContentEntry]:
        """加载怪物数据"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return ContentEntry(
                id=data["id"],
                type=ContentType.MONSTER,
                mod_id=mod_id,
                data=data,
                version="1.0",
                tags=data.get("tags", [])
            )
        except Exception as e:
            logger.error(f"加载怪物失败 {file_path}: {e}")
            return None
    
    def unload_mod(self, mod_id: str) -> bool:
        """卸载MOD"""
        if mod_id not in self.loaded_mods:
            return False
        
        # 移除MOD内容
        if mod_id in self.mod_contents:
            del self.mod_contents[mod_id]
        
        # 移除MOD信息
        del self.loaded_mods[mod_id]
        
        logger.info(f"卸载MOD: {mod_id}")
        return True
    
    def get_content_by_type(self, content_type: ContentType) -> List[ContentEntry]:
        """按类型获取内容"""
        results = []
        
        for mod_contents in self.mod_contents.values():
            for content in mod_contents:
                if content.type == content_type:
                    results.append(content)
        
        return results
    
    def get_content_by_id(self, content_id: str) -> Optional[ContentEntry]:
        """通过ID获取内容"""
        for mod_contents in self.mod_contents.values():
            for content in mod_contents:
                if content.id == content_id:
                    return content
        return None


class ContentRegistry:
    """内容注册表"""
    
    def __init__(self):
        self.registry: Dict[ContentType, Dict[str, Any]] = {
            content_type: {} for content_type in ContentType
        }
        self.validators: Dict[ContentType, Callable] = {}
        self.processors: Dict[ContentType, Callable] = {}
    
    def register_validator(self, content_type: ContentType, validator: Callable) -> None:
        """注册内容验证器"""
        self.validators[content_type] = validator
    
    def register_processor(self, content_type: ContentType, processor: Callable) -> None:
        """注册内容处理器"""
        self.processors[content_type] = processor
    
    def register_content(self, content: ContentEntry) -> bool:
        """注册内容"""
        # 验证内容
        if content.type in self.validators:
            if not self.validators[content.type](content):
                logger.error(f"内容验证失败: {content.id}")
                return False
        
        # 处理内容
        if content.type in self.processors:
            processed_data = self.processors[content.type](content)
            if processed_data:
                content.data = processed_data
        
        # 注册到表中
        self.registry[content.type][content.id] = content
        logger.debug(f"注册内容: {content.type.value}/{content.id}")
        return True
    
    def unregister_content(self, content_type: ContentType, content_id: str) -> bool:
        """取消注册内容"""
        if content_id in self.registry[content_type]:
            del self.registry[content_type][content_id]
            return True
        return False
    
    def get_content(self, content_type: ContentType, content_id: str) -> Optional[Any]:
        """获取内容"""
        return self.registry[content_type].get(content_id)
    
    def get_all_content(self, content_type: ContentType) -> Dict[str, Any]:
        """获取某类型的所有内容"""
        return self.registry[content_type].copy()
    
    def search_content(self, query: str, content_type: Optional[ContentType] = None) -> List[ContentEntry]:
        """搜索内容"""
        results = []
        query_lower = query.lower()
        
        types_to_search = [content_type] if content_type else ContentType
        
        for ct in types_to_search:
            for content_id, content in self.registry[ct].items():
                # 搜索ID
                if query_lower in content_id.lower():
                    results.append(content)
                    continue
                
                # 搜索名称
                if isinstance(content, ContentEntry):
                    name = content.data.get("name", "")
                    if query_lower in name.lower():
                        results.append(content)
                        continue
                    
                    # 搜索标签
                    for tag in content.tags:
                        if query_lower in tag.lower():
                            results.append(content)
                            break
        
        return results


class HotUpdateManager:
    """热更新管理器"""
    
    def __init__(self, mod_loader: ModLoader, content_registry: ContentRegistry):
        self.mod_loader = mod_loader
        self.content_registry = content_registry
        self.update_interval = 60  # 检查间隔（秒）
        self.last_check_time = 0
        self.mod_checksums: Dict[str, str] = {}
        self.update_callbacks: List[Callable] = []
    
    def check_updates(self) -> List[str]:
        """检查更新"""
        current_time = time.time()
        if current_time - self.last_check_time < self.update_interval:
            return []
        
        self.last_check_time = current_time
        updated_mods = []
        
        for mod_id, mod_info in self.mod_loader.loaded_mods.items():
            # 重新计算校验和
            new_checksum = self.mod_loader._calculate_checksum(Path(mod_info.path))
            old_checksum = self.mod_checksums.get(mod_id, mod_info.checksum)
            
            if new_checksum != old_checksum:
                logger.info(f"检测到MOD更新: {mod_id}")
                updated_mods.append(mod_id)
                self.mod_checksums[mod_id] = new_checksum
        
        return updated_mods
    
    def apply_updates(self, mod_ids: List[str]) -> Dict[str, bool]:
        """应用更新"""
        results = {}
        
        for mod_id in mod_ids:
            if mod_id in self.mod_loader.loaded_mods:
                mod_info = self.mod_loader.loaded_mods[mod_id]
                
                # 卸载旧版本
                self.mod_loader.unload_mod(mod_id)
                
                # 从注册表中移除旧内容
                if mod_id in self.mod_loader.mod_contents:
                    for content in self.mod_loader.mod_contents[mod_id]:
                        self.content_registry.unregister_content(content.type, content.id)
                
                # 重新加载
                new_mod_info = self.mod_loader._load_mod_info(Path(mod_info.path))
                if new_mod_info:
                    success = self.mod_loader.load_mod(new_mod_info)
                    
                    # 重新注册内容
                    if success and mod_id in self.mod_loader.mod_contents:
                        for content in self.mod_loader.mod_contents[mod_id]:
                            self.content_registry.register_content(content)
                    
                    results[mod_id] = success
                    
                    # 触发更新回调
                    if success:
                        for callback in self.update_callbacks:
                            callback(mod_id, new_mod_info)
                else:
                    results[mod_id] = False
        
        return results


class ModCreator:
    """MOD创建工具"""
    
    def __init__(self, mods_directory: str = "mods"):
        self.mods_directory = Path(mods_directory)
    
    def create_mod(self, mod_id: str, mod_name: str, author: str, description: str) -> bool:
        """创建新MOD"""
        mod_path = self.mods_directory / mod_id
        
        if mod_path.exists():
            logger.error(f"MOD {mod_id} 已存在")
            return False
        
        try:
            # 创建目录结构
            mod_path.mkdir()
            
            # 创建子目录
            subdirs = ["npcs", "items", "skills", "locations", "events", "quests", "dialogues", "monsters"]
            for subdir in subdirs:
                (mod_path / subdir).mkdir()
            
            # 创建MOD信息文件
            mod_info = {
                "id": mod_id,
                "name": mod_name,
                "version": "1.0.0",
                "author": author,
                "description": description,
                "dependencies": [],
                "content_types": []
            }
            
            with open(mod_path / "mod.json", "w", encoding="utf-8") as f:
                json.dump(mod_info, f, ensure_ascii=False, indent=2)
            
            # 创建README
            readme_content = f"""# {mod_name}

作者：{author}

## 描述
{description}

## 内容
- NPCs: 放置在 npcs/ 目录
- 物品: 放置在 items/ 目录
- 技能: 放置在 skills/ 目录
- 地点: 放置在 locations/ 目录
- 事件: 放置在 events/ 目录
- 任务: 放置在 quests/ 目录
- 对话: 放置在 dialogues/ 目录
- 怪物: 放置在 monsters/ 目录

## 使用方法
1. 将MOD文件夹放入游戏的 mods 目录
2. 在游戏中启用MOD
3. 享受新内容！
"""
            
            with open(mod_path / "README.md", "w", encoding="utf-8") as f:
                f.write(readme_content)
            
            logger.info(f"成功创建MOD: {mod_name}")
            return True
            
        except Exception as e:
            logger.error(f"创建MOD失败: {e}")
            return False
    
    def add_content_to_mod(self, mod_id: str, content_type: ContentType, content_data: Dict[str, Any]) -> bool:
        """向MOD添加内容"""
        mod_path = self.mods_directory / mod_id
        
        if not mod_path.exists():
            logger.error(f"MOD {mod_id} 不存在")
            return False
        
        # 确定子目录
        subdir_map = {
            ContentType.NPC: "npcs",
            ContentType.ITEM: "items",
            ContentType.SKILL: "skills",
            ContentType.LOCATION: "locations",
            ContentType.EVENT: "events",
            ContentType.QUEST: "quests",
            ContentType.DIALOGUE: "dialogues",
            ContentType.MONSTER: "monsters"
        }
        
        subdir = subdir_map.get(content_type)
        if not subdir:
            logger.error(f"不支持的内容类型: {content_type}")
            return False
        
        # 保存内容
        content_id = content_data.get("id", f"{content_type.value}_{int(time.time())}")
        file_path = mod_path / subdir / f"{content_id}.json"
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(content_data, f, ensure_ascii=False, indent=2)
            
            # 更新MOD信息
            mod_info_path = mod_path / "mod.json"
            with open(mod_info_path, "r", encoding="utf-8") as f:
                mod_info = json.load(f)
            
            if content_type.value not in mod_info["content_types"]:
                mod_info["content_types"].append(content_type.value)
                
                with open(mod_info_path, "w", encoding="utf-8") as f:
                    json.dump(mod_info, f, ensure_ascii=False, indent=2)
            
            logger.info(f"成功添加内容到MOD {mod_id}: {content_type.value}/{content_id}")
            return True
            
        except Exception as e:
            logger.error(f"添加内容失败: {e}")
            return False


class ContentEcosystem:
    """内容生态系统管理器"""
    
    def __init__(self):
        self.mod_loader = ModLoader()
        self.content_registry = ContentRegistry()
        self.hot_update_manager = HotUpdateManager(self.mod_loader, self.content_registry)
        self.mod_creator = ModCreator()
        
        # 初始化验证器和处理器
        self._init_validators()
        self._init_processors()
        
        # 加载初始MODs
        self.load_all_mods()
    
    def _init_validators(self) -> None:
        """初始化内容验证器"""
        # NPC验证器
        def validate_npc(content: ContentEntry) -> bool:
            required_fields = ["id", "name"]
            return all(field in content.data for field in required_fields)
        
        # 物品验证器
        def validate_item(content: ContentEntry) -> bool:
            required_fields = ["id", "name", "type"]
            return all(field in content.data for field in required_fields)
        
        # 技能验证器
        def validate_skill(content: ContentEntry) -> bool:
            required_fields = ["id", "name", "damage", "mana_cost"]
            return all(field in content.data for field in required_fields)
        
        self.content_registry.register_validator(ContentType.NPC, validate_npc)
        self.content_registry.register_validator(ContentType.ITEM, validate_item)
        self.content_registry.register_validator(ContentType.SKILL, validate_skill)
    
    def _init_processors(self) -> None:
        """初始化内容处理器"""
        # NPC处理器
        def process_npc(content: ContentEntry) -> Dict[str, Any]:
            data = content.data.copy()
            # 添加默认值
            data.setdefault("level", 1)
            data.setdefault("faction", "neutral")
            return data
        
        # 物品处理器
        def process_item(content: ContentEntry) -> Dict[str, Any]:
            data = content.data.copy()
            # 添加默认值
            data.setdefault("stackable", True)
            data.setdefault("tradeable", True)
            return data
        
        self.content_registry.register_processor(ContentType.NPC, process_npc)
        self.content_registry.register_processor(ContentType.ITEM, process_item)
    
    def load_all_mods(self) -> None:
        """加载所有MODs"""
        mods = self.mod_loader.scan_mods()
        
        # 按加载顺序排序
        mods.sort(key=lambda m: m.load_order)
        
        for mod in mods:
            if mod.enabled:
                success = self.mod_loader.load_mod(mod)
                
                # 注册内容
                if success and mod.id in self.mod_loader.mod_contents:
                    for content in self.mod_loader.mod_contents[mod.id]:
                        self.content_registry.register_content(content)
    
    def check_and_apply_updates(self) -> Dict[str, bool]:
        """检查并应用更新"""
        updated_mods = self.hot_update_manager.check_updates()
        if updated_mods:
            return self.hot_update_manager.apply_updates(updated_mods)
        return {}
    
    def create_new_mod(self, mod_id: str, mod_name: str, author: str, description: str) -> bool:
        """创建新MOD"""
        return self.mod_creator.create_mod(mod_id, mod_name, author, description)
    
    def get_ecosystem_stats(self) -> Dict[str, Any]:
        """获取生态系统统计"""
        stats = {
            "loaded_mods": len(self.mod_loader.loaded_mods),
            "total_content": 0,
            "content_by_type": {}
        }
        
        for content_type in ContentType:
            count = len(self.content_registry.get_all_content(content_type))
            stats["content_by_type"][content_type.value] = count
            stats["total_content"] += count
        
        return stats


# 全局实例
content_ecosystem = ContentEcosystem()
