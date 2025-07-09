#!/usr/bin/env python
"""
NLP 高级特性示例

演示修仙世界引擎 NLP 模块的高级功能，包括：
- 异步处理
- 自定义工具
- 上下文压缩
- 性能监控
- 自定义 LLM 提供商
"""

import asyncio
import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from xwe.core.nlp import DeepSeekNLPProcessor, ParsedCommand
from xwe.core.nlp.tool_router import register_tool, dispatch
from xwe.core.nlp.monitor import get_nlp_monitor
from xwe.core.nlp.context import ContextCompressor


def example_1_async_processing():
    """示例1: 异步命令处理"""
    print("=== 示例1: 异步处理 ===\n")
    
    async def process_commands_async():
        nlp = DeepSeekNLPProcessor()
        
        # 需要处理的命令列表
        commands = [
            "去青云峰修炼",
            "使用聚气丹",
            "查看修为进度",
            "学习新功法",
            "寻找修炼资源"
        ]
        
        # 异步并发处理
        print("并发处理多个命令...")
        start_time = time.time()
        
        # 创建异步任务
        tasks = [nlp.parse_command_async(cmd) for cmd in commands]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        
        # 显示结果
        for cmd, result in zip(commands, results):
            print(f"  {cmd} -> {result.normalized_command}")
        
        print(f"\n总耗时: {end_time - start_time:.2f}秒")
        print(f"平均每个命令: {(end_time - start_time) / len(commands):.2f}秒")
    
    # 运行异步示例
    asyncio.run(process_commands_async())


def example_2_custom_tools():
    """示例2: 自定义工具系统"""
    print("\n\n=== 示例2: 自定义工具 ===\n")
    
    # 注册自定义修炼工具
    @register_tool("advanced_cultivation")
    def advanced_cultivation(payload: Dict[str, Any]) -> Dict[str, Any]:
        """高级修炼系统"""
        technique = payload.get("technique", "基础功法")
        duration = payload.get("duration", 60)
        resources = payload.get("resources", [])
        
        # 计算修炼效果
        base_exp = 100
        multiplier = 1.0
        
        if "高级功法" in technique:
            multiplier *= 2.0
        
        if "灵石" in resources:
            multiplier *= 1.5
        
        exp_gained = int(base_exp * duration / 60 * multiplier)
        
        return {
            "success": True,
            "exp_gained": exp_gained,
            "technique_progress": 0.1,
            "message": f"修炼{technique}，获得{exp_gained}经验值",
            "side_effects": ["灵力提升", "悟性增加"]
        }
    
    # 注册炼丹工具
    @register_tool("alchemy")
    def alchemy(payload: Dict[str, Any]) -> Dict[str, Any]:
        """炼丹系统"""
        materials = payload.get("materials", [])
        furnace_level = payload.get("furnace_level", 1)
        
        # 简单的炼丹逻辑
        if len(materials) < 2:
            return {"success": False, "message": "材料不足"}
        
        success_rate = min(0.3 + furnace_level * 0.1, 0.9)
        import random
        
        if random.random() < success_rate:
            pills = ["聚气丹", "回春丹", "破障丹"]
            result_pill = random.choice(pills)
            return {
                "success": True,
                "result": result_pill,
                "quality": random.choice(["下品", "中品", "上品"]),
                "message": f"炼制成功，获得{result_pill}"
            }
        else:
            return {
                "success": False,
                "message": "炼丹失败，材料损毁"
            }
    
    # 测试工具调用
    print("测试自定义工具调用:")
    
    # 修炼工具
    result = dispatch("advanced_cultivation", {
        "technique": "高级功法",
        "duration": 120,
        "resources": ["灵石", "聚气丹"]
    })
    print(f"\n修炼结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 炼丹工具
    result = dispatch("alchemy", {
        "materials": ["灵草", "妖丹", "千年灵芝"],
        "furnace_level": 3
    })
    print(f"\n炼丹结果: {json.dumps(result, ensure_ascii=False, indent=2)}")


def example_3_context_compression():
    """示例3: 上下文压缩"""
    print("\n\n=== 示例3: 上下文压缩 ===\n")
    
    # 模拟长对话历史
    conversation_history = []
    for i in range(50):
        conversation_history.append({
            "turn": i,
            "user": f"用户命令 {i}",
            "response": f"系统响应 {i}",
            "timestamp": time.time() - (50 - i) * 60
        })
    
    print(f"原始对话历史长度: {len(conversation_history)} 轮")
    
    # 使用上下文压缩器
    nlp = DeepSeekNLPProcessor()
    
    # 构建包含长历史的上下文
    context = {
        "conversation_history": conversation_history,
        "player_state": {
            "level": 50,
            "cultivation_stage": "金丹期",
            "current_quest": "寻找天材地宝"
        }
    }
    
    # 使用压缩后的上下文进行解析
    print("\n使用压缩上下文解析命令...")
    result = nlp.parse_command("继续之前的任务", context=context)
    
    print(f"解析结果: {result.normalized_command}")
    print(f"相关意图: {result.intent}")
    
    # 显示压缩效果
    if hasattr(nlp, 'context_compressor') and nlp.context_compressor:
        compressed_size = nlp.context_compressor.get_compressed_size()
        original_size = len(json.dumps(context))
        print(f"\n压缩效果:")
        print(f"  原始大小: {original_size} 字节")
        print(f"  压缩后大小: {compressed_size} 字节")
        print(f"  压缩率: {(1 - compressed_size/original_size)*100:.1f}%")


def example_4_performance_monitoring():
    """示例4: 性能监控"""
    print("\n\n=== 示例4: 性能监控 ===\n")
    
    # 获取监控实例
    monitor = get_nlp_monitor()
    monitor.reset()  # 重置统计
    
    nlp = DeepSeekNLPProcessor()
    
    # 执行一些操作以生成监控数据
    test_commands = [
        "攻击", "防御", "使用技能 剑气纵横",
        "查看地图", "前往洞府", "修炼一个时辰",
        "无效命令测试", "查看背包", "使用灵石"
    ]
    
    print("执行测试命令...")
    for cmd in test_commands:
        try:
            result = nlp.parse_command(cmd)
            print(f"  ✓ {cmd}")
        except Exception as e:
            print(f"  ✗ {cmd} (错误: {type(e).__name__})")
    
    # 获取监控统计
    stats = monitor.get_stats()
    
    print(f"\n监控统计:")
    print(f"  总请求数: {stats.get('total_requests', 0)}")
    print(f"  成功数: {stats.get('successful_requests', 0)}")
    print(f"  失败数: {stats.get('failed_requests', 0)}")
    print(f"  成功率: {stats.get('success_rate', 0):.1%}")
    print(f"  平均延迟: {stats.get('avg_latency', 0):.3f}秒")
    print(f"  缓存命中率: {stats.get('cache_hit_rate', 0):.1%}")
    
    # 显示按意图分类的统计
    intent_stats = stats.get('intent_distribution', {})
    if intent_stats:
        print(f"\n意图分布:")
        for intent, count in intent_stats.items():
            print(f"  {intent}: {count}")


def example_5_custom_llm_provider():
    """示例5: 自定义 LLM 提供商"""
    print("\n\n=== 示例5: 自定义 LLM 提供商 ===\n")
    
    from xwe.core.nlp.llm_client import LLMClient
    
    class CustomLLMProvider:
        """自定义 LLM 提供商示例"""
        
        def __init__(self, name="CustomLLM"):
            self.name = name
            self.call_count = 0
        
        def complete(self, prompt: str, **kwargs) -> str:
            """模拟 LLM 完成"""
            self.call_count += 1
            
            # 简单的规则匹配作为示例
            if "攻击" in prompt:
                return json.dumps({
                    "intent": "combat.attack",
                    "command": "attack",
                    "args": {"target": "enemy"}
                })
            elif "修炼" in prompt:
                return json.dumps({
                    "intent": "cultivation.cultivate",
                    "command": "cultivate",
                    "args": {"duration": 60}
                })
            else:
                return json.dumps({
                    "intent": "unknown",
                    "command": "unknown",
                    "args": {}
                })
        
        async def complete_async(self, prompt: str, **kwargs) -> str:
            """异步版本"""
            await asyncio.sleep(0.1)  # 模拟网络延迟
            return self.complete(prompt, **kwargs)
    
    # 创建自定义提供商
    custom_provider = CustomLLMProvider()
    
    print("使用自定义 LLM 提供商:")
    print(f"  提供商名称: {custom_provider.name}")
    
    # 测试调用
    test_prompts = ["用户想要攻击", "用户想要修炼", "用户想要喝水"]
    
    for prompt in test_prompts:
        response = custom_provider.complete(prompt)
        result = json.loads(response)
        print(f"\n  输入: {prompt}")
        print(f"  意图: {result['intent']}")
        print(f"  命令: {result['command']}")
    
    print(f"\n总调用次数: {custom_provider.call_count}")


def example_6_advanced_context():
    """示例6: 高级上下文管理"""
    print("\n\n=== 示例6: 高级上下文管理 ===\n")
    
    nlp = DeepSeekNLPProcessor()
    
    # 构建复杂的游戏上下文
    complex_context = {
        "player": {
            "name": "云逸",
            "level": 45,
            "cultivation": {
                "stage": "金丹期",
                "progress": 0.75,
                "breakthrough_ready": True
            },
            "stats": {
                "hp": 8000,
                "mp": 5000,
                "attack": 1200,
                "defense": 800
            },
            "inventory": {
                "灵石": 500,
                "破障丹": 3,
                "天灵果": 1
            }
        },
        "location": {
            "region": "东域",
            "area": "青云山脉",
            "zone": "灵脉洞府",
            "special_features": ["高浓度灵气", "适合突破"]
        },
        "active_quests": [
            {
                "name": "突破之路",
                "stage": "准备突破",
                "requirements": ["破障丹", "安全地点", "充足灵力"]
            }
        ],
        "recent_actions": [
            {"action": "enter_cave", "result": "success", "time": -300},
            {"action": "meditate", "result": "mp_restored", "time": -120},
            {"action": "check_breakthrough", "result": "ready", "time": -30}
        ]
    }
    
    # 基于复杂上下文的智能命令解析
    test_commands = [
        "我准备好了",  # 应该理解为准备突破
        "使用道具",     # 应该推荐使用破障丹
        "开始吧",       # 应该开始突破
    ]
    
    print("基于丰富上下文的命令理解:\n")
    
    for cmd in test_commands:
        result = nlp.parse_command(cmd, context=complex_context)
        print(f"输入: '{cmd}'")
        print(f"  理解为: {result.normalized_command}")
        print(f"  意图: {result.intent}")
        print(f"  解释: {result.explanation}")
        if result.args:
            print(f"  参数: {result.args}")
        print()


def main():
    """运行所有高级示例"""
    print("修仙世界引擎 - NLP 高级特性示例")
    print("=" * 50)
    
    # 使用模拟模式
    os.environ["USE_MOCK_LLM"] = "true"
    
    try:
        example_1_async_processing()
        example_2_custom_tools()
        example_3_context_compression()
        example_4_performance_monitoring()
        example_5_custom_llm_provider()
        example_6_advanced_context()
        
        print("\n✅ 所有高级示例运行完成！")
        
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()