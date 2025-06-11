"""
存档服务
负责游戏存档的管理
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import os
import json
import time
from pathlib import Path

from . import ServiceBase, ServiceContainer


class ISaveService(ABC):
    """存档服务接口"""
    
    @abstractmethod
    def create_save(self, save_name: str, save_data: Dict[str, Any]) -> str:
        """创建存档"""
        pass
        
    @abstractmethod
    def load_save(self, save_id: str) -> Optional[Dict[str, Any]]:
        """加载存档"""
        pass
        
    @abstractmethod
    def update_save(self, save_id: str, save_data: Dict[str, Any]) -> bool:
        """更新存档"""
        pass
        
    @abstractmethod
    def delete_save(self, save_id: str) -> bool:
        """删除存档"""
        pass
        
    @abstractmethod
    def list_saves(self) -> List[Dict[str, Any]]:
        """列出所有存档"""
        pass
        
    @abstractmethod
    def get_save_info(self, save_id: str) -> Optional[Dict[str, Any]]:
        """获取存档信息"""
        pass


class SaveService(ServiceBase[ISaveService], ISaveService):
    """存档服务实现"""
    
    def __init__(self, container: ServiceContainer):
        super().__init__(container)
        self._save_dir = Path('saves')
        self._max_saves = 10
        
    def _do_initialize(self) -> None:
        """初始化服务"""
        # 确保存档目录存在
        self._save_dir.mkdir(exist_ok=True)
        
    def create_save(self, save_name: str, save_data: Dict[str, Any]) -> str:
        """创建存档"""
        # 生成存档ID
        save_id = f"save_{int(time.time())}_{os.urandom(4).hex()}"
        
        # 构建完整存档数据
        full_save_data = {
            'id': save_id,
            'name': save_name,
            'created_at': time.time(),
            'modified_at': time.time(),
            'version': '1.0.0',
            'data': save_data
        }
        
        # 保存到文件
        save_path = self._save_dir / f"{save_id}.json"
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(full_save_data, f, ensure_ascii=False, indent=2)
            
        self.logger.info(f"Created save: {save_name} (ID: {save_id})")
        
        # 检查存档数量限制
        self._check_save_limit()
        
        return save_id
        
    def load_save(self, save_id: str) -> Optional[Dict[str, Any]]:
        """加载存档"""
        save_path = self._save_dir / f"{save_id}.json"
        
        if not save_path.exists():
            self.logger.warning(f"Save not found: {save_id}")
            return None
            
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
                
            self.logger.info(f"Loaded save: {save_data.get('name')} (ID: {save_id})")
            return save_data.get('data', {})
            
        except Exception as e:
            self.logger.error(f"Failed to load save {save_id}: {e}")
            return None
            
    def update_save(self, save_id: str, save_data: Dict[str, Any]) -> bool:
        """更新存档"""
        save_path = self._save_dir / f"{save_id}.json"
        
        if not save_path.exists():
            return False
            
        try:
            # 读取现有存档
            with open(save_path, 'r', encoding='utf-8') as f:
                full_save_data = json.load(f)
                
            # 更新数据
            full_save_data['data'] = save_data
            full_save_data['modified_at'] = time.time()
            
            # 保存回文件
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(full_save_data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Updated save: {save_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update save {save_id}: {e}")
            return False
            
    def delete_save(self, save_id: str) -> bool:
        """删除存档"""
        save_path = self._save_dir / f"{save_id}.json"
        
        if not save_path.exists():
            return False
            
        try:
            save_path.unlink()
            self.logger.info(f"Deleted save: {save_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete save {save_id}: {e}")
            return False
            
    def list_saves(self) -> List[Dict[str, Any]]:
        """列出所有存档"""
        saves = []
        
        for save_file in self._save_dir.glob("save_*.json"):
            try:
                with open(save_file, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                    
                saves.append({
                    'id': save_data['id'],
                    'name': save_data['name'],
                    'created_at': save_data['created_at'],
                    'modified_at': save_data['modified_at']
                })
                
            except Exception as e:
                self.logger.error(f"Failed to read save file {save_file}: {e}")
                continue
                
        # 按修改时间排序
        saves.sort(key=lambda x: x['modified_at'], reverse=True)
        
        return saves
        
    def get_save_info(self, save_id: str) -> Optional[Dict[str, Any]]:
        """获取存档信息"""
        save_path = self._save_dir / f"{save_id}.json"
        
        if not save_path.exists():
            return None
            
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
                
            # 提取基本信息
            info = {
                'id': save_data['id'],
                'name': save_data['name'],
                'created_at': save_data['created_at'],
                'modified_at': save_data['modified_at'],
                'version': save_data.get('version', 'unknown'),
                'size': save_path.stat().st_size
            }
            
            # 提取游戏信息
            game_data = save_data.get('data', {})
            if 'player' in game_data:
                player_data = game_data['player']
                info['player_info'] = {
                    'name': player_data.get('name', '未知'),
                    'level': player_data.get('level', 1),
                    'realm': player_data.get('realm', '炼气期')
                }
                
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to get save info {save_id}: {e}")
            return None
            
    def _check_save_limit(self) -> None:
        """检查并清理超出限制的存档"""
        saves = self.list_saves()
        
        if len(saves) > self._max_saves:
            # 删除最旧的存档
            saves_to_delete = saves[self._max_saves:]
            
            for save_info in saves_to_delete:
                self.delete_save(save_info['id'])
                self.logger.info(f"Auto-deleted old save: {save_info['name']}")
