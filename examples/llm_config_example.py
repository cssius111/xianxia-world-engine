# examples/llm_config_example.py
"""
LLM配置示例

展示如何配置和使用不同的LLM提供者。
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from xwe.core.nlp import LLMClient, NLPProcessor, NLPConfig
from xwe.core import CommandParser


def example_deepseek():
    """DeepSeek API示例"""
    print("=== DeepSeek API 示例 ===")
    
    # 方法1：通过环境变量设置
    # export DEEPSEEK_API_KEY="your_api_key"
    
    # 方法2：直接在代码中设置（不推荐在生产环境中使用）
    config = {
        "api_key": "sk-15e3638d218d4e448365fb53fe011db7",
        "api_base": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "temperature": 0.7
    }
    
    # 创建LLM客户端
    llm_client = LLMClient(provider="deepseek", config=config)
    
    # 测试命令解析
    user_input = "我想用剑气斩攻击那个妖兽"
    result = llm_client.parse_command(user_input)
    print(f"输入: {user_input}")
    print(f"解析结果: {result}")


def example_openai():
    """OpenAI API示例"""
    print("\n=== OpenAI API 示例 ===")
    
    # 配置OpenAI
    config = {
        "api_key": os.getenv("OPENAI_API_KEY", "your_openai_api_key_here"),
        "model": "gpt-3.5-turbo",
        "temperature": 0.7
    }
    
    # 创建LLM客户端
    llm_client = LLMClient(provider="openai", config=config)
    
    # 测试对话
    messages = [
        {"role": "system", "content": "你是一个修仙游戏的助手。"},
        {"role": "user", "content": "我刚开始玩，应该做什么？"}
    ]
    
    response = llm_client.chat(messages)
    print("问: 我刚开始玩，应该做什么？")
    print(f"答: {response}")


def example_nlp_processor():
    """完整的NLP处理器示例"""
    print("\n=== NLP处理器完整示例 ===")
    
    # 创建命令解析器
    command_parser = CommandParser()
    
    # 配置NLP处理器
    nlp_config = NLPConfig(
        enable_llm=True,
        llm_provider="deepseek",  # 可以改为 "openai" 或 "mock"
        llm_config={
            "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
            "temperature": 0.7
        },
        fallback_to_rules=True,
        confidence_threshold=0.7
    )
    
    # 创建NLP处理器
    nlp_processor = NLPProcessor(command_parser, nlp_config)
    
    # 测试各种输入
    test_inputs = [
        "我想攻击那个妖兽",
        "用剑气斩轰他",
        "看看我现在什么状态",
        "我要修炼一会儿",
        "打开背包看看有什么",
        "这是什么地方？"
    ]
    
    # 模拟战斗上下文
    combat_context = {
        'in_combat': True,
        'enemies': [
            {'name': '低阶妖兽', 'health_percent': 0.7}
        ],
        'available_skills': ['剑气斩', '疾风步']
    }
    
    print("\n普通模式测试:")
    for user_input in test_inputs[:3]:
        print(f"\n输入: '{user_input}'")
        command = nlp_processor.parse(user_input)
        print(f"命令类型: {command.command_type.value}")
        if command.target:
            print(f"目标: {command.target}")
        explanation = nlp_processor.explain_command(command)
        print(f"解释: {explanation}")
    
    print("\n\n战斗模式测试:")
    print("当前在战斗中，敌人: 低阶妖兽")
    for user_input in ["攻击", "用剑气斩", "防御一下"]:
        print(f"\n输入: '{user_input}'")
        command = nlp_processor.parse(user_input, combat_context)
        print(f"命令类型: {command.command_type.value}")
        if command.target:
            print(f"目标: {command.target}")


def main():
    """主函数"""
    print("LLM配置示例程序")
    print("=" * 50)
    
    # 检查API密钥
    has_deepseek = bool(os.getenv("DEEPSEEK_API_KEY"))
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    
    if not has_deepseek and not has_openai:
        print("\n警告：未检测到LLM API密钥")
        print("请设置环境变量：")
        print("  - DEEPSEEK_API_KEY=你的DeepSeek API密钥")
        print("  - OPENAI_API_KEY=你的OpenAI API密钥")
        print("\n将使用Mock模式进行演示...")
        
        # 使用Mock模式演示
        command_parser = CommandParser()
        nlp_processor = NLPProcessor(command_parser)
        
        test_input = "我想攻击那个妖兽"
        command = nlp_processor.parse(test_input)
        print(f"\n测试输入: '{test_input}'")
        print(f"解析结果: {command.command_type.value}")
    else:
        if has_deepseek:
            print("\n检测到DeepSeek API密钥")
            # example_deepseek()  # 需要真实API密钥
        
        if has_openai:
            print("\n检测到OpenAI API密钥")
            # example_openai()  # 需要真实API密钥
        
        example_nlp_processor()
    
    print("\n" + "=" * 50)
    print("提示：")
    print("1. 在生产环境中，请使用环境变量存储API密钥")
    print("2. 可以在nlp_config.json中配置默认的LLM提供者")
    print("3. 支持的提供者：deepseek, openai, mock")


if __name__ == "__main__":
    main()
