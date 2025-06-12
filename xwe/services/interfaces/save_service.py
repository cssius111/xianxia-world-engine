"""
存档服务接口定义
负责游戏存档的创建、管理、加载和云同步
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SaveType(Enum):
    """存档类型"""
    MANUAL = "manual"          # 手动存档
    AUTO = "auto"              # 自动存档
    QUICK = "quick"            # 快速存档
    CHECKPOINT = "checkpoint"   # 检查点存档
    CLOUD = "cloud"            # 云存档


@dataclass
class SaveInfo:
    """存档信息"""
    id: str
    name: str
    type: SaveType
    created_at: datetime
    updated_at: datetime
    
    # 游戏信息
    player_name: str
    player_level: int
    player_realm: str
    location: str
    play_time: float  # 游戏时长（秒）
    
    # 存档元数据
    version: str
    size: int  # 字节
    description: str = ""
    thumbnail: Optional[str] = None  # 缩略图路径
    is_corrupted: bool = False
    is_cloud_synced: bool = False
    
    # 统计信息
    save_count: int = 1  # 该位置的保存次数
    load_count: int = 0  # 加载次数
    
    @property
    def formatted_play_time(self) -> str:
        """格式化的游戏时长"""
        hours = int(self.play_time // 3600)
        minutes = int((self.play_time % 3600) // 60)
        return f"{hours}小时{minutes}分钟"


@dataclass
class SaveData:
    """存档数据"""
    info: SaveInfo
    game_state: Dict[str, Any]
    player_data: Dict[str, Any]
    world_data: Dict[str, Any]
    system_data: Dict[str, Any] = field(default_factory=dict)
    mod_data: Dict[str, Any] = field(default_factory=dict)
    
    def get_size(self) -> int:
        """计算存档大小"""
        import json
        data_str = json.dumps({
            'game_state': self.game_state,
            'player_data': self.player_data,
            'world_data': self.world_data,
            'system_data': self.system_data,
            'mod_data': self.mod_data
        })
        return len(data_str.encode('utf-8'))


class ISaveService(ABC):
    """
    存档服务接口
    
    主要职责：
    1. 存档的创建和保存
    2. 存档的加载和恢复
    3. 存档的管理（列表、删除、重命名）
    4. 自动存档和快速存档
    5. 存档的导入导出
    6. 云存档同步
    7. 存档完整性检查
    """
    
    # ========== 存档创建和保存 ==========
    
    @abstractmethod
    def create_save(self, name: str, save_data: Dict[str, Any], 
                    save_type: SaveType = SaveType.MANUAL) -> str:
        """
        创建新存档
        
        Args:
            name: 存档名称
            save_data: 要保存的数据
            save_type: 存档类型
            
        Returns:
            str: 存档ID
            
        Example:
            >>> save_id = save_service.create_save(
            ...     "第一章完成",
            ...     game.get_save_data(),
            ...     SaveType.MANUAL
            ... )
        """
        pass
        
    @abstractmethod
    def save(self, save_id: str, save_data: Dict[str, Any]) -> bool:
        """
        覆盖保存到现有存档
        
        Args:
            save_id: 存档ID
            save_data: 要保存的数据
            
        Returns:
            bool: 是否保存成功
        """
        pass
        
    @abstractmethod
    def quick_save(self, save_data: Dict[str, Any]) -> str:
        """
        快速保存
        
        Args:
            save_data: 要保存的数据
            
        Returns:
            str: 快速存档ID
        """
        pass
        
    @abstractmethod
    def auto_save(self, save_data: Dict[str, Any]) -> str:
        """
        自动保存
        
        Args:
            save_data: 要保存的数据
            
        Returns:
            str: 自动存档ID
        """
        pass
        
    # ========== 存档加载 ==========
    
    @abstractmethod
    def load_save(self, save_id: str) -> Optional[SaveData]:
        """
        加载存档
        
        Args:
            save_id: 存档ID
            
        Returns:
            SaveData: 存档数据，如果不存在或损坏返回None
        """
        pass
        
    @abstractmethod
    def quick_load(self) -> Optional[SaveData]:
        """
        加载快速存档
        
        Returns:
            SaveData: 快速存档数据
        """
        pass
        
    @abstractmethod
    def load_latest_save(self) -> Optional[SaveData]:
        """
        加载最新的存档
        
        Returns:
            SaveData: 最新存档数据
        """
        pass
        
    @abstractmethod
    def load_auto_save(self) -> Optional[SaveData]:
        """
        加载自动存档
        
        Returns:
            SaveData: 自动存档数据
        """
        pass
        
    # ========== 存档管理 ==========
    
    @abstractmethod
    def list_saves(self, save_type: Optional[SaveType] = None) -> List[SaveInfo]:
        """
        列出所有存档
        
        Args:
            save_type: 筛选存档类型，None表示所有类型
            
        Returns:
            List[SaveInfo]: 存档信息列表
        """
        pass
        
    @abstractmethod
    def get_save_info(self, save_id: str) -> Optional[SaveInfo]:
        """
        获取存档信息
        
        Args:
            save_id: 存档ID
            
        Returns:
            SaveInfo: 存档信息
        """
        pass
        
    @abstractmethod
    def delete_save(self, save_id: str) -> bool:
        """
        删除存档
        
        Args:
            save_id: 存档ID
            
        Returns:
            bool: 是否删除成功
        """
        pass
        
    @abstractmethod
    def rename_save(self, save_id: str, new_name: str) -> bool:
        """
        重命名存档
        
        Args:
            save_id: 存档ID
            new_name: 新名称
            
        Returns:
            bool: 是否重命名成功
        """
        pass
        
    @abstractmethod
    def duplicate_save(self, save_id: str, new_name: str) -> Optional[str]:
        """
        复制存档
        
        Args:
            save_id: 原存档ID
            new_name: 新存档名称
            
        Returns:
            str: 新存档ID，失败返回None
        """
        pass
        
    # ========== 存档设置 ==========
    
    @abstractmethod
    def set_max_saves(self, max_saves: int) -> bool:
        """
        设置最大存档数量
        
        Args:
            max_saves: 最大数量
            
        Returns:
            bool: 是否设置成功
        """
        pass
        
    @abstractmethod
    def set_auto_save_interval(self, interval: int) -> bool:
        """
        设置自动存档间隔
        
        Args:
            interval: 间隔时间（秒）
            
        Returns:
            bool: 是否设置成功
        """
        pass
        
    @abstractmethod
    def enable_auto_save(self, enabled: bool) -> bool:
        """
        启用/禁用自动存档
        
        Args:
            enabled: 是否启用
            
        Returns:
            bool: 是否设置成功
        """
        pass
        
    # ========== 存档导入导出 ==========
    
    @abstractmethod
    def export_save(self, save_id: str, filepath: str) -> bool:
        """
        导出存档到文件
        
        Args:
            save_id: 存档ID
            filepath: 导出路径
            
        Returns:
            bool: 是否导出成功
        """
        pass
        
    @abstractmethod
    def import_save(self, filepath: str, name: str = None) -> Optional[str]:
        """
        从文件导入存档
        
        Args:
            filepath: 导入路径
            name: 存档名称（可选）
            
        Returns:
            str: 导入的存档ID，失败返回None
        """
        pass
        
    @abstractmethod
    def export_all_saves(self, directory: str) -> int:
        """
        导出所有存档
        
        Args:
            directory: 导出目录
            
        Returns:
            int: 导出的存档数量
        """
        pass
        
    # ========== 云存档 ==========
    
    @abstractmethod
    def sync_to_cloud(self, save_id: str) -> bool:
        """
        同步存档到云端
        
        Args:
            save_id: 存档ID
            
        Returns:
            bool: 是否同步成功
        """
        pass
        
    @abstractmethod
    def sync_from_cloud(self, cloud_save_id: str) -> Optional[str]:
        """
        从云端同步存档
        
        Args:
            cloud_save_id: 云存档ID
            
        Returns:
            str: 本地存档ID，失败返回None
        """
        pass
        
    @abstractmethod
    def list_cloud_saves(self) -> List[SaveInfo]:
        """
        列出云端存档
        
        Returns:
            List[SaveInfo]: 云存档列表
        """
        pass
        
    @abstractmethod
    def enable_cloud_sync(self, enabled: bool) -> bool:
        """
        启用/禁用云同步
        
        Args:
            enabled: 是否启用
            
        Returns:
            bool: 是否设置成功
        """
        pass
        
    # ========== 存档完整性 ==========
    
    @abstractmethod
    def verify_save(self, save_id: str) -> bool:
        """
        验证存档完整性
        
        Args:
            save_id: 存档ID
            
        Returns:
            bool: 存档是否完整
        """
        pass
        
    @abstractmethod
    def repair_save(self, save_id: str) -> bool:
        """
        修复损坏的存档
        
        Args:
            save_id: 存档ID
            
        Returns:
            bool: 是否修复成功
        """
        pass
        
    @abstractmethod
    def create_backup(self, save_id: str) -> Optional[str]:
        """
        创建存档备份
        
        Args:
            save_id: 存档ID
            
        Returns:
            str: 备份ID，失败返回None
        """
        pass
        
    # ========== 存档统计 ==========
    
    @abstractmethod
    def get_save_statistics(self) -> Dict[str, Any]:
        """
        获取存档统计信息
        
        Returns:
            Dict: 统计信息
                - total_saves: 总存档数
                - total_size: 总大小（字节）
                - saves_by_type: 各类型存档数
                - corrupted_saves: 损坏的存档数
        """
        pass
        
    @abstractmethod
    def clean_old_saves(self, days: int = 30) -> int:
        """
        清理旧存档
        
        Args:
            days: 保留最近N天的存档
            
        Returns:
            int: 清理的存档数量
        """
        pass
        
    @abstractmethod
    def get_save_directory(self) -> str:
        """
        获取存档目录路径
        
        Returns:
            str: 存档目录路径
        """
        pass
