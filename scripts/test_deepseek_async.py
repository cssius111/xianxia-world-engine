#!/usr/bin/env python3
"""Quick test script for DeepSeek async functionality."""

import asyncio
import sys
import os
import time

# Add project path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai.deepseek_client import DeepSeekClient


async def test_basic_functionality():
    """Test basic async functionality."""
    print("DeepSeek Async Quick Test")
    print("=" * 50)
    
    # Create client
    client = DeepSeekClient()
    
    # Check configuration
    print(f"API Key configured: {'Yes' if client.api_key else 'No'}")
    print(f"Model: {client.model}")
    print(f"Base URL: {client.base_url}")
    
    if not client.api_key:
        print("\n⚠️  Warning: DEEPSEEK_API_KEY not set!")
        print("   Using mock responses for testing")
    
    print("\n" + "-" * 50)
    
    # Test 1: Single async chat
    print("\n1. Testing single async chat...")
    try:
        start = time.time()
        result = await client.chat_async("你好，测试异步功能")
        duration = time.time() - start
        
        print(f"   ✅ Success! Response in {duration:.2f}s")
        print(f"   Response: {result['text'][:100]}...")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 2: Multiple concurrent requests
    print("\n2. Testing concurrent requests...")
    try:
        prompts = [f"测试并发请求 {i}" for i in range(5)]
        
        start = time.time()
        tasks = [client.chat_async(prompt) for prompt in prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start
        
        successful = sum(1 for r in results if isinstance(r, dict) and 'text' in r)
        print(f"   ✅ Completed {successful}/{len(prompts)} requests in {duration:.2f}s")
        print(f"   Average time per request: {duration/len(prompts):.2f}s")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 3: Parse with context
    print("\n3. Testing parse with context...")
    try:
        # Mock context
        class MockContext:
            scene = "禁地"
            player = type('Player', (), {'realm': '筑基期'})()
            target_realm = '元婴期'
            laws = [
                type('Law', (), {'enabled': True, 'code': 'FORBIDDEN_ARTS'})()
            ]
        
        ctx = MockContext()
        
        start = time.time()
        result = await client.parse_async("我要使用禁术攻击", ctx)
        duration = time.time() - start
        
        print(f"   ✅ Success! Parsed in {duration:.2f}s")
        print(f"   Intent: {result.get('intent', 'unknown')}")
        print(f"   Allowed: {result.get('allowed', True)}")
        print(f"   Reason: {result.get('reason', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 4: Performance comparison
    print("\n4. Performance comparison (sync vs async)...")
    try:
        num_requests = 10
        test_prompt = "性能测试"
        
        # Sync test
        print(f"   Testing {num_requests} sync requests...")
        start = time.time()
        for _ in range(num_requests):
            client.chat(test_prompt)
        sync_duration = time.time() - start
        
        # Async test
        print(f"   Testing {num_requests} async requests...")
        start = time.time()
        tasks = [client.chat_async(test_prompt) for _ in range(num_requests)]
        await asyncio.gather(*tasks)
        async_duration = time.time() - start
        
        speedup = sync_duration / async_duration
        improvement = (sync_duration - async_duration) / sync_duration * 100
        
        print(f"\n   Results:")
        print(f"   Sync:  {sync_duration:.2f}s ({sync_duration/num_requests:.2f}s per request)")
        print(f"   Async: {async_duration:.2f}s ({async_duration/num_requests:.2f}s per request)")
        print(f"   ✅ Speedup: {speedup:.1f}x ({improvement:.0f}% improvement)")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Cleanup
    print("\n5. Cleanup...")
    try:
        await client.close()
        print("   ✅ Async client closed successfully")
    except Exception as e:
        print(f"   ❌ Cleanup failed: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")


async def test_api_endpoints():
    """Test API endpoints if server is running."""
    import httpx
    
    print("\n\nTesting API Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:5001"
    
    async with httpx.AsyncClient() as client:
        # Check if server is running
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code != 200:
                print("Server not running, skipping API tests")
                return
        except Exception:
            print("Server not running, skipping API tests")
            return
        
        print("Server is running, testing endpoints...")
        
        # Test 1: Status endpoint
        print("\n1. Testing /api/llm/status...")
        try:
            response = await client.get(f"{base_url}/api/llm/status")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {data['status']}")
                print(f"   Async enabled: {data['async_enabled']}")
            else:
                print(f"   ❌ Status code: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        # Test 2: Chat endpoint
        print("\n2. Testing /api/llm/chat...")
        try:
            response = await client.post(
                f"{base_url}/api/llm/chat",
                json={"prompt": "测试异步API"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success! Mode: {data.get('mode', 'unknown')}")
                print(f"   Response: {data['text'][:50]}...")
            else:
                print(f"   ❌ Status code: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        # Test 3: Batch endpoint
        print("\n3. Testing /api/llm/batch...")
        try:
            response = await client.post(
                f"{base_url}/api/llm/batch",
                json={
                    "requests": [
                        {"prompt": "批量请求1"},
                        {"prompt": "批量请求2"},
                        {"prompt": "批量请求3"}
                    ]
                }
            )
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success! Processed {data['total']} requests")
                print(f"   Successful: {data['successful']}, Failed: {data['failed']}")
            else:
                print(f"   ❌ Status code: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")


async def main():
    """Main test function."""
    # Test basic functionality
    await test_basic_functionality()
    
    # Test API endpoints if available
    await test_api_endpoints()
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    # Set up basic environment
    os.environ.setdefault('USE_ASYNC_DEEPSEEK', '1')
    os.environ.setdefault('FLASK_ASYNC_ENABLED', '1')
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("Error: Python 3.7+ required for async features")
        sys.exit(1)
    
    # Run tests
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
