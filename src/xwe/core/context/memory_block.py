"""
记忆块数据结构
用于存储压缩后的上下文摘要
"""

import time
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MemoryBlock:
    """
    记忆块 - 存储压缩后的上下文摘要
    
    Attributes:
        summary: 摘要内容
        original_messages: 原始消息列表（可选，用于调试）
        message_count: 原始消息数量
        created_at: 创建时间戳
        token_estimate: 预估的 token 数量
        importance_score: 重要性评分（0-1）
    """
    summary: str
    message_count: int
    created_at: float = field(default_factory=time.time)
    token_estimate: int = 0
    importance_score: float = 0.5
    original_messages: Optional[List[str]] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.token_estimate == 0:
            # 简单的 token 估算（中文约 2 字符/token）
            self.token_estimate = len(self.summary) // 2
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "summary": self.summary,
            "message_count": self.message_count,
            "created_at": self.created_at,
            "token_estimate": self.token_estimate,
            "importance_score": self.importance_score
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"[记忆块: {self.message_count}条消息的摘要 ({self.token_estimate} tokens)]"
