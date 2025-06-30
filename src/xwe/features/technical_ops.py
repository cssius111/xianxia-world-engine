"""
技术运维系统
处理游戏的技术层面功能，如存档、性能监控等
"""

import json
import os
import time
import psutil
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import gzip
import pickle


class TechnicalOps:
    """
    技术运维管理器
    
    负责游戏的技术层面操作
    """
    
    def __init__(self, save_dir: str = "saves"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        # 性能监控数据
        self.performance_data = {
            "frame_times": [],
            "memory_usage": [],
            "cpu_usage": [],
            "api_response_times": []
        }
        
        # 日志配置
        self.logger = logging.getLogger("xwe.technical")
        
        # 自动保存配置
        self.auto_save_enabled = True
        self.auto_save_interval = 300  # 5分钟
        self.last_auto_save = time.time()
        
    def save_game(self, game_state: Any, filename: Optional[str] = None) -> bool:
        """
        保存游戏
        
        Args:
            game_state: 游戏状态对象
            filename: 保存文件名（不含扩展名）
            
        Returns:
            是否保存成功
        """
        try:
            if filename is None:
                filename = f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            filepath = self.save_dir / f"{filename}.json"
            
            # 准备保存数据
            save_data = {
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "game_state": self._serialize_game_state(game_state)
            }
            
            # 保存为JSON（可读格式）
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            # 同时保存压缩版本（节省空间）
            compressed_path = self.save_dir / f"{filename}.gz"
            with gzip.open(compressed_path, 'wb') as f:
                pickle.dump(save_data, f)
            
            self.logger.info(f"游戏已保存到: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存游戏失败: {e}")
            return False
    
    def load_game(self, filename: str) -> Optional[Any]:
        """
        加载游戏
        
        Args:
            filename: 保存文件名（不含扩展名）
            
        Returns:
            游戏状态对象，如果失败返回None
        """
        try:
            # 优先尝试加载压缩版本
            compressed_path = self.save_dir / f"{filename}.gz"
            if compressed_path.exists():
                with gzip.open(compressed_path, 'rb') as f:
                    save_data = pickle.load(f)
            else:
                # 加载JSON版本
                filepath = self.save_dir / f"{filename}.json"
                with open(filepath, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
            
            # 反序列化游戏状态
            game_state = self._deserialize_game_state(save_data["game_state"])
            
            self.logger.info(f"游戏已加载: {filename}")
            return game_state
            
        except Exception as e:
            self.logger.error(f"加载游戏失败: {e}")
            return None
    
    def list_saves(self) -> List[Dict[str, Any]]:
        """列出所有存档"""
        saves = []
        
        for filepath in self.save_dir.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                saves.append({
                    "filename": filepath.stem,
                    "timestamp": data.get("timestamp", "unknown"),
                    "size": filepath.stat().st_size,
                    "version": data.get("version", "unknown")
                })
            except:
                pass
        
        # 按时间排序
        saves.sort(key=lambda x: x["timestamp"], reverse=True)
        return saves
    
    def delete_save(self, filename: str) -> bool:
        """删除存档"""
        try:
            # 删除JSON文件
            json_path = self.save_dir / f"{filename}.json"
            if json_path.exists():
                json_path.unlink()
            
            # 删除压缩文件
            gz_path = self.save_dir / f"{filename}.gz"
            if gz_path.exists():
                gz_path.unlink()
            
            return True
        except Exception as e:
            self.logger.error(f"删除存档失败: {e}")
            return False
    
    def check_auto_save(self, game_state: Any) -> bool:
        """检查并执行自动保存"""
        if not self.auto_save_enabled:
            return False
        
        current_time = time.time()
        if current_time - self.last_auto_save >= self.auto_save_interval:
            success = self.save_game(game_state, "autosave")
            if success:
                self.last_auto_save = current_time
            return success
        
        return False
    
    def monitor_performance(self) -> Dict[str, float]:
        """监控性能指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # 内存使用
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_mb = memory.used / 1024 / 1024
            
            # 记录数据
            self.performance_data["cpu_usage"].append(cpu_percent)
            self.performance_data["memory_usage"].append(memory_mb)
            
            # 保持最近100个数据点
            for key in self.performance_data:
                if len(self.performance_data[key]) > 100:
                    self.performance_data[key] = self.performance_data[key][-100:]
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_mb": memory_mb
            }
            
        except Exception as e:
            self.logger.error(f"性能监控失败: {e}")
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "memory_mb": 0
            }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        def calculate_avg(data_list):
            return sum(data_list) / len(data_list) if data_list else 0
        
        return {
            "avg_cpu": calculate_avg(self.performance_data["cpu_usage"]),
            "avg_memory": calculate_avg(self.performance_data["memory_usage"]),
            "avg_frame_time": calculate_avg(self.performance_data["frame_times"]),
            "avg_api_response": calculate_avg(self.performance_data["api_response_times"])
        }
    
    def optimize_game_data(self, game_state: Any) -> None:
        """优化游戏数据（清理无用数据、压缩等）"""
        # 清理过期的临时数据
        if hasattr(game_state, 'temp_data'):
            game_state.temp_data.clear()
        
        # 清理过老的日志
        if hasattr(game_state, 'logs') and len(game_state.logs) > 1000:
            game_state.logs = game_state.logs[-500:]  # 保留最近500条
        
        # 压缩聊天记录
        if hasattr(game_state, 'chat_history') and len(game_state.chat_history) > 200:
            game_state.chat_history = game_state.chat_history[-100:]
    
    def export_game_data(self, game_state: Any, format: str = "json") -> Optional[str]:
        """
        导出游戏数据
        
        Args:
            game_state: 游戏状态
            format: 导出格式 (json, csv, etc.)
            
        Returns:
            导出文件路径
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if format == "json":
                export_path = self.save_dir / f"export_{timestamp}.json"
                data = self._serialize_game_state(game_state)
                
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                return str(export_path)
            
            # 可以添加其他格式的支持
            
        except Exception as e:
            self.logger.error(f"导出数据失败: {e}")
            return None
    
    def _serialize_game_state(self, game_state: Any) -> Dict[str, Any]:
        """序列化游戏状态"""
        # 这里简化处理，实际应该根据具体的游戏状态结构来序列化
        if hasattr(game_state, 'to_dict'):
            return game_state.to_dict()
        elif hasattr(game_state, '__dict__'):
            return {
                k: v for k, v in game_state.__dict__.items()
                if not k.startswith('_') and not callable(v)
            }
        else:
            return {"data": str(game_state)}
    
    def _deserialize_game_state(self, data: Dict[str, Any]) -> Any:
        """反序列化游戏状态"""
        # 这里简化处理，实际应该根据具体的游戏状态结构来反序列化
        # 可能需要导入GameState类并调用from_dict方法
        return data

    def run_diagnostics(self) -> Dict[str, Any]:
        """运行诊断检查"""
        diagnostics = {
            "save_dir_exists": self.save_dir.exists(),
            "save_dir_writable": os.access(self.save_dir, os.W_OK),
            "save_count": len(list(self.save_dir.glob("*.json"))),
            "disk_space_mb": psutil.disk_usage(str(self.save_dir)).free / 1024 / 1024,
            "python_version": os.sys.version,
            "platform": os.sys.platform
        }

        return diagnostics


# ---------------------------------------------------------------------------
# 以下类和函数目前尚未完整实现，仅提供占位实现以避免导入错误
# ---------------------------------------------------------------------------


class AutoBackupManager:
    """AUTO-STUB：自动备份管理器"""

    pass


class ErrorHandler:
    """AUTO-STUB：技术错误处理器"""

    pass


class ErrorLog:
    """AUTO-STUB：错误日志记录"""

    pass


class PerformanceMonitor:
    """AUTO-STUB：性能监控器"""

    pass


class SaveGame:
    """AUTO-STUB：存档对象"""

    pass


class SaveManager:
    """AUTO-STUB：存档管理器"""

    pass


class TechnicalOpsSystem:
    """AUTO-STUB：技术运维系统入口"""

    def __init__(self):
        self.ops = TechnicalOps()


tech_ops_system = TechnicalOpsSystem()


def integrate_technical_features(game: Any) -> None:
    """AUTO-STUB：将技术运维功能整合到游戏对象"""

    game.tech_ops_system = tech_ops_system

