#!/usr/bin/env python3
"""
测试 DeepSeek API 连接
验证 API key 和网络连接是否正常
"""

import os
import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

def test_deepseek_connection():
    """测试 DeepSeek API 连接"""
    print("🔍 测试 DeepSeek API 连接...")
    print("-" * 50)
    
    # 检查 API key
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 错误: DEEPSEEK_API_KEY 未在环境变量中设置")
        print("请确保 .env 文件中包含: DEEPSEEK_API_KEY=sk-xxx")
        return False
    
    print(f"✅ 找到 API Key: {api_key[:10]}...")
    
    try:
        # 导入 deepseek 模块
        from deepseek import DeepSeek, test_connection
        print("✅ deepseek 模块导入成功")
        
        # 测试基本连接
        print("\n📡 测试 API 连接...")
        if test_connection():
            print("\n✅ DeepSeek API 连接测试通过！")
            
            # 测试不同模型
            print("\n🧪 测试不同模型...")
            
            # 测试 DeepSeek-V3 (deepseek-chat)
            client_v3 = DeepSeek(model="deepseek-chat")
            response_v3 = client_v3.chat("请用一句话介绍你自己")
            print(f"\nDeepSeek-V3 响应: {response_v3['text']}")
            
            # 测试 DeepSeek-R1 (deepseek-reasoner)
            print("\n测试 DeepSeek-R1...")
            client_r1 = DeepSeek(model="deepseek-reasoner")
            response_r1 = client_r1.chat("1+1等于多少？请简短回答")
            print(f"DeepSeek-R1 响应: {response_r1['text']}")
            
            # 显示使用统计
            print(f"\n📊 Token 使用统计:")
            print(f"- V3 模型: {response_v3['usage']['total_tokens']} tokens")
            print(f"- R1 模型: {response_r1['usage']['total_tokens']} tokens")
            
            return True
        else:
            return False
            
    except ImportError as e:
        print(f"❌ 导入错误: {str(e)}")
        print("请确保已安装 openai: pip install openai")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_llm_client():
    """测试 LLMClient 是否可以正常工作"""
    print("\n" + "=" * 50)
    print("📝 测试 LLMClient 集成...")
    
    try:
        from xwe.core.nlp.llm_client import LLMClient
        
        client = LLMClient()
        response = client.chat("Hello, World!")
        print(f"✅ LLMClient 响应: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ LLMClient 测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 DeepSeek API 集成测试")
    print("=" * 50)
    
    # 测试 DeepSeek 连接
    connection_ok = test_deepseek_connection()
    
    # 测试 LLMClient
    if connection_ok:
        llm_client_ok = test_llm_client()
    else:
        llm_client_ok = False
    
    # 总结
    print("\n" + "=" * 50)
    print("📋 测试总结:")
    print(f"- DeepSeek API 连接: {'✅ 成功' if connection_ok else '❌ 失败'}")
    print(f"- LLMClient 集成: {'✅ 成功' if llm_client_ok else '❌ 失败'}")
    
    if connection_ok and llm_client_ok:
        print("\n🎉 所有测试通过！DeepSeek API 已正确配置。")
        print("\n下一步:")
        print("1. 运行项目: python entrypoints/run_web_ui_optimized.py")
        print("2. 或者: python main_menu.py")
    else:
        print("\n⚠️ 部分测试失败，请检查上述错误信息。")

if __name__ == "__main__":
    main()
