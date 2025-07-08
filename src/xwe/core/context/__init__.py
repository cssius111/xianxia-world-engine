"""
修仙世界引擎 - 上下文压缩模块

提供智能的上下文管理和压缩功能，通过滑动窗口和 LLM 摘要技术
优化长对话的 Token 使用效率。
"""

from .compressor import ContextCompressor
from .memory_block import MemoryBlock
from .summarizer import ContextSummarizer

__all__ = [
    "ContextCompressor",
    "MemoryBlock", 
    "ContextSummarizer"
]
