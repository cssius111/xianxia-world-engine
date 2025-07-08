# Context Compressor 配置示例

以下是在 `nlp_config.json` 或环境变量中配置 Context Compressor 的示例。

## 1. 默认配置（推荐）

```json
{
  "enabled": true,
  "context_compression": {
    "enabled": true,
    "window_size": 20,
    "block_size": 30,
    "max_memory_blocks": 10,
    "summarization_temperature": 0.3,
    "summarization_max_tokens": 150,
    "enable_structured_summary": false,
    "auto_save_memory": false,
    "memory_save_path": "saves/context_memory.json"
  },
  "context_limit": 4096
}
```

## 2. 长对话优化配置

适用于需要处理长时间对话的场景：

```json
{
  "context_compression": {
    "enabled": true,
    "window_size": 10,
    "block_size": 20,
    "max_memory_blocks": 20,
    "summarization_temperature": 0.2,
    "summarization_max_tokens": 200,
    "enable_structured_summary": true,
    "auto_save_memory": true,
    "memory_save_path": "saves/long_conversation_memory.json"
  }
}
```

## 3. 资源受限配置

适用于 API 调用成本敏感的场景：

```json
{
  "context_compression": {
    "enabled": true,
    "window_size": 5,
    "block_size": 50,
    "max_memory_blocks": 5,
    "summarization_temperature": 0.1,
    "summarization_max_tokens": 100,
    "enable_structured_summary": false
  }
}
```

## 4. 禁用压缩配置

如果需要禁用压缩功能：

```json
{
  "context_compression": {
    "enabled": false
  }
}
```

## 5. 环境变量配置

也可以通过环境变量覆盖配置：

```bash
# 启用/禁用压缩
export NLP_CONTEXT_COMPRESSION_ENABLED=true

# 调整窗口大小
export NLP_CONTEXT_WINDOW_SIZE=15

# 调整压缩阈值
export NLP_CONTEXT_BLOCK_SIZE=25

# 设置最大记忆块
export NLP_CONTEXT_MAX_MEMORY_BLOCKS=15
```

## 6. 代码中动态配置

```python
from src.xwe.core.nlp.config import get_nlp_config

# 获取配置实例
config = get_nlp_config()

# 动态更新压缩配置
config.update({
    "context_compression": {
        "enabled": True,
        "window_size": 25,
        "block_size": 35,
        "max_memory_blocks": 12
    }
})

# 保存配置
config.save_config()
```

## 配置参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | true | 是否启用上下文压缩 |
| `window_size` | int | 20 | 保留的最近消息数 |
| `block_size` | int | 30 | 触发压缩的消息数阈值 |
| `max_memory_blocks` | int | 10 | 最大记忆块数量 |
| `summarization_temperature` | float | 0.3 | LLM 摘要生成温度（0-1） |
| `summarization_max_tokens` | int | 150 | 摘要最大长度 |
| `enable_structured_summary` | bool | false | 是否生成结构化摘要（JSON格式） |
| `auto_save_memory` | bool | false | 是否自动保存记忆到文件 |
| `memory_save_path` | string | "saves/context_memory.json" | 记忆保存路径 |

## 性能调优建议

1. **高频交互场景**：减小 `window_size` 和 `block_size`，增加压缩频率
2. **成本敏感场景**：增大 `block_size`，减少 LLM 调用次数
3. **质量优先场景**：增大 `window_size` 和 `summarization_max_tokens`
4. **内存受限场景**：减小 `max_memory_blocks`

## 监控和调试

启用调试日志查看压缩器工作状态：

```python
import logging

# 设置日志级别
logging.getLogger("xwe.nlp").setLevel(logging.DEBUG)

# 获取压缩器统计
processor = DeepSeekNLPProcessor()
stats = processor.get_context_stats()
print(f"压缩统计: {stats}")
```
