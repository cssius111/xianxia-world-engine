"""
Mock DeepSeek API for testing
"""
import json
import random
import time

class MockDeepSeekClient:
    """Mock DeepSeek客户端"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.call_count = 0
    
    def chat(self, messages, model="deepseek-chat", **kwargs):
        """模拟聊天API"""
        self.call_count += 1
        
        # 模拟延迟
        time.sleep(random.uniform(0.01, 0.05))
        
        # 根据输入生成响应
        last_message = messages[-1]['content'] if messages else ""
        
        # 默认响应
        response_content = {
            "action": "explore",
            "parameters": {"direction": "north"},
            "reason": "探索未知区域"
        }
        
        # 根据关键词调整响应
        if "修炼" in last_message:
            response_content = {
                "action": "cultivate",
                "parameters": {"hours": 1},
                "reason": "提升修为"
            }
        elif "战斗" in last_message:
            response_content = {
                "action": "attack",
                "parameters": {"target": "妖兽"},
                "reason": "获取经验"
            }
        
        return {
            "choices": [{
                "message": {
                    "content": json.dumps(response_content, ensure_ascii=False)
                }
            }],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }

# 全局mock实例
mock_client = MockDeepSeekClient()

def get_mock_client():
    """获取mock客户端"""
    return mock_client
