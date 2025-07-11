# Xianxia World Engine 异步化改造计划

## 项目信息
- **项目名称**: Xianxia World Engine  
- **当前状态**: Flask + JSON 数据驱动的文字游戏  
- **改造目标**: 实现 DeepSeek API 调用的异步化  
- **当前 QPS**: ~10  
- **部署方式**: 单机部署，未来可能多实例  

## 约束条件
1. 不修改现有函数签名（只能新增或包装）
2. 兼容现有日志与错误处理（logger）
3. 所有新增依赖须更新 requirements.txt 与 pyproject.toml
4. 保证 pytest -q 通过

## 执行步骤

### 1️⃣ 技术方案评估 [待完成]

**目标**: 比较三种异步化方案的优劣

| 方案 | 资源占用 | 侵入性 | 可扩展性 | 代码量 | 潜在陷阱 | 推荐度 |
|------|---------|--------|----------|---------|-----------|--------|
| A. httpx.AsyncClient | 3/5 | 2/5 | 4/5 | 3/5 | 3/5 | ⭐⭐⭐⭐ |
| B. ThreadPoolExecutor | 4/5 | 1/5 | 3/5 | 2/5 | 2/5 | ⭐⭐⭐ |
| C. Celery + Redis | 5/5 | 5/5 | 5/5 | 5/5 | 4/5 | ⭐⭐ |

**推荐方案**: httpx.AsyncClient
- **理由**: 资源占用适中，侵入性低，易于集成到现有Flask应用，可扩展性好

### 2️⃣ httpx.AsyncClient 实现方案 [待完成]

**文件**: `src/ai/deepseek_client.py`

**实现要点**:
- 新增 `async def chat_async(...)` 方法
- 使用 `httpx.AsyncClient` 替代 `requests`
- 保留原有同步方法不变
- 添加超时和重试机制

**依赖更新**:
```toml
# pyproject.toml
httpx = "^0.25.0"
```

**Flask 路由示例**:
```python
@app.get("/api/llm")
async def llm_endpoint():
    response = await deepseek_client.chat_async(prompt)
    return jsonify(response)
```

### 3️⃣ 线程池方案（备选）[待完成]

**实现要点**:
- 使用 `asyncio.run_in_executor`
- 线程池大小通过 `LLM_MAX_WORKERS` 环境变量配置
- 单例模式管理线程池

### 4️⃣ Celery + Redis 方案（备选）[待完成]

**实现要点**:
- 创建 `tasks.py` 定义异步任务
- 实现任务状态查询接口
- 配置 Celery broker 和 backend

### 5️⃣ 单元测试 [待完成]

**测试文件**: `tests/test_llm_async.py`

**测试内容**:
- 功能等价性测试：异步结果与同步结果一致
- 并发测试：50个并发请求，超时5秒
- 错误处理测试：API失败时的降级处理

### 6️⃣ 回滚/降级脚本 [待完成]

**脚本**: `scripts/toggle_async.sh`

**功能**:
- 通过环境变量切换同步/异步模式
- 无需重启 Gunicorn
- 支持健康检查

## 实施进度

| 步骤 | 状态 | 负责人 | 开始时间 | 完成时间 | 备注 |
|------|------|--------|----------|----------|------|
| 1️⃣ 技术评估 | 待开始 | - | - | - | 需要性能基准测试 |
| 2️⃣ httpx 实现 | 待开始 | - | - | - | 优先实施 |
| 3️⃣ 线程池实现 | 待开始 | - | - | - | 备选方案 |
| 4️⃣ Celery 实现 | 待开始 | - | - | - | 备选方案 |
| 5️⃣ 单元测试 | 待开始 | - | - | - | 必须完成 |
| 6️⃣ 回滚脚本 | 待开始 | - | - | - | 上线前准备 |

## 风险评估

### 技术风险
1. **异步兼容性**: Flask 2.3+ 需要正确配置异步支持
2. **依赖冲突**: httpx 可能与现有依赖冲突
3. **性能回退**: 异步化可能在低并发时性能不如同步

### 缓解措施
1. 充分测试 Flask 异步路由配置
2. 使用虚拟环境隔离测试依赖
3. 实施灰度发布，监控性能指标

## 验收标准

1. **功能完整性**
   - [ ] 异步方法实现完成
   - [ ] 原有同步接口正常工作
   - [ ] 日志记录正常

2. **性能指标**
   - [ ] 并发 50 请求响应时间 < 5s
   - [ ] CPU 占用率不超过同步版本 20%
   - [ ] 内存占用稳定

3. **质量保证**
   - [ ] 单元测试覆盖率 > 80%
   - [ ] 集成测试通过
   - [ ] 代码审查完成

4. **文档完善**
   - [ ] API 文档更新
   - [ ] 部署文档更新
   - [ ] 运维手册更新

## 参考资源

- [Flask 异步支持文档](https://flask.palletsprojects.com/en/2.3.x/async-await/)
- [httpx 文档](https://www.python-httpx.org/)
- [Python 异步编程最佳实践](https://docs.python.org/3/library/asyncio.html)

## 更新日志

- 2025-01-25: 初始计划创建
- 待更新...