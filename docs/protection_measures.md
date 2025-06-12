# 修仙世界引擎 - 监控防护措施与最佳实践

## 🛡️ 防护措施

根据代码审计反馈，我们已实施以下防护措施：

### 1. 指标基数控制

**问题**：为每个玩家创建动态标签会导致时间序列爆炸

**解决方案**：
- 限制每个指标最多1000个标签组合（`MAX_LABEL_CARDINALITY`）
- 超过限制后使用"overflow"标签
- 移除player_id等高基数标签，改为记录到日志

```python
# ❌ 错误：高基数标签
inc_counter("game_events_total", 1, {
    "event_type": "login",
    "player_id": "12345"  # 会导致爆炸！
})

# ✅ 正确：服务级别标签
inc_counter("game_events_total", 1, {
    "event_type": "login",
    "category": "auth"
})

# 玩家信息记录到日志
logger.info("Player login", player_id="12345", event_type="login")
```

### 2. 日志量控制

**问题**：JSON格式 + DEBUG级别会快速占满磁盘

**解决方案**：
- 环境变量控制日志级别：`LOG_LEVEL=INFO`（生产环境默认）
- 自动日志轮转（10MB per file, 5个备份）
- 结构化字段避免冗余

```bash
# 开发环境
export LOG_LEVEL=DEBUG
export LOG_FORMAT=text

# 生产环境
export LOG_LEVEL=INFO
export LOG_FORMAT=json
export LOG_FILE=/var/log/xwe/app.log
```

### 3. 开发API安全

**问题**：调试端点暴露敏感信息

**解决方案**：
- 必须显式启用：`ENABLE_DEV_API=true`
- 生产环境自动警告
- 未来集成JWT认证

```python
# 配置自动验证
if config.FLASK_ENV == 'production':
    if config.ENABLE_DEV_API:
        print("WARNING: Dev API enabled in production!")
```

### 4. 健康检查准确性

**问题**：简单的ping不足以反映系统状态

**解决方案**：
- 检查多个组件：存储、服务、内存、会话
- 三级状态：healthy、degraded、unhealthy
- 详细的错误信息

```json
{
  "status": "degraded",
  "checks": {
    "storage": "ok",
    "services": "warning",
    "memory": "ok"
  },
  "details": {
    "services": {
      "registered": 10,
      "initialized": 5,
      "warning": "Some services not initialized"
    }
  }
}
```

## 📊 最佳实践

### 1. 标签设计原则

```python
# 标签层次结构
# Level 1: 服务级别（< 10个值）
service = ["game", "auth", "storage"]

# Level 2: 操作类型（< 50个值）  
operation = ["create", "read", "update", "delete"]

# Level 3: 状态码（< 10个值）
status = ["200", "400", "500"]

# 避免：
# - 用户ID、会话ID、请求ID作为标签
# - 动态生成的值
# - 高基数的枚举值
```

### 2. 日志规范

```python
# 标准字段
logger.info("Operation completed", 
    # 必需字段
    operation="user_login",
    duration_ms=150,
    
    # 可选但推荐
    user_id="12345",
    trace_id=request.trace_id,
    
    # 元数据
    metadata={
        "ip": "192.168.1.1",
        "user_agent": "..."
    }
)

# 错误日志
try:
    process_request()
except Exception as e:
    logger.error("Request failed",
        error=e,  # 自动提取stack trace
        request_id=request.id,
        user_id=user_id
    )
```

### 3. 监控告警规则

```yaml
# Prometheus告警示例
groups:
  - name: xwe_alerts
    rules:
      # 错误率告警
      - alert: HighErrorRate
        expr: rate(errors_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "错误率超过5%"
          
      # 响应时间告警
      - alert: SlowResponse
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "P95响应时间超过1秒"
          
      # 内存使用告警
      - alert: HighMemoryUsage
        expr: memory_usage_bytes / memory_limit_bytes > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "内存使用超过90%"
```

### 4. 容器资源限制

```yaml
# docker-compose.yml
services:
  xwe:
    # ... 其他配置 ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 🔍 故障排查指南

### 问题：指标端点响应慢

**诊断步骤**：
1. 检查标签基数：`curl /api/v1/dev/debug/metrics | jq .`
2. 查看是否有overflow标签
3. 检查直方图bucket数量

**解决方案**：
- 减少标签维度
- 增加`MAX_LABEL_CARDINALITY`限制
- 使用采样减少数据量

### 问题：日志文件过大

**诊断步骤**：
1. 检查日志级别：`echo $LOG_LEVEL`
2. 分析日志频率：`tail -f app.log | pv -l -r`
3. 查看最频繁的日志

**解决方案**：
- 调整日志级别到WARNING
- 添加采样逻辑
- 配置更激进的轮转策略

### 问题：Docker容器OOM

**诊断步骤**：
1. 查看容器状态：`docker stats`
2. 检查内存泄漏：访问 `/api/v1/dev/debug`
3. 分析内存分配

**解决方案**：
- 设置合理的内存限制
- 启用内存profiling
- 优化数据结构

## 🚀 性能优化建议

### 1. 指标聚合

```python
# 使用预聚合减少计算
class MetricsAggregator:
    def __init__(self):
        self._buckets = defaultdict(lambda: defaultdict(float))
        
    def record(self, metric, value, timestamp):
        # 按分钟聚合
        bucket = timestamp // 60
        self._buckets[bucket][metric] += value
```

### 2. 日志批处理

```python
# 批量写入减少IO
class BatchLogger:
    def __init__(self, batch_size=100):
        self._buffer = []
        self._batch_size = batch_size
        
    def log(self, entry):
        self._buffer.append(entry)
        if len(self._buffer) >= self._batch_size:
            self._flush()
```

### 3. 缓存策略

```python
# 缓存常用查询
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_player_stats(player_id: str):
    # 昂贵的计算
    return calculate_stats(player_id)
```

## 📈 容量规划

基于负载测试，单实例建议配置：

| 指标 | 开发环境 | 生产环境 |
|------|----------|----------|
| CPU | 1 core | 2-4 cores |
| 内存 | 512MB | 2-4GB |
| 并发用户 | 10 | 100-500 |
| 日志存储 | 1GB | 50GB |
| 指标保留 | 1天 | 30天 |

## 🔐 安全加固

1. **API密钥管理**
   ```python
   # 使用环境变量
   API_KEY = os.environ.get('API_KEY')
   if not API_KEY:
       raise ValueError("API_KEY not set")
   ```

2. **速率限制**
   ```python
   from flask_limiter import Limiter
   
   limiter = Limiter(
       app,
       key_func=get_remote_address,
       default_limits=["100 per minute"]
   )
   ```

3. **输入验证**
   ```python
   from flask import request
   from jsonschema import validate
   
   schema = {
       "type": "object",
       "properties": {
           "player_id": {"type": "string", "maxLength": 50}
       }
   }
   validate(request.json, schema)
   ```

---

更新日期：2025-06-12  
版本：1.0.1

根据实际运行情况持续更新此文档。
