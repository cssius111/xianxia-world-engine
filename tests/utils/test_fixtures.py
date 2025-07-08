"""
测试数据和模拟对象
提供测试所需的固定数据和模拟实现
"""

import random
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import time


@dataclass
class MockUser:
    """模拟用户"""
    id: str
    name: str
    level: int = 1
    realm: str = "炼气期"
    location: str = "青云城"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'level': self.level,
            'realm': self.realm,
            'location': self.location
        }


@dataclass
class MockGameState:
    """模拟游戏状态"""
    player: MockUser
    current_location: str
    inventory: List[Dict[str, Any]]
    active_quests: List[str]
    combat_state: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'player': self.player.to_dict(),
            'current_location': self.current_location,
            'inventory': self.inventory,
            'active_quests': self.active_quests,
            'combat_state': self.combat_state
        }


class MockLLMClient:
    """模拟 LLM 客户端"""
    
    def __init__(self, response_delay: float = 0.1):
        self.response_delay = response_delay
        self.call_count = 0
        self.last_prompt = None
        
    def chat(self, prompt: str, **kwargs) -> str:
        """模拟聊天响应"""
        self.call_count += 1
        self.last_prompt = prompt
        
        # 模拟延迟
        time.sleep(self.response_delay)
        
        # 根据输入生成响应
        if "探索" in prompt:
            return json.dumps({
                "normalized_command": "探索",
                "intent": "action",
                "args": {"direction": "周围"},
                "explanation": "玩家想要探索周围环境"
            }, ensure_ascii=False)
        elif "战斗" in prompt or "攻击" in prompt:
            return json.dumps({
                "normalized_command": "攻击",
                "intent": "combat",
                "args": {"target": "敌人"},
                "explanation": "玩家发起攻击"
            }, ensure_ascii=False)
        elif "状态" in prompt:
            return json.dumps({
                "normalized_command": "查看状态",
                "intent": "check",
                "args": {},
                "explanation": "玩家查看自身状态"
            }, ensure_ascii=False)
        else:
            return json.dumps({
                "normalized_command": "未知",
                "intent": "unknown",
                "args": {},
                "explanation": "无法理解的命令"
            }, ensure_ascii=False)
    
    async def chat_async(self, prompt: str, **kwargs) -> str:
        """模拟异步聊天响应"""
        import asyncio
        await asyncio.sleep(self.response_delay)
        return self.chat(prompt, **kwargs)
    
    def cleanup(self):
        """清理资源"""
        pass


class TestDataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def generate_conversation_history(length: int = 10) -> List[Dict[str, str]]:
        """生成对话历史"""
        conversation = []
        commands = [
            "探索周围", "查看状态", "使用物品", "与NPC对话",
            "开始战斗", "修炼功法", "查看地图", "完成任务"
        ]
        
        for i in range(length):
            user_msg = random.choice(commands)
            assistant_msg = f"执行了{user_msg}的操作"
            
            conversation.extend([
                {"role": "user", "content": user_msg},
                {"role": "assistant", "content": assistant_msg}
            ])
        
        return conversation
    
    @staticmethod
    def generate_game_commands(count: int = 100) -> List[str]:
        """生成游戏命令列表"""
        templates = [
            "探索{location}",
            "攻击{monster}",
            "使用{item}",
            "与{npc}对话",
            "学习{skill}",
            "前往{destination}",
            "查看{target}",
            "购买{goods}",
            "出售{item}",
            "修炼{time}小时"
        ]
        
        locations = ["东方密林", "西方沙漠", "南方火山", "北方冰原"]
        monsters = ["妖兽", "魔物", "邪修", "凶兽"]
        items = ["回血丹", "灵石", "法宝", "符箓"]
        npcs = ["长老", "商人", "守卫", "神秘人"]
        skills = ["剑法", "身法", "阵法", "炼丹术"]
        
        commands = []
        for _ in range(count):
            template = random.choice(templates)
            command = template.format(
                location=random.choice(locations),
                monster=random.choice(monsters),
                item=random.choice(items),
                npc=random.choice(npcs),
                skill=random.choice(skills),
                destination=random.choice(locations),
                target=random.choice(["状态", "背包", "任务", "地图"]),
                goods=random.choice(items),
                time=random.randint(1, 6)
            )
            commands.append(command)
        
        return commands
    
    @staticmethod
    def generate_stress_test_data() -> Dict[str, Any]:
        """生成压力测试数据"""
        return {
            'users': [
                MockUser(
                    id=f"user_{i}",
                    name=f"测试玩家{i}",
                    level=random.randint(1, 100),
                    realm=random.choice(["炼气期", "筑基期", "金丹期", "元婴期"])
                )
                for i in range(100)
            ],
            'commands': TestDataGenerator.generate_game_commands(1000),
            'large_context': [
                {"content": "x" * 1000} for _ in range(100)
            ],
            'edge_cases': [
                "",  # 空命令
                " " * 100,  # 纯空格
                "a" * 10000,  # 超长命令
                "��������",  # 特殊字符
                "'; DROP TABLE users; --",  # SQL注入
                "<script>alert('xss')</script>",  # XSS
                "../../etc/passwd",  # 路径遍历
            ]
        }


class MockDatabase:
    """模拟数据库"""
    
    def __init__(self):
        self.data = {}
        self.query_count = 0
        self.transaction_active = False
    
    def save(self, key: str, value: Any) -> bool:
        """保存数据"""
        self.query_count += 1
        self.data[key] = value
        return True
    
    def load(self, key: str) -> Optional[Any]:
        """加载数据"""
        self.query_count += 1
        return self.data.get(key)
    
    def delete(self, key: str) -> bool:
        """删除数据"""
        self.query_count += 1
        if key in self.data:
            del self.data[key]
            return True
        return False
    
    def begin_transaction(self):
        """开始事务"""
        self.transaction_active = True
    
    def commit(self):
        """提交事务"""
        self.transaction_active = False
    
    def rollback(self):
        """回滚事务"""
        self.transaction_active = False
        # 实际实现中应该恢复数据
    
    def clear(self):
        """清空数据库"""
        self.data.clear()
        self.query_count = 0


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {
            'request_count': 0,
            'total_time': 0,
            'error_count': 0,
            'response_times': []
        }
    
    def record_request(self, duration: float, success: bool = True):
        """记录请求"""
        self.metrics['request_count'] += 1
        self.metrics['total_time'] += duration
        self.metrics['response_times'].append(duration)
        
        if not success:
            self.metrics['error_count'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        response_times = self.metrics['response_times']
        
        if not response_times:
            return {
                'request_count': 0,
                'avg_response_time': 0,
                'error_rate': 0
            }
        
        return {
            'request_count': self.metrics['request_count'],
            'avg_response_time': sum(response_times) / len(response_times),
            'p95_response_time': sorted(response_times)[int(len(response_times) * 0.95)],
            'error_rate': self.metrics['error_count'] / self.metrics['request_count'],
            'total_time': self.metrics['total_time']
        }
    
    def reset(self):
        """重置统计"""
        self.metrics = {
            'request_count': 0,
            'total_time': 0,
            'error_count': 0,
            'response_times': []
        }


# 预定义的测试场景
TEST_SCENARIOS = {
    'basic_gameplay': {
        'name': '基础游戏流程',
        'commands': [
            "查看状态",
            "探索周围",
            "拾取物品",
            "查看背包",
            "使用回血丹",
            "继续探索"
        ]
    },
    'combat_scenario': {
        'name': '战斗场景',
        'commands': [
            "寻找敌人",
            "查看敌人信息",
            "使用攻击技能",
            "使用防御技能",
            "使用药品",
            "逃跑"
        ]
    },
    'social_interaction': {
        'name': '社交互动',
        'commands': [
            "查看附近玩家",
            "与玩家交谈",
            "添加好友",
            "组队邀请",
            "交易请求",
            "查看好友列表"
        ]
    },
    'cultivation_system': {
        'name': '修炼系统',
        'commands': [
            "开始修炼",
            "查看修炼进度",
            "突破境界",
            "学习新技能",
            "强化技能",
            "查看技能列表"
        ]
    }
}


# 错误注入器
class ErrorInjector:
    """用于测试的错误注入器"""
    
    def __init__(self, error_rate: float = 0.1):
        self.error_rate = error_rate
        self.enabled = True
    
    def should_fail(self) -> bool:
        """判断是否应该失败"""
        return self.enabled and random.random() < self.error_rate
    
    def inject_error(self):
        """注入错误"""
        if not self.should_fail():
            return
        
        errors = [
            TimeoutError("模拟超时"),
            ConnectionError("模拟连接错误"),
            ValueError("模拟数据错误"),
            MemoryError("模拟内存错误"),
            RuntimeError("模拟运行时错误")
        ]
        
        raise random.choice(errors)
    
    def inject_delay(self, min_delay: float = 0.1, max_delay: float = 2.0):
        """注入延迟"""
        if self.should_fail():
            delay = random.uniform(min_delay, max_delay)
            time.sleep(delay)


# 导出所有测试工具
__all__ = [
    'MockUser',
    'MockGameState',
    'MockLLMClient',
    'TestDataGenerator',
    'MockDatabase',
    'PerformanceMonitor',
    'TEST_SCENARIOS',
    'ErrorInjector'
]
