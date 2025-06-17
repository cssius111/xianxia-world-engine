"""
输出管理器 - 统一的游戏输出管理模块

负责管理所有游戏输出，包括：
- 多输出通道管理（控制台、文件、Web等）
- 消息格式化和样式
- 输出缓冲和批处理
- 上下文感知的消息组合
- 输出过滤和优先级
"""

import logging
from typing import Dict, List, Optional, Any, Callable, Set, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from abc import ABC, abstractmethod
import json
import re
from pathlib import Path
from collections import deque
import threading
from queue import Queue, Empty
import time

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """消息类型"""
    SYSTEM = "system"          # 系统消息
    NARRATIVE = "narrative"    # 叙述文本
    DIALOGUE = "dialogue"      # 对话
    COMBAT = "combat"          # 战斗信息
    STATUS = "status"          # 状态信息
    ACHIEVEMENT = "achievement" # 成就通知
    ERROR = "error"            # 错误信息
    WARNING = "warning"        # 警告信息
    SUCCESS = "success"        # 成功消息
    INFO = "info"              # 一般信息
    PROMPT = "prompt"          # 输入提示
    MENU = "menu"              # 菜单选项
    DEBUG = "debug"            # 调试信息


class MessagePriority(Enum):
    """消息优先级"""
    DEBUG = 0      # 调试信息
    LOW = 1        # 低优先级
    NORMAL = 2     # 普通
    HIGH = 3       # 高优先级
    CRITICAL = 4   # 关键信息


@dataclass
class OutputMessage:
    """输出消息数据类"""
    content: str
    type: MessageType = MessageType.SYSTEM
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    context_id: Optional[str] = None  # 用于关联相关消息
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'content': self.content,
            'type': self.type.value,
            'priority': self.priority.value,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'metadata': self.metadata,
            'context_id': self.context_id
        }


@dataclass
class OutputContext:
    """输出上下文，用于管理相关消息的组合"""
    id: str
    type: str
    messages: List[OutputMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True


class OutputChannel(ABC):
    """输出通道抽象基类"""
    
    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled
        self.filters: List[Callable[[OutputMessage], bool]] = []
        
    @abstractmethod
    def write(self, message: OutputMessage) -> None:
        """写入消息"""
        pass
    
    @abstractmethod
    def flush(self) -> None:
        """刷新缓冲"""
        pass
    
    def add_filter(self, filter_func: Callable[[OutputMessage], bool]) -> None:
        """添加过滤器"""
        self.filters.append(filter_func)
    
    def should_output(self, message: OutputMessage) -> bool:
        """检查是否应该输出此消息"""
        if not self.enabled:
            return False
        
        # 应用所有过滤器
        for filter_func in self.filters:
            if not filter_func(message):
                return False
        
        return True


class ConsoleChannel(OutputChannel):
    """控制台输出通道"""
    
    # ANSI 颜色代码
    COLORS = {
        MessageType.SYSTEM: '\033[90m',      # 灰色
        MessageType.NARRATIVE: '\033[0m',    # 默认
        MessageType.DIALOGUE: '\033[94m',    # 蓝色
        MessageType.COMBAT: '\033[91m',      # 红色
        MessageType.STATUS: '\033[93m',      # 黄色
        MessageType.ACHIEVEMENT: '\033[95m', # 紫色
        MessageType.ERROR: '\033[91m',       # 红色
        MessageType.WARNING: '\033[93m',     # 黄色
        MessageType.SUCCESS: '\033[92m',     # 绿色
        MessageType.INFO: '\033[96m',        # 青色
        MessageType.PROMPT: '\033[97m',      # 白色
        MessageType.MENU: '\033[94m',        # 蓝色
        MessageType.DEBUG: '\033[90m',       # 灰色
    }
    
    RESET = '\033[0m'
    
    def __init__(self, colored: bool = True, **kwargs):
        super().__init__("console", **kwargs)
        self.colored = colored
    
    def write(self, message: OutputMessage) -> None:
        """输出到控制台"""
        if not self.should_output(message):
            return
        
        # 格式化输出
        output = self._format_message(message)
        
        # 添加颜色
        if self.colored and message.type in self.COLORS:
            output = f"{self.COLORS[message.type]}{output}{self.RESET}"
        
        print(output)
    
    def flush(self) -> None:
        """控制台不需要显式刷新"""
        pass
    
    def _format_message(self, message: OutputMessage) -> str:
        """格式化消息"""
        # 基本格式
        content = message.content
        
        # 根据类型添加前缀
        if message.type == MessageType.ERROR:
            content = f"[错误] {content}"
        elif message.type == MessageType.WARNING:
            content = f"[警告] {content}"
        elif message.type == MessageType.DEBUG:
            content = f"[调试] {content}"
        elif message.type == MessageType.ACHIEVEMENT:
            content = f"🎉 {content}"
        
        # 对话格式
        if message.type == MessageType.DIALOGUE and 'speaker' in message.metadata:
            speaker = message.metadata['speaker']
            content = f"【{speaker}】: {content}"
        
        return content


class FileChannel(OutputChannel):
    """文件输出通道"""
    
    def __init__(self, filepath: Path, append: bool = True, **kwargs):
        super().__init__("file", **kwargs)
        self.filepath = Path(filepath)
        self.append = append
        self.buffer: List[str] = []
        self.buffer_size = 100  # 缓冲大小
        
        # 确保目录存在
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果不是追加模式，清空文件
        if not append:
            self.filepath.write_text("", encoding='utf-8')
    
    def write(self, message: OutputMessage) -> None:
        """写入到缓冲"""
        if not self.should_output(message):
            return
        
        # 格式化为日志行
        log_line = self._format_log_line(message)
        self.buffer.append(log_line)
        
        # 如果缓冲满了，写入文件
        if len(self.buffer) >= self.buffer_size:
            self.flush()
    
    def flush(self) -> None:
        """将缓冲写入文件"""
        if not self.buffer:
            return
        
        try:
            with open(self.filepath, 'a', encoding='utf-8') as f:
                f.write('\n'.join(self.buffer) + '\n')
            self.buffer.clear()
        except Exception as e:
            logger.error(f"写入日志文件失败: {e}")
    
    def _format_log_line(self, message: OutputMessage) -> str:
        """格式化日志行"""
        timestamp = message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        type_str = message.type.value.upper()
        priority = message.priority.value
        
        # 基本格式：[时间] [类型] [优先级] 内容
        line = f"[{timestamp}] [{type_str}] [P{priority}] {message.content}"
        
        # 添加元数据
        if message.metadata:
            meta_str = json.dumps(message.metadata, ensure_ascii=False)
            line += f" | META: {meta_str}"
        
        return line


class HTMLChannel(OutputChannel):
    """HTML输出通道（改进版）"""
    
    def __init__(self, filepath: Path, title: str = "游戏日志", 
                 auto_refresh: int = 2, max_messages: int = 500, **kwargs):
        super().__init__("html", **kwargs)
        self.filepath = Path(filepath)
        self.title = title
        self.auto_refresh = auto_refresh
        self.max_messages = max_messages
        self.messages: deque = deque(maxlen=max_messages)
        self.status_data: Dict[str, Any] = {}
        
        # 确保目录存在
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化HTML文件
        self._write_html()
    
    def write(self, message: OutputMessage) -> None:
        """写入消息"""
        if not self.should_output(message):
            return
        
        self.messages.append(message)
        self._write_html()
    
    def update_status(self, status: Dict[str, Any]) -> None:
        """更新状态显示"""
        self.status_data = status
        self._write_html()
    
    def flush(self) -> None:
        """确保HTML文件是最新的"""
        self._write_html()
    
    def _write_html(self) -> None:
        """生成并写入HTML"""
        html = self._generate_html()
        try:
            self.filepath.write_text(html, encoding='utf-8')
        except Exception as e:
            logger.error(f"写入HTML文件失败: {e}")
    
    def _generate_html(self) -> str:
        """生成HTML内容"""
        # 状态栏HTML
        status_items = [
            f"<li><strong>{k}</strong>: {v}</li>"
            for k, v in self.status_data.items()
        ]
        status_html = '\n'.join(status_items)
        
        # 消息HTML
        message_html = self._generate_messages_html()
        
        return f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="{self.auto_refresh}">
    <title>{self.title}</title>
    <style>
        {self._get_styles()}
    </style>
</head>
<body>
    <div id="container">
        <div id="status">
            <h2>游戏状态</h2>
            <ul>{status_html}</ul>
        </div>
        <div id="messages">
            <h2>游戏日志</h2>
            <div id="message-list">
                {message_html}
            </div>
        </div>
    </div>
    <script>
        // 自动滚动到底部
        window.onload = function() {{
            var messageList = document.getElementById('message-list');
            messageList.scrollTop = messageList.scrollHeight;
        }};
    </script>
</body>
</html>"""
    
    def _generate_messages_html(self) -> str:
        """生成消息HTML"""
        # 按上下文分组消息
        context_groups = self._group_messages_by_context()
        
        html_parts = []
        for context_id, messages in context_groups:
            if context_id and len(messages) > 1:
                # 多条相关消息，组合显示
                html_parts.append(self._render_message_group(messages))
            else:
                # 单独消息
                for msg in messages:
                    html_parts.append(self._render_single_message(msg))
        
        return '\n'.join(html_parts)
    
    def _group_messages_by_context(self) -> List[tuple]:
        """按上下文分组消息"""
        groups = []
        current_context = None
        current_group = []
        
        for msg in self.messages:
            if msg.context_id != current_context:
                if current_group:
                    groups.append((current_context, current_group))
                current_context = msg.context_id
                current_group = [msg]
            else:
                current_group.append(msg)
        
        if current_group:
            groups.append((current_context, current_group))
        
        return groups
    
    def _render_single_message(self, message: OutputMessage) -> str:
        """渲染单条消息"""
        css_class = f"message {message.type.value}"
        content = self._escape_html(message.content)
        
        # 处理对话
        if message.type == MessageType.DIALOGUE and 'speaker' in message.metadata:
            speaker = self._escape_html(message.metadata['speaker'])
            content = f'<span class="speaker">{speaker}</span>: {content}'
        
        # 处理换行
        content = content.replace('\n', '<br>')
        
        return f'<div class="{css_class}">{content}</div>'
    
    def _render_message_group(self, messages: List[OutputMessage]) -> str:
        """渲染消息组"""
        if not messages:
            return ''
        
        # 使用第一条消息的类型作为组类型
        group_type = messages[0].type.value
        css_class = f"message-group {group_type}"
        
        parts = []
        for msg in messages:
            content = self._escape_html(msg.content)
            if msg.type == MessageType.DIALOGUE and 'speaker' in msg.metadata:
                speaker = self._escape_html(msg.metadata['speaker'])
                content = f'<span class="speaker">{speaker}</span>: {content}'
            parts.append(content)
        
        content = '<br>'.join(parts)
        return f'<div class="{css_class}">{content}</div>'
    
    def _escape_html(self, text: str) -> str:
        """转义HTML特殊字符"""
        return (text.replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#39;'))
    
    def _get_styles(self) -> str:
        """获取CSS样式"""
        return """
        body {
            font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f5f5;
        }
        #container {
            display: flex;
            height: 100vh;
        }
        #status {
            width: 300px;
            background: #fff;
            padding: 20px;
            box-shadow: 2px 0 5px rgba(0,0,0,0.1);
            overflow-y: auto;
        }
        #status h2 {
            margin-top: 0;
            color: #333;
        }
        #status ul {
            list-style: none;
            padding: 0;
        }
        #status li {
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        #messages {
            flex: 1;
            padding: 20px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        #messages h2 {
            margin-top: 0;
            color: #333;
        }
        #message-list {
            flex: 1;
            overflow-y: auto;
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .message {
            margin: 10px 0;
            padding: 12px;
            border-radius: 6px;
            line-height: 1.6;
        }
        .message-group {
            margin: 15px 0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #4a90e2;
            background: #fff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .speaker {
            font-weight: bold;
            color: #2c3e50;
        }
        
        /* 消息类型样式 */
        .system { background: #f8f9fa; color: #6c757d; border-left-color: #6c757d; }
        .narrative { background: #fff; color: #333; }
        .dialogue { background: #e3f2fd; color: #1976d2; border-left-color: #1976d2; }
        .combat { background: #ffebee; color: #c62828; border-left-color: #c62828; }
        .status { background: #fff8e1; color: #f57c00; border-left-color: #f57c00; }
        .achievement { background: #f3e5f5; color: #7b1fa2; border-left-color: #7b1fa2; }
        .error { background: #ffcdd2; color: #d32f2f; font-weight: bold; }
        .warning { background: #fff3cd; color: #856404; }
        .success { background: #d4edda; color: #155724; border-left-color: #28a745; }
        .info { background: #d1ecf1; color: #0c5460; }
        .debug { background: #f5f5f5; color: #999; font-size: 0.9em; }
        """


class WebChannel(OutputChannel):
    """Web API输出通道（用于前后端分离）"""
    
    def __init__(self, message_queue: Queue, **kwargs):
        super().__init__("web", **kwargs)
        self.message_queue = message_queue
        self.max_queue_size = 1000
    
    def write(self, message: OutputMessage) -> None:
        """将消息放入队列"""
        if not self.should_output(message):
            return
        
        # 如果队列满了，移除最旧的消息
        if self.message_queue.qsize() >= self.max_queue_size:
            try:
                self.message_queue.get_nowait()
            except Empty:
                pass
        
        # 添加新消息
        self.message_queue.put(message.to_dict())
    
    def flush(self) -> None:
        """Web通道不需要刷新"""
        pass


class OutputFormatter:
    """输出格式化器"""
    
    @staticmethod
    def format_status(status_dict: Dict[str, Any], title: str = "角色状态") -> str:
        """格式化状态信息"""
        lines = [f"=== {title} ==="]
        
        max_key_length = max(len(str(k)) for k in status_dict.keys())
        
        for key, value in status_dict.items():
            # 对齐输出
            lines.append(f"{str(key):<{max_key_length}} : {value}")
        
        lines.append("=" * (len(title) + 8))
        return '\n'.join(lines)
    
    @staticmethod
    def format_table(data: List[Dict[str, Any]], headers: Optional[List[str]] = None) -> str:
        """格式化表格"""
        if not data:
            return "（空）"
        
        # 确定列
        if headers is None:
            headers = list(data[0].keys())
        
        # 计算列宽
        col_widths = {}
        for header in headers:
            col_widths[header] = len(str(header))
            for row in data:
                if header in row:
                    col_widths[header] = max(col_widths[header], len(str(row[header])))
        
        # 生成表格
        lines = []
        
        # 表头
        header_line = " | ".join(
            str(h).ljust(col_widths[h]) for h in headers
        )
        lines.append(header_line)
        lines.append("-" * len(header_line))
        
        # 数据行
        for row in data:
            row_line = " | ".join(
                str(row.get(h, '')).ljust(col_widths[h]) for h in headers
            )
            lines.append(row_line)
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_menu(options: List[str], title: Optional[str] = None) -> str:
        """格式化菜单"""
        lines = []
        
        if title:
            lines.append(f"=== {title} ===")
        
        for i, option in enumerate(options, 1):
            lines.append(f"{i}. {option}")
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_progress(current: float, total: float, 
                       width: int = 20, show_percentage: bool = True) -> str:
        """格式化进度条"""
        if total == 0:
            percentage = 0
        else:
            percentage = min(100, (current / total) * 100)
        
        filled = int(width * percentage / 100)
        bar = '█' * filled + '░' * (width - filled)
        
        if show_percentage:
            return f"[{bar}] {percentage:.1f}%"
        else:
            return f"[{bar}] {current}/{total}"


class OutputManager:
    """
    输出管理器主类
    
    负责管理所有游戏输出，提供统一的接口
    """
    
    def __init__(self):
        """初始化输出管理器"""
        self.channels: Dict[str, OutputChannel] = {}
        self.contexts: Dict[str, OutputContext] = {}
        self.active_context: Optional[str] = None
        self.formatter = OutputFormatter()
        
        # 输出历史
        self.history: deque = deque(maxlen=1000)
        
        # 批处理设置
        self.batch_mode = False
        self.batch_buffer: List[OutputMessage] = []
        self.batch_size = 50
        
        # 线程安全
        self._lock = threading.RLock()
        
        logger.info("输出管理器初始化完成")
    
    def add_channel(self, channel: OutputChannel) -> None:
        """添加输出通道"""
        with self._lock:
            self.channels[channel.name] = channel
            logger.info(f"添加输出通道: {channel.name}")
    
    def remove_channel(self, name: str) -> None:
        """移除输出通道"""
        with self._lock:
            if name in self.channels:
                # 刷新通道
                self.channels[name].flush()
                del self.channels[name]
                logger.info(f"移除输出通道: {name}")
    
    def get_channel(self, name: str) -> Optional[OutputChannel]:
        """获取输出通道"""
        return self.channels.get(name)
    
    def output(self, content: str, 
               msg_type: MessageType = MessageType.SYSTEM,
               priority: MessagePriority = MessagePriority.NORMAL,
               source: Optional[str] = None,
               metadata: Optional[Dict[str, Any]] = None,
               context_id: Optional[str] = None) -> None:
        """
        输出消息
        
        Args:
            content: 消息内容
            msg_type: 消息类型
            priority: 优先级
            source: 消息来源
            metadata: 额外元数据
            context_id: 上下文ID（用于关联消息）
        """
        # 如果没有指定上下文，使用当前活动上下文
        if context_id is None and self.active_context:
            context_id = self.active_context
        
        # 创建消息
        message = OutputMessage(
            content=content,
            type=msg_type,
            priority=priority,
            source=source,
            metadata=metadata or {},
            context_id=context_id
        )
        
        with self._lock:
            # 添加到历史
            self.history.append(message)
            
            # 添加到上下文（如果有）
            if context_id and context_id in self.contexts:
                self.contexts[context_id].messages.append(message)
            
            # 批处理模式
            if self.batch_mode:
                self.batch_buffer.append(message)
                if len(self.batch_buffer) >= self.batch_size:
                    self.flush_batch()
            else:
                # 立即输出
                self._write_to_channels(message)
    
    def _write_to_channels(self, message: OutputMessage) -> None:
        """写入到所有通道"""
        for channel in self.channels.values():
            try:
                channel.write(message)
            except Exception as e:
                logger.error(f"输出到通道 {channel.name} 失败: {e}")
    
    # === 上下文管理 ===
    
    def create_context(self, context_id: str, context_type: str,
                      metadata: Optional[Dict[str, Any]] = None) -> OutputContext:
        """创建输出上下文"""
        with self._lock:
            context = OutputContext(
                id=context_id,
                type=context_type,
                metadata=metadata or {}
            )
            self.contexts[context_id] = context
            return context
    
    def set_active_context(self, context_id: Optional[str]) -> None:
        """设置活动上下文"""
        with self._lock:
            self.active_context = context_id
    
    def end_context(self, context_id: str) -> None:
        """结束上下文"""
        with self._lock:
            if context_id in self.contexts:
                self.contexts[context_id].is_active = False
                if self.active_context == context_id:
                    self.active_context = None
    
    # === 批处理 ===
    
    def enable_batch_mode(self, batch_size: int = 50) -> None:
        """启用批处理模式"""
        with self._lock:
            self.batch_mode = True
            self.batch_size = batch_size
    
    def disable_batch_mode(self) -> None:
        """禁用批处理模式"""
        with self._lock:
            self.flush_batch()
            self.batch_mode = False
    
    def flush_batch(self) -> None:
        """刷新批处理缓冲"""
        with self._lock:
            for message in self.batch_buffer:
                self._write_to_channels(message)
            self.batch_buffer.clear()
    
    def flush_all(self) -> None:
        """刷新所有通道"""
        with self._lock:
            # 先刷新批处理
            if self.batch_mode:
                self.flush_batch()
            
            # 刷新所有通道
            for channel in self.channels.values():
                try:
                    channel.flush()
                except Exception as e:
                    logger.error(f"刷新通道 {channel.name} 失败: {e}")
    
    # === 便捷方法 ===
    
    def system(self, content: str, **kwargs) -> None:
        """输出系统消息"""
        self.output(content, MessageType.SYSTEM, **kwargs)
    
    def narrative(self, content: str, **kwargs) -> None:
        """输出叙述文本"""
        self.output(content, MessageType.NARRATIVE, **kwargs)
    
    def dialogue(self, speaker: str, content: str, **kwargs) -> None:
        """输出对话"""
        metadata = kwargs.get('metadata', {})
        metadata['speaker'] = speaker
        kwargs['metadata'] = metadata
        self.output(content, MessageType.DIALOGUE, **kwargs)
    
    def combat(self, content: str, **kwargs) -> None:
        """输出战斗信息"""
        self.output(content, MessageType.COMBAT, **kwargs)
    
    def status(self, content: str, **kwargs) -> None:
        """输出状态信息"""
        self.output(content, MessageType.STATUS, **kwargs)
    
    def achievement(self, content: str, **kwargs) -> None:
        """输出成就通知"""
        self.output(content, MessageType.ACHIEVEMENT, 
                   priority=MessagePriority.HIGH, **kwargs)
    
    def error(self, content: str, **kwargs) -> None:
        """输出错误信息"""
        self.output(content, MessageType.ERROR, 
                   priority=MessagePriority.HIGH, **kwargs)
    
    def warning(self, content: str, **kwargs) -> None:
        """输出警告信息"""
        self.output(content, MessageType.WARNING, **kwargs)
    
    def success(self, content: str, **kwargs) -> None:
        """输出成功消息"""
        self.output(content, MessageType.SUCCESS, **kwargs)
    
    def info(self, content: str, **kwargs) -> None:
        """输出一般信息"""
        self.output(content, MessageType.INFO, **kwargs)
    
    def debug(self, content: str, **kwargs) -> None:
        """输出调试信息"""
        self.output(content, MessageType.DEBUG, 
                   priority=MessagePriority.DEBUG, **kwargs)
    
    def prompt(self, content: str, **kwargs) -> None:
        """输出输入提示"""
        self.output(content, MessageType.PROMPT, **kwargs)
    
    def menu(self, options: List[str], title: Optional[str] = None, **kwargs) -> None:
        """输出菜单"""
        content = self.formatter.format_menu(options, title)
        self.output(content, MessageType.MENU, **kwargs)
    
    # === 格式化输出 ===
    
    def output_status(self, status_dict: Dict[str, Any], 
                     title: str = "角色状态", **kwargs) -> None:
        """输出格式化的状态信息"""
        content = self.formatter.format_status(status_dict, title)
        self.status(content, **kwargs)
    
    def output_table(self, data: List[Dict[str, Any]], 
                    headers: Optional[List[str]] = None, **kwargs) -> None:
        """输出表格"""
        content = self.formatter.format_table(data, headers)
        self.system(content, **kwargs)
    
    def output_progress(self, current: float, total: float, 
                       label: str = "", **kwargs) -> None:
        """输出进度条"""
        progress = self.formatter.format_progress(current, total)
        content = f"{label}: {progress}" if label else progress
        self.status(content, **kwargs)
    
    # === 特殊输出 ===
    
    def combat_sequence(self, actions: List[str], **kwargs) -> None:
        """输出战斗序列"""
        # 创建战斗上下文
        context_id = f"combat_{datetime.now().timestamp()}"
        self.create_context(context_id, "combat")
        
        # 输出所有动作
        for action in actions:
            self.combat(action, context_id=context_id, **kwargs)
        
        # 结束上下文
        self.end_context(context_id)
    
    def dialogue_exchange(self, exchanges: List[tuple], **kwargs) -> None:
        """输出对话交流"""
        # 创建对话上下文
        context_id = f"dialogue_{datetime.now().timestamp()}"
        self.create_context(context_id, "dialogue")
        
        # 输出所有对话
        for speaker, content in exchanges:
            self.dialogue(speaker, content, context_id=context_id, **kwargs)
        
        # 结束上下文
        self.end_context(context_id)
    
    # === 状态更新 ===
    
    def update_status(self, status_data: Dict[str, Any]) -> None:
        """更新状态显示（用于HTML等通道）"""
        for channel in self.channels.values():
            if hasattr(channel, 'update_status'):
                channel.update_status(status_data)
    
    # === 历史和查询 ===
    
    def get_history(self, count: int = 100, 
                   msg_type: Optional[MessageType] = None) -> List[OutputMessage]:
        """获取历史消息"""
        with self._lock:
            messages = list(self.history)
            
            # 过滤类型
            if msg_type:
                messages = [m for m in messages if m.type == msg_type]
            
            # 返回最新的N条
            return messages[-count:]
    
    def clear_history(self) -> None:
        """清空历史"""
        with self._lock:
            self.history.clear()
    
    def search_history(self, pattern: str, 
                      msg_type: Optional[MessageType] = None) -> List[OutputMessage]:
        """搜索历史消息"""
        regex = re.compile(pattern, re.IGNORECASE)
        results = []
        
        with self._lock:
            for msg in self.history:
                if msg_type and msg.type != msg_type:
                    continue
                
                if regex.search(msg.content):
                    results.append(msg)
        
        return results


# 创建默认的输出管理器实例
_default_manager: Optional[OutputManager] = None


def get_default_output_manager() -> OutputManager:
    """获取默认的输出管理器"""
    global _default_manager
    if _default_manager is None:
        _default_manager = OutputManager()
        
        # 添加默认的控制台通道
        _default_manager.add_channel(ConsoleChannel())
        
    return _default_manager


# 导出主要类和函数
__all__ = [
    'OutputManager',
    'OutputChannel',
    'ConsoleChannel',
    'FileChannel',
    'HTMLChannel',
    'WebChannel',
    'OutputMessage',
    'MessageType',
    'MessagePriority',
    'OutputContext',
    'OutputFormatter',
    'get_default_output_manager'
]
