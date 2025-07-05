"""
LLM 客户端优化功能测试
测试重试次数配置、Mock 模式等新功能
"""

import json
import os
import pytest
from unittest.mock import Mock, patch

from src.xwe.core.nlp.llm_client import LLMClient


class TestLLMClientOptimizations:
    """LLM 客户端优化测试"""
    
    def test_mock_mode_enabled(self):
        """测试 Mock 模式启用"""
        with patch.dict(os.environ, {"USE_MOCK_LLM": "true"}):
            client = LLMClient()
            assert client.use_mock is True
            
            # 测试 Mock 响应
            response = client.chat("探索")
            assert "探索" in response
            
    def test_mock_mode_disabled(self):
        """测试 Mock 模式禁用"""
        with patch.dict(os.environ, {"USE_MOCK_LLM": "false", "DEEPSEEK_API_KEY": "test"}):
            client = LLMClient()
            assert client.use_mock is False
    
    def test_configurable_retries(self):
        """测试可配置重试次数"""
        with patch.dict(os.environ, {"XWE_MAX_LLM_RETRIES": "5", "DEEPSEEK_API_KEY": "test"}):
            client = LLMClient()
            assert client.max_retries == 5
    
    def test_default_retries(self):
        """测试默认重试次数"""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test"}, clear=True):
            client = LLMClient()
            assert client.max_retries == 3
    
    def test_mock_response_generation(self):
        """测试 Mock 响应生成"""
        with patch.dict(os.environ, {"USE_MOCK_LLM": "true"}):
            client = LLMClient()
            
            # 测试不同命令的 Mock 响应
            test_cases = [
                ("探索", "探索"),
                ("修炼", "修炼"),
                ("背包", "打开背包"),
                ("状态", "查看状态"),
                ("未知命令xxx", "未知")
            ]
            
            for user_input, expected_command in test_cases:
                response = client.chat(user_input)
                parsed = json.loads(response)
                
                assert parsed["raw"] == user_input
                assert expected_command in parsed["normalized_command"]
