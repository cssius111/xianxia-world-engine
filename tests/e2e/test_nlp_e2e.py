"""
端到端测试套件
测试完整的用户场景和系统集成
"""

import pytest
import asyncio
import time
import json
import os
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import tracemalloc
import gc

# 添加项目路径
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# 设置测试环境
os.environ['USE_MOCK_LLM'] = 'true'
os.environ['ENABLE_PROMETHEUS'] = 'true'
os.environ['ENABLE_CONTEXT_COMPRESSION'] = 'true'


class TestNLPEndToEnd:
    """NLP 模块端到端测试"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return app.test_client()
    
    @pytest.fixture
    def nlp_processor(self):
        """创建 NLP 处理器"""
        from xwe.core.nlp.nlp_processor import NLPProcessor
        return NLPProcessor(use_context_compression=True)
    
    def test_complete_user_journey(self, client, nlp_processor):
        """测试完整的用户旅程"""
        # 1. 用户注册/登录
        response = client.post('/api/auth/login', json={
            'username': 'test_user',
            'password': 'test_pass'
        })
        assert response.status_code in [200, 404]  # 可能需要注册
        
        # 2. 创建游戏会话
        response = client.post('/api/game/start', json={
            'player_name': '测试道友',
            'difficulty': 'normal'
        })
        assert response.status_code in [200, 201]
        
        # 3. 执行一系列游戏命令
        test_commands = [
            "查看我的状态",
            "探索周围环境",
            "拾取灵石",
            "开始修炼",
            "查看背包",
            "使用回血丹",
            "与商人对话",
            "购买法宝",
            "挑战野怪",
            "返回城镇"
        ]
        
        for cmd in test_commands:
            # 处理命令
            result = nlp_processor.process(cmd)
            assert result is not None
            assert 'normalized_command' in result
            
            # 发送到服务器
            response = client.post('/api/game/command', json={
                'command': cmd
            })
            assert response.status_code == 200
            
            # 验证响应
            data = response.get_json()
            assert 'success' in data or 'result' in data
    
    @pytest.mark.slow
    def test_long_conversation(self, nlp_processor):
        """测试长对话（100+ 轮）"""
        conversation_rounds = 120
        context = []
        memory_usage_start = self._get_memory_usage()
        
        for i in range(conversation_rounds):
            # 生成对话
            if i % 10 == 0:
                command = "查看状态"
            elif i % 5 == 0:
                command = f"探索第{i//5}层秘境"
            else:
                command = f"与NPC_{i}对话"
            
            # 处理命令
            start_time = time.time()
            result = nlp_processor.process(command, context)
            process_time = time.time() - start_time
            
            # 验证结果
            assert result is not None
            assert process_time < 5.0  # 处理时间应小于5秒
            
            # 更新上下文
            context.append({
                'command': command,
                'result': result
            })
            
            # 每20轮检查一次内存
            if i % 20 == 0:
                gc.collect()
                memory_usage = self._get_memory_usage()
                memory_growth = memory_usage - memory_usage_start
                
                # 内存增长应该是合理的
                assert memory_growth < 100 * 1024 * 1024  # 小于100MB
                
                # 验证上下文压缩是否工作
                if hasattr(nlp_processor, 'context_compressor'):
                    compressed = nlp_processor.context_compressor.get_context()
                    compressed_size = len(str(compressed))
                    original_size = len(str(context))
                    compression_ratio = compressed_size / original_size if original_size > 0 else 1
                    assert compression_ratio < 0.8  # 至少20%的压缩率
    
    @pytest.mark.slow
    def test_concurrent_users(self, app):
        """测试并发用户（10+ 并发）"""
        from xwe.core.nlp.nlp_processor import NLPProcessor
        
        concurrent_users = 15
        commands_per_user = 20
        
        def simulate_user(user_id: int) -> Dict[str, Any]:
            """模拟单个用户的行为"""
            processor = NLPProcessor(use_context_compression=True)
            results = []
            errors = []
            
            for i in range(commands_per_user):
                try:
                    # 生成随机命令
                    commands = [
                        f"用户{user_id}探索区域{i}",
                        f"用户{user_id}战斗",
                        f"用户{user_id}修炼",
                        f"用户{user_id}查看背包"
                    ]
                    command = commands[i % len(commands)]
                    
                    # 处理命令
                    start_time = time.time()
                    result = processor.process(command)
                    duration = time.time() - start_time
                    
                    results.append({
                        'command': command,
                        'duration': duration,
                        'success': True
                    })
                    
                except Exception as e:
                    errors.append(str(e))
                    results.append({
                        'command': command,
                        'duration': 0,
                        'success': False,
                        'error': str(e)
                    })
            
            return {
                'user_id': user_id,
                'results': results,
                'errors': errors
            }
        
        # 使用线程池执行并发测试
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            start_time = time.time()
            
            for i in range(concurrent_users):
                future = executor.submit(simulate_user, i)
                futures.append(future)
            
            # 收集结果
            all_results = []
            for future in as_completed(futures):
                result = future.result()
                all_results.append(result)
            
            total_time = time.time() - start_time
        
        # 分析结果
        total_commands = 0
        successful_commands = 0
        total_errors = 0
        avg_duration = 0
        
        for user_result in all_results:
            for cmd_result in user_result['results']:
                total_commands += 1
                if cmd_result['success']:
                    successful_commands += 1
                    avg_duration += cmd_result['duration']
                else:
                    total_errors += 1
        
        if successful_commands > 0:
            avg_duration /= successful_commands
        
        # 验证结果
        success_rate = successful_commands / total_commands if total_commands > 0 else 0
        assert success_rate > 0.95  # 95%以上的成功率
        assert avg_duration < 1.0  # 平均处理时间小于1秒
        assert total_time < 60  # 总时间小于60秒
        
        print(f"\n并发测试结果:")
        print(f"  总命令数: {total_commands}")
        print(f"  成功率: {success_rate * 100:.2f}%")
        print(f"  平均处理时间: {avg_duration * 1000:.2f}ms")
        print(f"  总耗时: {total_time:.2f}秒")
    
    def test_error_recovery(self, nlp_processor):
        """测试错误恢复"""
        # 1. 测试无效输入恢复
        invalid_inputs = [
            "",  # 空输入
            " " * 1000,  # 超长空格
            "❌🔥💀" * 100,  # 大量表情符号
            "\n" * 50,  # 大量换行
            "a" * 10000,  # 超长输入
        ]
        
        for invalid_input in invalid_inputs:
            try:
                result = nlp_processor.process(invalid_input)
                # 应该返回合理的默认结果
                assert result is not None
                assert 'normalized_command' in result
            except Exception as e:
                # 不应该崩溃
                pytest.fail(f"处理无效输入时崩溃: {e}")
        
        # 2. 测试 API 超时恢复
        original_timeout = os.environ.get('LLM_TIMEOUT', '30')
        os.environ['LLM_TIMEOUT'] = '0.001'  # 设置极短超时
        
        try:
            # 即使超时也应该返回结果
            result = nlp_processor.process("测试超时恢复")
            assert result is not None
        finally:
            os.environ['LLM_TIMEOUT'] = original_timeout
        
        # 3. 测试内存压力恢复
        large_context = [{"content": "x" * 1000} for _ in range(1000)]
        try:
            result = nlp_processor.process("测试大上下文", large_context)
            assert result is not None
        except MemoryError:
            # 应该优雅处理内存错误
            pass
    
    @pytest.mark.slow
    def test_memory_leak_detection(self, nlp_processor):
        """内存泄漏检测"""
        # 启动内存追踪
        tracemalloc.start()
        
        # 获取初始快照
        snapshot1 = tracemalloc.take_snapshot()
        
        # 执行大量操作
        for i in range(100):
            context = [{"round": j, "data": "test" * 100} for j in range(50)]
            result = nlp_processor.process(f"测试命令 {i}", context)
            
            # 每10轮强制垃圾回收
            if i % 10 == 0:
                gc.collect()
        
        # 获取结束快照
        snapshot2 = tracemalloc.take_snapshot()
        
        # 比较差异
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        
        # 分析内存增长
        total_growth = 0
        suspicious_files = []
        
        for stat in top_stats[:10]:
            growth = stat.size_diff
            total_growth += growth
            
            # 检查是否有可疑的内存增长
            if growth > 10 * 1024 * 1024:  # 10MB
                suspicious_files.append({
                    'file': stat.traceback.format()[0],
                    'growth': growth / 1024 / 1024  # 转换为MB
                })
        
        # 停止追踪
        tracemalloc.stop()
        
        # 验证
        assert total_growth < 50 * 1024 * 1024  # 总增长小于50MB
        
        if suspicious_files:
            print("\n可疑的内存增长:")
            for file_info in suspicious_files:
                print(f"  {file_info['file']}: {file_info['growth']:.2f}MB")
    
    @pytest.mark.asyncio
    async def test_async_operations(self):
        """测试异步操作"""
        from xwe.core.nlp.llm_client import LLMClient
        
        client = LLMClient()
        
        # 测试异步并发
        tasks = []
        for i in range(10):
            task = client.chat_async(f"异步测试消息 {i}")
            tasks.append(task)
        
        # 等待所有任务完成
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # 验证结果
        assert len(results) == 10
        assert all(r is not None for r in results)
        assert total_time < 5.0  # 并发应该比串行快
        
        # 清理
        client.cleanup()
    
    def _get_memory_usage(self) -> int:
        """获取当前内存使用量（字节）"""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss


class TestSystemIntegration:
    """系统集成测试"""
    
    def test_full_system_workflow(self, app):
        """测试完整的系统工作流"""
        with app.test_client() as client:
            # 1. 健康检查
            response = client.get('/health')
            assert response.status_code in [200, 404]
            
            # 2. 指标端点
            response = client.get('/metrics')
            assert response.status_code == 200
            metrics_data = response.data.decode('utf-8')
            assert 'xwe_nlp_request_seconds' in metrics_data
            
            # 3. 游戏流程
            # 这里可以添加更多的集成测试
    
    def test_configuration_changes(self):
        """测试配置变更"""
        configs = [
            {'USE_MOCK_LLM': 'true', 'ENABLE_CONTEXT_COMPRESSION': 'true'},
            {'USE_MOCK_LLM': 'true', 'ENABLE_CONTEXT_COMPRESSION': 'false'},
            {'USE_MOCK_LLM': 'false', 'ENABLE_CONTEXT_COMPRESSION': 'true'},
        ]
        
        for config in configs:
            # 设置环境变量
            for key, value in config.items():
                os.environ[key] = value
            
            # 创建新的处理器
            from xwe.core.nlp.nlp_processor import NLPProcessor
            processor = NLPProcessor()
            
            # 测试基本功能
            result = processor.process("测试配置")
            assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
