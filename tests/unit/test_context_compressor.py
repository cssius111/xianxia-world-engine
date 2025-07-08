"""
单元测试 - 上下文压缩器
测试 ContextCompressor 的核心功能
"""

import pytest
import json
import time
from typing import List, Dict, Any

from xwe.core.context.context_compressor import ContextCompressor


class TestContextCompressor:
    """上下文压缩器单元测试"""
    
    @pytest.fixture
    def compressor(self):
        """创建压缩器实例"""
        return ContextCompressor()
    
    @pytest.fixture
    def sample_context(self):
        """创建示例上下文"""
        return [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！有什么可以帮助你的吗？"},
            {"role": "user", "content": "我想了解游戏规则"},
            {"role": "assistant", "content": "这是一个修仙世界..."},
            {"role": "user", "content": "如何提升境界？"},
            {"role": "assistant", "content": "提升境界需要修炼..."}
        ]
    
    def test_initialization(self):
        """测试初始化"""
        compressor = ContextCompressor(
            max_tokens=1000,
            compression_ratio=0.5,
            preserve_recent=5
        )
        
        assert compressor is not None
        assert compressor.max_tokens == 1000
        assert compressor.compression_ratio == 0.5
        assert compressor.preserve_recent == 5
    
    def test_compress_small_context(self, compressor, sample_context):
        """测试压缩小型上下文"""
        compressed = compressor.compress(sample_context)
        
        assert compressed is not None
        assert isinstance(compressed, list)
        # 小上下文可能不需要压缩
        assert len(compressed) <= len(sample_context)
    
    def test_compress_large_context(self, compressor):
        """测试压缩大型上下文"""
        # 创建大型上下文
        large_context = []
        for i in range(100):
            large_context.extend([
                {"role": "user", "content": f"这是第{i}个用户消息，包含一些重要信息"},
                {"role": "assistant", "content": f"这是第{i}个助手回复，提供详细解答"}
            ])
        
        original_size = len(json.dumps(large_context, ensure_ascii=False))
        compressed = compressor.compress(large_context)
        compressed_size = len(json.dumps(compressed, ensure_ascii=False))
        
        # 验证压缩效果
        assert compressed is not None
        assert len(compressed) < len(large_context)
        assert compressed_size < original_size
        
        # 计算压缩率
        compression_ratio = compressed_size / original_size
        assert compression_ratio < 0.8  # 至少20%的压缩
    
    def test_preserve_recent_messages(self, compressor):
        """测试保留最近消息"""
        context = []
        for i in range(20):
            context.append({
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"消息{i}"
            })
        
        compressor.preserve_recent = 5
        compressed = compressor.compress(context)
        
        # 验证最近的消息被保留
        recent_messages = context[-5:]
        compressed_contents = [msg['content'] for msg in compressed]
        
        for msg in recent_messages:
            assert msg['content'] in compressed_contents
    
    def test_preserve_important_messages(self, compressor):
        """测试保留重要消息"""
        context = [
            {"role": "system", "content": "重要系统消息"},
            {"role": "user", "content": "普通消息1"},
            {"role": "assistant", "content": "普通回复1"},
            {"role": "user", "content": "设置玩家名称：独孤求败"},  # 重要
            {"role": "assistant", "content": "名称已设置"},
            {"role": "user", "content": "普通消息2"},
            {"role": "assistant", "content": "普通回复2"},
        ]
        
        compressed = compressor.compress(context)
        compressed_str = json.dumps(compressed, ensure_ascii=False)
        
        # 验证重要信息被保留
        assert "系统消息" in compressed_str or "system" in compressed_str
        assert "独孤求败" in compressed_str or "玩家名称" in compressed_str
    
    def test_message_deduplication(self, compressor):
        """测试消息去重"""
        # 包含重复消息的上下文
        context = [
            {"role": "user", "content": "查看状态"},
            {"role": "assistant", "content": "你的状态是..."},
            {"role": "user", "content": "查看状态"},  # 重复
            {"role": "assistant", "content": "你的状态是..."},  # 重复
            {"role": "user", "content": "查看状态"},  # 重复
            {"role": "assistant", "content": "你的状态是..."},  # 重复
        ]
        
        compressed = compressor.compress(context)
        
        # 重复的消息应该被减少
        assert len(compressed) < len(context)
    
    def test_conversation_flow_preservation(self, compressor):
        """测试对话流程保留"""
        context = [
            {"role": "user", "content": "我想买装备"},
            {"role": "assistant", "content": "这里有剑、甲、盾"},
            {"role": "user", "content": "我要买剑"},
            {"role": "assistant", "content": "剑的价格是100金币"},
            {"role": "user", "content": "买了"},
            {"role": "assistant", "content": "购买成功"},
        ]
        
        compressed = compressor.compress(context)
        
        # 验证对话的逻辑流程被保留
        compressed_str = json.dumps(compressed, ensure_ascii=False)
        
        # 关键信息应该被保留
        key_words = ["装备", "剑", "100金币", "购买成功"]
        preserved_count = sum(1 for word in key_words if word in compressed_str)
        assert preserved_count >= 2  # 至少保留一半的关键信息
    
    def test_empty_context_handling(self, compressor):
        """测试空上下文处理"""
        # 空列表
        result = compressor.compress([])
        assert result == []
        
        # None
        result = compressor.compress(None)
        assert result == []
    
    def test_invalid_message_format(self, compressor):
        """测试无效消息格式处理"""
        invalid_contexts = [
            [{"content": "缺少role字段"}],
            [{"role": "user"}],  # 缺少content
            [{"role": "user", "content": None}],  # content为None
            ["这不是字典"],  # 错误类型
        ]
        
        for invalid_context in invalid_contexts:
            try:
                result = compressor.compress(invalid_context)
                assert isinstance(result, list)
            except Exception as e:
                pytest.fail(f"处理无效格式时崩溃: {e}")
    
    def test_compression_strategies(self, compressor):
        """测试不同的压缩策略"""
        # 创建不同类型的上下文
        context = []
        
        # 1. 聊天类消息（低重要性）
        for i in range(10):
            context.extend([
                {"role": "user", "content": f"闲聊{i}"},
                {"role": "assistant", "content": f"回应闲聊{i}"}
            ])
        
        # 2. 游戏操作（中等重要性）
        for i in range(5):
            context.extend([
                {"role": "user", "content": f"使用物品{i}"},
                {"role": "assistant", "content": f"使用成功{i}"}
            ])
        
        # 3. 关键信息（高重要性）
        context.extend([
            {"role": "user", "content": "设置密码：123456"},
            {"role": "assistant", "content": "密码已设置"},
            {"role": "user", "content": "充值1000元"},
            {"role": "assistant", "content": "充值成功"},
        ])
        
        compressed = compressor.compress(context)
        compressed_str = json.dumps(compressed, ensure_ascii=False)
        
        # 验证压缩策略：关键信息应该被优先保留
        assert "密码" in compressed_str or "充值" in compressed_str
        
        # 闲聊内容应该被更多地压缩
        chat_count = sum(1 for msg in compressed if "闲聊" in msg.get('content', ''))
        assert chat_count < 10  # 闲聊消息应该被压缩
    
    def test_performance(self, compressor):
        """测试压缩性能"""
        # 创建大量上下文
        huge_context = []
        for i in range(1000):
            huge_context.append({
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"这是一条包含很多内容的消息 {i} " * 10
            })
        
        start_time = time.time()
        compressed = compressor.compress(huge_context)
        compression_time = time.time() - start_time
        
        # 验证性能
        assert compression_time < 1.0  # 应该在1秒内完成
        assert len(compressed) < len(huge_context)
        
        print(f"压缩1000条消息耗时: {compression_time:.3f}秒")
        print(f"压缩比: {len(compressed)/len(huge_context):.2%}")
    
    def test_incremental_compression(self, compressor):
        """测试增量压缩"""
        # 模拟对话逐步增长的场景
        context = []
        compression_ratios = []
        
        for i in range(50):
            # 添加新消息
            context.extend([
                {"role": "user", "content": f"用户消息{i}"},
                {"role": "assistant", "content": f"助手回复{i}"}
            ])
            
            # 每10轮压缩一次
            if i % 10 == 9:
                original_len = len(context)
                compressed = compressor.compress(context)
                compressed_len = len(compressed)
                
                ratio = compressed_len / original_len
                compression_ratios.append(ratio)
                
                # 更新上下文为压缩后的版本
                context = compressed
        
        # 验证压缩率随着对话增长而提高
        assert all(r < 1.0 for r in compression_ratios)
        # 后期的压缩率应该更高
        if len(compression_ratios) > 2:
            assert compression_ratios[-1] <= compression_ratios[0]
    
    def test_context_coherence(self, compressor):
        """测试上下文连贯性"""
        # 创建一个有明确因果关系的对话
        context = [
            {"role": "user", "content": "我叫张三"},
            {"role": "assistant", "content": "你好，张三"},
            {"role": "user", "content": "记住这个数字：42"},
            {"role": "assistant", "content": "我记住了数字42"},
            {"role": "user", "content": "刚才我说的数字是多少？"},
            {"role": "assistant", "content": "你刚才说的数字是42"},
        ]
        
        # 添加一些填充内容
        for i in range(20):
            context.extend([
                {"role": "user", "content": f"无关消息{i}"},
                {"role": "assistant", "content": f"无关回复{i}"}
            ])
        
        compressed = compressor.compress(context)
        compressed_str = json.dumps(compressed, ensure_ascii=False)
        
        # 验证关键的因果关系被保留
        if "数字" in compressed_str:
            assert "42" in compressed_str  # 如果保留了问题，答案也应该被保留
    
    def test_token_counting(self, compressor):
        """测试 token 计数"""
        if hasattr(compressor, 'count_tokens'):
            text = "这是一个测试文本"
            token_count = compressor.count_tokens(text)
            
            assert isinstance(token_count, int)
            assert token_count > 0
            
            # 更长的文本应该有更多 tokens
            longer_text = text * 10
            longer_count = compressor.count_tokens(longer_text)
            assert longer_count > token_count
    
    def test_custom_importance_scoring(self, compressor):
        """测试自定义重要性评分"""
        # 如果支持自定义评分函数
        if hasattr(compressor, 'set_importance_scorer'):
            def custom_scorer(message):
                # 包含"重要"的消息得高分
                if "重要" in message.get('content', ''):
                    return 1.0
                return 0.1
            
            compressor.set_importance_scorer(custom_scorer)
            
            context = [
                {"role": "user", "content": "普通消息1"},
                {"role": "user", "content": "重要：记住密码123"},
                {"role": "user", "content": "普通消息2"},
                {"role": "user", "content": "重要：明天开会"},
            ]
            
            compressed = compressor.compress(context)
            compressed_contents = [msg['content'] for msg in compressed]
            
            # 重要消息应该被保留
            assert any("重要" in content for content in compressed_contents)


class TestCompressionStrategies:
    """测试不同的压缩策略"""
    
    def test_sliding_window_strategy(self):
        """测试滑动窗口策略"""
        compressor = ContextCompressor(strategy='sliding_window', window_size=10)
        
        context = [{"role": "user", "content": f"消息{i}"} for i in range(20)]
        compressed = compressor.compress(context)
        
        # 应该只保留最近的窗口大小的消息
        assert len(compressed) <= 10
        
        # 最近的消息应该被保留
        assert compressed[-1]['content'] == "消息19"
    
    def test_importance_based_strategy(self):
        """测试基于重要性的策略"""
        compressor = ContextCompressor(strategy='importance_based')
        
        context = [
            {"role": "system", "content": "系统消息", "importance": 1.0},
            {"role": "user", "content": "普通消息", "importance": 0.1},
            {"role": "user", "content": "重要命令", "importance": 0.9},
            {"role": "assistant", "content": "确认执行", "importance": 0.8},
        ]
        
        compressed = compressor.compress(context)
        compressed_contents = [msg['content'] for msg in compressed]
        
        # 高重要性的消息应该被保留
        assert "系统消息" in compressed_contents
        assert "重要命令" in compressed_contents
    
    def test_hybrid_strategy(self):
        """测试混合策略"""
        compressor = ContextCompressor(strategy='hybrid')
        
        # 创建包含不同类型消息的上下文
        context = []
        
        # 旧的重要消息
        context.append({"role": "system", "content": "游戏规则说明..."})
        
        # 中间的普通对话
        for i in range(50):
            context.extend([
                {"role": "user", "content": f"普通对话{i}"},
                {"role": "assistant", "content": f"普通回复{i}"}
            ])
        
        # 最近的操作
        context.extend([
            {"role": "user", "content": "购买终极装备"},
            {"role": "assistant", "content": "花费10000金币购买成功"},
        ])
        
        compressed = compressor.compress(context)
        compressed_str = json.dumps(compressed, ensure_ascii=False)
        
        # 验证混合策略的效果
        assert len(compressed) < len(context)
        assert "游戏规则" in compressed_str or "system" in compressed_str  # 重要信息
        assert "终极装备" in compressed_str  # 最近信息


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
