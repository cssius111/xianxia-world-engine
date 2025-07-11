"""Integration tests for DeepSeek async API endpoints."""

import asyncio
import json
import time
from typing import List, Dict, Any
import httpx
import pytest
import logging

logger = logging.getLogger(__name__)

# Test configuration
BASE_URL = "http://localhost:5001"
API_BASE = f"{BASE_URL}/api/llm"
TIMEOUT = httpx.Timeout(30.0, connect=5.0)


class TestDeepSeekAsyncIntegration:
    """Integration tests for DeepSeek async endpoints."""
    
    @pytest.fixture
    async def client(self):
        """Create async HTTP client."""
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            yield client
    
    @pytest.fixture
    def test_prompts(self):
        """Test prompts for various scenarios."""
        return [
            "你好，介绍一下修仙世界",
            "如何突破到金丹期？",
            "禁地探索有什么危险？",
            "给我讲一个关于剑仙的故事",
            "修仙者的日常生活是怎样的？"
        ]
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test if the server is running."""
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_deepseek_status(self, client):
        """Test DeepSeek API status endpoint."""
        response = await client.get(f"{API_BASE}/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "endpoints" in data
        assert len(data["endpoints"]) >= 5
        assert data["async_enabled"] is True
    
    @pytest.mark.asyncio
    async def test_async_chat_single(self, client):
        """Test single async chat request."""
        payload = {
            "prompt": "你好，我是新手玩家"
        }
        
        start_time = time.time()
        response = await client.post(f"{API_BASE}/chat", json=payload)
        duration = time.time() - start_time
        
        assert response.status_code == 200
        data = response.json()
        assert "text" in data
        assert len(data["text"]) > 0
        assert data.get("mode") == "async"
        
        logger.info(f"Async chat completed in {duration:.2f}s")
    
    @pytest.mark.asyncio
    async def test_sync_chat_compatibility(self, client):
        """Test sync chat endpoint for backward compatibility."""
        payload = {
            "prompt": "测试同步接口"
        }
        
        response = await client.post(f"{API_BASE}/chat/sync", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "text" in data
        assert "mode" not in data  # Sync endpoint doesn't return mode
    
    @pytest.mark.asyncio
    async def test_parse_with_context(self, client):
        """Test parse endpoint with game context."""
        payload = {
            "utterance": "我要使用禁术攻击敌人",
            "context": {
                "scene": "禁地",
                "player": {
                    "realm": "筑基期"
                },
                "target_realm": "元婴期",
                "laws": [
                    {
                        "enabled": True,
                        "code": "FORBIDDEN_ARTS"
                    },
                    {
                        "enabled": True,
                        "code": "CROSS_REALM_KILL"
                    }
                ]
            }
        }
        
        response = await client.post(f"{API_BASE}/parse", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "intent" in data
        assert "slots" in data
        assert "allowed" in data
        assert "reason" in data
        
        # Should not allow forbidden arts
        assert data["allowed"] is False
        assert "禁术" in data.get("reason", "")
    
    @pytest.mark.asyncio
    async def test_batch_processing(self, client, test_prompts):
        """Test batch processing endpoint."""
        payload = {
            "requests": [{"prompt": prompt} for prompt in test_prompts]
        }
        
        start_time = time.time()
        response = await client.post(f"{API_BASE}/batch", json=payload)
        duration = time.time() - start_time
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "total" in data
        assert "successful" in data
        assert "failed" in data
        
        assert data["total"] == len(test_prompts)
        assert data["successful"] > 0
        assert len(data["results"]) == len(test_prompts)
        
        # Check individual results
        for result in data["results"]:
            if result.get("success"):
                assert "text" in result
                assert len(result["text"]) > 0
        
        logger.info(f"Batch processing {len(test_prompts)} requests in {duration:.2f}s")
        logger.info(f"Average time per request: {duration/len(test_prompts):.2f}s")
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client):
        """Test multiple concurrent requests."""
        num_requests = 10
        prompts = [f"并发请求测试 {i}" for i in range(num_requests)]
        
        async def make_request(prompt):
            return await client.post(
                f"{API_BASE}/chat",
                json={"prompt": prompt}
            )
        
        start_time = time.time()
        tasks = [make_request(prompt) for prompt in prompts]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start_time
        
        # Count successful responses
        successful = 0
        for response in responses:
            if isinstance(response, httpx.Response) and response.status_code == 200:
                successful += 1
        
        assert successful >= num_requests * 0.8  # At least 80% success rate
        
        logger.info(f"Concurrent test: {successful}/{num_requests} successful")
        logger.info(f"Total time: {duration:.2f}s, avg: {duration/num_requests:.2f}s")
    
    @pytest.mark.asyncio
    async def test_error_handling(self, client):
        """Test error handling for invalid requests."""
        # Missing required field
        response = await client.post(f"{API_BASE}/chat", json={})
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        
        # Invalid batch request
        response = await client.post(f"{API_BASE}/batch", json={"requests": "not a list"})
        assert response.status_code == 400
        
        # Missing utterance in parse
        response = await client.post(f"{API_BASE}/parse", json={"context": {}})
        assert response.status_code == 400


class TestPerformanceComparison:
    """Compare performance between sync and async modes."""
    
    @pytest.mark.asyncio
    async def test_performance_comparison(self):
        """Compare sync vs async performance."""
        num_requests = 20
        prompt = "测试性能对比"
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Test sync mode performance
            sync_start = time.time()
            for i in range(num_requests):
                response = await client.post(
                    f"{API_BASE}/chat",
                    json={"prompt": prompt, "async": False}
                )
                assert response.status_code == 200
            sync_duration = time.time() - sync_start
            
            # Test async mode with concurrent requests
            async_start = time.time()
            tasks = [
                client.post(
                    f"{API_BASE}/chat",
                    json={"prompt": prompt, "async": True}
                )
                for _ in range(num_requests)
            ]
            responses = await asyncio.gather(*tasks)
            async_duration = time.time() - async_start
            
            # All should be successful
            assert all(r.status_code == 200 for r in responses)
            
            # Calculate improvement
            improvement = (sync_duration - async_duration) / sync_duration * 100
            
            logger.info(f"\nPerformance Comparison ({num_requests} requests):")
            logger.info(f"Sync mode: {sync_duration:.2f}s ({sync_duration/num_requests:.2f}s/req)")
            logger.info(f"Async mode: {async_duration:.2f}s ({async_duration/num_requests:.2f}s/req)")
            logger.info(f"Improvement: {improvement:.1f}%")
            logger.info(f"Speedup: {sync_duration/async_duration:.1f}x")


@pytest.mark.asyncio
async def test_stress_test():
    """Stress test with high concurrency."""
    num_requests = 100
    batch_size = 20
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # First check if server is ready
        response = await client.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            pytest.skip("Server not available")
        
        results = {
            "successful": 0,
            "failed": 0,
            "timeouts": 0,
            "errors": []
        }
        
        async def make_batch_request(batch_prompts):
            try:
                response = await client.post(
                    f"{API_BASE}/batch",
                    json={"requests": [{"prompt": p} for p in batch_prompts]}
                )
                if response.status_code == 200:
                    data = response.json()
                    results["successful"] += data.get("successful", 0)
                    results["failed"] += data.get("failed", 0)
                else:
                    results["failed"] += len(batch_prompts)
            except httpx.TimeoutException:
                results["timeouts"] += 1
                results["failed"] += len(batch_prompts)
            except Exception as e:
                results["errors"].append(str(e))
                results["failed"] += len(batch_prompts)
        
        # Create batches
        prompts = [f"压力测试 {i}" for i in range(num_requests)]
        batches = [prompts[i:i+batch_size] for i in range(0, num_requests, batch_size)]
        
        start_time = time.time()
        tasks = [make_batch_request(batch) for batch in batches]
        await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start_time
        
        total_processed = results["successful"] + results["failed"]
        success_rate = results["successful"] / total_processed * 100 if total_processed > 0 else 0
        
        logger.info(f"\nStress Test Results ({num_requests} requests in {len(batches)} batches):")
        logger.info(f"Total time: {duration:.2f}s")
        logger.info(f"Successful: {results['successful']}")
        logger.info(f"Failed: {results['failed']}")
        logger.info(f"Timeouts: {results['timeouts']}")
        logger.info(f"Success rate: {success_rate:.1f}%")
        logger.info(f"Throughput: {total_processed/duration:.1f} req/s")
        
        if results["errors"]:
            logger.error(f"Errors encountered: {results['errors'][:5]}")  # Show first 5 errors


if __name__ == "__main__":
    # Run tests with asyncio
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    async def main():
        """Run all tests."""
        print("Starting DeepSeek Async API Integration Tests...")
        print(f"Target: {BASE_URL}")
        print("-" * 60)
        
        # Check server availability
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{BASE_URL}/health")
                if response.status_code != 200:
                    print("❌ Server is not running!")
                    sys.exit(1)
                print("✅ Server is running")
            except Exception as e:
                print(f"❌ Cannot connect to server: {e}")
                sys.exit(1)
        
        # Run tests
        test_integration = TestDeepSeekAsyncIntegration()
        test_performance = TestPerformanceComparison()
        
        try:
            # Create client
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                # Run integration tests
                print("\n1. Testing API Status...")
                await test_integration.test_deepseek_status(client)
                print("✅ API Status OK")
                
                print("\n2. Testing Async Chat...")
                await test_integration.test_async_chat_single(client)
                print("✅ Async Chat OK")
                
                print("\n3. Testing Parse with Context...")
                await test_integration.test_parse_with_context(client)
                print("✅ Parse Endpoint OK")
                
                print("\n4. Testing Batch Processing...")
                test_prompts = test_integration.test_prompts(None)
                await test_integration.test_batch_processing(client, test_prompts)
                print("✅ Batch Processing OK")
                
                print("\n5. Testing Concurrent Requests...")
                await test_integration.test_concurrent_requests(client)
                print("✅ Concurrent Requests OK")
            
            print("\n6. Running Performance Comparison...")
            await test_performance.test_performance_comparison()
            print("✅ Performance Test Complete")
            
            print("\n7. Running Stress Test...")
            await test_stress_test()
            print("✅ Stress Test Complete")
            
            print("\n" + "="*60)
            print("✅ All tests passed successfully!")
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    # Run the async main function
    asyncio.run(main())
