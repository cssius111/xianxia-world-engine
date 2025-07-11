#!/usr/bin/env python3
"""
DeepSeek API 性能基准测试脚本
用于测试同步和异步API的性能对比
"""

import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import requests
import httpx
import json
import os
import sys
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 测试配置
TEST_CONFIG = {
    "base_url": "http://localhost:5001",
    "test_prompts": [
        "玩家想要突破到金丹期",
        "我要去禁地探索",
        "使用禁术攻击敌人",
        "查看我的修为境界",
        "前往主城交易",
    ],
    "concurrent_requests": [1, 5, 10, 20, 50],
    "requests_per_test": 100,
    "timeout": 30
}


class BenchmarkResult:
    """基准测试结果"""
    def __init__(self, name: str):
        self.name = name
        self.response_times: List[float] = []
        self.errors = 0
        self.total_time = 0
        
    def add_response(self, response_time: float):
        self.response_times.append(response_time)
        
    def add_error(self):
        self.errors += 1
        
    def calculate_stats(self) -> Dict[str, Any]:
        if not self.response_times:
            return {
                "name": self.name,
                "error": "No successful responses"
            }
            
        return {
            "name": self.name,
            "total_requests": len(self.response_times) + self.errors,
            "successful_requests": len(self.response_times),
            "failed_requests": self.errors,
            "error_rate": self.errors / (len(self.response_times) + self.errors) * 100,
            "min_time": min(self.response_times),
            "max_time": max(self.response_times),
            "avg_time": statistics.mean(self.response_times),
            "median_time": statistics.median(self.response_times),
            "p95_time": self.percentile(95),
            "p99_time": self.percentile(99),
            "total_time": self.total_time,
            "requests_per_second": len(self.response_times) / self.total_time if self.total_time > 0 else 0
        }
        
    def percentile(self, p: int) -> float:
        """计算百分位数"""
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * p / 100)
        return sorted_times[min(index, len(sorted_times) - 1)]


class DeepSeekBenchmark:
    """DeepSeek API 基准测试"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.sync_client = requests.Session()
        self.async_client = None
        
    async def _get_async_client(self) -> httpx.AsyncClient:
        """获取异步客户端"""
        if self.async_client is None:
            self.async_client = httpx.AsyncClient(
                timeout=httpx.Timeout(TEST_CONFIG["timeout"]),
                limits=httpx.Limits(max_keepalive_connections=50, max_connections=100)
            )
        return self.async_client
        
    def test_sync_api(self, prompt: str) -> tuple[float, bool]:
        """测试同步API"""
        start_time = time.time()
        try:
            response = self.sync_client.post(
                f"{self.base_url}/api/llm/chat/sync",
                json={"prompt": prompt},
                timeout=TEST_CONFIG["timeout"]
            )
            response.raise_for_status()
            response_time = time.time() - start_time
            return response_time, True
        except Exception as e:
            print(f"Sync API error: {e}")
            return time.time() - start_time, False
            
    async def test_async_api(self, prompt: str) -> tuple[float, bool]:
        """测试异步API"""
        client = await self._get_async_client()
        start_time = time.time()
        try:
            response = await client.post(
                f"{self.base_url}/api/llm/chat",
                json={"prompt": prompt}
            )
            response.raise_for_status()
            response_time = time.time() - start_time
            return response_time, True
        except Exception as e:
            print(f"Async API error: {e}")
            return time.time() - start_time, False
            
    def run_sync_benchmark(self, num_requests: int, concurrency: int) -> BenchmarkResult:
        """运行同步API基准测试"""
        result = BenchmarkResult(f"Sync API (concurrency={concurrency})")
        prompts = TEST_CONFIG["test_prompts"] * (num_requests // len(TEST_CONFIG["test_prompts"]) + 1)
        prompts = prompts[:num_requests]
        
        print(f"\n运行同步API测试 (并发={concurrency}, 请求数={num_requests})")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(self.test_sync_api, prompt) for prompt in prompts]
            
            for future in as_completed(futures):
                response_time, success = future.result()
                if success:
                    result.add_response(response_time)
                else:
                    result.add_error()
                    
        result.total_time = time.time() - start_time
        return result
        
    async def run_async_benchmark(self, num_requests: int, concurrency: int) -> BenchmarkResult:
        """运行异步API基准测试"""
        result = BenchmarkResult(f"Async API (concurrency={concurrency})")
        prompts = TEST_CONFIG["test_prompts"] * (num_requests // len(TEST_CONFIG["test_prompts"]) + 1)
        prompts = prompts[:num_requests]
        
        print(f"\n运行异步API测试 (并发={concurrency}, 请求数={num_requests})")
        start_time = time.time()
        
        # 创建并发任务
        semaphore = asyncio.Semaphore(concurrency)
        
        async def limited_request(prompt):
            async with semaphore:
                return await self.test_async_api(prompt)
                
        tasks = [limited_request(prompt) for prompt in prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in results:
            if isinstance(res, Exception):
                result.add_error()
            else:
                response_time, success = res
                if success:
                    result.add_response(response_time)
                else:
                    result.add_error()
                    
        result.total_time = time.time() - start_time
        return result
        
    async def cleanup(self):
        """清理资源"""
        if self.async_client:
            await self.async_client.aclose()
        self.sync_client.close()


def print_results(results: List[Dict[str, Any]]):
    """打印测试结果"""
    print("\n" + "="*80)
    print("基准测试结果")
    print("="*80)
    
    for result in results:
        print(f"\n{result['name']}:")
        if "error" in result:
            print(f"  错误: {result['error']}")
            continue
            
        print(f"  总请求数: {result['total_requests']}")
        print(f"  成功请求: {result['successful_requests']}")
        print(f"  失败请求: {result['failed_requests']}")
        print(f"  错误率: {result['error_rate']:.2f}%")
        print(f"  最小响应时间: {result['min_time']:.3f}s")
        print(f"  最大响应时间: {result['max_time']:.3f}s")
        print(f"  平均响应时间: {result['avg_time']:.3f}s")
        print(f"  中位数响应时间: {result['median_time']:.3f}s")
        print(f"  95%响应时间: {result['p95_time']:.3f}s")
        print(f"  99%响应时间: {result['p99_time']:.3f}s")
        print(f"  总耗时: {result['total_time']:.3f}s")
        print(f"  请求/秒: {result['requests_per_second']:.2f}")


def save_results(results: List[Dict[str, Any]], filename: str):
    """保存测试结果到JSON文件"""
    output = {
        "test_time": datetime.now().isoformat(),
        "config": TEST_CONFIG,
        "results": results
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n结果已保存到: {filename}")


async def main():
    """主函数"""
    print("DeepSeek API 性能基准测试")
    print("="*80)
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{TEST_CONFIG['base_url']}/status")
        response.raise_for_status()
        print(f"✓ 服务运行正常: {TEST_CONFIG['base_url']}")
    except Exception as e:
        print(f"✗ 服务连接失败: {e}")
        print("请确保服务已启动")
        return
        
    benchmark = DeepSeekBenchmark(TEST_CONFIG["base_url"])
    all_results = []
    
    try:
        # 测试不同并发数
        for concurrency in TEST_CONFIG["concurrent_requests"]:
            # 同步API测试
            sync_result = benchmark.run_sync_benchmark(
                TEST_CONFIG["requests_per_test"], 
                concurrency
            )
            all_results.append(sync_result.calculate_stats())
            
            # 异步API测试（如果已实现）
            try:
                async_result = await benchmark.run_async_benchmark(
                    TEST_CONFIG["requests_per_test"], 
                    concurrency
                )
                all_results.append(async_result.calculate_stats())
            except Exception as e:
                print(f"异步API测试失败: {e}")
                print("（可能异步API尚未实现）")
                
            # 短暂休息，避免过载
            await asyncio.sleep(2)
            
    finally:
        await benchmark.cleanup()
        
    # 打印和保存结果
    print_results(all_results)
    
    # 保存到文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"benchmark_results_{timestamp}.json"
    save_results(all_results, filename)
    
    # 生成对比报告
    generate_comparison_report(all_results)


def generate_comparison_report(results: List[Dict[str, Any]]):
    """生成对比报告"""
    print("\n" + "="*80)
    print("性能对比分析")
    print("="*80)
    
    # 按并发数分组
    comparisons = {}
    for result in results:
        if "error" in result:
            continue
            
        # 提取并发数
        concurrency = int(result['name'].split('=')[1].rstrip(')'))
        if concurrency not in comparisons:
            comparisons[concurrency] = {}
            
        if "Sync" in result['name']:
            comparisons[concurrency]['sync'] = result
        else:
            comparisons[concurrency]['async'] = result
            
    # 打印对比
    for concurrency, data in sorted(comparisons.items()):
        print(f"\n并发数 {concurrency}:")
        
        if 'sync' in data and 'async' in data:
            sync_data = data['sync']
            async_data = data['async']
            
            # 计算性能提升
            avg_improvement = (sync_data['avg_time'] - async_data['avg_time']) / sync_data['avg_time'] * 100
            rps_improvement = (async_data['requests_per_second'] - sync_data['requests_per_second']) / sync_data['requests_per_second'] * 100
            
            print(f"  平均响应时间提升: {avg_improvement:.1f}%")
            print(f"  吞吐量(RPS)提升: {rps_improvement:.1f}%")
            print(f"  同步API RPS: {sync_data['requests_per_second']:.2f}")
            print(f"  异步API RPS: {async_data['requests_per_second']:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
