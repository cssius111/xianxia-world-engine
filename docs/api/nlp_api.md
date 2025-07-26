# NLP API 文档

## 目录

- [概述](#概述)
- [快速开始](#快速开始)
- [API 参考](#api-参考)
- [配置](#配置)
- [错误码](#错误码)
- [版本兼容性](#版本兼容性)
- [示例](#示例)

## 概述

修仙世界引擎的 NLP（自然语言处理）模块提供了智能的命令解析功能，允许玩家使用自然语言与游戏进行交互。该模块基于 DeepSeek API，并包含了完善的缓存、错误处理和回退机制。

### 核心功能

- **自然语言理解**: 将玩家的自然语言输入转换为游戏可理解的命令
- **上下文感知**: 根据当前游戏状态智能解析命令
- **多模型支持**: 支持 DeepSeek、OpenAI 等多种 LLM 提供商
- **智能缓存**: 缓存常用命令解析结果，提高响应速度
- **离线回退**: API 不可用时自动切换到规则引擎

## 快速开始

### 1. 环境配置

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export DEEPSEEK_API_KEY="your_api_key_here"
```

### 2. 基本使用

```python
from xwe.core.nlp import DeepSeekNLPProcessor

# 初始化处理器
nlp = DeepSeekNLPProcessor()

# 解析命令
result = nlp.parse_command("我要去洞府修炼")
print(result.normalized_command)  # "move 洞府"
print(result.intent)  # "exploration.move"
```

## API 参考

### DeepSeekNLPProcessor

主要的 NLP 处理器类。

#### 初始化

```python
DeepSeekNLPProcessor(
    api_key: Optional[str] = None,
    cache_size: int = None
)
```

**参数：**
- `api_key` (可选): DeepSeek API 密钥，如未提供则从环境变量读取
- `cache_size` (可选): 缓存大小，默认 128

#### parse_command

解析自然语言命令。

```python
def parse_command(
    self,
    raw_input: str,
    context: Optional[Dict[str, Any]] = None
) -> ParsedCommand
```

**参数：**
- `raw_input`: 用户的原始输入
- `context`: 游戏上下文信息（可选）

**返回：**
```python
@dataclass
class ParsedCommand:
    raw: str                    # 原始输入
    normalized_command: str     # 标准化命令
    intent: str                # 意图类别
    args: Dict[str, Any]       # 命令参数
    explanation: str           # 解析说明
    confidence: float = 1.0    # 置信度
```

#### parse_command_async

异步解析命令。

```python
async def parse_command_async(
    self,
    raw_input: str,
    context: Optional[Dict[str, Any]] = None
) -> ParsedCommand
```

参数和返回值同 `parse_command`。

### 工具路由 (Tool Router)

管理和调度各种游戏动作。

#### register_tool

注册新的工具函数。

```python
@register_tool("tool_name")
def my_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    # 工具实现
    return {"action": "tool_name", "payload": payload}
```

#### dispatch

调用已注册的工具。

```python
result = dispatch("start_cultivation", {"duration": 60})
```

### 监控 API

提供运行时监控和统计。

#### get_nlp_monitor

获取 NLP 监控实例。

```python
from xwe.core.nlp import get_nlp_monitor

monitor = get_nlp_monitor()
stats = monitor.get_stats()
```

## 配置

### 配置文件位置

`src/xwe/data/interaction/nlp_config.json`

### 主要配置项

```json
{
  "nlp_config": {
    "enable_llm": true,              // 是否启用 LLM
    "llm_provider": "deepseek",      // LLM 提供商
    "confidence_threshold": 0.7,     // 置信度阈值
    "cache_enabled": true,           // 是否启用缓存
    "cache_size": 100,               // 缓存大小
    "fallback_to_rules": true        // 是否回退到规则引擎
  },
  "llm_providers": {
    "deepseek": {
      "api_base": "https://api.deepseek.com/v1",
      "model": "deepseek-chat",
      "temperature": 0.7,
      "max_tokens": 500
    }
  }
}
```

### 环境变量

- `DEEPSEEK_API_KEY`: DeepSeek API 密钥
- `NLP_DEBUG`: 启用调试日志

## 错误码

### 常见错误码

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| `NLP_001` | API 密钥无效 | 检查 API 密钥配置 |
| `NLP_002` | API 请求超时 | 重试或增加超时时间 |
| `NLP_003` | 解析失败 | 检查输入格式，使用规则引擎 |
| `NLP_004` | 上下文无效 | 确保提供有效的游戏上下文 |
| `NLP_005` | 缓存错误 | 清理缓存或禁用缓存功能 |

### 错误处理示例

```python
try:
    result = nlp.parse_command("攻击")
except NLPException as e:
    if e.code == "NLP_002":
        # 使用规则引擎回退
        result = fallback_parser.parse(raw_input)
    else:
        logger.error(f"NLP 错误: {e}")
```

## 版本兼容性

### 当前版本

- **版本**: 1.0.0
- **发布日期**: 2025-01-09
- **API 版本**: v1

### 兼容性矩阵

| NLP 版本 | 游戏引擎版本 | Python 版本 | 说明 |
|----------|-------------|-------------|------|
| 1.0.0 | 0.3.0+ | 3.8+ | 当前稳定版本 |
| 0.9.x | 0.2.x | 3.7+ | 已废弃 |

### 破坏性变更

- v1.0.0: `parse_command` 返回值从字典改为 `ParsedCommand` 数据类
- v1.0.0: 移除了 `parse_batch` 方法，使用异步方法代替

## 示例

### 基础使用示例

```python
from xwe.core.nlp import DeepSeekNLPProcessor

# 初始化
nlp = DeepSeekNLPProcessor()

# 简单命令解析
result = nlp.parse_command("攻击妖兽")
print(f"命令: {result.normalized_command}")  # "attack 妖兽"
print(f"意图: {result.intent}")              # "combat.attack"

# 带上下文的解析
context = {
    "current_scene": "combat",
    "enemies": ["妖兽", "魔修"],
    "player_hp": 50
}
result = nlp.parse_command("快跑", context=context)
print(f"命令: {result.normalized_command}")  # "flee"
```

### 高级功能示例

```python
# 批量异步处理
import asyncio

async def batch_parse(commands):
    tasks = [nlp.parse_command_async(cmd) for cmd in commands]
    return await asyncio.gather(*tasks)

commands = ["去市集", "买灵石", "回洞府修炼"]
results = asyncio.run(batch_parse(commands))
```

### 自定义工具示例

```python
from xwe.core.nlp import register_tool, dispatch

# 注册自定义工具
@register_tool("custom_action")
def custom_action(payload):
    # 实现自定义逻辑
    return {
        "success": True,
        "message": f"执行自定义动作: {payload}"
    }

# 使用工具
result = dispatch("custom_action", {"param": "value"})
```

### 错误处理示例

```python
from xwe.core.nlp import DeepSeekNLPProcessor, NLPException

nlp = DeepSeekNLPProcessor()

try:
    result = nlp.parse_command("复杂的自然语言输入...")
except NLPException as e:
    # 处理 NLP 特定错误
    logger.error(f"NLP 错误 {e.code}: {e.message}")
    # 回退到简单解析
    result = simple_parse(raw_input)
except Exception as e:
    # 处理其他错误
    logger.error(f"未知错误: {e}")
```

## 性能优化建议

1. **启用缓存**: 确保 `cache_enabled` 设置为 `true`
2. **调整缓存大小**: 根据使用情况调整 `cache_size`
3. **使用异步方法**: 对于批量处理使用异步接口
4. **合理设置超时**: 根据网络情况调整 `timeout` 值
5. **启用上下文压缩**: 减少 API 调用的 token 消耗

## 调试技巧

1. **启用调试日志**:
   ```bash
   export NLP_DEBUG=true
   ```

2. **查看监控数据**:
   ```python
   monitor = get_nlp_monitor()
   print(monitor.get_stats())
   ```


## 常见问题

**Q: 如何处理 API 限流？**
A: 系统自动实现了指数退避重试，也可以通过配置调整重试策略。

**Q: 如何提高解析准确度？**
A: 提供更多的上下文信息，调整 `temperature` 参数，或使用更强大的模型。

**Q: 缓存如何失效？**
A: 缓存使用 LRU 策略，可以手动调用 `clear_cache()` 清理。

## 更多资源

- [架构文档](../architecture/nlp_architecture.md)
- [开发指南](../dev/nlp_development.md)
- [运维手册](../ops/nlp_operations.md)
- [故障排查](../troubleshooting/nlp_issues.md)