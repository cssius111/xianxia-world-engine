# Context Compressor 模块文档

## 概述

Context Compressor 是一个智能的上下文管理模块，专门为修仙世界引擎设计，用于优化 LLM 调用时的 Token 使用效率。

## 核心特性

### 1. 滑动窗口机制
- 保留最近的 N 条消息（默认 20 条）
- 自动丢弃超出窗口的旧消息
- 确保最新对话始终可见

### 2. 智能压缩
- 每累积 M 条消息（默认 30 条）触发压缩
- 使用 LLM 生成高质量摘要
- 保留关键信息（事件、状态变化、重要 NPC 等）

### 3. 分层记忆
- 记忆块按时间顺序组织
- 支持重要性评分
- 限制最大记忆块数量防止无限增长

### 4. Token 控制
- 实时估算 Token 使用量
- 自动触发压缩避免超限
- 提供压缩率统计

## 快速开始

```python
from src.xwe.core.context import ContextCompressor
from src.xwe.core.nlp.llm_client import LLMClient

# 创建压缩器
compressor = ContextCompressor(
    llm_client=LLMClient(api_key="your_key"),
    window_size=20,      # 保留最近20条消息
    block_size=30,       # 每30条触发压缩
    max_memory_blocks=10 # 最多10个记忆块
)

# 添加消息
compressor.append("玩家: 探索周围")
compressor.append("系统: 你发现了一个洞穴")

# 获取压缩后的上下文
context = compressor.get_context()
```

## API 参考

### ContextCompressor

#### 初始化参数
- `llm_client`: LLM 客户端实例（可选）
- `window_size`: 滑动窗口大小（默认 20）
- `block_size`: 压缩触发阈值（默认 30）
- `max_memory_blocks`: 最大记忆块数（默认 10）
- `enable_compression`: 是否启用压缩（默认 True）

#### 主要方法
- `append(message: str)`: 添加新消息
- `get_context() -> str`: 获取完整上下文
- `get_stats() -> dict`: 获取统计信息
- `clear()`: 清空所有数据
- `export_memory() -> list`: 导出记忆数据
- `import_memory(data: list)`: 导入记忆数据

### MemoryBlock

记忆块数据结构，包含：
- `summary`: 摘要内容
- `message_count`: 原始消息数
- `created_at`: 创建时间
- `token_estimate`: Token 估算
- `importance_score`: 重要性评分

### ContextSummarizer

摘要生成器，提供：
- `summarize()`: 生成文本摘要
- `calculate_importance()`: 计算重要性
- `extract_entities()`: 提取实体

## 配置建议

### 短对话场景
```python
compressor = ContextCompressor(
    window_size=50,
    block_size=100,
    max_memory_blocks=2
)
```

### 长对话场景
```python
compressor = ContextCompressor(
    window_size=10,
    block_size=20,
    max_memory_blocks=20
)
```

### 资源受限场景
```python
compressor = ContextCompressor(
    window_size=5,
    block_size=10,
    max_memory_blocks=5
)
```

## 性能优化

1. **缓存复用**：压缩后的记忆块可重复使用
2. **异步压缩**：可配合异步 LLM 调用
3. **批量处理**：累积消息批量压缩
4. **降级策略**：LLM 失败时使用本地摘要

## 监控指标

通过 `get_stats()` 获取：
- `total_messages`: 总消息数
- `total_compressions`: 压缩次数
- `total_tokens_saved`: 节省的 Token
- `compression_ratio`: 压缩率
- `compression_errors`: 错误次数

## 集成示例

### 与 NLPProcessor 集成

```python
class DeepSeekNLPProcessor:
    def __init__(self):
        self.context_compressor = ContextCompressor(
            llm_client=self.llm
        )
    
    def build_prompt(self, user_input: str):
        # 添加到压缩器
        self.context_compressor.append(user_input)
        
        # 使用压缩的上下文
        context = self.context_compressor.get_context()
        return f"{context}\n\n当前输入: {user_input}"
```

## 注意事项

1. **API 调用成本**：每次压缩会调用一次 LLM API
2. **压缩延迟**：摘要生成需要 1-2 秒
3. **信息损失**：压缩不可避免会丢失部分细节
4. **内存使用**：长时间运行需定期清理

## 测试

运行单元测试：
```bash
pytest src/xwe/core/context/test_context_compressor.py -v
```

运行示例：
```bash
python src/xwe/core/context/example_usage.py
```

## 后续优化方向

1. **向量存储**：使用嵌入向量进行语义检索
2. **重要性学习**：基于用户反馈优化重要性评分
3. **增量压缩**：支持部分更新而非全量重写
4. **多级压缩**：支持多层次的摘要层级
