"""
Prometheus 监控集成示例
展示如何在 XWE 中使用监控功能
"""

import time
from src.xwe.metrics.monitors.nlp_monitor import nlp_monitor

# 示例 1: 使用装饰器监控函数
@nlp_monitor.monitor_llm_call(model="deepseek-chat")
def call_deepseek_api(prompt: str) -> dict:
    """模拟 DeepSeek API 调用"""
    # 模拟 API 延迟
    time.sleep(0.5)
    
    # 模拟返回结果
    return {
        "choices": [{
            "message": {
                "content": "这是一个测试响应"
            }
        }],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }

# 示例 2: 手动记录指标
def process_player_command(command: str):
    """处理玩家命令"""
    start_time = time.time()
    
    try:
        # 调用 NLP API
        response = call_deepseek_api(f"玩家说：{command}")
        
        # 处理响应...
        
        # 手动记录成功
        nlp_monitor.record_request(
            prompt=command,
            response=response,
            duration=time.time() - start_time,
            model="deepseek-chat"
        )
        
    except Exception as e:
        # 记录失败
        nlp_monitor.record_request(
            prompt=command,
            response=None,
            duration=time.time() - start_time,
            model="deepseek-chat",
            error=e
        )
        raise

if __name__ == "__main__":
    print("🧪 测试 Prometheus 监控集成...")
    
    # 测试装饰器方式
    result = call_deepseek_api("探索周围环境")
    print(f"✅ API 调用成功: {result}")
    
    # 测试手动记录方式
    process_player_command("开始修炼")
    print("✅ 命令处理成功")
    
    print("\n📊 指标已记录，访问 http://localhost:5000/metrics 查看")
