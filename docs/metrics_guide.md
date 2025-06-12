# 修仙世界引擎 - 监控与调试指南

## 概述

第4阶段功能增强为修仙世界引擎添加了以下监控和调试功能：

1. **结构化日志** - JSON格式日志输出
2. **Prometheus监控** - 性能指标收集
3. **API文档** - 自动生成的Swagger文档
4. **开发调试控制台** - 系统状态实时监控
5. **Docker容器化** - 一键部署

## 功能使用

### 1. 结构化日志

使用新的StructuredLogger类输出JSON格式日志：

```python
from xwe.services.log_service import StructuredLogger

# 创建日志记录器
logger = StructuredLogger(service_name="game_service")

# 记录不同级别的日志
logger.info("Player logged in", player_id="123", ip="192.168.1.1")
logger.error("Combat calculation failed", error=exception, player_id="123")
```

输出格式：
```json
{
  "timestamp": "2025-06-12T10:30:45.123Z",
  "level": "INFO",
  "service": "game_service",
  "message": "Player logged in",
  "player_id": "123",
  "metadata": {
    "ip": "192.168.1.1"
  }
}
```

### 2. Prometheus监控指标

系统预定义了以下核心指标：

- `http_request_duration_seconds` - HTTP请求延迟（直方图）
- `game_events_total` - 游戏事件总数（计数器）
- `active_players` - 在线玩家数（仪表）
- `memory_usage_bytes` - 内存使用（仪表）
- `cpu_usage_percent` - CPU使用率（仪表）

访问指标端点：
```
GET http://localhost:5001/api/v1/system/metrics
```

使用示例：
```python
from xwe.metrics import metrics_registry, inc_counter, time_histogram

# 记录游戏事件
inc_counter("game_events_total", 1, {
    "event_type": "combat_start",
    "player_id": "123"
})

# 记录API请求时间
with time_histogram("http_request_duration_seconds", {
    "method": "POST",
    "path": "/api/v1/game/action",
    "status": "200"
}):
    # 处理请求
    process_request()
```

### 3. API文档

访问Swagger UI查看完整的API文档：
```
http://localhost:5001/api/docs
```

特性：
- 自动从代码生成文档
- 交互式API测试
- 请求/响应示例
- 参数说明

### 4. 开发调试控制台

调试端点提供系统内部状态的实时视图：

#### 获取完整调试信息
```
GET http://localhost:5001/api/v1/dev/debug
```

返回：
- 系统信息（Python版本、平台等）
- 服务状态（已注册/已初始化的服务）
- 事件总线状态
- 性能指标摘要
- 资源使用情况

#### 获取服务详情
```
GET http://localhost:5001/api/v1/dev/debug/services
```

#### 获取事件监听器
```
GET http://localhost:5001/api/v1/dev/debug/events
```

#### 获取最近日志
```
GET http://localhost:5001/api/v1/dev/debug/logs
```

### 5. Docker部署

#### 构建镜像
```bash
docker build -t xwe:latest .
```

#### 运行容器
```bash
# 基本运行
docker run -p 5001:5001 xwe:latest

# 使用docker-compose（推荐）
docker-compose up -d
```

#### 开发模式
```bash
# 挂载源代码，支持热重载
docker-compose -f docker-compose.yml up
```

#### 查看日志
```bash
docker-compose logs -f xwe
```

## 集成步骤

### 1. 启用监控中间件

在Flask应用中添加：

```python
from api.middleware import register_middleware
from xwe.metrics import metrics_registry, time_histogram

@app.before_request
def before_request():
    # 记录请求开始时间
    request.start_time = time.time()

@app.after_request
def after_request(response):
    # 记录请求指标
    duration = time.time() - request.start_time
    metrics_registry.observe_histogram(
        "http_request_duration_seconds",
        duration,
        {
            "method": request.method,
            "path": request.path,
            "status": str(response.status_code)
        }
    )
    return response
```

### 2. 配置Prometheus

使用提供的`prometheus.yml`配置文件：

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'xwe-metrics'
    static_configs:
      - targets: ['localhost:5001']
    metrics_path: '/api/v1/system/metrics'
```

### 3. 环境变量

支持的环境变量：

- `FLASK_ENV` - 运行环境（development/production）
- `FLASK_DEBUG` - 调试模式（0/1）
- `LOG_LEVEL` - 日志级别（DEBUG/INFO/WARNING/ERROR）
- `ENABLE_DEV_API` - 生产环境启用调试API（true/false）

## 性能优化建议

1. **日志优化**
   - 生产环境使用WARNING级别
   - 定期轮转日志文件
   - 考虑使用异步日志

2. **指标优化**
   - 限制标签基数
   - 定期清理过期指标
   - 使用采样减少开销

3. **容器优化**
   - 使用多阶段构建减小镜像体积
   - 限制容器资源使用
   - 配置健康检查

## 故障排查

### 问题：指标端点返回空数据
- 检查metrics_registry是否正确初始化
- 确认有指标被记录
- 查看日志是否有错误

### 问题：Docker容器无法启动
- 检查端口是否被占用
- 查看容器日志：`docker logs xianxia-world-engine`
- 确认requirements.txt包含所有依赖

### 问题：API文档无法访问
- 确认flask-swagger-ui已安装
- 检查是否有路由冲突
- 查看浏览器控制台错误

## 下一步计划

1. 添加更多业务指标
2. 集成ELK日志栈
3. 实现分布式追踪
4. 添加告警规则
5. 性能基准测试

---

更新日期：2025-06-12
版本：1.0.0
