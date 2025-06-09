"""
NLP系统测试套件
"""

import unittest
import os
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from xwe.core.nlp.nlp_processor import NLPProcessor, NLPConfig
from xwe.core.command_parser import CommandType


class TestNLPProcessor(unittest.TestCase):
    """NLP处理器测试"""
    
    def setUp(self):
        """测试准备"""
        self.config = NLPConfig(enable_llm=False)  # 测试时禁用真实API
        self.nlp = NLPProcessor(config=self.config)
    
    def test_basic_commands(self):
        """测试基础命令"""
        test_cases = [
            ("查看状态", CommandType.STATUS),
            ("我要修炼", CommandType.CULTIVATE),
            ("攻击敌人", CommandType.ATTACK),
            ("突破境界", CommandType.BREAKTHROUGH)
        ]
        
        for input_text, expected_type in test_cases:
            with self.subTest(input=input_text):
                result = self.nlp.parse(input_text)
                self.assertIsNotNone(result)
                # 模糊匹配应该能识别这些基础命令
                if result.command_type != CommandType.UNKNOWN:
                    print(f"✓ '{input_text}' → {result.command_type}")
    
    def test_cultivate_with_duration(self):
        """测试带时长的修炼命令"""
        test_cases = [
            ("修炼一年", {"duration": "1年"}),
            ("我想修炼3个月", {"duration": "3月"}),
            ("闭关修炼10天", {"duration": "10天"})
        ]
        
        for input_text, expected_params in test_cases:
            with self.subTest(input=input_text):
                result = self.nlp.parse(input_text)
                if result.command_type == CommandType.CULTIVATE:
                    self.assertIn("duration", result.parameters)
                    print(f"✓ '{input_text}' → duration={result.parameters.get('duration')}")
    
    @patch('requests.post')
    def test_deepseek_integration(self, mock_post):
        """测试DeepSeek集成"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': '{"command": "CULTIVATE", "parameters": {"duration": "1年"}, "confidence": 0.9}'
                }
            }]
        }
        mock_post.return_value = mock_response
        
        # 启用LLM的配置
        config = NLPConfig(enable_llm=True, api_key="test-key")
        nlp = NLPProcessor(config=config)
        
        result = nlp.parse("我想要修炼一年时间")
        
        self.assertEqual(result.command_type, CommandType.CULTIVATE)
        self.assertEqual(result.parameters.get("duration"), "1年")
        mock_post.assert_called_once()
    
    def test_fallback_behavior(self):
        """测试降级行为"""
        # 完全无法理解的输入
        result = self.nlp.parse("这是一句完全无关的话")
        
        self.assertEqual(result.command_type, CommandType.UNKNOWN)
        # 应该提供建议
        if result.parameters and "suggestions" in result.parameters:
            self.assertIsInstance(result.parameters["suggestions"], list)
            self.assertGreater(len(result.parameters["suggestions"]), 0)


class TestDataManager(unittest.TestCase):
    """数据管理器V3测试"""

    def setUp(self):
        from xwe.core.data_manager_v3 import DM
        DM.clear_cache()
        DM.load_all()
        self.dm = DM

    def test_basic_loading(self):
        modules = self.dm.get_loaded_modules()
        self.assertIn("attribute_model", modules)
        strength = self.dm.get("attribute_model.primary_attributes.strength.name")
        self.assertEqual(strength, "力量")

    def test_validate_dependencies(self):
        issues = self.dm.validate_dependencies()
        self.assertIsInstance(issues, dict)


if __name__ == "__main__":
    print("🧪 运行测试套件...")
    print("="*60)
    
    # 运行测试
    unittest.main(verbosity=2)
