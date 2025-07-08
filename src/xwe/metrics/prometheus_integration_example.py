"""
Prometheus 监控集成示例
展示如何在 XianXia World Engine 中使用 Prometheus 指标
"""

import asyncio
import random
import time
from typing import Optional

# 导入监控相关模块
from src.xwe.metrics.prometheus_metrics import get_metrics_collector
from src.xwe.core.nlp.monitor import get_nlp_monitor
from src.xwe.core.nlp.llm_client import LLMClient


class MonitoredGameSystem:
    """带监控的游戏系统示例"""
    
    def __init__(self):
        self.metrics_collector = get_metrics_collector()
        self.nlp_monitor = get_nlp_monitor()
        self.llm_client = LLMClient()
        
    def process_player_command(self, command: str) -> dict:
        """
        处理玩家命令（带监控）
        
        Args:
            command: 玩家输入的命令
            
        Returns:
            处理结果
        """
        start_time = time.time()
        success = True
        error = None
        result = {}
        
        try:
            # 1. 解析命令类型
            command_type = self._get_command_type(command)
            
            # 2. 使用上下文管理器记录时间
            with self.metrics_collector.measure_time(
                histogram=None,  # 这里简化了，实际使用时传入对应的 histogram
                labels={'command_type': command_type, 'status': 'processing'}
            ):
                # 3. 检查缓存
                cached_result = self._check_cache(command)
                if cached_result:
                    self.metrics_collector.record_nlp_request(
                        command_type=command_type,
                        duration=time.time() - start_time,
                        success=True,
                        use_cache=True
                    )
                    return cached_result
                
                # 4. 调用 NLP 处理
                nlp_result = self._process_with_nlp(command)
                
                # 5. 执行游戏逻辑
                result = self._execute_game_logic(command_type, nlp_result)
                
        except Exception as e:
            success = False
            error = str(e)
            result = {'error': error}
            
        finally:
            # 6. 记录请求指标
            duration = time.time() - start_time
            self.nlp_monitor.record_request(
                command=command,
                handler=f"{command_type}_handler",
                duration=duration,
                success=success,
                confidence=0.9,
                use_cache=False,
                error=error,
                token_count=random.randint(50, 200)  # 示例
            )
            
        return result
    
    async def process_player_command_async(self, command: str) -> dict:
        """
        异步处理玩家命令（带监控）
        
        Args:
            command: 玩家输入的命令
            
        Returns:
            处理结果
        """
        # 更新异步队列指标
        self.metrics_collector.update_async_metrics(
            queue_size=1  # 示例值
        )
        
        try:
            # 使用异步 LLM 调用
            response = await self.llm_client.chat_async(
                prompt=f"解析游戏命令: {command}",
                temperature=0.1,
                max_tokens=256
            )
            
            # 处理响应...
            return {'response': response}
            
        finally:
            # 更新队列指标
            self.metrics_collector.update_async_metrics(
                queue_size=0
            )
    
    def _get_command_type(self, command: str) -> str:
        """提取命令类型"""
        if "探索" in command:
            return "explore"
        elif "战斗" in command or "攻击" in command:
            return "battle"
        elif "修炼" in command:
            return "cultivate"
        elif "背包" in command or "物品" in command:
            return "inventory"
        else:
            return "other"
    
    def _check_cache(self, command: str) -> Optional[dict]:
        """检查缓存（示例）"""
        # 这里简化处理，实际应该使用真正的缓存系统
        return None
    
    def _process_with_nlp(self, command: str) -> dict:
        """NLP 处理（示例）"""
        # 模拟 NLP 处理
        time.sleep(0.1)  # 模拟处理时间
        return {
            'intent': 'action',
            'entities': [],
            'confidence': 0.9
        }
    
    def _execute_game_logic(self, command_type: str, nlp_result: dict) -> dict:
        """执行游戏逻辑（示例）"""
        # 记录命令执行
        with self.metrics_collector.measure_time(
            histogram=None,
            labels={'command': command_type, 'handler': 'game_logic'}
        ):
            # 模拟游戏逻辑处理
            time.sleep(random.uniform(0.05, 0.2))
            
        return {
            'success': True,
            'message': f"执行了 {command_type} 命令",
            'data': {}
        }


class SystemMonitor:
    """系统监控器示例"""
    
    def __init__(self):
        self.metrics_collector = get_metrics_collector()
        self.running = False
        
    async def start_monitoring(self):
        """启动系统监控"""
        self.running = True
        
        while self.running:
            try:
                # 更新系统指标
                self._update_system_metrics()
                
                # 更新游戏指标
                self._update_game_metrics()
                
                # 每 30 秒更新一次
                await asyncio.sleep(30)
                
            except Exception as e:
                print(f"监控更新失败: {e}")
                await asyncio.sleep(60)  # 出错时等待更长时间
    
    def stop_monitoring(self):
        """停止监控"""
        self.running = False
    
    def _update_system_metrics(self):
        """更新系统资源指标"""
        try:
            import psutil
            
            # CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用
            memory = psutil.virtual_memory()
            memory_mb = memory.used / 1024 / 1024
            
            self.metrics_collector.update_system_metrics(
                cpu_percent=cpu_percent,
                memory_mb=memory_mb
            )
            
        except ImportError:
            # psutil 未安装，使用模拟数据
            self.metrics_collector.update_system_metrics(
                cpu_percent=random.uniform(10, 50),
                memory_mb=random.uniform(500, 2000)
            )
    
    def _update_game_metrics(self):
        """更新游戏状态指标"""
        # 这里使用模拟数据，实际应该从游戏状态获取
        self.metrics_collector.update_game_metrics(
            instances=random.randint(1, 10),
            players=random.randint(0, 50)
        )


def main():
    """示例主函数"""
    print("Prometheus 监控集成示例")
    print("-" * 50)
    
    # 创建监控的游戏系统
    game_system = MonitoredGameSystem()
    
    # 模拟处理一些命令
    test_commands = [
        "探索周围环境",
        "攻击野怪",
        "查看背包",
        "修炼心法",
        "使用丹药"
    ]
    
    print("\n同步处理命令示例:")
    for cmd in test_commands:
        print(f"\n处理命令: {cmd}")
        result = game_system.process_player_command(cmd)
        print(f"结果: {result}")
    
    # 获取监控统计
    monitor = get_nlp_monitor()
    stats = monitor.get_stats()
    
    print("\n" + "=" * 50)
    print("监控统计:")
    print(f"总请求数: {stats['total_requests']}")
    print(f"成功率: {stats['success_rate']}%")
    print(f"平均响应时间: {stats['avg_duration_ms']}ms")
    print(f"缓存命中率: {stats['cache_hit_rate']}%")
    
    # 异步示例
    print("\n" + "=" * 50)
    print("异步处理示例:")
    
    async def async_example():
        """异步处理示例"""
        # 创建系统监控器
        system_monitor = SystemMonitor()
        
        # 启动监控任务
        monitor_task = asyncio.create_task(system_monitor.start_monitoring())
        
        # 处理一些异步命令
        tasks = []
        for cmd in test_commands[:3]:
            task = game_system.process_player_command_async(cmd)
            tasks.append(task)
        
        # 等待命令处理完成
        results = await asyncio.gather(*tasks)
        
        print("\n异步处理结果:")
        for i, result in enumerate(results):
            print(f"命令 {i+1}: {result}")
        
        # 停止监控
        system_monitor.stop_monitoring()
        monitor_task.cancel()
        
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
    
    # 运行异步示例
    asyncio.run(async_example())
    
    print("\n" + "=" * 50)
    print("示例完成！")
    print("\n提示: 访问 http://localhost:5000/metrics 查看 Prometheus 指标")


if __name__ == "__main__":
    # 设置环境变量
    import os
    os.environ['ENABLE_PROMETHEUS'] = 'true'
    os.environ['USE_MOCK_LLM'] = 'true'
    
    main()
