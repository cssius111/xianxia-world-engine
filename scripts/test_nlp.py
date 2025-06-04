#!/usr/bin/env python
"""
测试NLP功能 - 使用DeepSeek API
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from xwe.core.nlp import NLPProcessor, NLPConfig
from xwe.core.command_parser import CommandType
import json


def test_nlp():
    """测试NLP功能"""
    print("="*60)
    print("修仙世界引擎 - NLP测试")
    print("="*60)
    
    # 检查配置
    config_path = project_root / "xwe/data/interaction/nlp_config.json"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        print(f"\n当前配置：")
        print(f"- LLM提供者: {config_data.get('llm_provider', 'unknown')}")
        print(f"- 启用LLM: {config_data.get('enable_llm', False)}")
    
    # 创建NLP处理器
    config = NLPConfig(enable_llm=True)
    nlp = NLPProcessor(None, config)
    
    print("\n开始测试自然语言理解...")
    print("输入 'quit' 退出测试\n")
    
    # 测试用例
    test_cases = [
        "我想攻击那个妖兽",
        "用剑气斩轰他",
        "看看我的状态",
        "我要修炼一会儿",
        "去坊市逛逛",
        "和王老板聊聊天"
    ]
    
    print("预设测试用例：")
    for i, case in enumerate(test_cases, 1):
        print(f"{i}. {case}")
    
    print("\n" + "-"*60)
    
    while True:
        user_input = input("\n请输入命令（或输入数字选择测试用例）: ").strip()
        
        if user_input.lower() == 'quit':
            break
        
        # 如果输入数字，使用测试用例
        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(test_cases):
                user_input = test_cases[idx]
                print(f"使用测试用例: {user_input}")
            else:
                print("无效的数字")
                continue
        
        # 处理输入
        context = {
            "location": "qingyun_city",
            "in_combat": False,
            "has_target": True,
            "skills": ["basic_attack", "sword_slash", "meditation"]
        }
        
        result = nlp.parse(user_input, context)
        
        print(f"\n解析结果：")
        print(f"- 命令类型: {result.command_type.value if result.command_type else 'unknown'}")
        print(f"- 目标: {result.target}")
        print(f"- 参数: {result.parameters}")
        print(f"- 置信度: {result.confidence:.2f}")
        
        # 显示命令解释
        if result.command_type != CommandType.UNKNOWN:
            explanation = nlp.explain_command(result)
            print(f"- 解释: {explanation}")


def test_llm_direct():
    """直接测试LLM客户端"""
    print("\n" + "="*60)
    print("直接测试LLM客户端")
    print("="*60)
    
    from xwe.core.nlp.llm_client import LLMClient
    
    # 从配置文件读取
    config_path = project_root / "xwe/data/interaction/nlp_config.json"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        provider = config_data.get('llm_provider', 'mock')
    else:
        provider = 'mock'
    
    print(f"\n使用提供者: {provider}")
    
    client = LLMClient(provider=provider)
    
    prompt = "将下面的自然语言转换为游戏命令：我想攻击前面的妖兽"
    
    print(f"\n测试提示: {prompt}")
    response = client.complete(prompt)
    print(f"响应: {response}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NLP功能测试")
    parser.add_argument("--direct", action="store_true", help="直接测试LLM客户端")
    
    args = parser.parse_args()
    
    if args.direct:
        test_llm_direct()
    else:
        test_nlp()


if __name__ == "__main__":
    main()
