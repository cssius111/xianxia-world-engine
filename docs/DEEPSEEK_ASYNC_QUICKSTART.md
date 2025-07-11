# DeepSeek 异步 API 快速启动指南

## 🚀 5分钟快速上手

### 1. 设置环境变量

```bash
# 创建或编辑 .env 文件
echo "DEEPSEEK_API_KEY=your_api_key_here" >> .env
echo "USE_ASYNC_DEEPSEEK=1" >> .env
echo "FLASK_ASYNC_ENABLED=1" >> .env
```

### 2. 启用异步模式

```bash
# 使用切换脚本
./scripts/toggle_async.sh enable

# 或手动设置
export USE_ASYNC_DEEPSEEK=1
export FLASK_ASYNC_ENABLED=1
```

### 3. 快速测试

```bash
# 运行异步单元测试
python scripts/run_async_tests.py
```

### 4. 启动服务

```bash
# 启动 Flask 应用
python app.py

# 或使用启动脚本
./scripts/start.sh
```

### 5. 测试 API

```bash
# 测试状态
curl http://localhost:5001/api/llm/status

# 测试异步聊天
curl -X POST http://localhost:5001/api/llm/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "你好，世界"}'

# 测试批量处理
curl -X POST http://localhost:5001/api/llm/batch \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {"prompt": "请求1"},
      {"prompt": "请求2"},
      {"prompt": "请求3"}
    ]
  }'
```

## 📝 Python 代码示例

### 基础使用

```python
from src.ai.deepseek_client import DeepSeekClient
import asyncio

async def main():
    # 创建客户端
    client = DeepSeekClient()
    
    # 单个异步请求
    response = await client.chat_async("你好")
    print(response['text'])
    
    # 并发请求
    prompts = ["问题1", "问题2", "问题3"]
    tasks = [client.chat_async(p) for p in prompts]
    results = await asyncio.gather(*tasks)
    
    for i, result in enumerate(results):
        print(f"回答{i+1}: {result['text']}")
    
    # 清理资源
    await client.close()

# 运行
asyncio.run(main())
```

### API 调用示例

```python
import httpx
import asyncio

async def call_api():
    async with httpx.AsyncClient() as client:
        # 单个请求
        response = await client.post(
            "http://localhost:5001/api/llm/chat",
            json={"prompt": "测试"}
        )
        print(response.json())
        
        # 批量请求
        batch_response = await client.post(
            "http://localhost:5001/api/llm/batch",
            json={
                "requests": [
                    {"prompt": "批量1"},
                    {"prompt": "批量2"}
                ]
            }
        )
        print(batch_response.json())

asyncio.run(call_api())
```

## 🔧 常用命令

### 模式切换

```bash
# 启用异步
./scripts/toggle_async.sh enable

# 禁用异步（回退到同步）
./scripts/toggle_async.sh disable

# 查看状态
./scripts/toggle_async.sh status
```

### 性能测试

```bash
# 运行基准测试
python scripts/benchmark_deepseek_api.py

# 运行集成测试
python tests/integration/test_deepseek_async.py
```

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log | grep deepseek
```

## ⚡ 性能对比

| 场景 | 同步模式 | 异步模式 | 提升 |
|------|---------|---------|------|
| 单请求 | 1.0s | 1.0s | 1x |
| 10并发 | 10.0s | 2.0s | 5x |
| 50并发 | 50.0s | 5.0s | 10x |

## 🔍 故障排查

### 问题1：API Key 未配置

```bash
# 检查环境变量
echo $DEEPSEEK_API_KEY

# 设置 API Key
export DEEPSEEK_API_KEY=your_key_here
```

### 问题2：异步模式未启用

```bash
# 检查状态
./scripts/toggle_async.sh status

# 启用异步
./scripts/toggle_async.sh enable
```

### 问题3：连接超时

```python
# 调整超时设置
client = DeepSeekClient()
client.timeout = httpx.Timeout(60.0, connect=10.0)
```

## 📚 更多资源

- [完整 API 文档](./docs/api/deepseek_async_api.md)
- [实施指南](./docs/ASYNC_IMPLEMENTATION_GUIDE.md)
- [技术评估报告](./docs/reports/async_tech_evaluation.md)

## 🆘 获取帮助

如遇到问题：

1. 查看 [API 文档](./docs/api/deepseek_async_api.md)
2. 运行测试脚本：`python scripts/test_deepseek_async.py`
3. 查看日志：`tail -f logs/*.log`
4. 联系技术支持

---

祝您使用愉快！🎉