# NLPProcessor Context Compressor 集成迁移指南

## 概述

本指南帮助您将现有的 XianXia World Engine 项目升级到支持上下文压缩的新版本。

## 版本兼容性

- ✅ **完全向后兼容**：所有现有代码无需修改即可继续工作
- ✅ **默认启用压缩**：新功能默认开启，可通过配置禁用
- ✅ **API 保持不变**：所有公开接口保持原样

## 快速开始

### 1. 更新代码

确保您的项目包含以下新文件：
```
src/xwe/core/context/
├── __init__.py
├── compressor.py
├── memory_block.py
└── summarizer.py
```

### 2. 默认行为

升级后，NLPProcessor 会自动：
- 启用上下文压缩
- 保留最近 20 条消息
- 每 30 条消息触发一次压缩
- 最多保留 10 个记忆块

如果您对默认配置满意，**无需任何额外操作**。

## 配置调整

### 禁用压缩（保持原有行为）

如果您希望完全禁用新功能，保持原有行为：

```python
# 方法1：环境变量
export NLP_CONTEXT_COMPRESSION_ENABLED=false

# 方法2：配置文件
{
  "context_compression": {
    "enabled": false
  }
}
```

### 调整压缩参数

根据您的使用场景调整参数：

```json
{
  "context_compression": {
    "window_size": 15,      // 减少内存使用
    "block_size": 40,       // 减少 API 调用
    "max_memory_blocks": 5  // 限制历史长度
  }
}
```

## 新增 API

虽然核心功能自动工作，但您可以使用以下新 API 进行高级控制：

### 1. 上下文管理

```python
# 清空上下文
processor.clear_context()

# 获取压缩统计
stats = processor.get_context_stats()
print(f"总消息数: {stats['total_messages']}")
print(f"压缩次数: {stats['total_compressions']}")
print(f"Token 节省: {stats['total_tokens_saved']}")
```

### 2. 记忆持久化

```python
# 保存对话记忆
processor.save_context_memory("saves/game_memory.json")

# 恢复对话记忆
processor.load_context_memory("saves/game_memory.json")
```

## 性能影响

### 预期改进
- ✅ **Token 使用减少 50-70%**：通过智能压缩
- ✅ **上下文长度无限制**：突破 4K token 限制
- ✅ **更好的长对话体验**：保留关键信息

### 潜在开销
- ⚠️ **额外 API 调用**：每次压缩调用一次 LLM
- ⚠️ **轻微延迟增加**：压缩过程需要 1-2 秒
- ⚠️ **内存使用略增**：存储记忆块

## 监控和调试

### 查看压缩日志

```python
import logging
logging.getLogger("xwe.nlp").setLevel(logging.INFO)
```

日志示例：
```
INFO: 上下文压缩器已启用
INFO: 压缩完成: 30条消息 -> 150字符, 耗时1.2秒, 节省350 tokens
```

### 性能监控

压缩相关指标会自动集成到现有监控系统：

```python
monitor = get_nlp_monitor()
report = monitor.get_performance_report()
print(report)
```

## 常见问题

### Q: 压缩会丢失重要信息吗？
A: 压缩器设计为保留关键游戏事件（境界提升、物品获得、位置变化等）。普通对话细节可能被简化。

### Q: 如何处理压缩失败？
A: 系统会自动降级到传统模式，不会影响游戏运行。查看日志了解失败原因。

### Q: 可以自定义压缩策略吗？
A: 是的，可以通过继承 `ContextSummarizer` 类实现自定义摘要生成逻辑。

### Q: 压缩的记忆可以跨会话保存吗？
A: 可以，使用 `save_context_memory()` 和 `load_context_memory()` 方法。

## 最佳实践

1. **开发环境**：使用较小的 `window_size` 和 `block_size` 快速测试
2. **生产环境**：根据实际使用情况调整参数
3. **成本控制**：监控 API 调用次数，必要时增大 `block_size`
4. **质量保证**：定期检查压缩后的上下文质量

## 回滚方案

如果遇到问题需要回滚：

1. 设置环境变量 `NLP_CONTEXT_COMPRESSION_ENABLED=false`
2. 或在配置中禁用 `"enabled": false`
3. 系统将完全恢复原有行为

## 支持

遇到问题请：
1. 查看日志文件 `logs/xwe.log`
2. 运行集成测试 `pytest test_integration_context.py`
3. 提交 Issue 到项目仓库

---

**重要提示**：建议先在测试环境验证新功能，确认符合预期后再部署到生产环境。
