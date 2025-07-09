# NLP 故障排查指南

## 目录

- [常见问题 FAQ](#常见问题-faq)
- [错误信息解释](#错误信息解释)
- [调试技巧](#调试技巧)
- [日志分析](#日志分析)
- [性能问题排查](#性能问题排查)
- [API 问题](#api-问题)
- [集成问题](#集成问题)
- [紧急修复](#紧急修复)

## 常见问题 FAQ

### Q1: NLP 模块无法启动

**症状：**
```
ImportError: cannot import name 'DeepSeekNLPProcessor' from 'xwe.core.nlp'
```

**可能原因：**
1. 依赖未安装
2. Python 路径问题
3. 模块文件缺失

**解决方案：**
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 检查 Python 路径
python -c "import sys; print(sys.path)"

# 3. 验证模块存在
ls src/xwe/core/nlp/

# 4. 设置 PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
```

### Q2: API 密钥错误

**症状：**
```
ValueError: Missing DEEPSEEK_API_KEY
```

**解决方案：**
```bash
# 方法1: 环境变量
export DEEPSEEK_API_KEY="your_api_key_here"

# 方法2: .env 文件
echo "DEEPSEEK_API_KEY=your_api_key_here" >> .env

# 方法3: 代码中设置
nlp = DeepSeekNLPProcessor(api_key="your_api_key_here")

# 方法4: 使用模拟模式（开发测试）
export USE_MOCK_LLM=true
```

### Q3: 命令解析失败

**症状：**
```
NLPException: Failed to parse command
```

**排查步骤：**
1. 检查输入格式
2. 验证上下文结构
3. 查看调试日志
4. 测试规则引擎

```python
# 启用调试模式
import logging
logging.basicConfig(level=logging.DEBUG)

# 测试简单命令
nlp = DeepSeekNLPProcessor()
result = nlp.parse_command("攻击")  # 应该成功

# 检查上下文
context = {"player": {"level": 1}}  # 确保格式正确
result = nlp.parse_command("使用技能", context)
```

### Q4: 缓存问题

**症状：**
- 相同命令返回不同结果
- 内存使用持续增长

**解决方案：**
```python
# 清理缓存
nlp.clear_cache()

# 禁用缓存
nlp = DeepSeekNLPProcessor(cache_size=0)

# 查看缓存状态
stats = nlp.get_cache_stats()
print(f"缓存大小: {stats['size']}")
print(f"命中率: {stats['hit_rate']}")
```

### Q5: 性能问题

**症状：**
- 响应时间过长
- CPU 使用率高

**优化方法：**
```python
# 1. 启用缓存
nlp = DeepSeekNLPProcessor(cache_size=256)

# 2. 使用异步方法
result = await nlp.parse_command_async("命令")

# 3. 批量处理
results = nlp.parse_batch(["命令1", "命令2", "命令3"])

# 4. 调整超时
nlp = DeepSeekNLPProcessor(timeout=10)  # 10秒超时
```

## 错误信息解释

### NLP 特定错误

#### NLP_001: API 密钥无效
```
NLPException[NLP_001]: Invalid API key
```

**含义：** 提供的 API 密钥格式错误或已失效

**解决：**
1. 检查密钥格式（应为 sk-xxx 格式）
2. 确认密钥未过期
3. 验证密钥权限

#### NLP_002: API 请求超时
```
NLPException[NLP_002]: API request timeout after 30s
```

**含义：** API 调用超过设定的超时时间

**解决：**
1. 检查网络连接
2. 增加超时时间
3. 使用重试机制
4. 考虑使用规则引擎

#### NLP_003: 解析失败
```
NLPException[NLP_003]: Failed to parse LLM response
```

**含义：** LLM 返回的内容无法解析为有效格式

**解决：**
1. 检查 prompt 模板
2. 验证响应格式
3. 查看原始响应
4. 更新解析逻辑

#### NLP_004: 上下文无效
```
NLPException[NLP_004]: Invalid context structure
```

**含义：** 提供的上下文不符合预期格式

**解决：**
```python
# 正确的上下文格式
context = {
    "player": {
        "name": "string",
        "level": 1,  # 整数
        "location": "string"
    },
    "scene": {
        "type": "combat|exploration|dialogue",
        "entities": []  # 列表
    }
}
```

#### NLP_005: 缓存错误
```
NLPException[NLP_005]: Cache operation failed
```

**含义：** 缓存读写操作失败

**解决：**
1. 清理缓存
2. 减小缓存大小
3. 检查内存限制
4. 重启服务

### 系统错误

#### ConnectionError
```
ConnectionError: Failed to establish connection to API
```

**排查：**
```bash
# 测试网络连接
curl -I https://api.deepseek.com

# 检查防火墙
sudo iptables -L

# 测试 API 端点
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-chat", "messages": [{"role": "user", "content": "test"}]}'
```

#### MemoryError
```
MemoryError: Unable to allocate memory for cache
```

**解决：**
```python
# 减少缓存大小
nlp = DeepSeekNLPProcessor(cache_size=50)

# 手动垃圾回收
import gc
gc.collect()

# 监控内存使用
import psutil
process = psutil.Process()
print(f"内存使用: {process.memory_info().rss / 1024 / 1024:.1f} MB")
```

## 调试技巧

### 1. 启用详细日志

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nlp_debug.log'),
        logging.StreamHandler()
    ]
)

# 只为 NLP 模块启用调试
logger = logging.getLogger('xwe.nlp')
logger.setLevel(logging.DEBUG)
```

### 2. 使用调试工具

```python
# 使用 pdb 调试
import pdb

def debug_parse_command():
    nlp = DeepSeekNLPProcessor()
    pdb.set_trace()  # 断点
    result = nlp.parse_command("测试命令")
    return result

# 使用 ipdb（更强大）
import ipdb

def complex_debugging():
    ipdb.set_trace()
    # 可以使用 IPython 功能
```

### 3. 监控实时状态

```python
from xwe.core.nlp.monitor import get_nlp_monitor

# 启用实时监控
monitor = get_nlp_monitor()
monitor.enable_debug_mode()

# 查看实时统计
while True:
    stats = monitor.get_realtime_stats()
    print(f"\rRPS: {stats['rps']}, 延迟: {stats['latency']}ms", end="")
    time.sleep(1)
```

### 4. 追踪函数调用

```python
import sys
import trace

# 创建追踪器
tracer = trace.Trace(
    count=False,
    trace=True,
    countfuncs=False
)

# 追踪执行
tracer.run('nlp.parse_command("测试")')
```

## 日志分析

### 1. 日志位置

```
logs/
├── nlp.log          # 主日志
├── nlp_error.log    # 错误日志
├── nlp_access.log   # 访问日志
└── nlp_perf.log     # 性能日志
```

### 2. 分析命令

```bash
# 查看错误频率
grep ERROR logs/nlp_error.log | awk '{print $5}' | sort | uniq -c

# 分析响应时间
grep "response_time" logs/nlp_perf.log | awk '{print $NF}' | \
  awk '{sum+=$1; count++} END {print "平均:", sum/count, "ms"}'

# 查找特定错误
grep -B5 -A5 "NLP_002" logs/nlp_error.log

# 实时监控日志
tail -f logs/nlp.log | grep --line-buffered ERROR
```

### 3. 日志格式解析

```python
import re
from datetime import datetime

def parse_log_line(line):
    """解析日志行"""
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (\w+) - (\w+) - (.+)'
    match = re.match(pattern, line)
    
    if match:
        return {
            'timestamp': datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S'),
            'logger': match.group(2),
            'level': match.group(3),
            'message': match.group(4)
        }
    return None

# 分析日志文件
with open('logs/nlp.log', 'r') as f:
    errors = []
    for line in f:
        parsed = parse_log_line(line)
        if parsed and parsed['level'] == 'ERROR':
            errors.append(parsed)

print(f"发现 {len(errors)} 个错误")
```

## 性能问题排查

### 1. 性能分析工具

```python
import cProfile
import pstats
from pstats import SortKey

# 性能分析
profiler = cProfile.Profile()
profiler.enable()

# 运行代码
nlp = DeepSeekNLPProcessor()
for i in range(100):
    nlp.parse_command("测试命令")

profiler.disable()

# 生成报告
stats = pstats.Stats(profiler)
stats.sort_stats(SortKey.CUMULATIVE)
stats.print_stats(20)  # 打印前20个最耗时的函数
```

### 2. 内存泄漏检测

```python
import tracemalloc
import gc

# 开始追踪
tracemalloc.start()

# 获取初始快照
snapshot1 = tracemalloc.take_snapshot()

# 运行可能泄漏的代码
for i in range(1000):
    nlp.parse_command(f"命令{i}")

# 获取结束快照
snapshot2 = tracemalloc.take_snapshot()

# 比较差异
top_stats = snapshot2.compare_to(snapshot1, 'lineno')

print("内存增长最多的代码位置:")
for stat in top_stats[:10]:
    print(stat)

# 强制垃圾回收
gc.collect()
```

### 3. 并发问题

```python
import threading
import queue

# 测试线程安全
def stress_test(nlp, results_queue):
    """压力测试"""
    try:
        for i in range(100):
            result = nlp.parse_command(f"测试{i}")
            results_queue.put(("success", result))
    except Exception as e:
        results_queue.put(("error", str(e)))

# 创建多个线程
nlp = DeepSeekNLPProcessor()
results = queue.Queue()
threads = []

for i in range(10):
    t = threading.Thread(target=stress_test, args=(nlp, results))
    threads.append(t)
    t.start()

# 等待完成
for t in threads:
    t.join()

# 检查结果
errors = 0
while not results.empty():
    status, _ = results.get()
    if status == "error":
        errors += 1

print(f"错误数: {errors}")
```

## API 问题

### 1. 速率限制

**症状：**
```
429 Too Many Requests
```

**解决方案：**
```python
import time
from functools import wraps

def rate_limit(calls_per_minute=60):
    """速率限制装饰器"""
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

# 应用速率限制
@rate_limit(calls_per_minute=30)
def call_api():
    return nlp.parse_command("测试")
```

### 2. 重试机制

```python
import backoff

@backoff.on_exception(
    backoff.expo,
    Exception,
    max_tries=3,
    max_time=60
)
def robust_parse_command(nlp, command):
    """带重试的命令解析"""
    return nlp.parse_command(command)
```

### 3. 健康检查

```python
def health_check():
    """NLP 服务健康检查"""
    try:
        # 测试基本功能
        nlp = DeepSeekNLPProcessor()
        result = nlp.parse_command("test")
        
        # 检查监控
        monitor = get_nlp_monitor()
        stats = monitor.get_stats()
        
        # 检查缓存
        cache_stats = nlp.get_cache_stats()
        
        return {
            "status": "healthy",
            "nlp_functional": True,
            "monitor_active": stats is not None,
            "cache_operational": cache_stats['size'] >= 0
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

## 集成问题

### 1. Flask 集成问题

**问题：** NLP 处理阻塞 Web 请求

**解决：**
```python
from flask import Flask, jsonify
from concurrent.futures import ThreadPoolExecutor
import asyncio

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=10)
nlp = DeepSeekNLPProcessor()

@app.route('/parse', methods=['POST'])
def parse_command():
    command = request.json.get('command')
    
    # 异步处理
    future = executor.submit(nlp.parse_command, command)
    
    try:
        result = future.result(timeout=5)  # 5秒超时
        return jsonify(result)
    except TimeoutError:
        return jsonify({"error": "处理超时"}), 504
```

### 2. 数据库集成

**问题：** 缓存与数据库不同步

**解决：**
```python
class DatabaseAwareNLP(DeepSeekNLPProcessor):
    def __init__(self, db_connection, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = db_connection
    
    def parse_command(self, command, context=None):
        # 先检查数据库缓存
        db_result = self.db.get_cached_parse(command)
        if db_result:
            return db_result
        
        # 调用父类方法
        result = super().parse_command(command, context)
        
        # 保存到数据库
        self.db.save_parse_result(command, result)
        
        return result
```

## 紧急修复

### 1. 服务降级

```python
class DegradedNLPService:
    """降级的 NLP 服务（仅规则匹配）"""
    
    def __init__(self):
        self.patterns = {
            "攻击": "combat.attack",
            "防御": "combat.defend",
            "移动": "exploration.move",
            "查看": "information.view"
        }
    
    def parse_command(self, command):
        for pattern, intent in self.patterns.items():
            if pattern in command:
                return ParsedCommand(
                    raw=command,
                    normalized_command=pattern,
                    intent=intent,
                    args={},
                    explanation="降级模式",
                    confidence=0.7
                )
        
        return ParsedCommand(
            raw=command,
            normalized_command="unknown",
            intent="unknown",
            args={},
            explanation="降级模式-未识别",
            confidence=0.3
        )

# 切换到降级服务
if api_is_down():
    nlp = DegradedNLPService()
else:
    nlp = DeepSeekNLPProcessor()
```

### 2. 快速回滚

```bash
#!/bin/bash
# rollback.sh

# 保存当前版本
cp -r src/xwe/core/nlp src/xwe/core/nlp.backup

# 回滚到上一版本
git checkout HEAD~1 src/xwe/core/nlp/

# 重启服务
systemctl restart xwe-nlp

# 验证
curl http://localhost:5001/health
```

### 3. 紧急修复清单

- [ ] 确认问题范围
- [ ] 切换到降级模式
- [ ] 通知相关人员
- [ ] 收集错误日志
- [ ] 实施临时修复
- [ ] 测试修复效果
- [ ] 部署到生产环境
- [ ] 监控运行状态
- [ ] 编写事故报告
- [ ] 制定长期解决方案

## 联系支持

如果以上方法都无法解决问题，请：

1. 收集相关日志和错误信息
2. 记录重现步骤
3. 联系技术支持团队
4. 提交 Issue 到项目仓库

**技术支持信息：**
- 项目仓库: https://github.com/your-org/xianxia_world_engine
- Issue 追踪: https://github.com/your-org/xianxia_world_engine/issues
- 文档网站: https://docs.xwe.com
- 社区论坛: https://forum.xwe.com