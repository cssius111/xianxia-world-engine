#!/usr/bin/env python3
"""
基础优化功能测试
"""
import time
import logging

# 添加项目路径

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_cache():
    logger.info("测试缓存系统...")
    try:
        from xwe.core.optimizations.smart_cache import SmartCache
        
        cache = SmartCache(max_size=5, ttl=1.0)
        
        # 测试基本操作
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # 测试TTL
        time.sleep(1.1)
        assert cache.get("key1") is None
        
        # 测试统计
        stats = cache.get_stats()
        assert 'hit_rate' in stats
        
        logger.info("✓ 缓存系统测试通过")
        return True
    except Exception as e:
        logger.error(f"✗ 缓存系统测试失败: {e}")
        return False

def test_events():
    logger.info("测试事件系统...")
    try:
        from xwe.core.optimizations.async_event_system import AsyncEventHandler
        
        handler = AsyncEventHandler(max_workers=1)
        handler.start()
        
        # 注册处理器
        results = []
        def test_handler(data):
            results.append(data['message'])
        
        handler.register_handler("test", test_handler)
        
        # 触发事件
        handler.trigger_event_sync("test", {"message": "hello"})
        
        # 处理事件
        handler.process_pending_events()
        time.sleep(0.1)
        
        handler.stop()
        
        # 验证结果
        assert len(results) > 0
        assert results[0] == "hello"
        
        logger.info("✓ 事件系统测试通过")
        return True
    except Exception as e:
        logger.error(f"✗ 事件系统测试失败: {e}")
        return False

def main():
    logger.info("开始测试基础优化功能...")
    
    tests = [test_cache, test_events]
    passed = 0
    
    for test in tests:
        if test():
            passed += 1
    
    logger.info(f"测试完成: {passed}/{len(tests)} 通过")
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
