"""Unit tests for DeepSeek async client implementation."""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
import json

from src.ai.deepseek_client import DeepSeekClient


class TestDeepSeekAsyncClient:
    """Test cases for DeepSeek async client."""
    
    @pytest.fixture
    def client(self):
        """Create a test client instance."""
        return DeepSeekClient(api_key="test_key", model="test-model")
    
    @pytest.fixture
    def mock_context(self):
        """Create a mock game context."""
        class MockContext:
            def __init__(self):
                self.scene = "测试场景"
                self.player = Mock(realm="筑基期")
                self.target_realm = "金丹期"
                self.laws = [
                    Mock(enabled=True, code="FORBIDDEN_ARTS"),
                    Mock(enabled=False, code="CROSS_REALM_KILL")
                ]
        return MockContext()
    
    @pytest.mark.asyncio
    async def test_chat_async_success(self, client):
        """Test successful async chat request."""
        # Mock the async HTTP response
        mock_response = {
            "choices": [{
                "message": {
                    "content": "这是一个测试响应"
                }
            }]
        }
        
        with patch.object(client, '_call_openai_async', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response
            
            result = await client.chat_async("测试提示词")
            
            assert result["text"] == "这是一个测试响应"
            mock_call.assert_called_once_with("测试提示词")
    
    @pytest.mark.asyncio
    async def test_chat_async_error_handling(self, client):
        """Test error handling in async chat."""
        with patch.object(client, '_call_openai_async', new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = Exception("API错误")
            
            result = await client.chat_async("测试提示词")
            
            assert result["text"] == ""
            assert mock_call.called
    
    def test_chat_sync_backward_compatibility(self, client):
        """Test that sync chat method still works."""
        mock_response = {
            "choices": [{
                "message": {
                    "content": "同步响应"
                }
            }]
        }
        
        with patch.object(client, '_call_openai') as mock_call:
            mock_call.return_value = mock_response
            
            result = client.chat("测试提示词")
            
            assert result["text"] == "同步响应"
            mock_call.assert_called_once_with("测试提示词")
    
    @pytest.mark.asyncio
    async def test_parse_async_with_context(self, client, mock_context):
        """Test async parse with game context."""
        mock_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "intent": "cultivate",
                        "slots": {"target": "金丹期"},
                        "allowed": True,
                        "reason": ""
                    })
                }
            }]
        }
        
        with patch.object(client, '_call_openai_async', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response
            
            result = await client.parse_async("我要突破到金丹期", mock_context)
            
            assert result["intent"] == "cultivate"
            assert result["slots"]["target"] == "金丹期"
            assert result["allowed"] is True
            
            # Verify prompt contains context info
            call_args = mock_call.call_args[0][0]
            assert "测试场景" in call_args
            assert "筑基期" in call_args
            assert "禁止使用禁术" in call_args
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client):
        """Test multiple concurrent async requests."""
        mock_response = {
            "choices": [{
                "message": {
                    "content": "并发响应"
                }
            }]
        }
        
        with patch.object(client, '_call_openai_async', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response
            
            # Create 10 concurrent requests
            tasks = [client.chat_async(f"请求{i}") for i in range(10)]
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 10
            assert all(r["text"] == "并发响应" for r in results)
            assert mock_call.call_count == 10
    
    @pytest.mark.asyncio
    async def test_async_client_singleton(self, client):
        """Test that async client uses singleton pattern."""
        # Get client twice
        client1 = await client._get_async_client()
        client2 = await client._get_async_client()
        
        # Should be the same instance
        assert client1 is client2
    
    @pytest.mark.asyncio
    async def test_retry_logic(self, client):
        """Test retry logic with exponential backoff."""
        # Mock responses: fail twice, then succeed
        mock_responses = [
            Exception("Timeout"),
            Exception("Timeout"),
            {
                "choices": [{
                    "message": {
                        "content": "成功"
                    }
                }]
            }
        ]
        
        call_count = 0
        
        async def mock_post(*args, **kwargs):
            nonlocal call_count
            response = mock_responses[call_count]
            call_count += 1
            
            if isinstance(response, Exception):
                import httpx
                raise httpx.TimeoutException("Timeout")
            
            # Mock successful response
            mock_resp = Mock()
            mock_resp.json.return_value = response
            mock_resp.raise_for_status = Mock()
            return mock_resp
        
        with patch('httpx.AsyncClient.post', new=mock_post):
            client._async_client = None  # Reset client
            result = await client.chat_async("测试重试")
            
            assert result["text"] == "成功"
            assert call_count == 3  # Should retry twice
    
    @pytest.mark.asyncio
    async def test_close_async_client(self, client):
        """Test closing async client connections."""
        # Create a mock client
        mock_client = AsyncMock()
        client._async_client = mock_client
        
        await client.close()
        
        mock_client.aclose.assert_called_once()
        assert client._async_client is None
    
    def test_summarize_laws(self, client, mock_context):
        """Test law summarization logic."""
        summary = client._summarize_laws(mock_context.laws)
        
        # Should only include enabled laws
        assert "禁止使用禁术" in summary
        assert "禁止跨境界斩杀" not in summary
    
    @pytest.mark.asyncio
    async def test_http2_enabled(self, client):
        """Test that HTTP/2 is enabled for better performance."""
        async_client = await client._get_async_client()
        
        # Check HTTP/2 is enabled
        assert async_client._transport._pool._http2 is True


class TestDeepSeekClientIntegration:
    """Integration tests with mock API."""
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not os.getenv("DEEPSEEK_API_KEY"), reason="No API key")
    async def test_real_api_call(self):
        """Test real API call (requires API key)."""
        client = DeepSeekClient()
        
        result = await client.chat_async("你好")
        
        assert "text" in result
        assert len(result["text"]) > 0
    
    @pytest.mark.asyncio
    async def test_performance_comparison(self):
        """Compare performance of sync vs async methods."""
        import time
        
        client = DeepSeekClient(api_key="test_key")
        
        # Mock fast response
        mock_response = {
            "choices": [{
                "message": {
                    "content": "测试"
                }
            }]
        }
        
        # Test sync performance
        with patch.object(client, '_call_openai') as mock_sync:
            mock_sync.return_value = mock_response
            
            start = time.time()
            for _ in range(10):
                client.chat("测试")
            sync_time = time.time() - start
        
        # Test async performance
        with patch.object(client, '_call_openai_async', new_callable=AsyncMock) as mock_async:
            mock_async.return_value = mock_response
            
            start = time.time()
            tasks = [client.chat_async("测试") for _ in range(10)]
            await asyncio.gather(*tasks)
            async_time = time.time() - start
        
        # Async should be faster for concurrent requests
        print(f"Sync time: {sync_time:.3f}s, Async time: {async_time:.3f}s")
        # Note: In real scenarios, async would be significantly faster


@pytest.mark.asyncio
async def test_memory_cleanup():
    """Test that resources are properly cleaned up."""
    client = DeepSeekClient(api_key="test_key")
    
    # Create and use async client
    await client.chat_async("测试")
    
    # Close explicitly
    await client.close()
    
    # Verify cleanup
    assert client._async_client is None
    
    # Test __del__ cleanup
    client2 = DeepSeekClient(api_key="test_key")
    await client2.chat_async("测试")
    
    # Simulate deletion
    del client2
    
    # Give time for cleanup
    await asyncio.sleep(0.1)
