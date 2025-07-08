"""
上下文压缩器核心实现
使用滑动窗口和 LLM 摘要技术管理对话上下文
"""

import logging
import time
from collections import deque
from typing import List, Optional, Deque, Dict, Any
import json

from .memory_block import MemoryBlock
from .summarizer import ContextSummarizer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..nlp.llm_client import LLMClient

logger = logging.getLogger(__name__)


class ContextCompressor:
    """
    上下文压缩器 - 智能管理游戏对话历史
    
    特性：
    1. 滑动窗口：保留最近的 N 条消息
    2. 自动摘要：累积的旧消息达到阈值时生成摘要
    3. 记忆分层：重要记忆优先保留
    4. Token 控制：确保总 token 不超过限制
    """
    
    def __init__(self,
                 llm_client: Optional["LLMClient"] = None,
                 window_size: int = 20,
                 block_size: int = 30,
                 max_memory_blocks: int = 10,
                 enable_compression: bool = True):
        """
        初始化压缩器
        
        Args:
            llm_client: LLM 客户端实例
            window_size: 滑动窗口大小（保留的最近消息数）
            block_size: 触发压缩的消息数量阈值
            max_memory_blocks: 最大记忆块数量
            enable_compression: 是否启用压缩（用于测试）
        """
        if llm_client is None:
            from ..nlp.llm_client import LLMClient
            llm_client = LLMClient()

        self.window_size = window_size
        self.block_size = block_size
        self.max_memory_blocks = max_memory_blocks
        self.enable_compression = enable_compression
        
        # 初始化组件
        self.llm_client = llm_client
        self.summarizer = ContextSummarizer(llm_client)
        
        # 数据结构
        self.recent_messages: Deque[str] = deque(maxlen=window_size)
        self.pending_messages: List[str] = []
        self.memory_blocks: Deque[MemoryBlock] = deque(maxlen=max_memory_blocks)
        
        # 统计信息
        self.stats = {
            "total_messages": 0,
            "total_compressions": 0,
            "total_tokens_saved": 0,
            "compression_errors": 0
        }
        
        logger.info(
            f"ContextCompressor 初始化: "
            f"window={window_size}, block={block_size}, "
            f"max_blocks={max_memory_blocks}"
        )

    def compress(self, messages: List[Dict[str, Any]]) -> str:
        """一次性压缩给定的消息列表并返回摘要"""

        contents = [m.get("content", "") for m in messages]
        return self.summarizer.summarize(contents, structured=False)
    
    def append(self, message: str) -> None:
        """
        添加新消息到上下文
        
        Args:
            message: 新消息内容
        """
        if not message:
            return
        
        # 更新统计
        self.stats["total_messages"] += 1
        
        # 添加到最近消息队列
        self.recent_messages.append(message)
        
        # 添加到待压缩队列
        self.pending_messages.append(message)
        
        # 检查是否需要压缩
        if self.enable_compression and self._should_compress():
            self._compress_old_messages()
        
        logger.debug(
            f"消息已添加: {len(message)}字符, "
            f"待压缩: {len(self.pending_messages)}, "
            f"最近: {len(self.recent_messages)}"
        )
    
    def get_context(self) -> str:
        """
        获取压缩后的完整上下文
        
        Returns:
            格式化的上下文字符串
        """
        context_parts = []
        
        # 1. 添加记忆块摘要
        if self.memory_blocks:
            context_parts.append("=== 历史记忆 ===")
            for i, block in enumerate(self.memory_blocks):
                context_parts.append(f"[记忆{i+1}] {block.summary}")
            context_parts.append("")
        
        # 2. 添加最近的对话
        if self.recent_messages:
            context_parts.append("=== 最近对话 ===")
            context_parts.extend(list(self.recent_messages))
        
        # 3. 组合上下文
        full_context = "\n".join(context_parts)
        
        # 4. Token 限制检查
        estimated_tokens = self._estimate_tokens(full_context)
        if estimated_tokens > 3500:  # 留出余量
            logger.warning(f"上下文可能过长: {estimated_tokens} tokens")
            # 可以在这里进一步压缩
        
        return full_context
    
    def _should_compress(self) -> bool:
        """
        判断是否需要进行压缩
        
        Returns:
            是否需要压缩
        """
        # 待压缩消息达到阈值
        if len(self.pending_messages) >= self.block_size:
            return True
        
        # 总 token 数接近限制
        total_tokens = self._estimate_total_tokens()
        if total_tokens > 3000:
            return True
        
        return False
    
    def _compress_old_messages(self) -> None:
        """
        压缩旧消息为摘要
        """
        if not self.pending_messages:
            return
        
        try:
            start_time = time.time()
            
            # 获取要压缩的消息
            messages_to_compress = self.pending_messages[:self.block_size]
            
            # 生成摘要
            summary = self.summarizer.summarize(
                messages_to_compress,
                structured=False,
                max_tokens=150
            )
            
            if not summary:
                logger.warning("摘要生成失败，使用降级方案")
                summary = f"[{len(messages_to_compress)}条历史消息]"
            
            # 计算重要性
            importance = self.summarizer.calculate_importance(messages_to_compress)
            
            # 创建记忆块
            memory_block = MemoryBlock(
                summary=summary,
                message_count=len(messages_to_compress),
                importance_score=importance,
                original_messages=messages_to_compress if logger.isEnabledFor(logging.DEBUG) else None
            )
            
            # 添加到记忆块队列
            self.memory_blocks.append(memory_block)
            
            # 清理已压缩的消息
            self.pending_messages = self.pending_messages[self.block_size:]
            
            # 更新统计
            elapsed = time.time() - start_time
            self.stats["total_compressions"] += 1
            tokens_before = sum(self._estimate_tokens(m) for m in messages_to_compress)
            tokens_after = self._estimate_tokens(summary)
            self.stats["total_tokens_saved"] += (tokens_before - tokens_after)
            
            logger.info(
                f"压缩完成: {len(messages_to_compress)}条消息 -> "
                f"{len(summary)}字符, 耗时{elapsed:.2f}秒, "
                f"节省{tokens_before - tokens_after} tokens"
            )
            
        except Exception as e:
            logger.error(f"压缩失败: {e}")
            self.stats["compression_errors"] += 1
            # 失败时清理部分消息避免无限增长
            if len(self.pending_messages) > self.block_size * 2:
                self.pending_messages = self.pending_messages[self.block_size:]
    
    def _estimate_tokens(self, text: str) -> int:
        """
        估算文本的 token 数量
        
        Args:
            text: 输入文本
            
        Returns:
            估算的 token 数
        """
        # 简单估算：中文约 2 字符/token，英文约 4 字符/token
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars
        return chinese_chars // 2 + other_chars // 4
    
    def _estimate_total_tokens(self) -> int:
        """
        估算当前总 token 数
        
        Returns:
            总 token 数估算
        """
        total = 0
        
        # 记忆块的 tokens
        for block in self.memory_blocks:
            total += block.token_estimate
        
        # 最近消息的 tokens
        for msg in self.recent_messages:
            total += self._estimate_tokens(msg)
        
        # 待压缩消息的 tokens
        for msg in self.pending_messages:
            total += self._estimate_tokens(msg)
        
        return total
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取压缩器统计信息
        
        Returns:
            统计信息字典
        """
        return {
            **self.stats,
            "current_memory_blocks": len(self.memory_blocks),
            "current_recent_messages": len(self.recent_messages),
            "current_pending_messages": len(self.pending_messages),
            "estimated_total_tokens": self._estimate_total_tokens(),
            "compression_ratio": self._calculate_compression_ratio()
        }
    
    def _calculate_compression_ratio(self) -> float:
        """
        计算压缩率
        
        Returns:
            压缩率（0-1，越小越好）
        """
        if self.stats["total_compressions"] == 0:
            return 1.0
        
        # 基于节省的 token 计算
        total_original = self.stats["total_tokens_saved"] + self._estimate_total_tokens()
        if total_original == 0:
            return 1.0
        
        return self._estimate_total_tokens() / total_original
    
    def clear(self) -> None:
        """
        清空所有上下文
        """
        self.recent_messages.clear()
        self.pending_messages.clear()
        self.memory_blocks.clear()
        logger.info("上下文已清空")
    
    def export_memory(self) -> List[Dict[str, Any]]:
        """
        导出记忆数据（用于持久化）
        
        Returns:
            记忆数据列表
        """
        return [block.to_dict() for block in self.memory_blocks]
    
    def import_memory(self, memory_data: List[Dict[str, Any]]) -> None:
        """
        导入记忆数据
        
        Args:
            memory_data: 记忆数据列表
        """
        self.memory_blocks.clear()
        for data in memory_data:
            block = MemoryBlock(
                summary=data["summary"],
                message_count=data["message_count"],
                created_at=data.get("created_at", time.time()),
                token_estimate=data.get("token_estimate", 0),
                importance_score=data.get("importance_score", 0.5)
            )
            self.memory_blocks.append(block)
        
        logger.info(f"导入了 {len(memory_data)} 个记忆块")
