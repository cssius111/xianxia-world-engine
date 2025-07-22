# Xianxia World Engine 异步化改造实施指南

## 概述

本指南提供了将 DeepSeek API 客户端从同步改造为异步的详细步骤和代码示例。

## 方案 A: httpx.AsyncClient 实现（推荐）

### 步骤 1: 安装依赖

```bash
pip install httpx
```

### 步骤 2: 修改 deepseek_client.py

```python
# 在文件顶部添加导入
import httpx
import asyncio
from typing import Optional, Dict, Any

# 在 DeepSeekClient 类中添加异步方法
class DeepSeekClient:
    def __init__(self, api_key: str = "", model: str = "deepseek-chat"):
        # ... 现有代码 ...
        self.timeout = httpx.Timeout(30.0, connect=5.0)
        self._async_client: Optional[httpx.AsyncClient] = None
    
    async def _get_async_client(self) -> httpx.AsyncClient:
        """获取或创建异步 HTTP 客户端（单例模式）"""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                timeout=self.timeout,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
        return self._async_client
    
    async def _call_openai_async(self, prompt: str) -> Dict[str, Any]:
        """异步调用 OpenAI 兼容 API"""
        if not self.api_key:
            raise ValueError("API key not configured")
        
        client = await self._get_async_client()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful game AI assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }
        
        try:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            logger.error("API call timeout")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"API call failed with status {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"API call failed: {e}")
            raise
    
    async def chat_async(self, prompt: str) -> Dict[str, str]:
        """异步发送聊天请求到 DeepSeek 模型"""
        try:
            response = await self._call_openai_async(prompt)
            return {"text": response["choices"][0]["message"]["content"]}
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {"text": ""}
    
    async def parse_async(self, utterance: str, ctx: Any) -> Dict[str, Any]:
        """异步解析用户输入（带游戏上下文）"""
        # 提取上下文信息（与同步版本相同）
        scene = getattr(ctx, 'scene', '主城')
        player_realm = getattr(ctx.player, 'realm', '炼气期') if hasattr(ctx, 'player') else '炼气期'
        target_realm = getattr(ctx, 'target_realm', '未知')
        laws_summary = self._summarize_laws(getattr(ctx, 'laws', []))
        
        # 格式化提示词
        prompt = self.PROMPT_TMPL.format(
            scene=scene,
            player_realm=player_realm,
            target_realm=target_realm,
            laws_summary=laws_summary,
            utterance=utterance[:200]
        )
        
        try:
            response = await self._call_openai_async(prompt)
            content = response["choices"][0]["message"]["content"]
            result = json.loads(content)
            return result
        except Exception as e:
            logger.error(f"DeepSeek parse error: {e}")
            return {
                "intent": "unknown",
                "slots": {},
                "allowed": True,
                "reason": ""
            }
    
    async def close(self):
        """关闭异步客户端连接"""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None
```

### 步骤 3: Flask 异步路由示例

```python
# app.py 或路由文件中
from flask import Flask, jsonify, request
import asyncio

app = Flask(__name__)
deepseek_client = DeepSeekClient()

# Flask 2.3+ 支持异步路由
@app.get("/api/llm/chat")
async def llm_chat_async():
    """异步聊天接口"""
    data = request.get_json()
    prompt = data.get("prompt", "")
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    try:
        response = await deepseek_client.chat_async(prompt)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 保留同步版本以兼容
@app.post("/api/llm/chat/sync")
def llm_chat_sync():
    """同步聊天接口（向后兼容）"""
    data = request.get_json()
    prompt = data.get("prompt", "")
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    try:
        response = deepseek_client.chat(prompt)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### 步骤 4: 更新依赖文件

**requirements.txt:**
```txt
httpx>=0.25.0
```

**pyproject.toml:**
```toml
[tool.poetry.dependencies]
httpx = "^0.25.0"
```

## 方案 B: ThreadPoolExecutor 实现（备选）

### 实现代码

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os

class DeepSeekClient:
    def __init__(self, api_key: str = "", model: str = "deepseek-chat"):
        # ... 现有代码 ...
        self._executor = None
    
    def _get_executor(self) -> ThreadPoolExecutor:
        """获取线程池执行器（单例）"""
        if self._executor is None:
            max_workers = int(os.getenv("LLM_MAX_WORKERS", "5"))
            self._executor = ThreadPoolExecutor(
                max_workers=max_workers,
                thread_name_prefix="deepseek-"
            )
        return self._executor
    
    async def chat_async(self, prompt: str) -> Dict[str, str]:
        """使用线程池包装同步方法"""
        loop = asyncio.get_event_loop()
        executor = self._get_executor()
        
        # 在线程池中运行同步方法
        result = await loop.run_in_executor(
            executor, 
            self.chat, 
            prompt
        )
        return result
```

## 方案 C: Celery + Redis 实现（高级）

### 步骤 1: 创建 tasks.py

```python
# tasks.py
from celery import Celery
import os
from src.ai.deepseek_client import DeepSeekClient

# Celery 配置
app = Celery('xianxia_tasks')
app.config_from_object({
    'broker_url': os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    'result_backend': os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    'task_serializer': 'json',
    'result_serializer': 'json',
    'accept_content': ['json'],
    'timezone': 'UTC',
    'enable_utc': True,
})

@app.task(bind=True, max_retries=3)
def deepseek_chat_task(self, prompt: str, **kwargs):
    """DeepSeek 聊天异步任务"""
    try:
        client = DeepSeekClient()
        result = client.chat(prompt)
        return result
    except Exception as exc:
        # 指数退避重试
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
```

### 步骤 2: 修改客户端

```python
# deepseek_client.py 添加
from tasks import deepseek_chat_task

class DeepSeekClient:
    async def chat_async_celery(self, prompt: str) -> Dict[str, str]:
        """使用 Celery 队列的异步版本"""
        task = deepseek_chat_task.delay(prompt)
        return {"task_id": task.id, "status": "pending"}
```

### 步骤 3: 状态查询接口

```python
# Flask 路由
from celery.result import AsyncResult

@app.get("/api/llm/status/<task_id>")
def get_task_status(task_id: str):
    """查询任务状态"""
    result = AsyncResult(task_id)
    
    if result.ready():
        return jsonify({
            "task_id": task_id,
            "status": "completed",
            "result": result.get()
        })
    else:
        return jsonify({
            "task_id": task_id,
            "status": "pending"
        })
```

## 单元测试示例

```python
# tests/test_deepseek_async.py
import pytest
import asyncio
from src.ai.deepseek_client import DeepSeekClient

@pytest.mark.asyncio
async def test_chat_async():
    """测试异步聊天功能"""
    client = DeepSeekClient()
    prompt = "测试提示词"
    
    # 测试异步调用
    result = await client.chat_async(prompt)
    assert isinstance(result, dict)
    assert "text" in result

@pytest.mark.asyncio
async def test_concurrent_requests():
    """测试并发请求"""
    client = DeepSeekClient()
    prompts = [f"测试提示词 {i}" for i in range(50)]
    
    # 并发执行
    tasks = [client.chat_async(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 验证结果
    success_count = sum(1 for r in results if isinstance(r, dict))
    assert success_count >= 45  # 允许少量失败
```

## 性能测试

### 使用 Apache Bench (ab)

```bash
# 测试同步接口
ab -n 1000 -c 50 -p request.json -T 'application/json' \
   http://localhost:5000/api/llm/chat/sync

# 测试异步接口
ab -n 1000 -c 50 -p request.json -T 'application/json' \
   http://localhost:5000/api/llm/chat
```

### 使用 wrk

```bash
# 准备测试脚本
cat > test.lua << EOF
wrk.method = "POST"
wrk.body   = '{"prompt": "测试提示词"}'
wrk.headers["Content-Type"] = "application/json"
EOF

# 运行测试
wrk -t12 -c400 -d30s -s test.lua http://localhost:5000/api/llm/chat
```

## 回滚脚本

```bash
#!/bin/bash
# scripts/toggle_async.sh

MODE=$1

if [ "$MODE" = "enable" ]; then
    echo "启用异步模式..."
    export USE_ASYNC_DEEPSEEK=1
    echo "USE_ASYNC_DEEPSEEK=1" >> .env
elif [ "$MODE" = "disable" ]; then
    echo "禁用异步模式..."
    unset USE_ASYNC_DEEPSEEK
    sed -i '/USE_ASYNC_DEEPSEEK/d' .env
else
    echo "用法: $0 [enable|disable]"
    exit 1
fi

# 重新加载应用（不重启）
kill -HUP $(pgrep -f gunicorn)
echo "切换完成"
```

## 监控和日志

### Prometheus 指标

```python
# 添加监控指标
from prometheus_client import Counter, Histogram

deepseek_requests = Counter('deepseek_requests_total', 'Total DeepSeek API requests')
deepseek_errors = Counter('deepseek_errors_total', 'Total DeepSeek API errors')
deepseek_duration = Histogram('deepseek_duration_seconds', 'DeepSeek API call duration')

# 在异步方法中使用
@deepseek_duration.time()
async def chat_async(self, prompt: str) -> Dict[str, str]:
    deepseek_requests.inc()
    try:
        # ... 调用逻辑 ...
    except Exception as e:
        deepseek_errors.inc()
        raise
```

## 最佳实践

1. **连接池管理**：使用单例模式管理 HTTP 客户端
2. **超时设置**：合理设置连接和读取超时
3. **错误处理**：区分不同类型的错误并适当重试
4. **资源清理**：应用关闭时清理异步资源
5. **监控告警**：设置关键指标的监控和告警

## 故障排查

### 常见问题

1. **连接泄漏**：确保正确关闭异步客户端
2. **事件循环冲突**：避免在同步代码中调用异步方法
3. **超时配置**：根据实际情况调整超时参数
4. **并发限制**：设置合理的连接池大小

### 调试技巧

```python
# 启用详细日志
import logging
logging.getLogger("httpx").setLevel(logging.DEBUG)

# 环境变量调试
export DEEPSEEK_VERBOSE=1
export PYTHONASYNCIO DEBUG=1
```

## 总结

选择合适的异步化方案需要考虑：
- 当前系统架构
- 预期并发量
- 团队技术栈
- 运维复杂度

对于大多数场景，httpx.AsyncClient 方案提供了最好的平衡。