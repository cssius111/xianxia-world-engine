# XianXia World Engine 监控指南

## 概述

XianXia World Engine 集成了 Prometheus 监控系统，提供全面的性能指标和系统状态监控。

## 指标说明

### NLP 相关指标

#### xwe_nlp_request_seconds
- **类型**: Histogram
- **描述**: NLP 请求处理时间（秒）
- **标签**: 
  - `command_type`: 命令类型（如 explore, battle, status）
  - `status`: 请求状态（success/failure）
- **用途**: 监控 NLP 处理性能，识别慢请求

#### xwe_nlp_token_count
- **类型**: Histogram  
- **描述**: 每个请求的 token 使用量
- **标签**:
  - `model`: 使用的模型（如 deepseek-chat）
- **用途**: 跟踪 API 使用成本

#### xwe_nlp_cache_hit_total
- **类型**: Counter
- **描述**: 缓存命中总数
- **标签**:
  - `cache_type`: 缓存类型
- **用途**: 评估缓存效率

#### xwe_nlp_error_total
- **类型**: Counter
- **描述**: NLP 错误总数
- **标签**:
  - `error_type`: 错误类型
- **用途**: 跟踪错误率和错误类型分布

### 上下文压缩指标

#### xwe_context_compression_total
- **类型**: Counter
- **描述**: 上下文压缩执行次数
- **用途**: 监控压缩功能使用情况

#### xwe_context_memory_blocks_gauge
- **类型**: Gauge
- **描述**: 当前记忆块数量
- **用途**: 跟踪内存使用情况

### 异步处理指标

#### xwe_async_thread_pool_size
- **类型**: Gauge
- **描述**: 异步线程池大小
- **用途**: 监控并发处理能力

#### xwe_async_request_queue_size
- **类型**: Gauge
- **描述**: 异步请求队列长度
- **用途**: 识别处理瓶颈

### 系统指标

#### xwe_system_cpu_usage_percent
- **类型**: Gauge
- **描述**: 系统 CPU 使用率（百分比）

#### xwe_system_memory_usage_mb
- **类型**: Gauge
- **描述**: 系统内存使用量（MB）

#### xwe_game_instances_gauge
- **类型**: Gauge
- **描述**: 活跃游戏实例数

#### xwe_players_online_gauge
- **类型**: Gauge
- **描述**: 在线玩家数

## 访问指标

启动应用后，访问 `/metrics` 端点查看所有指标：

```bash
curl http://localhost:5000/metrics
```

## Grafana 仪表板示例

### NLP 性能仪表板

```json
{
  "dashboard": {
    "title": "XianXia World Engine - NLP Performance",
    "panels": [
      {
        "title": "请求响应时间（P95）",
        "targets": [{
          "expr": "histogram_quantile(0.95, rate(xwe_nlp_request_seconds_bucket[5m]))"
        }]
      },
      {
        "title": "请求速率",
        "targets": [{
          "expr": "sum(rate(xwe_nlp_request_seconds_count[1m])) * 60"
        }]
      },
      {
        "title": "错误率",
        "targets": [{
          "expr": "sum(rate(xwe_nlp_error_total[5m])) / sum(rate(xwe_nlp_request_seconds_count[5m]))"
        }]
      },
      {
        "title": "缓存命中率",
        "targets": [{
          "expr": "sum(rate(xwe_nlp_cache_hit_total[5m])) / sum(rate(xwe_nlp_request_seconds_count[5m]))"
        }]
      }
    ]
  }
}
```

### 系统资源仪表板

```json
{
  "dashboard": {
    "title": "XianXia World Engine - System Resources",
    "panels": [
      {
        "title": "CPU 使用率",
        "targets": [{
          "expr": "xwe_system_cpu_usage_percent"
        }]
      },
      {
        "title": "内存使用量",
        "targets": [{
          "expr": "xwe_system_memory_usage_mb"
        }]
      },
      {
        "title": "游戏实例数",
        "targets": [{
          "expr": "xwe_game_instances_gauge"
        }]
      },
      {
        "title": "在线玩家数",
        "targets": [{
          "expr": "xwe_players_online_gauge"
        }]
      }
    ]
  }
}
```

## 告警配置示例

### Prometheus AlertManager 配置

```yaml
# alertmanager.yml
global:
  slack_api_url: 'YOUR_SLACK_WEBHOOK_URL'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'xwe-alerts'

receivers:
- name: 'xwe-alerts'
  slack_configs:
  - channel: '#xwe-monitoring'
    title: 'XianXia World Engine Alert'
    text: '{{ range .Alerts }}{{ .Annotations.summary }}\n{{ .Annotations.description }}{{ end }}'
```

### 关键告警规则

1. **高延迟告警**
   ```promql
   alert: HighNLPRequestLatency
   expr: histogram_quantile(0.95, rate(xwe_nlp_request_seconds_bucket[5m])) > 5
   for: 5m
   ```

2. **高错误率告警**
   ```promql
   alert: HighNLPErrorRate
   expr: rate(xwe_nlp_error_total[5m]) > 0.1
   for: 5m
   ```

3. **资源告警**
   ```promql
   alert: HighCPUUsage
   expr: xwe_system_cpu_usage_percent > 80
   for: 5m
   ```

## 性能优化建议

### 1. 降级模式

在高负载情况下，可以启用降级模式减少指标收集：

```python
from src.xwe.metrics.prometheus_metrics import get_metrics_collector

collector = get_metrics_collector()
collector.set_degraded(True)  # 减少非关键指标收集
```

### 2. 环境变量配置

- `ENABLE_PROMETHEUS`: 设置为 `false` 完全禁用 Prometheus 指标
- `XWE_MAX_LLM_RETRIES`: 控制 LLM API 重试次数
- `LLM_ASYNC_WORKERS`: 控制异步线程池大小

### 3. 指标基数控制

避免高基数标签：
- 限制 `command_type` 标签长度（最多20字符）
- 使用预定义的错误类型分类
- 避免在标签中使用用户 ID 等高基数值

## 故障排查

### 1. 指标未显示

检查：
- Prometheus 是否已安装：`pip install prometheus-flask-exporter`
- 环境变量 `ENABLE_PROMETHEUS` 是否为 `true`
- 访问 `/metrics` 端点是否有响应

### 2. 性能影响

如果监控影响性能：
1. 启用降级模式
2. 减少指标收集频率
3. 优化标签使用

### 3. 内存泄漏

监控以下指标识别内存问题：
- `xwe_system_memory_usage_mb` 持续增长
- `xwe_context_memory_blocks_gauge` 异常高

## 最佳实践

1. **定期审查指标**
   - 每周查看性能趋势
   - 识别性能退化
   - 优化慢查询

2. **容量规划**
   - 使用历史数据预测增长
   - 提前扩容避免瓶颈

3. **告警优化**
   - 避免告警疲劳
   - 设置合理阈值
   - 定期调整告警规则

## 集成其他监控工具

### 与 ELK Stack 集成

```python
# 在日志中添加指标信息
import logging
from src.xwe.metrics.prometheus_metrics import get_metrics_collector

logger = logging.getLogger(__name__)
collector = get_metrics_collector()

# 在日志中包含性能数据
stats = collector.get_stats()
logger.info(f"Performance stats: {stats}")
```

### 与 Jaeger 追踪集成

```python
# 添加追踪 span
from jaeger_client import Config

config = Config(
    config={
        'sampler': {'type': 'const', 'param': 1},
        'logging': True,
    },
    service_name='xwe-nlp',
)
tracer = config.initialize_tracer()

with tracer.start_span('nlp_request') as span:
    span.set_tag('command_type', command_type)
    # 处理请求
```

## 未来改进计划

1. **更多指标**
   - 战斗系统性能指标
   - 存储系统 I/O 指标
   - 网络延迟指标

2. **自动化**
   - 自动性能基线
   - 异常检测
   - 自动扩缩容

3. **可视化**
   - 预配置 Grafana 仪表板
   - 实时性能大屏
   - 移动端监控 App
