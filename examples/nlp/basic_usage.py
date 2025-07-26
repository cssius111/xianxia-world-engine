#!/usr/bin/env python
"""
NLP 基础使用示例

这个脚本演示了如何使用修仙世界引擎的 NLP 模块进行基本的命令解析。
"""

import os
import sys
from pathlib import Path

# 添加项目路径到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from xwe.core.nlp import DeepSeekNLPProcessor, ParsedCommand
from xwe.core.nlp.exceptions import NLPException


def example_1_simple_commands():
    """示例1: 解析简单命令"""
    print("=== 示例1: 简单命令解析 ===\n")
    
    # 初始化 NLP 处理器
    nlp = DeepSeekNLPProcessor()
    
    # 测试命令列表
    commands = [
        "攻击",
        "防御",
        "逃跑",
        "查看状态",
        "打开背包"
    ]
    
    for cmd in commands:
        try:
            result = nlp.parse_command(cmd)
            print(f"输入: {cmd}")
            print(f"  意图: {result.intent}")
            print(f"  标准命令: {result.normalized_command}")
            print(f"  参数: {result.args}")
            print(f"  解释: {result.explanation}")
            print()
        except NLPException as e:
            print(f"解析失败: {e}")
            print()


def example_2_natural_language():
    """示例2: 自然语言输入"""
    print("\n=== 示例2: 自然语言解析 ===\n")
    
    nlp = DeepSeekNLPProcessor()
    
    # 自然语言命令
    natural_commands = [
        "我想攻击那只妖兽",
        "快帮我防御一下",
        "这里太危险了，我要逃跑",
        "让我看看我的状态怎么样",
        "我的背包里有什么东西"
    ]
    
    for cmd in natural_commands:
        result = nlp.parse_command(cmd)
        print(f"输入: {cmd}")
        print(f"  解析结果: {result.normalized_command}")
        print(f"  置信度: {result.confidence:.2f}")
        print()


def example_3_with_context():
    """示例3: 带上下文的命令解析"""
    print("\n=== 示例3: 上下文感知解析 ===\n")
    
    nlp = DeepSeekNLPProcessor()
    
    # 战斗场景上下文
    combat_context = {
        "scene": {
            "type": "combat",
            "enemies": ["妖兽", "魔修"],
            "turn": 3
        },
        "player": {
            "hp": 50,
            "mp": 80,
            "status": "正常"
        }
    }
    
    # 探索场景上下文
    exploration_context = {
        "scene": {
            "type": "exploration",
            "location": "青云峰",
            "discovered_items": ["灵石", "草药"]
        }
    }
    
    # 相同的命令在不同上下文下的解析
    command = "快跑"
    
    # 战斗场景
    result1 = nlp.parse_command(command, context=combat_context)
    print(f"战斗场景 - 输入: {command}")
    print(f"  解析: {result1.normalized_command} (意图: {result1.intent})")
    
    # 探索场景
    result2 = nlp.parse_command(command, context=exploration_context)
    print(f"\n探索场景 - 输入: {command}")
    print(f"  解析: {result2.normalized_command} (意图: {result2.intent})")


def example_4_error_handling():
    """示例4: 错误处理"""
    print("\n\n=== 示例4: 错误处理 ===\n")
    
    # 如果未设置 API key，可在此处指定测试值
    os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY", "test")
    nlp = DeepSeekNLPProcessor()
    
    # 测试各种异常情况
    test_cases = [
        "",  # 空输入
        "a" * 1001,  # 超长输入
        "!@#$%^&*()",  # 特殊字符
        "这是一个完全无法理解的命令啊啊啊"  # 无法识别的命令
    ]
    
    for test_input in test_cases:
        try:
            result = nlp.parse_command(test_input)
            if result:
                print(f"输入: {test_input[:50]}...")
                print(f"  结果: {result.normalized_command}")
            else:
                print(f"输入: {test_input[:50]}...")
                print(f"  结果: 无法解析")
        except Exception as e:
            print(f"输入: {test_input[:50]}...")
            print(f"  错误: {type(e).__name__}: {e}")
        print()


def example_5_cache_demo():
    """示例5: 缓存效果演示"""
    print("\n=== 示例5: 缓存效果 ===\n")
    
    import time
    
    nlp = DeepSeekNLPProcessor(cache_size=10)
    
    # 相同命令多次调用
    command = "攻击妖兽"
    
    # 第一次调用（无缓存）
    start = time.time()
    result1 = nlp.parse_command(command)
    time1 = time.time() - start
    
    # 第二次调用（有缓存）
    start = time.time()
    result2 = nlp.parse_command(command)
    time2 = time.time() - start
    
    print(f"命令: {command}")
    print(f"第一次调用耗时: {time1:.3f}秒")
    print(f"第二次调用耗时: {time2:.3f}秒")
    print(f"性能提升: {(time1/time2):.1f}x")
    
    # 显示缓存统计
    stats = nlp.get_cache_stats()
    print(f"\n缓存统计:")
    print(f"  命中率: {stats.get('hit_rate', 0):.1%}")
    print(f"  缓存大小: {stats.get('size', 0)}")


def example_6_batch_processing():
    """示例6: 批量处理"""
    print("\n\n=== 示例6: 批量处理 ===\n")
    
    nlp = DeepSeekNLPProcessor()
    
    # 批量命令
    commands = [
        "去洞府",
        "修炼一个时辰",
        "查看修炼进度",
        "使用灵石",
        "突破境界"
    ]
    
    print("批量解析命令:")
    results = []
    for cmd in commands:
        result = nlp.parse_command(cmd)
        results.append(result)
        print(f"  {cmd} -> {result.normalized_command}")
    
    # 统计意图分布
    intents = {}
    for r in results:
        intent_category = r.intent.split('.')[0]
        intents[intent_category] = intents.get(intent_category, 0) + 1
    
    print(f"\n意图分布:")
    for intent, count in intents.items():
        print(f"  {intent}: {count}")


def main():
    """运行所有示例"""
    print("修仙世界引擎 - NLP 基础使用示例")
    print("=" * 50)
    
    os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY", "test")
    
    try:
        example_1_simple_commands()
        example_2_natural_language()
        example_3_with_context()
        example_4_error_handling()
        example_5_cache_demo()
        example_6_batch_processing()
        
        print("\n✅ 所有示例运行完成！")
        
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()