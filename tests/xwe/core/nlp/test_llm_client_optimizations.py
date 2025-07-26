"""
LLM 客户端优化功能测试
测试可配置的重试机制等功能
"""

import json
import os
import pytest
from unittest.mock import Mock, patch

from src.xwe.core.nlp.llm_client import LLMClient


class TestLLMClientOptimizations:
    """LLM 客户端优化测试"""
    
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
    
