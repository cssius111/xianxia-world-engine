"""
测试 DeepSeek MCP 命令解析器
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from xwe.core.nlp.nlp_processor import DeepSeekNLPProcessor, NLPProcessor

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def test_deepseek_parser():
    """测试 DeepSeek 命令解析器"""
    print("=== 测试 DeepSeek MCP 命令解析器 ===\n")
    
    # 初始化处理器
    processor = DeepSeekNLPProcessor()
    
    # 测试用例
    test_cases = [
        # 基础探索命令
        "四处探索一下",
        "随便走走看看",
        "到处逛逛",
        
        # 修炼命令
        "我想休息一个时辰",
        "打坐修炼三小时",
        "快速闭关一天",
        
        # 查看命令
        "打开背包看看",
        "查看我的状态",
        "给我瞧瞧当前属性",
        
        # 移动命令
        "去丹药铺",
        "前往青云峰",
        "到藏经阁看看",
        
        # 使用物品
        "使用回春丹",
        "吃一颗培元丹",
        "服用疗伤药",
        
        # 交互命令
        "和李掌柜聊聊天",
        "与长老对话",
        "找掌门说话",
        
        # 复杂命令
        "先探索一下再修炼",
        "使用回春丹恢复血量",
        "去丹药铺买些疗伤药",
        
        # 模糊命令
        "嗯",
        "看看",
        "这是什么",
    ]
    
    print("开始测试命令解析...\n")
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"测试 {i}: {test_input}")
        print("-" * 50)
        
        try:
            # 解析命令
            result = processor.parse(test_input, use_cache=False)
            
            # 打印结果
            print(f"原始输入: {result.raw}")
            print(f"标准命令: {result.normalized_command}")
            print(f"意图类别: {result.intent}")
            print(f"参数: {result.args}")
            print(f"解释: {result.explanation}")
            print(f"置信度: {result.confidence}")
            
        except Exception as e:
            print(f"错误: {e}")
            
        print("\n")
        
    # 测试缓存功能
    print("=== 测试缓存功能 ===")
    print("第一次调用（无缓存）...")
    result1 = processor.parse("探索周围", use_cache=True)
    
    print("第二次调用（有缓存）...")
    result2 = processor.parse("探索周围", use_cache=True)
    
    # 显示缓存信息
    cache_info = processor.get_cache_info()
    print(f"\n缓存统计:")
    print(f"命中次数: {cache_info['hits']}")
    print(f"未命中次数: {cache_info['misses']}")
    print(f"命中率: {cache_info['hit_rate']:.2%}")
    print(f"当前缓存大小: {cache_info['currsize']}/{cache_info['maxsize']}")


def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n=== 测试向后兼容性 ===\n")
    
    # 使用旧的 NLPProcessor
    nlp = NLPProcessor()
    
    # 测试 parse_command 方法
    result = nlp.parse_command("去丹药铺买药")
    print("parse_command 结果:")
    print(result)
    
    # 测试 chat 方法
    print("\n测试 chat 方法:")
    response = nlp.chat("你好，我是一名修仙者")
    print(f"回复: {response}")
    

def test_local_fallback():
    """测试本地回退功能"""
    print("\n=== 测试本地回退功能 ===\n")
    
    processor = DeepSeekNLPProcessor()
    
    # 直接测试本地回退
    test_inputs = [
        "探索一下",
        "去青云峰",
        "使用回春丹",
        "这是什么鬼"
    ]
    
    for test_input in test_inputs:
        result = processor.local_fallback(test_input)
        print(f"输入: {test_input}")
        print(f"结果: {result}")
        print()


if __name__ == "__main__":
    # 检查环境变量
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("错误: 请设置 DEEPSEEK_API_KEY 环境变量")
        print("可以在 .env 文件中设置或使用:")
        print("export DEEPSEEK_API_KEY='your-api-key'")
        sys.exit(1)
        
    # 运行测试
    try:
        # 先测试本地回退
        test_local_fallback()
        
        # 测试主要功能
        test_deepseek_parser()
        
        # 测试向后兼容性
        test_backward_compatibility()
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
