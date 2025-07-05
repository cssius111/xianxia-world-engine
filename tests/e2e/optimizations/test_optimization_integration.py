"""
优化功能 E2E 集成测试
测试 Mock 模式、重试机制的端到端功能
"""

import os
import pytest
from unittest.mock import patch

from src.xwe.core.nlp.nlp_processor import DeepSeekNLPProcessor


class TestOptimizationIntegration:
    """优化功能集成测试"""
    
    def test_mock_mode_end_to_end(self):
        """测试 Mock 模式端到端流程"""
        with patch.dict(os.environ, {"USE_MOCK_LLM": "true"}):
            processor = DeepSeekNLPProcessor()
            
            # 测试完整的解析流程
            test_cases = [
                ("探索周围环境", "探索", "action"),
                ("修炼提升实力", "修炼", "train"),
                ("查看当前状态", "查看状态", "check"),
                ("打开背包看看", "打开背包", "check")
            ]
            
            for command, expected_normalized, expected_intent in test_cases:
                result = processor.parse(command)
                
                # 验证结果格式
                assert result.raw == command
                assert result.normalized_command == expected_normalized
                assert result.intent == expected_intent
                assert isinstance(result.args, dict)
                assert result.confidence == 1.0
    
    def test_fallback_on_api_failure_simulation(self):
        """测试模拟 API 失败的回退机制"""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test"}):
            processor = DeepSeekNLPProcessor()
            
            # 模拟 DeepSeek API 调用失败
            with patch.object(processor, '_call_deepseek_api', side_effect=Exception("API Error")):
                result = processor.parse("探索")
                
                # 应该回退到本地解析
                assert result.normalized_command == "探索"
                assert result.intent == "action"
                assert result.confidence == 0.5  # 回退模式置信度
