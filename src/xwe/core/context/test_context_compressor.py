"""
ContextCompressor 单元测试
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock

from src.xwe.core.context import ContextCompressor, MemoryBlock, ContextSummarizer
from src.xwe.core.nlp.llm_client import LLMClient


class TestContextCompressor:
    """ContextCompressor 测试类"""
    
    @pytest.fixture
    def mock_llm_client(self):
        """创建模拟的 LLM 客户端"""
        client = Mock(spec=LLMClient)
        # 模拟 chat 方法返回摘要
        client.chat.return_value = "玩家进行了多次探索和修炼，境界有所提升。"
        return client
    
    @pytest.fixture
    def compressor(self, mock_llm_client):
        """创建测试用的压缩器实例"""
        return ContextCompressor(
            llm_client=mock_llm_client,
            window_size=5,
            block_size=3,
            max_memory_blocks=2
        )
    
    def test_initialization(self, compressor):
        """测试初始化"""
        assert compressor.window_size == 5
        assert compressor.block_size == 3
        assert compressor.max_memory_blocks == 2
        assert len(compressor.recent_messages) == 0
        assert len(compressor.pending_messages) == 0
        assert len(compressor.memory_blocks) == 0
    
    def test_append_message(self, compressor):
        """测试添加消息"""
        compressor.append("玩家: 探索周围环境")
        assert len(compressor.recent_messages) == 1
        assert len(compressor.pending_messages) == 1
        assert compressor.stats["total_messages"] == 1
        
        compressor.append("系统: 你发现了一个神秘洞穴")
        assert len(compressor.recent_messages) == 2
        assert len(compressor.pending_messages) == 2
    
    def test_sliding_window(self, compressor):
        """测试滑动窗口机制"""
        # 添加超过窗口大小的消息
        for i in range(7):
            compressor.append(f"消息 {i}")
        
        # 最近消息应该只保留窗口大小的数量
        assert len(compressor.recent_messages) == 5
        assert list(compressor.recent_messages) == [
            "消息 2", "消息 3", "消息 4", "消息 5", "消息 6"
        ]
    
    def test_compression_trigger(self, compressor, mock_llm_client):
        """测试压缩触发"""
        # 添加达到 block_size 的消息
        for i in range(3):
            compressor.append(f"消息 {i}")
        
        # 应该触发压缩
        assert len(compressor.memory_blocks) == 1
        assert len(compressor.pending_messages) == 0
        assert compressor.stats["total_compressions"] == 1
        
        # 验证 LLM 被调用
        mock_llm_client.chat.assert_called_once()
    
    def test_memory_block_limit(self, compressor, mock_llm_client):
        """测试记忆块数量限制"""
        # 触发多次压缩
        for batch in range(4):  # 4批，每批3条
            for i in range(3):
                compressor.append(f"批次{batch}-消息{i}")
        
        # 应该只保留最大数量的记忆块
        assert len(compressor.memory_blocks) == 2
        assert compressor.stats["total_compressions"] == 4
    
    def test_get_context(self, compressor, mock_llm_client):
        """测试获取上下文"""
        # 添加一些消息触发压缩
        for i in range(4):
            compressor.append(f"历史消息 {i}")
        
        # 添加最近消息
        compressor.append("最近消息 1")
        compressor.append("最近消息 2")
        
        # 获取上下文
        context = compressor.get_context()
        
        # 验证包含记忆和最近消息
        assert "=== 历史记忆 ===" in context
        assert "=== 最近对话 ===" in context
        assert "最近消息 1" in context
        assert "最近消息 2" in context
    
    def test_disable_compression(self, mock_llm_client):
        """测试禁用压缩"""
        compressor = ContextCompressor(
            llm_client=mock_llm_client,
            window_size=5,
            block_size=3,
            enable_compression=False
        )
        
        # 添加超过 block_size 的消息
        for i in range(5):
            compressor.append(f"消息 {i}")
        
        # 不应该触发压缩
        assert len(compressor.memory_blocks) == 0
        assert len(compressor.pending_messages) == 5
        mock_llm_client.chat.assert_not_called()
    
    def test_compression_error_handling(self, compressor, mock_llm_client):
        """测试压缩错误处理"""
        # 模拟 LLM 调用失败
        mock_llm_client.chat.side_effect = Exception("API 错误")
        
        # 添加消息触发压缩
        for i in range(3):
            compressor.append(f"消息 {i}")
        
        # 应该进行降级处理而不会崩溃
        assert compressor.stats["compression_errors"] == 0
        assert len(compressor.pending_messages) == 0  # 消息被清理
        assert len(compressor.memory_blocks) == 1
    
    def test_token_estimation(self, compressor):
        """测试 Token 估算"""
        # 测试中文
        chinese_text = "这是一段中文文本"
        tokens = compressor._estimate_tokens(chinese_text)
        assert tokens > 0
        assert tokens < len(chinese_text)  # 中文压缩
        
        # 测试英文
        english_text = "This is English text"
        tokens = compressor._estimate_tokens(english_text)
        assert tokens > 0
        assert tokens < len(english_text)
    
    def test_stats(self, compressor):
        """测试统计信息"""
        # 添加一些消息
        for i in range(5):
            compressor.append(f"消息 {i}")
        
        stats = compressor.get_stats()
        assert stats["total_messages"] == 5
        assert stats["current_recent_messages"] == 5
        assert stats["total_compressions"] == 1
        assert "compression_ratio" in stats
    
    def test_clear(self, compressor):
        """测试清空功能"""
        # 添加数据
        for i in range(5):
            compressor.append(f"消息 {i}")
        
        # 清空
        compressor.clear()
        
        # 验证所有数据被清空
        assert len(compressor.recent_messages) == 0
        assert len(compressor.pending_messages) == 0
        assert len(compressor.memory_blocks) == 0
    
    def test_export_import_memory(self, compressor, mock_llm_client):
        """测试记忆导入导出"""
        # 创建一些记忆块
        for i in range(6):
            compressor.append(f"消息 {i}")
        
        # 导出记忆
        exported = compressor.export_memory()
        assert len(exported) == 2
        assert all("summary" in block for block in exported)
        
        # 清空并重新导入
        compressor.clear()
        compressor.import_memory(exported)
        
        # 验证导入成功
        assert len(compressor.memory_blocks) == 2


class TestMemoryBlock:
    """MemoryBlock 测试类"""
    
    def test_creation(self):
        """测试创建记忆块"""
        block = MemoryBlock(
            summary="测试摘要",
            message_count=10
        )
        
        assert block.summary == "测试摘要"
        assert block.message_count == 10
        assert block.importance_score == 0.5
        assert block.token_estimate > 0
        assert block.created_at > 0
    
    def test_to_dict(self):
        """测试转换为字典"""
        block = MemoryBlock(
            summary="测试摘要",
            message_count=10,
            importance_score=0.8
        )
        
        data = block.to_dict()
        assert data["summary"] == "测试摘要"
        assert data["message_count"] == 10
        assert data["importance_score"] == 0.8
        assert "created_at" in data
        assert "token_estimate" in data


class TestContextSummarizer:
    """ContextSummarizer 测试类"""
    
    @pytest.fixture
    def summarizer(self):
        """创建测试用的摘要器"""
        mock_client = Mock(spec=LLMClient)
        mock_client.chat.return_value = "这是一个测试摘要"
        return ContextSummarizer(mock_client)
    
    def test_summarize(self, summarizer):
        """测试生成摘要"""
        messages = [
            "玩家: 我要探索这个洞穴",
            "系统: 你进入了幽暗的洞穴",
            "玩家: 使用火把照明"
        ]
        
        summary = summarizer.summarize(messages)
        assert summary == "这是一个测试摘要"
        assert summarizer.llm_client.chat.called
    
    def test_fallback_summary(self, summarizer):
        """测试降级摘要"""
        messages = [
            "玩家进行了探索",
            "玩家开始修炼",
            "玩家获得了宝物"
        ]
        
        summary = summarizer._fallback_summary(messages)
        assert "3次交互" in summary
        assert "探索" in summary or "修炼" in summary
    
    def test_calculate_importance(self, summarizer):
        """测试重要性计算"""
        # 普通消息
        messages1 = ["聊天内容1", "聊天内容2"]
        score1 = summarizer.calculate_importance(messages1)
        assert 0 <= score1 <= 1
        
        # 重要消息
        messages2 = ["玩家突破到了筑基期", "获得了极品法宝"]
        score2 = summarizer.calculate_importance(messages2)
        assert score2 > score1  # 重要消息分数应该更高
    
    def test_extract_entities(self, summarizer):
        """测试实体提取"""
        text = "玩家前往青云城，遇到了李道人，获得了回春丹"
        entities = summarizer.extract_entities(text)
        
        # 这是简单的规则提取，可能不完全准确
        # 主要测试功能是否正常
        assert isinstance(entities, dict)
        assert "npcs" in entities
        assert "locations" in entities
        assert "items" in entities


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
