"""
内容生态系统模块
管理游戏内容的创建、分发和更新
"""

from enum import Enum
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import json
import os


class ContentType(Enum):
    """内容类型"""
    MOD = "mod"
    SCRIPT = "script"
    ASSET = "asset"
    CONFIG = "config"
    TRANSLATION = "translation"


@dataclass
class ModInfo:
    """模组信息"""
    id: str
    name: str
    version: str
    author: str
    description: str
    dependencies: List[str]
    content_type: ContentType
    enabled: bool = True


@dataclass
class ContentEntry:
    """内容条目"""
    id: str
    name: str
    type: ContentType
    version: str
    data: Dict
    metadata: Dict


class ContentRegistry:
    """内容注册表"""
    
    def __init__(self):
        self.entries: Dict[str, ContentEntry] = {}
        self.types: Dict[ContentType, Set[str]] = {t: set() for t in ContentType}
    
    def register(self, entry: ContentEntry):
        """注册内容"""
        self.entries[entry.id] = entry
        self.types[entry.type].add(entry.id)
    
    def get(self, content_id: str) -> Optional[ContentEntry]:
        """获取内容"""
        return self.entries.get(content_id)
    
    def get_by_type(self, content_type: ContentType) -> List[ContentEntry]:
        """按类型获取内容"""
        return [self.entries[id] for id in self.types.get(content_type, [])]


class ModLoader:
    """模组加载器"""
    
    def __init__(self, mods_path: str = "mods"):
        self.mods_path = mods_path
        self.loaded_mods: Dict[str, ModInfo] = {}
        self.registry = ContentRegistry()
    
    def load_mod(self, mod_path: str):
        """加载模组"""
        info_path = os.path.join(mod_path, "mod.json")
        if not os.path.exists(info_path):
            return None
            
        with open(info_path, 'r', encoding='utf-8') as f:
            mod_data = json.load(f)
            
        mod_info = ModInfo(**mod_data)
        self.loaded_mods[mod_info.id] = mod_info
        
        # 加载模组内容
        self._load_mod_content(mod_path, mod_info)
        
        return mod_info
    
    def _load_mod_content(self, mod_path: str, mod_info: ModInfo):
        """加载模组内容"""
        # 这里可以扩展加载各种类型的内容
        pass
    
    def enable_mod(self, mod_id: str):
        """启用模组"""
        if mod_id in self.loaded_mods:
            self.loaded_mods[mod_id].enabled = True
    
    def disable_mod(self, mod_id: str):
        """禁用模组"""
        if mod_id in self.loaded_mods:
            self.loaded_mods[mod_id].enabled = False


class ModCreator:
    """模组创建器"""
    
    def __init__(self):
        self.template = {
            "id": "",
            "name": "",
            "version": "1.0.0",
            "author": "",
            "description": "",
            "dependencies": [],
            "content_type": "mod"
        }
    
    def create_mod(self, mod_info: Dict) -> ModInfo:
        """创建模组"""
        mod_data = self.template.copy()
        mod_data.update(mod_info)
        return ModInfo(**mod_data)
    
    def save_mod(self, mod_info: ModInfo, path: str):
        """保存模组"""
        os.makedirs(path, exist_ok=True)
        info_path = os.path.join(path, "mod.json")
        
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump({
                "id": mod_info.id,
                "name": mod_info.name,
                "version": mod_info.version,
                "author": mod_info.author,
                "description": mod_info.description,
                "dependencies": mod_info.dependencies,
                "content_type": mod_info.content_type.value
            }, f, ensure_ascii=False, indent=2)


class HotUpdateManager:
    """热更新管理器"""
    
    def __init__(self):
        self.update_queue: List[ContentEntry] = []
        self.update_callbacks = []
    
    def check_updates(self):
        """检查更新"""
        # 这里可以实现检查服务器更新的逻辑
        pass
    
    def apply_update(self, content: ContentEntry):
        """应用更新"""
        self.update_queue.append(content)
        for callback in self.update_callbacks:
            callback(content)
    
    def register_update_callback(self, callback):
        """注册更新回调"""
        self.update_callbacks.append(callback)


class ContentEcosystem:
    """内容生态系统"""
    
    def __init__(self):
        self.registry = ContentRegistry()
        self.mod_loader = ModLoader()
        self.mod_creator = ModCreator()
        self.update_manager = HotUpdateManager()
    
    def initialize(self):
        """初始化"""
        # 加载默认内容
        self._load_default_content()
        
        # 加载模组
        if os.path.exists("mods"):
            for mod_dir in os.listdir("mods"):
                mod_path = os.path.join("mods", mod_dir)
                if os.path.isdir(mod_path):
                    self.mod_loader.load_mod(mod_path)
    
    def _load_default_content(self):
        """加载默认内容"""
        # 这里可以加载游戏自带的内容
        pass
    
    def register_content(self, content: ContentEntry):
        """注册内容"""
        self.registry.register(content)
    
    def get_content(self, content_id: str) -> Optional[ContentEntry]:
        """获取内容"""
        return self.registry.get(content_id)
    
    def create_mod(self, mod_info: Dict) -> ModInfo:
        """创建模组"""
        return self.mod_creator.create_mod(mod_info)
    
    def save_mod(self, mod_info: ModInfo, path: str):
        """保存模组"""
        self.mod_creator.save_mod(mod_info, path)


# 全局实例
content_ecosystem = ContentEcosystem()
