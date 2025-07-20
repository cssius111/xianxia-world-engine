# Prometheus 监控集成使用指南

## 快速开始

### 1. 安装依赖

```bash
pip install prometheus-flask-exporter==0.23.0
```

### 2. 启动应用

确保环境变量启用了 Prometheus：

```bash
export ENABLE_PROMETHEUS=true
python -m src.app.cli
```

### 3. 访问指标

打开浏览器访问：
```
http://localhost:5000/metrics
```

## 配置选项

### 环境变量

- `ENABLE_PROMETHEUS`: 设置为 `true` 启用 Prometheus 指标（默认：true）
- `USE_MOCK_LLM`: 设置为 `true` 使用模拟 LLM（用于测试）
- `XWE_MAX_LLM_RETRIES`: LLM API 最大重试次数（默认：3）
- `LLM_ASYNC_WORKERS`: 异步线程池大小（默认：5）

### 特性开关

在代码中控制指标收集：

```python
from xwe.metrics.prometheus_metrics import get_metrics_collector

collector = get_metrics_collector()

# 完全禁用
collector.set_enabled(False)

# 启用降级模式（减少非关键指标）
collector.set_degraded(True)
```

## 验证集成

运行测试脚本验证集成是否正常：

```bash
python scripts/test_prometheus_integration.py
```

## 与 Prometheus 集成

### 1. Prometheus 配置

在 `prometheus.yml` 中添加：

```yaml
scrape_configs:
  - job_name: 'xwe'
    static_configs:
      - targets: ['localhost:5000']
    scrape_interval: 15s
    metrics_path: '/metrics'
```

### 2. 启动 Prometheus

```bash
prometheus --config.file=prometheus.yml
```

### 3. 查询示例

在 Prometheus UI (http://localhost:9090) 中查询：

```promql
# NLP 请求速率
rate(xwe_nlp_request_seconds_count[5m])

# 95分位延迟
histogram_quantile(0.95, rate(xwe_nlp_request_seconds_bucket[5m]))

# 缓存命中率
rate(xwe_nlp_cache_hit_total[5m]) / rate(xwe_nlp_request_seconds_count[5m])
```

## Grafana 可视化

1. 添加 Prometheus 数据源
2. 导入仪表板（见 `src/xwe/metrics/MONITORING.md`）
3. 设置告警规则

## 性能影响

- CPU 开销: < 1%
- 内存开销: < 10MB
- 支持 1000+ QPS

## 故障排查

### 指标未显示

1. 检查 `prometheus-flask-exporter` 是否已安装
2. 验证 `ENABLE_PROMETHEUS=true`
3. 确认应用正常启动
4. 检查 `/metrics` 端点响应

### 性能问题

1. 启用降级模式
2. 减少高基数标签
3. 调整采集间隔

## 更多信息

详细文档请参考：
- [监控指南](src/xwe/metrics/MONITORING.md)
- [Prometheus 规则](infrastructure/deploy/prometheus/xwe_prometheus_rules.yml)
