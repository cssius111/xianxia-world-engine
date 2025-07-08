#!/usr/bin/env python3
"""
验证 Prometheus 监控集成的脚本
用于测试指标是否正确暴露
"""

import os
import sys
import time
import requests
from pathlib import Path

# 添加项目路径
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# 设置环境变量
os.environ['ENABLE_PROMETHEUS'] = 'true'
os.environ['USE_MOCK_LLM'] = 'true'

def test_metrics_collection():
    """测试指标收集功能"""
    print("测试 Prometheus 指标收集...")
    
    try:
        from xwe.metrics.prometheus_metrics import get_metrics_collector
        from xwe.core.nlp.monitor import get_nlp_monitor
        
        # 获取收集器
        collector = get_metrics_collector()
        monitor = get_nlp_monitor()
        
        print("✓ 成功导入指标模块")
        
        # 模拟一些请求
        for i in range(5):
            monitor.record_request(
                command=f"test_command_{i}",
                handler="test_handler",
                duration=0.1 * (i + 1),
                success=i % 2 == 0,
                token_count=50 * (i + 1),
                use_cache=i == 2
            )
        
        print("✓ 成功记录测试请求")
        
        # 更新其他指标
        collector.update_game_metrics(instances=3, players=2)
        collector.update_async_metrics(thread_pool_size=5, queue_size=10)
        
        print("✓ 成功更新游戏和异步指标")
        
        # 获取统计信息
        stats = monitor.get_stats()
        print(f"\n统计信息:")
        print(f"  总请求数: {stats['total_requests']}")
        print(f"  成功率: {stats['success_rate']}%")
        print(f"  缓存命中率: {stats['cache_hit_rate']}%")
        print(f"  平均响应时间: {stats['avg_duration_ms']}ms")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False
    
    return True

def test_flask_integration():
    """测试 Flask 集成"""
    print("\n测试 Flask 集成...")
    
    try:
        from app import create_app
        
        # 创建应用
        app = create_app()
        
        print("✓ 成功创建 Flask 应用")
        
        # 创建测试客户端
        with app.test_client() as client:
            # 测试 metrics 端点
            response = client.get('/metrics')
            
            if response.status_code == 200:
                print("✓ /metrics 端点可访问")
                
                # 检查响应内容
                content = response.data.decode('utf-8')
                
                # 验证自定义指标
                custom_metrics = [
                    'xwe_nlp_request_seconds',
                    'xwe_nlp_token_count',
                    'xwe_nlp_cache_hit_total',
                    'xwe_game_instances_gauge'
                ]
                
                found_metrics = []
                for metric in custom_metrics:
                    if metric in content:
                        found_metrics.append(metric)
                
                print(f"\n找到的自定义指标:")
                for metric in found_metrics:
                    print(f"  ✓ {metric}")
                
                missing_metrics = set(custom_metrics) - set(found_metrics)
                if missing_metrics:
                    print(f"\n缺失的指标:")
                    for metric in missing_metrics:
                        print(f"  ✗ {metric}")
                
            else:
                print(f"✗ /metrics 端点返回错误: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"✗ Flask 集成测试失败: {e}")
        return False
    
    return True

def test_performance():
    """测试性能开销"""
    print("\n测试性能开销...")
    
    try:
        from xwe.metrics.prometheus_metrics import get_metrics_collector
        
        collector = get_metrics_collector()
        
        # 测试 1000 次记录的时间
        start_time = time.time()
        
        for i in range(1000):
            collector.record_nlp_request(
                command_type="test",
                duration=0.01,
                success=True,
                token_count=10
            )
        
        elapsed = time.time() - start_time
        ops_per_second = 1000 / elapsed
        
        print(f"✓ 1000 次指标记录耗时: {elapsed:.3f} 秒")
        print(f"✓ 每秒操作数: {ops_per_second:.0f}")
        
        if elapsed < 0.1:  # 应该在 100ms 内完成
            print("✓ 性能符合要求 (< 100ms)")
        else:
            print("✗ 性能不符合要求")
            return False
            
    except Exception as e:
        print(f"✗ 性能测试失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("XianXia World Engine Prometheus 集成验证")
    print("=" * 50)
    
    tests = [
        ("指标收集", test_metrics_collection),
        ("Flask 集成", test_flask_integration),
        ("性能测试", test_performance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 30}")
        print(f"运行测试: {test_name}")
        print(f"{'=' * 30}")
        
        result = test_func()
        results.append((test_name, result))
    
    print(f"\n{'=' * 50}")
    print("测试结果汇总:")
    print(f"{'=' * 50}")
    
    passed = 0
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(tests)} 测试通过")
    
    if passed == len(tests):
        print("\n🎉 所有测试通过！Prometheus 集成正常工作。")
    else:
        print("\n⚠️  部分测试失败，请检查配置。")

if __name__ == "__main__":
    main()
