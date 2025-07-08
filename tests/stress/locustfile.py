"""
Locust 压力测试脚本
用于模拟大量并发用户
"""

from locust import HttpUser, task, between, events
import json
import random
import time
from typing import Dict, Any


class XianXiaWorldUser(HttpUser):
    """修仙世界引擎用户行为模拟"""
    
    wait_time = between(1, 3)  # 用户操作间隔1-3秒
    
    def on_start(self):
        """用户开始时的初始化"""
        # 创建游戏会话
        response = self.client.post("/api/game/start", json={
            "player_name": f"测试玩家_{self.environment.runner.user_count}",
            "difficulty": "normal"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.session_id = data.get("session_id", "default")
        else:
            self.session_id = "default"
        
        # 命令池
        self.command_pool = [
            "查看状态",
            "探索周围",
            "开始修炼",
            "查看背包",
            "使用回血丹",
            "攻击野怪",
            "与商人对话",
            "购买物品",
            "接受任务",
            "查看地图",
            "返回城镇",
            "挑战副本",
            "学习技能",
            "强化装备",
            "查看排行榜"
        ]
    
    @task(3)
    def execute_command(self):
        """执行游戏命令（高频任务）"""
        command = random.choice(self.command_pool)
        
        with self.client.post(
            "/api/game/command",
            json={
                "command": command,
                "session_id": self.session_id
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success", False):
                    response.success()
                else:
                    response.failure(f"Command failed: {data.get('error', 'Unknown error')}")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def check_status(self):
        """查看状态（中频任务）"""
        self.client.get(f"/api/game/status?session_id={self.session_id}")
    
    @task(1)
    def view_inventory(self):
        """查看背包（中频任务）"""
        self.client.get(f"/api/game/inventory?session_id={self.session_id}")
    
    @task(2)
    def explore_area(self):
        """探索区域（较高频任务）"""
        areas = ["青云山", "幽冥谷", "天机阁", "万兽林", "极北冰原"]
        area = random.choice(areas)
        
        self.client.post("/api/game/explore", json={
            "area": area,
            "session_id": self.session_id
        })
    
    @task(1)
    def battle_monster(self):
        """战斗系统（中频任务）"""
        # 寻找怪物
        find_response = self.client.post("/api/game/find_monster", json={
            "session_id": self.session_id
        })
        
        if find_response.status_code == 200:
            # 发起战斗
            self.client.post("/api/game/battle", json={
                "action": "attack",
                "session_id": self.session_id
            })
    
    def on_stop(self):
        """用户结束时的清理"""
        # 保存游戏进度
        self.client.post("/api/game/save", json={
            "session_id": self.session_id
        })


class AdminUser(HttpUser):
    """管理员用户行为模拟"""
    
    wait_time = between(5, 10)  # 管理员操作间隔较长
    
    @task
    def check_metrics(self):
        """查看监控指标"""
        self.client.get("/metrics")
    
    @task
    def check_health(self):
        """健康检查"""
        self.client.get("/health")
    
    @task
    def view_statistics(self):
        """查看统计信息"""
        self.client.get("/api/admin/statistics")


class MobileUser(HttpUser):
    """移动端用户行为模拟"""
    
    wait_time = between(2, 5)  # 移动端操作稍慢
    
    def on_start(self):
        """设置移动端标识"""
        self.client.headers.update({
            "User-Agent": "XianXiaWorld-Mobile/1.0"
        })
        
        # 简化的命令池（移动端）
        self.simple_commands = [
            "状态",
            "背包",
            "修炼",
            "探索",
            "战斗"
        ]
    
    @task(5)
    def quick_command(self):
        """快速命令（移动端优化）"""
        command = random.choice(self.simple_commands)
        
        self.client.post("/api/mobile/quick_command", json={
            "cmd": command
        })
    
    @task(2)
    def auto_play(self):
        """自动游戏（移动端特性）"""
        self.client.post("/api/mobile/auto_play", json={
            "duration": 60  # 自动游戏60秒
        })


# 自定义统计
@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """初始化时的设置"""
    print("Locust 压力测试初始化完成")
    print(f"目标主机: {environment.host}")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """请求事件监听器"""
    if exception:
        print(f"请求失败: {name} - {exception}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """测试开始时的处理"""
    print(f"压力测试开始 - 用户数: {environment.runner.target_user_count}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束时的处理"""
    print("压力测试结束")
    
    # 打印统计信息
    stats = environment.stats
    print(f"\n测试统计:")
    print(f"  总请求数: {stats.total.num_requests}")
    print(f"  失败请求: {stats.total.num_failures}")
    print(f"  平均响应时间: {stats.total.avg_response_time:.2f}ms")
    print(f"  最大响应时间: {stats.total.max_response_time:.2f}ms")
    print(f"  RPS: {stats.total.current_rps:.2f}")


# 自定义负载形状（可选）
class StagesShape:
    """阶段性负载形状"""
    
    stages = [
        {"duration": 60, "users": 10, "spawn_rate": 1},     # 预热阶段
        {"duration": 300, "users": 100, "spawn_rate": 5},   # 正常负载
        {"duration": 120, "users": 500, "spawn_rate": 10},  # 高峰负载
        {"duration": 60, "users": 1000, "spawn_rate": 20},  # 压力测试
        {"duration": 120, "users": 100, "spawn_rate": 10},  # 恢复阶段
    ]
    
    def tick(self):
        run_time = self.get_run_time()
        
        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data
        
        return None


if __name__ == "__main__":
    # 可以直接运行进行调试
    print("请使用以下命令运行 Locust 压力测试:")
    print("locust -f locustfile.py --host=http://localhost:5000")
    print("\n或使用 Web UI:")
    print("locust -f locustfile.py --host=http://localhost:5000 --web-host=0.0.0.0")
    print("\n或使用无界面模式:")
    print("locust -f locustfile.py --host=http://localhost:5000 --headless -u 100 -r 10 -t 5m")
