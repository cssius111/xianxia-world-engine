"""
NLPProcessor 与 ContextCompressor 集成测试
"""

import pytest
import os
import json
import tempfile
from unittest.mock import Mock, patch

from src.xwe.core.nlp.nlp_processor import DeepSeekNLPProcessor
from src.xwe.core.nlp.config import get_nlp_config
from src.xwe.core.context import ContextCompressor


class TestNLPProcessorIntegration:
    """测试 NLPProcessor 与 ContextCompressor 的集成"""
    
    @pytest.fixture
    def mock_config(self):
        """创建模拟配置"""
        config = Mock()
        config.get.return_value = {
            "enabled": True,
            "window_size": 5,
            "block_size": 3,
            "max_memory_blocks": 2
        }
        config.is_enabled.return_value = True
        config.validate_config.return_value = True
        config.get_api_key.return_value = "test_key"
        return config
    
    @pytest.fixture
    def processor_with_compression(self, mock_config):
        """创建启用压缩的处理器"""
        with patch('src.xwe.core.nlp.nlp_processor.get_nlp_config', return_value=mock_config):
            # 设置环境变量使用 Mock LLM
            os.environ["USE_MOCK_LLM"] = "true"
            processor = DeepSeekNLPProcessor()
            yield processor
            # 清理
            del os.environ["USE_MOCK_LLM"]
    
    def test_compression_enabled_initialization(self, processor_with_compression):
        """测试压缩器正确初始化"""
        assert processor_with_compression.context_compressor is not None
        assert isinstance(processor_with_compression.context_compressor, ContextCompressor)
        assert processor_with_compression.context_compressor.window_size == 5
        assert processor_with_compression.context_compressor.block_size == 3
    
    def test_build_prompt_with_compression(self, processor_with_compression):
        """测试使用压缩器构建 prompt"""
        # 添加一些历史对话
        processor_with_compression.context_compressor.append("用户: 探索周围")
        processor_with_compression.context_compressor.append("系统: 你发现了一个洞穴")
        
        # 构建新的 prompt
        prompt = processor_with_compression.build_prompt("进入洞穴")
        
        # 验证 prompt 包含上下文
        assert "对话上下文" in prompt
        assert "探索周围" in prompt
        assert "你发现了一个洞穴" in prompt
        assert "进入洞穴" in prompt
    
    def test_parse_with_context_recording(self, processor_with_compression):
        """测试解析时记录上下文"""
        # 执行几次解析
        commands = ["探索周围", "查看背包", "使用回春丹"]
        
        for cmd in commands:
            parsed = processor_with_compression.parse(cmd)
            # 验证命令被记录
            assert parsed is not None
        
        # 获取上下文统计
        stats = processor_with_compression.get_context_stats()
        assert stats["total_messages"] >= len(commands) * 2  # 用户输入 + 系统响应
    
    def test_compression_trigger(self, processor_with_compression):
        """测试压缩触发机制"""
        # 设置较小的 block_size 以便测试
        processor_with_compression.context_compressor.block_size = 3
        
        # 添加足够的消息触发压缩
        for i in range(4):
            processor_with_compression.parse(f"测试命令 {i}")
        
        # 检查压缩是否触发
        stats = processor_with_compression.get_context_stats()
        assert stats["total_compressions"] > 0
        assert stats["current_memory_blocks"] > 0
    
    def test_context_persistence(self, processor_with_compression):
        """测试上下文持久化"""
        # 添加一些对话
        processor_with_compression.parse("探索青云城")
        processor_with_compression.parse("前往丹药铺")
        processor_with_compression.parse("购买回春丹")
        
        # 触发压缩
        for i in range(5):
            processor_with_compression.parse(f"额外命令 {i}")
        
        # 保存记忆
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # 保存
            success = processor_with_compression.save_context_memory(temp_path)
            assert success
            
            # 验证文件内容
            with open(temp_path, 'r') as f:
                data = json.load(f)
            assert isinstance(data, list)
            assert len(data) > 0
            assert all("summary" in item for item in data)
            
            # 清空并重新加载
            processor_with_compression.clear_context()
            stats_after_clear = processor_with_compression.get_context_stats()
            assert stats_after_clear["current_memory_blocks"] == 0
            
            # 加载
            success = processor_with_compression.load_context_memory(temp_path)
            assert success
            
            # 验证加载成功
            stats_after_load = processor_with_compression.get_context_stats()
            assert stats_after_load["current_memory_blocks"] > 0
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_fallback_without_compression(self):
        """测试禁用压缩时的降级行为"""
        # 创建禁用压缩的配置
        config = Mock()
        config.get.side_effect = lambda key, default=None: {
            "context_compression": {"enabled": False},
            "cache_size": 128,
            "context_limit": 4096
        }.get(key, default)
        config.is_enabled.return_value = True
        config.validate_config.return_value = True
        config.get_api_key.return_value = "test_key"
        
        with patch('src.xwe.core.nlp.nlp_processor.get_nlp_config', return_value=config):
            os.environ["USE_MOCK_LLM"] = "true"
            processor = DeepSeekNLPProcessor()
            
            # 验证压缩器未初始化
            assert processor.context_compressor is None
            
            # 验证仍然可以正常工作
            prompt = processor.build_prompt("测试命令")
            assert "测试命令" in prompt
            
            # 清理
            del os.environ["USE_MOCK_LLM"]
    
    def test_compression_error_handling(self, processor_with_compression):
        """测试压缩错误处理"""
        # 模拟压缩器错误
        with patch.object(processor_with_compression.context_compressor, 'append', 
                         side_effect=Exception("压缩错误")):
            # 应该回退到传统模式
            prompt = processor_with_compression.build_prompt("测试命令")
            assert "测试命令" in prompt
    
    def test_clear_context(self, processor_with_compression):
        """测试清空上下文"""
        # 添加数据
        for i in range(5):
            processor_with_compression.parse(f"命令 {i}")
        
        # 验证有数据
        stats_before = processor_with_compression.get_context_stats()
        assert stats_before["total_messages"] > 0
        
        # 清空
        processor_with_compression.clear_context()
        
        # 验证已清空
        stats_after = processor_with_compression.get_context_stats()
        assert stats_after["current_recent_messages"] == 0
        assert stats_after["current_pending_messages"] == 0
        assert stats_after["current_memory_blocks"] == 0
    
    def test_monitoring_integration(self, processor_with_compression):
        """测试监控集成"""
        with patch.object(processor_with_compression.monitor, 'record_request') as mock_record:
            # 执行解析
            processor_with_compression.parse("测试命令")
            
            # 验证监控被调用并包含压缩信息
            mock_record.assert_called_once()
            call_args = mock_record.call_args[1]
            
            assert "context_compression_enabled" in call_args
            assert call_args["context_compression_enabled"] is True
            assert "context_compression_ratio" in call_args
            assert "token_count" in call_args


class TestPromptOptimization:
    """测试 Prompt 优化效果"""
    
    def test_token_reduction(self):
        """测试 Token 减少效果"""
        # 创建压缩器
        compressor = ContextCompressor(
            window_size=5,
            block_size=10
        )
        
        # 添加大量消息
        long_messages = [
            f"这是第{i}条很长的测试消息，包含了很多详细的信息和描述" * 3
            for i in range(20)
        ]
        
        for msg in long_messages:
            compressor.append(msg)
        
        # 获取压缩后的上下文
        compressed = compressor.get_context()
        
        # 计算原始长度和压缩后长度
        original_length = sum(len(msg) for msg in long_messages)
        compressed_length = len(compressed)
        
        # 验证压缩效果
        assert compressed_length < original_length
        compression_ratio = compressed_length / original_length
        assert compression_ratio < 0.5  # 至少压缩 50%
        
        print(f"压缩率: {compression_ratio:.2%}")
        print(f"原始长度: {original_length} 字符")
        print(f"压缩后: {compressed_length} 字符")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
