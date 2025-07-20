# NLP 运维手册

## 目录

- [部署指南](#部署指南)
- [配置管理](#配置管理)
- [监控配置](#监控配置)
- [故障排查](#故障排查)
- [性能调优](#性能调优)
- [备份恢复](#备份恢复)
- [安全管理](#安全管理)
- [维护计划](#维护计划)

## 部署指南

### 系统要求

- **操作系统**: Linux (推荐 Ubuntu 20.04+)、macOS、Windows
- **Python**: 3.8 或更高版本
- **内存**: 最低 2GB，推荐 4GB+
- **磁盘**: 最低 1GB 可用空间
- **网络**: 稳定的互联网连接（用于 API 调用）

### 部署步骤

#### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/your-org/xianxia_world_engine.git
cd xianxia_world_engine

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

#### 2. 配置文件

```bash
# 复制环境配置模板
cp .env.example .env

# 编辑配置文件
vim .env
```

必需的环境变量：
```bash
# DeepSeek API 配置
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_API_URL=https://api.deepseek.com/v1

# 可选配置
NLP_DEBUG=false
NLP_CACHE_SIZE=256
NLP_TIMEOUT=30
```

#### 3. 验证部署

```bash
# 运行测试
python -m pytest tests/test_nlp_processor.py -v

# 启动服务
python run.py
```

### Docker 部署

```dockerfile
# Dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/src

CMD ["python", "run.py"]
```

部署命令：
```bash
# 构建镜像
docker build -f infrastructure/Dockerfile -t xwe-nlp:latest infrastructure

# 运行容器
docker run -d \
  --name xwe-nlp \
  -p 5001:5001 \
  -e DEEPSEEK_API_KEY=your_key \
  -v $(pwd)/logs:/app/logs \
  xwe-nlp:latest
```

### Kubernetes 部署

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: xwe-nlp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: xwe-nlp
  template:
    metadata:
      labels:
        app: xwe-nlp
    spec:
      containers:
      - name: nlp
        image: xwe-nlp:latest
        ports:
        - containerPort: 5001
        env:
        - name: DEEPSEEK_API_KEY
          valueFrom:
            secretKeyRef:
              name: nlp-secrets
              key: api-key
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
```

## 配置管理

### 配置文件结构

```
config/
├── nlp_config.json     # NLP 主配置
├── prompts/           # Prompt 模板
│   ├── command.txt
│   └── context.txt
└── tools/             # 工具配置
    └── registry.json
```

### 动态配置更新

```python
# 热重载配置
from xwe.core.nlp import get_nlp_config

# 重新加载配置
config = get_nlp_config()
config.reload()

# 更新特定配置
config.update("cache_size", 512)
```

### 配置优先级

1. 环境变量
2. 命令行参数
3. 配置文件
4. 默认值

## 监控配置

### 监控指标

#### 1. 系统指标

```python
# 获取系统监控数据
from xwe.core.nlp import get_nlp_monitor

monitor = get_nlp_monitor()
stats = monitor.get_stats()

print(f"总请求数: {stats['total_requests']}")
print(f"成功率: {stats['success_rate']}%")
print(f"平均延迟: {stats['avg_latency']}ms")
print(f"缓存命中率: {stats['cache_hit_rate']}%")
```

#### 2. Prometheus 集成

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'xwe-nlp'
    static_configs:
      - targets: ['localhost:5001']
    metrics_path: '/metrics'
```

#### 3. 日志配置

```python
# logging.conf
[loggers]
keys=root,nlp

[handlers]
keys=console,file,error

[formatters]
keys=standard

[logger_nlp]
level=INFO
handlers=console,file
qualname=xwe.nlp

[handler_file]
class=handlers.RotatingFileHandler
level=INFO
formatter=standard
args=('logs/nlp.log', 'a', 10485760, 5)
```

### 告警配置

```yaml
# alerts.yml
groups:
  - name: nlp_alerts
    rules:
      - alert: HighErrorRate
        expr: nlp_error_rate > 0.05
        for: 5m
        annotations:
          summary: "NLP 错误率过高"
          
      - alert: LowCacheHitRate
        expr: nlp_cache_hit_rate < 0.5
        for: 10m
        annotations:
          summary: "缓存命中率过低"
          
      - alert: HighAPILatency
        expr: nlp_api_latency_p99 > 1000
        for: 5m
        annotations:
          summary: "API 延迟过高"
```

## 故障排查

### 常见问题

#### 1. API 连接失败

**症状：**
```
NLPException: Failed to connect to DeepSeek API
```

**排查步骤：**
1. 检查 API 密钥是否正确
2. 验证网络连接
3. 检查 API 服务状态
4. 查看防火墙设置

**解决方案：**
```bash
# 测试 API 连接
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-chat", "messages": [{"role": "user", "content": "test"}]}'
```

#### 2. 内存溢出

**症状：**
```
MemoryError: Unable to allocate array
```

**排查步骤：**
1. 检查缓存大小设置
2. 查看内存使用情况
3. 分析内存泄漏

**解决方案：**
```python
# 限制缓存大小
config.update("cache_size", 128)

# 手动清理缓存
nlp.clear_cache()

# 启用内存分析
import tracemalloc
tracemalloc.start()
```

#### 3. 性能下降

**症状：**
- 响应时间增加
- CPU 使用率高

**排查步骤：**
```bash
# 性能分析
python -m cProfile -o profile.stats run.py

# 查看分析结果
python -m pstats profile.stats
```

### 调试工具

#### 1. 日志分析

```bash
# 查看错误日志
tail -f logs/nlp_error.log | grep ERROR

# 分析请求模式
awk '{print $4}' logs/nlp_access.log | sort | uniq -c
```

#### 2. 实时监控

```python
# monitor.py
from xwe.core.nlp import get_nlp_monitor
import time

monitor = get_nlp_monitor()

while True:
    stats = monitor.get_realtime_stats()
    print(f"\r请求/秒: {stats['rps']}, 延迟: {stats['latency']}ms", end="")
    time.sleep(1)
```

## 性能调优

### 1. 缓存优化

```python
# 调整缓存策略
config = {
    "cache_size": 512,  # 增加缓存大小
    "cache_ttl": 3600,  # 缓存过期时间（秒）
    "cache_warmup": True  # 启用预热
}
```

### 2. 并发优化

```python
# 调整线程池大小
import concurrent.futures

executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
```

### 3. API 优化

```python
# 批量请求
async def batch_process(commands):
    tasks = [nlp.parse_command_async(cmd) for cmd in commands]
    return await asyncio.gather(*tasks)
```

### 4. 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_cache_key ON nlp_cache(cache_key);
CREATE INDEX idx_timestamp ON nlp_logs(timestamp);

-- 定期清理
DELETE FROM nlp_logs WHERE timestamp < NOW() - INTERVAL '7 days';
```

## 备份恢复

### 备份策略

#### 1. 配置备份

```bash
#!/bin/bash
# backup_config.sh

BACKUP_DIR="/backup/nlp/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# 备份配置文件
cp -r config/ $BACKUP_DIR/
cp .env $BACKUP_DIR/

# 备份缓存数据
cp -r data/nlp_cache/ $BACKUP_DIR/

# 创建备份清单
ls -la $BACKUP_DIR > $BACKUP_DIR/manifest.txt
```

#### 2. 数据备份

```python
# 导出缓存数据
import pickle

def backup_cache():
    cache_data = nlp.export_cache()
    with open('backup/cache_backup.pkl', 'wb') as f:
        pickle.dump(cache_data, f)
```

### 恢复流程

```bash
# 1. 停止服务
systemctl stop xwe-nlp

# 2. 恢复配置
cp -r /backup/nlp/20250109/config/* config/

# 3. 恢复缓存
cp -r /backup/nlp/20250109/nlp_cache/* data/nlp_cache/

# 4. 重启服务
systemctl start xwe-nlp

# 5. 验证恢复
curl http://localhost:5001/health
```

## 安全管理

### 1. API 密钥管理

```bash
# 使用密钥管理服务
export DEEPSEEK_API_KEY=$(vault kv get -field=api_key secret/nlp)

# 密钥轮换
vault kv put secret/nlp api_key=new_key_here
```

### 2. 访问控制

```python
# 添加认证中间件
from flask import request

@app.before_request
def authenticate():
    token = request.headers.get('Authorization')
    if not validate_token(token):
        return {'error': 'Unauthorized'}, 401
```

### 3. 数据加密

```python
# 加密敏感数据
from cryptography.fernet import Fernet

def encrypt_cache(data):
    key = Fernet.generate_key()
    f = Fernet(key)
    return f.encrypt(data.encode())
```

## 维护计划

### 日常维护

- **每日**：
  - 检查服务状态
  - 查看错误日志
  - 监控关键指标

- **每周**：
  - 清理过期缓存
  - 分析性能报告
  - 更新依赖包

- **每月**：
  - 全量备份
  - 性能优化
  - 安全审计

### 维护脚本

```bash
#!/bin/bash
# maintenance.sh

echo "开始日常维护..."

# 1. 清理日志
find logs/ -name "*.log" -mtime +7 -delete

# 2. 压缩旧日志
gzip logs/*.log.1

# 3. 清理缓存
python -c "from xwe.core.nlp import get_nlp_processor; nlp = get_nlp_processor(); nlp.cleanup_cache()"

# 4. 检查磁盘空间
df -h | grep -E "/$|/var|/tmp"

# 5. 生成报告
python scripts/generate_report.py > reports/maintenance_$(date +%Y%m%d).txt

echo "维护完成"
```

### 升级流程

```bash
# 1. 备份当前版本
./backup_config.sh

# 2. 拉取新版本
git fetch origin
git checkout v1.1.0

# 3. 更新依赖
pip install -r requirements.txt --upgrade

# 4. 运行迁移脚本
python scripts/migrate_v1.1.0.py

# 5. 重启服务
systemctl restart xwe-nlp

# 6. 验证升级
python -m pytest tests/test_nlp_processor.py
```

## 故障恢复

### 紧急响应流程

1. **识别问题**
   - 查看监控告警
   - 检查服务状态
   - 分析错误日志

2. **临时处理**
   - 切换到备用服务
   - 启用降级模式
   - 通知相关人员

3. **根因分析**
   - 收集相关日志
   - 重现问题
   - 定位根本原因

4. **永久修复**
   - 实施修复方案
   - 测试验证
   - 更新文档

### 灾难恢复

```bash
# DR 切换脚本
#!/bin/bash

# 1. 更新 DNS
update_dns_record nlp.xwe.com $DR_IP

# 2. 启动 DR 环境
ssh $DR_HOST "cd /app && docker-compose up -d"

# 3. 验证服务
for i in {1..10}; do
    if curl -f http://$DR_HOST:5001/health; then
        echo "DR 环境已就绪"
        break
    fi
    sleep 10
done

# 4. 切换流量
kubectl patch service xwe-nlp -p '{"spec":{"selector":{"env":"dr"}}}'
```