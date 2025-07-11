# DeepSeek API 异步端点文档

## 概述

本文档描述了 Xianxia World Engine 中 DeepSeek API 的异步端点。这些端点提供了高性能的 AI 聊天和自然语言处理功能。

## 基础信息

- **基础路径**: `/api/llm`
- **认证**: 需要有效的 DeepSeek API 密钥（通过环境变量配置）
- **内容类型**: `application/json`

## 端点列表

### 1. 异步聊天

**端点**: `POST /api/llm/chat`

**描述**: 使用 DeepSeek AI 进行异步聊天对话。

**请求体**:
```json
{
    "prompt": "string",      // 必需：聊天提示词
    "async": true           // 可选：是否使用异步模式（默认：true）
}
```

**响应**:
```json
{
    "text": "AI 生成的响应文本",
    "mode": "async"         // 返回使用的模式："async" 或 "sync"
}
```

**示例**:
```bash
curl -X POST http://localhost:5001/api/llm/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "给我讲一个修仙的故事"}'
```

### 2. 同步聊天（向后兼容）

**端点**: `POST /api/llm/chat/sync`

**描述**: 使用同步模式进行聊天（保持向后兼容）。

**请求体**:
```json
{
    "prompt": "string"      // 必需：聊天提示词
}
```

**响应**:
```json
{
    "text": "AI 生成的响应文本"
}
```

### 3. 游戏意图解析

**端点**: `POST /api/llm/parse`

**描述**: 解析玩家输入的游戏命令意图。

**请求体**:
```json
{
    "utterance": "string",  // 必需：玩家输入的文本
    "context": {            // 可选：游戏上下文
        "scene": "主城",
        "player": {
            "realm": "筑基期"
        },
        "target_realm": "金丹期",
        "laws": [
            {
                "enabled": true,
                "code": "FORBIDDEN_ARTS"
            }
        ]
    }
}
```

**响应**:
```json
{
    "intent": "cultivate",          // 意图类型
    "slots": {                      // 提取的参数
        "target": "金丹期"
    },
    "allowed": true,                // 是否允许执行
    "reason": ""                    // 如果不允许，说明原因
}
```

**支持的意图类型**:
- `attack` - 攻击
- `move` - 移动
- `talk` - 对话
- `cultivate` - 修炼
- `inventory` - 查看物品
- `unknown` - 未知意图

### 4. 批量处理

**端点**: `POST /api/llm/batch`

**描述**: 并发处理多个聊天请求。

**请求体**:
```json
{
    "requests": [
        {"prompt": "第一个提示词"},
        {"prompt": "第二个提示词"},
        {"prompt": "第三个提示词"}
    ]
}
```

**响应**:
```json
{
    "results": [
        {"text": "响应1", "success": true},
        {"text": "响应2", "success": true},
        {"error": "错误信息", "success": false}
    ],
    "total": 3,             // 总请求数
    "successful": 2,        // 成功数
    "failed": 1            // 失败数
}
```

### 5. 状态查询

**端点**: `GET /api/llm/status`

**描述**: 查询 DeepSeek API 服务状态。

**响应**:
```json
{
    "status": "ok",                     // "ok" 或 "error"
    "api_key_configured": true,         // API 密钥是否已配置
    "endpoints": [                      // 可用端点列表
        "/api/llm/chat",
        "/api/llm/chat/sync",
        "/api/llm/parse",
        "/api/llm/batch",
        "/api/llm/status"
    ],
    "version": "1.0.0",
    "async_enabled": true               // 异步功能是否启用
}
```

## 错误处理

所有端点使用标准 HTTP 状态码：

- `200` - 成功
- `400` - 请求错误（缺少必需字段等）
- `500` - 服务器错误

错误响应格式：
```json
{
    "error": "错误描述信息"
}
```

## 性能优化

### 连接池配置

异步客户端使用以下连接池配置：

- **最大保持连接数**: 10
- **最大连接数**: 20
- **HTTP/2**: 启用

### 超时设置

- **连接超时**: 5 秒
- **读取超时**: 25 秒
- **总超时**: 30 秒

### 重试机制

- **最大重试次数**: 3
- **重试策略**: 指数退避（1s, 2s, 4s）
- **重试条件**: 超时或 5xx 错误

## 使用建议

### 1. 选择合适的端点

- **单个请求**: 使用 `/api/llm/chat`
- **批量请求**: 使用 `/api/llm/batch` 提高吞吐量
- **游戏命令**: 使用 `/api/llm/parse` 进行意图识别

### 2. 优化并发

- 批量端点支持高并发处理
- 建议批次大小：10-50 个请求
- 避免单个批次超过 100 个请求

### 3. 错误处理

```python
import httpx
import asyncio

async def call_deepseek_api():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:5001/api/llm/chat",
                json={"prompt": "你好"},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            print("请求超时")
        except httpx.HTTPStatusError as e:
            print(f"HTTP 错误: {e.response.status_code}")
        except Exception as e:
            print(f"其他错误: {e}")
```

## 环境配置

### 必需的环境变量

```bash
# DeepSeek API 密钥
DEEPSEEK_API_KEY=your_api_key_here

# 启用异步模式
USE_ASYNC_DEEPSEEK=1

# 启用 Flask 异步支持
FLASK_ASYNC_ENABLED=1
```

### 可选配置

```bash
# 详细日志
DEEPSEEK_VERBOSE=1

# 线程池大小（用于 ThreadPool 方案）
LLM_MAX_WORKERS=10
```

## 监控指标

使用 Prometheus 监控以下指标：

- `deepseek_requests_total` - 总请求数
- `deepseek_errors_total` - 错误总数
- `deepseek_duration_seconds` - 请求耗时分布

## 版本历史

- **v1.0.0** (2025-01-25): 初始异步 API 发布

## 常见问题

### Q: 如何切换回同步模式？

A: 设置环境变量 `USE_ASYNC_DEEPSEEK=0` 或使用 `toggle_async.sh` 脚本：
```bash
./scripts/toggle_async.sh disable
```

### Q: 批量请求的最大数量是多少？

A: 建议不超过 100 个请求，最佳范围是 10-50 个。

### Q: 如何处理超时？

A: 可以通过环境变量调整超时设置，或在客户端实现重试逻辑。

---

如有问题，请联系技术支持团队。