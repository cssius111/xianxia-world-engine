from __future__ import annotations

"""输出管理器及相关类"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict


class MessageType(Enum):
    """消息类型"""
    TEXT = "text"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class MessagePriority(Enum):
    """消息优先级"""
    LOW = 1
    NORMAL = 5
    HIGH = 10


@dataclass
class OutputMessage:
    """输出消息"""
    content: str
    type: MessageType = MessageType.TEXT
    priority: MessagePriority = MessagePriority.NORMAL


@dataclass
class OutputContext:
    """输出上下文信息"""
    source: Optional[str] = None
    extra: Dict[str, str] = field(default_factory=dict)


class OutputFormatter:
    """格式化输出消息"""

    def format(self, message: OutputMessage, context: OutputContext | None = None) -> str:
        return f"[{message.type.value.upper()}] {message.content}"


class OutputChannel:
    """输出通道基类"""

    def send(self, formatted: str, context: OutputContext | None = None) -> None:
        raise NotImplementedError


class ConsoleChannel(OutputChannel):
    """控制台输出通道"""

    def __init__(self) -> None:
        self.messages: List[str] = []

    def send(self, formatted: str, context: OutputContext | None = None) -> None:
        print(formatted)
        self.messages.append(formatted)


class FileChannel(OutputChannel):
    """文件输出通道"""

    def __init__(self, path: str) -> None:
        self.path = path

    def send(self, formatted: str, context: OutputContext | None = None) -> None:
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")


class HTMLChannel(OutputChannel):
    """HTML 输出通道"""

    def __init__(self) -> None:
        self.messages: List[str] = []

    def send(self, formatted: str, context: OutputContext | None = None) -> None:
        html = f"<p>{formatted}</p>"
        self.messages.append(html)


class WebChannel(OutputChannel):
    """Web 输出通道，占位实现"""

    def __init__(self) -> None:
        self.messages: List[str] = []

    def send(self, formatted: str, context: OutputContext | None = None) -> None:
        self.messages.append(formatted)


class OutputManager:
    """输出管理器"""

    def __init__(self, channels: Optional[List[OutputChannel]] = None, formatter: Optional[OutputFormatter] = None) -> None:
        self.channels = channels or []
        self.formatter = formatter or OutputFormatter()

    def add_channel(self, channel: OutputChannel) -> None:
        self.channels.append(channel)

    def remove_channel(self, channel: OutputChannel) -> None:
        if channel in self.channels:
            self.channels.remove(channel)

    def send_message(self, message: OutputMessage, context: OutputContext | None = None) -> None:
        formatted = self.formatter.format(message, context)
        for ch in self.channels:
            ch.send(formatted, context)


_default_output_manager: OutputManager | None = None


def get_default_output_manager() -> OutputManager:
    """获取默认输出管理器"""
    global _default_output_manager
    if _default_output_manager is None:
        _default_output_manager = OutputManager([ConsoleChannel()])
    return _default_output_manager
