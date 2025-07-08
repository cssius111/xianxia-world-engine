# LLMClient 异步功能文档

## 概述

LLMClient 现在支持异步调用，通过线程池包装现有的同步方法，为未来的全面异步化做准备。这个实现保持了完全的向后兼容性，同时提供了显著的性能提升。

## 核心特性

### 1. 线程池异步包装
- 使用 `ThreadPoolExecutor` 包装同步方法
- 可配置的工作线程数（默认 5）
- 自动资源管理和清理

### 2. 完整的异步 API
- `chat_async()` - 异步聊天
- `chat_with_context_async()` - 异步上下文对话
- 所有方法签名与同步版本保持一致

### 3. 性能优化
- 并发请求处理
- 批量操作支持
- 可配置的超时控制

## 快速开始

### 基础使用

```python
import asyncio
from src.xwe.core.nlp.llm_client import LLMClient

async def main():
    client = LLMClient()
    
    # 单个异步请求
    response = await client.chat_async("你好")
    print(response)
    
    # 清理资源
    client.cleanup()

# 运行
asyncio.run(main())
```

### 并发请求

```python
async def concurrent_example():
    client = LLMClient()
    
    # 创建多个并发请求
    prompts = ["问题1", "问题2", "问题3"]
    tasks = [client.chat_async(p) for p in prompts]
    
    # 等待所有请求完成
    responses = await asyncio.gather(*tasks)
    
    client.cleanup()
```

## API 参考

### LLMClient.chat_async()

```python
async def chat_async(
    self,
    prompt: str,
    temperature: float = 0.0,
    max_tokens: int = 256,
    system_prompt: Optional[str] = None,
) -> str
```

异步发送聊天请求。

**参数：**
- `prompt`: 用户输入
- `temperature`: 生成温度（0-1）
- `max_tokens`: 最大生成长度
- `system_prompt`: 系统提示（可选）

**返回：**
- 模型生成的文本

### LLMClient.chat_with_context_async()

```python
async def chat_with_context_async(
    self, 
    messages: list, 
    temperature: float = 0.7, 
    max_tokens: int = 256
) -> str
```

带上下文的异步对话。

**参数：**
- `messages`: 对话历史列表
- `temperature`: 生成温度
- `max_tokens`: 最大生成长度

## 配置选项

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `LLM_ASYNC_WORKERS` | 5 | 线程池工作线程数 |
| `LLM_ASYNC_QUEUE_SIZE` | 100 | 任务队列大小 |
| `LLM_ASYNC_TIMEOUT` | 30.0 | 默认超时时间（秒） |
| `LLM_ASYNC_ENABLED` | true | 是否启用异步功能 |

### 代码配置

```python
from src.xwe.core.nlp.async_utils import AsyncConfig

# 获取配置
workers = AsyncConfig.get_worker_count()
timeout = AsyncConfig.get_timeout()

# 检查异步是否启用
if AsyncConfig.is_async_enabled():
    # 使用异步功能
    pass
```

## 高级功能

### 1. 批处理

```python
from src.xwe.core.nlp.async_utils import AsyncBatchProcessor

# 创建批处理器
processor = AsyncBatchProcessor(
    process_func=client.chat_async,
    batch_size=10,
    max_workers=5
)

# 批量处理
items = ["item1", "item2", ...]
results = await processor.process_batch(items)
```

### 2. 超时控制

```python
from src.xwe.core.nlp.async_utils import AsyncHelper

# 带超时的执行
try:
    result = await AsyncHelper.run_with_timeout(
        client.chat_async("prompt"),
        timeout=5.0
    )
except asyncio.TimeoutError:
    print("请求超时")
```

### 3. 并发限制

```python
# 限制并发数的批量请求
tasks = [client.chat_async(p) for p in prompts]
results = await AsyncHelper.gather_with_limit(tasks, limit=3)
```

## Flask 集成

### 异步路由装饰器

```python
from functools import wraps
import asyncio

def async_route(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
    return wrapper

@app.route('/api/chat', methods=['POST'])
@async_route
async def chat_endpoint():
    response = await client.chat_async(request.json['message'])
    return jsonify({'response': response})
```

### 在同步代码中使用

```python
from src.xwe.core.nlp.async_utils import AsyncHelper

# 在同步函数中调用异步方法
def sync_function():
    result = AsyncHelper.run_async_in_sync(
        client.chat_async("hello")
    )
    return result
```

## 性能优化建议

### 1. 合理配置线程池大小

```python
# CPU 密集型任务
workers = os.cpu_count()

# IO 密集型任务（如 API 调用）
workers = os.cpu_count() * 2

# 设置环境变量
os.environ["LLM_ASYNC_WORKERS"] = str(workers)
```

### 2. 批量处理优化

```python
# 不好：逐个处理
for item in items:
    result = await client.chat_async(item)

# 好：批量并发
tasks = [client.chat_async(item) for item in items]
results = await asyncio.gather(*tasks)
```

### 3. 资源管理

```python
# 使用上下文管理器（推荐）
class AsyncLLMClient:
    async def __aenter__(self):
        self.client = LLMClient()
        return self.client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.client.cleanup()

# 使用
async with AsyncLLMClient() as client:
    response = await client.chat_async("hello")
```

## 错误处理

### 基本错误处理

```python
try:
    response = await client.chat_async(prompt)
except RuntimeError as e:
    # 线程池已关闭
    print(f"客户端错误: {e}")
except Exception as e:
    # 其他错误
    print(f"请求失败: {e}")
```

### 批量请求错误处理

```python
# 使用 return_exceptions 参数
results = await asyncio.gather(
    *tasks,
    return_exceptions=True
)

for i, result in enumerate(results):
    if isinstance(result, Exception):
        print(f"请求 {i} 失败: {result}")
    else:
        print(f"请求 {i} 成功")
```

## 监控和调试

### 性能监控

```python
import time

start = time.time()
response = await client.chat_async(prompt)
duration = time.time() - start

print(f"请求耗时: {duration:.2f}秒")
```

### 线程池状态

```python
# 检查线程池状态
print(f"最大线程数: {client._executor._max_workers}")
print(f"活跃线程数: {len(client._executor._threads)}")
print(f"待处理任务: {client._executor._work_queue.qsize()}")
```

## 迁移指南

### 从同步到异步

```python
# 原同步代码
def process_message(message):
    response = client.chat(message)
    return response

# 迁移后的异步代码
async def process_message(message):
    response = await client.chat_async(message)
    return response
```

### 保持兼容性

```python
# 同时支持同步和异步
class HybridProcessor:
    def process_sync(self, message):
        return self.client.chat(message)
    
    async def process_async(self, message):
        return await self.client.chat_async(message)
    
    def process(self, message, async_mode=False):
        if async_mode:
            return AsyncHelper.run_async_in_sync(
                self.process_async(message)
            )
        return self.process_sync(message)
```

## 最佳实践

1. **始终清理资源**
   ```python
   client = LLMClient()
   try:
       # 使用客户端
       pass
   finally:
       client.cleanup()
   ```

2. **避免阻塞事件循环**
   ```python
   # 不好
   response = client.chat(prompt)  # 在异步函数中调用同步方法
   
   # 好
   response = await client.chat_async(prompt)
   ```

3. **合理使用并发**
   ```python
   # 限制并发数避免资源耗尽
   semaphore = asyncio.Semaphore(10)
   
   async def limited_request(prompt):
       async with semaphore:
           return await client.chat_async(prompt)
   ```

4. **错误重试策略**
   ```python
   async def retry_request(prompt, max_retries=3):
       for i in range(max_retries):
           try:
               return await client.chat_async(prompt)
           except Exception as e:
               if i == max_retries - 1:
                   raise
               await asyncio.sleep(2 ** i)  # 指数退避
   ```

## 常见问题

### Q: 异步方法比同步方法慢？
A: 单个请求可能略慢（线程切换开销），但并发请求会显著提升总体性能。

### Q: 如何在 Jupyter Notebook 中使用？
A: 使用 `await` 直接调用，或使用 `asyncio.run()`：
```python
# Jupyter 支持直接 await
response = await client.chat_async("hello")

# 或使用 asyncio.run
response = asyncio.run(client.chat_async("hello"))
```

### Q: 线程池大小如何确定？
A: 
- API 调用类任务：CPU 核心数 * 2-4
- 本地计算任务：CPU 核心数
- 可通过性能测试确定最优值

### Q: 内存使用是否会增加？
A: 会略微增加（线程池开销），但通过合理配置可以控制。

## 未来计划

1. **原生异步实现**：使用 `aiohttp` 替代 `requests`
2. **WebSocket 支持**：实现流式响应
3. **连接池优化**：复用 HTTP 连接
4. **更多异步工具**：队列、限流器等

---

更多示例请参考 `examples/` 目录中的代码。
