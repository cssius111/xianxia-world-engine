"""
Context Compressor 使用示例
展示如何在游戏中集成上下文压缩功能
"""

import os

from src.xwe.core.context import ContextCompressor
from src.xwe.core.nlp.llm_client import LLMClient


def example_basic_usage():
    """基础使用示例"""
    print("=== 基础使用示例 ===\n")

    # 创建压缩器（使用较小的参数便于演示）
    compressor = ContextCompressor(
        window_size=5,  # 保留最近5条消息
        block_size=3,  # 每3条消息触发压缩
        max_memory_blocks=2,  # 最多保留2个记忆块
    )

    # 模拟游戏对话
    game_messages = [
        "玩家: 探索周围环境",
        "系统: 你来到了青云城的中心广场",
        "玩家: 查看周围的NPC",
        "系统: 你看到了药铺老板、铁匠和一位神秘道人",
        "玩家: 和道人对话",
        "系统: 道人说：年轻人，我看你骨骼清奇...",
        "玩家: 接受道人的任务",
        "系统: 获得任务：寻找失落的灵石",
    ]

    # 逐条添加消息
    for i, msg in enumerate(game_messages):
        print(f"添加消息 {i+1}: {msg[:30]}...")
        compressor.append(msg)

        # 显示当前状态
        stats = compressor.get_stats()
        print(f"  - 最近消息数: {stats['current_recent_messages']}")
        print(f"  - 待压缩消息: {stats['current_pending_messages']}")
        print(f"  - 记忆块数: {stats['current_memory_blocks']}")
        print(f"  - 总压缩次数: {stats['total_compressions']}")
        print()

    # 获取最终上下文
    print("\n=== 最终上下文 ===")
    context = compressor.get_context()
    print(context)

    # 显示统计信息
    print("\n=== 统计信息 ===")
    stats = compressor.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")


def example_with_llm():
    """使用真实 LLM 的示例"""
    print("\n=== 使用 LLM 的示例 ===\n")

    # 检查是否有 API key
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("\u26A0\uFE0F 未检测到 DEEPSEEK_API_KEY 环境变量，跳过 LLM 示例")
        return

    # 创建 LLM 客户端
    llm_client = LLMClient(api_key=api_key)

    # 创建压缩器
    compressor = ContextCompressor(llm_client=llm_client, window_size=10, block_size=5)

    # 模拟长对话
    long_conversation = [
        "玩家: 我要开始修炼了",
        "系统: 你盘膝而坐，开始运转心法",
        "玩家: 专心修炼内功",
        "系统: 灵气缓缓流入你的经脉",
        "玩家: 尝试突破瓶颈",
        "系统: 你感到体内真气激荡，似乎要突破了！",
        "玩家: 全力冲击境界",
        "系统: 恭喜！你成功突破到练气二层",
        "玩家: 查看当前属性",
        "系统: 境界：练气二层，灵力：150/150",
        "玩家: 继续修炼稳固境界",
        "系统: 你的境界逐渐稳固下来",
    ]

    # 添加对话
    for msg in long_conversation:
        compressor.append(msg)

    # 显示压缩效果
    print("添加了 {} 条消息".format(len(long_conversation)))
    stats = compressor.get_stats()
    print(f"触发了 {stats['total_compressions']} 次压缩")
    print(f"节省了 {stats['total_tokens_saved']} 个 tokens")
    print(f"压缩率: {stats['compression_ratio']:.2%}")

    # 显示记忆块
    print("\n=== 生成的记忆块 ===")
    for i, block in enumerate(compressor.memory_blocks):
        print(f"记忆块 {i+1}: {block.summary}")


def example_advanced_features():
    """高级功能示例"""
    print("\n=== 高级功能示例 ===\n")

    compressor = ContextCompressor()

    # 1. 导入导出记忆
    print("1. 记忆持久化")

    # 添加一些消息生成记忆
    for i in range(10):
        compressor.append(f"历史消息 {i}")

    # 导出记忆
    memory_data = compressor.export_memory()
    print(f"导出了 {len(memory_data)} 个记忆块")

    # 清空并重新导入
    compressor.clear()
    compressor.import_memory(memory_data)
    print("记忆已恢复")

    # 2. 自定义压缩策略
    print("\n2. 自定义压缩参数")

    # 创建激进压缩策略（更频繁压缩）
    ContextCompressor(
        window_size=3, block_size=2, max_memory_blocks=5  # 只保留3条最新  # 每2条就压缩  # 保留更多历史
    )

    # 创建保守压缩策略（减少压缩）
    ContextCompressor(
        window_size=50,  # 保留大量最新消息
        block_size=30,  # 累积更多才压缩
        max_memory_blocks=3,  # 限制历史记忆
    )

    print("激进策略：频繁压缩，适合长对话")
    print("保守策略：减少压缩，适合短对话")


def example_integration():
    """集成到 NLPProcessor 的示例代码"""
    print("\n=== NLPProcessor 集成示例 ===\n")

    example_code = '''
# 在 nlp_processor.py 中的修改示例

class DeepSeekNLPProcessor:
    def __init__(self, api_key: Optional[str] = None, cache_size: int = None):
        # ... 现有初始化代码 ...

        # 初始化上下文压缩器
        self.context_compressor = ContextCompressor(
            llm_client=self.llm,
            window_size=self.config.get("context_window_size", 20),
            block_size=self.config.get("context_block_size", 30)
        )

    def build_prompt(self, user_input: str, context: Optional[Dict] = None) -> str:
        """构建prompt，使用压缩的上下文"""

        # 添加当前输入到压缩器
        self.context_compressor.append(f"用户: {user_input}")

        # 获取压缩后的上下文
        compressed_context = self.context_compressor.get_context()

        # 构建最终 prompt
        prompt = f"""
{compressed_context}

当前输入: {user_input}

请解析以上输入...
"""

        return prompt
'''

    print(example_code)


if __name__ == "__main__":
    # 运行所有示例
    example_basic_usage()
    example_with_llm()
    example_advanced_features()
    example_integration()
