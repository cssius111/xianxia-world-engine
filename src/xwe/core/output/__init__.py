"""
输出管理模块

提供统一的游戏输出管理，支持多通道、格式化和上下文感知的输出。
"""

from .output_manager import (
    ConsoleChannel,
    FileChannel,
    HTMLChannel,
    MessagePriority,
    MessageType,
    OutputChannel,
    OutputContext,
    OutputFormatter,
    OutputManager,
    OutputMessage,
    WebChannel,
    get_default_output_manager,
)

__all__ = [
    "OutputManager",
    "OutputChannel",
    "ConsoleChannel",
    "FileChannel",
    "HTMLChannel",
    "WebChannel",
    "OutputMessage",
    "MessageType",
    "MessagePriority",
    "OutputContext",
    "OutputFormatter",
    "get_default_output_manager",
]
