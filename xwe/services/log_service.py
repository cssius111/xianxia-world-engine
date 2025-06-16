"""
日志服务
负责游戏日志的记录、查询和管理
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import time
import json
import logging
from collections import deque
from enum import Enum
import threading
from pathlib import Path
import sys
from datetime import datetime
import uuid

from xwe.services import ServiceBase, ServiceContainer


class LogLevel(Enum):
    """日志级别"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SYSTEM = "system"
    COMBAT = "combat"
    ACHIEVEMENT = "achievement"
    CHAT = "chat"
    TRADE = "trade"


@dataclass
class LogEntry:
    """日志条目"""
    id: int
    timestamp: float
    level: LogLevel
    message: str
    category: str = "general"
    player_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'level': self.level.value,
            'category': self.category,
            'message': self.message,
            'player_id': self.player_id,
            'metadata': self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogEntry':
        """从字典创建"""
        data = data.copy()
        data['level'] = LogLevel(data['level'])
        return cls(**data)


@dataclass
class LogFilter:
    """日志过滤器"""
    levels: Optional[List[LogLevel]] = None
    categories: Optional[List[str]] = None
    player_id: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    search_text: Optional[str] = None
    
    def matches(self, entry: LogEntry) -> bool:
        """检查日志条目是否匹配过滤器"""
        # 级别过滤
        if self.levels and entry.level not in self.levels:
            return False
            
        # 类别过滤
        if self.categories and entry.category not in self.categories:
            return False
            
        # 玩家过滤
        if self.player_id and entry.player_id != self.player_id:
            return False
            
        # 时间过滤
        if self.start_time and entry.timestamp < self.start_time:
            return False
            
        if self.end_time and entry.timestamp > self.end_time:
            return False
            
        # 文本搜索
        if self.search_text and self.search_text.lower() not in entry.message.lower():
            return False
            
        return True


class ILogService(ABC):
    """日志服务接口"""
    
    @abstractmethod
    def log(self, level: LogLevel, message: str, **kwargs) -> int:
        """记录日志"""
        pass
        
    @abstractmethod
    def log_debug(self, message: str, **kwargs) -> int:
        """记录调试日志"""
        pass
        
    @abstractmethod
    def log_info(self, message: str, **kwargs) -> int:
        """记录信息日志"""
        pass
        
    @abstractmethod
    def log_warning(self, message: str, **kwargs) -> int:
        """记录警告日志"""
        pass
        
    @abstractmethod
    def log_error(self, message: str, **kwargs) -> int:
        """记录错误日志"""
        pass
        
    @abstractmethod
    def log_combat(self, message: str, **kwargs) -> int:
        """记录战斗日志"""
        pass
        
    @abstractmethod
    def log_achievement(self, message: str, **kwargs) -> int:
        """记录成就日志"""
        pass
        
    @abstractmethod
    def get_logs(self, filter: Optional[LogFilter] = None, limit: int = 100, 
                 offset: int = 0) -> List[LogEntry]:
        """获取日志"""
        pass
        
    @abstractmethod
    def get_recent_logs(self, limit: int = 50) -> List[LogEntry]:
        """获取最近的日志"""
        pass
        
    @abstractmethod
    def clear_logs(self, before_timestamp: Optional[float] = None) -> int:
        """清理日志"""
        pass
        
    @abstractmethod
    def export_logs(self, filepath: Path, filter: Optional[LogFilter] = None) -> bool:
        """导出日志"""
        pass
        
    @abstractmethod
    def get_log_statistics(self) -> Dict[str, Any]:
        """获取日志统计信息"""
        pass


class LogService(ServiceBase[ILogService], ILogService):
    """日志服务实现"""
    
    def __init__(self, container: ServiceContainer) -> None:
        super().__init__(container)
        self._logs: deque = deque(maxlen=10000)
        self._log_id_counter = 0
        self._lock = threading.RLock()
        self._log_file: Optional[Path] = None
        self._file_logger: Optional[logging.Logger] = None
        
    def _do_initialize(self) -> None:
        """初始化服务"""
        # 设置文件日志
        self._setup_file_logging()
        
        # 记录启动日志
        self.log_info("Log service initialized")
        
    def _setup_file_logging(self) -> None:
        """设置文件日志"""
        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 创建日志文件
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self._log_file = log_dir / f"game_{timestamp}.log"
        
        # 配置文件logger
        self._file_logger = logging.getLogger("GameLog")
        self._file_logger.setLevel(logging.DEBUG)
        
        # 添加文件处理器
        file_handler = logging.FileHandler(self._log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 设置格式
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        self._file_logger.addHandler(file_handler)
        
    def log(self, level: LogLevel, message: str, **kwargs) -> int:
        """记录日志"""
        with self._lock:
            # 生成日志ID
            self._log_id_counter += 1
            log_id = self._log_id_counter
            
            # 创建日志条目
            entry = LogEntry(
                id=log_id,
                timestamp=time.time(),
                level=level,
                message=message,
                category=kwargs.get('category', 'general'),
                player_id=kwargs.get('player_id'),
                metadata=kwargs.get('metadata', {})
            )
            
            # 添加到内存日志
            self._logs.append(entry)
            
            # 写入文件
            if self._file_logger:
                log_level = getattr(logging, level.value.upper(), logging.INFO)
                self._file_logger.log(log_level, f"[{entry.category}] {message}")
                
            return log_id
            
    def log_debug(self, message: str, **kwargs) -> int:
        """记录调试日志"""
        return self.log(LogLevel.DEBUG, message, **kwargs)
        
    def log_info(self, message: str, **kwargs) -> int:
        """记录信息日志"""
        return self.log(LogLevel.INFO, message, **kwargs)
        
    def log_warning(self, message: str, **kwargs) -> int:
        """记录警告日志"""
        return self.log(LogLevel.WARNING, message, **kwargs)
        
    def log_error(self, message: str, **kwargs) -> int:
        """记录错误日志"""
        return self.log(LogLevel.ERROR, message, **kwargs)
        
    def log_combat(self, message: str, **kwargs) -> int:
        """记录战斗日志"""
        kwargs['category'] = 'combat'
        return self.log(LogLevel.COMBAT, message, **kwargs)
        
    def log_achievement(self, message: str, **kwargs) -> int:
        """记录成就日志"""
        kwargs['category'] = 'achievement'
        return self.log(LogLevel.ACHIEVEMENT, message, **kwargs)
        
    def get_logs(self, filter: Optional[LogFilter] = None, limit: int = 100,
                 offset: int = 0) -> List[LogEntry]:
        """获取日志"""
        with self._lock:
            # 应用过滤器
            if filter:
                filtered_logs = [log for log in self._logs if filter.matches(log)]
            else:
                filtered_logs = list(self._logs)
                
            # 应用分页
            start = offset
            end = offset + limit
            
            return filtered_logs[start:end]
            
    def get_recent_logs(self, limit: int = 50) -> List[LogEntry]:
        """获取最近的日志"""
        with self._lock:
            # 获取最后N条日志
            if len(self._logs) <= limit:
                return list(self._logs)
            else:
                return list(self._logs)[-limit:]
                
    def clear_logs(self, before_timestamp: Optional[float] = None) -> int:
        """清理日志"""
        with self._lock:
            if before_timestamp is None:
                # 清空所有日志
                count = len(self._logs)
                self._logs.clear()
                return count
            else:
                # 清理指定时间之前的日志
                old_size = len(self._logs)
                self._logs = deque(
                    (log for log in self._logs if log.timestamp >= before_timestamp),
                    maxlen=self._logs.maxlen
                )
                return old_size - len(self._logs)
                
    def export_logs(self, filepath: Path, filter: Optional[LogFilter] = None) -> bool:
        """导出日志"""
        try:
            logs = self.get_logs(filter, limit=999999)
            
            # 转换为可序列化格式
            export_data = {
                'export_time': time.time(),
                'total_logs': len(logs),
                'logs': [log.to_dict() for log in logs]
            }
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
                
            self.log_info(f"Exported {len(logs)} logs to {filepath}")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to export logs: {e}")
            return False
            
    def get_log_statistics(self) -> Dict[str, Any]:
        """获取日志统计信息"""
        with self._lock:
            stats = {
                'total_logs': len(self._logs),
                'logs_by_level': {},
                'logs_by_category': {},
                'recent_errors': 0,
                'recent_warnings': 0
            }
            
            # 统计各级别日志数量
            for log in self._logs:
                level = log.level.value
                if level not in stats['logs_by_level']:
                    stats['logs_by_level'][level] = 0
                stats['logs_by_level'][level] += 1
                
                # 统计各类别日志数量
                category = log.category
                if category not in stats['logs_by_category']:
                    stats['logs_by_category'][category] = 0
                stats['logs_by_category'][category] += 1
                
            # 统计最近1小时的错误和警告
            one_hour_ago = time.time() - 3600
            for log in self._logs:
                if log.timestamp > one_hour_ago:
                    if log.level == LogLevel.ERROR:
                        stats['recent_errors'] += 1
                    elif log.level == LogLevel.WARNING:
                        stats['recent_warnings'] += 1
                        
            return stats
            
    def rotate_logs(self) -> None:
        """轮转日志文件"""
        if self._file_logger:
            # 关闭当前文件处理器
            for handler in self._file_logger.handlers[:]:
                handler.close()
                self._file_logger.removeHandler(handler)
                
            # 重新设置文件日志
            self._setup_file_logging()
            
            self.log_info("Log file rotated")


class StructuredLogger:
    """结构化日志记录器 - 输出JSON格式日志"""
    
    def __init__(self, service_name: str = "xwe", output_stream=None) -> None:
        self.service_name = service_name
        self.output_stream = output_stream or sys.stdout
        self._lock = threading.Lock()
        self._trace_id = None  # 支持请求追踪
        
    def _format_entry(self, level: str, message: str, **kwargs) -> Dict[str, Any]:
        """格式化日志条目为JSON结构"""
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level.upper(),
            "service": self.service_name,
            "message": message,
            "thread_id": threading.get_ident(),
        }
        
        # 添加trace_id（如果存在）
        if self._trace_id:
            entry["trace_id"] = self._trace_id
        elif "trace_id" in kwargs:
            entry["trace_id"] = kwargs.pop("trace_id")
        
        # 添加额外的元数据
        if kwargs:
            entry["metadata"] = kwargs
            
        # 特殊字段提升到顶层
        for field in ["player_id", "request_id", "category", "error"]:
            if field in kwargs:
                entry[field] = kwargs.pop(field)
                
        return entry
        
    def _write(self, entry: Dict[str, Any]) -> None:
        """写入日志条目"""
        with self._lock:
            json_line = json.dumps(entry, ensure_ascii=False)
            self.output_stream.write(json_line + "\n")
            self.output_stream.flush()
            
    def debug(self, message: str, **kwargs) -> None:
        """记录DEBUG级别日志"""
        entry = self._format_entry("debug", message, **kwargs)
        self._write(entry)
        
    def info(self, message: str, **kwargs) -> None:
        """记录INFO级别日志"""
        entry = self._format_entry("info", message, **kwargs)
        self._write(entry)
        
    def warning(self, message: str, **kwargs) -> None:
        """记录WARNING级别日志"""
        entry = self._format_entry("warning", message, **kwargs)
        self._write(entry)
        
    def error(self, message: str, error: Optional[Exception] = None, **kwargs) -> None:
        """记录ERROR级别日志"""
        if error:
            kwargs["error"] = {
                "type": type(error).__name__,
                "message": str(error),
                "stack": self._get_traceback(error)  # 改为stack字段
            }
        entry = self._format_entry("error", message, **kwargs)
        self._write(entry)
        
    def critical(self, message: str, **kwargs) -> None:
        """记录CRITICAL级别日志"""
        entry = self._format_entry("critical", message, **kwargs)
        self._write(entry)
        
    def _get_traceback(self, error: Exception) -> List[str]:
        """获取异常的堆栈跟踪"""
        import traceback
        return traceback.format_exception(type(error), error, error.__traceback__)
    
    def set_trace_id(self, trace_id: Optional[str] = None) -> None:
        """设置跟踪ID"""
        self._trace_id = trace_id or str(uuid.uuid4())
    
    def clear_trace_id(self) -> None:
        """清除跟踪ID"""
        self._trace_id = None
