# 部署验证清单

## 🚀 XianXia World Engine NLP 模块部署验证

### 1. 环境配置验证

- [ ] **Python 版本**
  - 确认 Python >= 3.8
  - 命令: `python --version`
  
- [ ] **依赖包安装**
  - 安装所有必需依赖: `pip install -r requirements.txt`
  - 验证 prometheus-flask-exporter: `pip show prometheus-flask-exporter`
  - 验证其他关键包: `pip list | grep -E "Flask|requests|psutil"`

- [ ] **环境变量配置**
  ```bash
  # 必需的环境变量
  export DEEPSEEK_API_KEY="your-api-key"
  export ENABLE_PROMETHEUS="true"
  export ENABLE_CONTEXT_COMPRESSION="true"
  export USE_MOCK_LLM="false"  # 生产环境设为 false
  export XWE_MAX_LLM_RETRIES="3"
  export LLM_ASYNC_WORKERS="5"
  ```

### 2. API 密钥验证

- [ ] **DeepSeek API 密钥**
  - 确认密钥已设置: `echo $DEEPSEEK_API_KEY`
  - 测试 API 连接:
    ```python
    from xwe.core.nlp.llm_client import LLMClient
    client = LLMClient()
    response = client.chat("测试连接")
    print(response)
    ```

### 3. 监控端点检查

- [ ] **Prometheus 指标端点**
  - 访问: `http://localhost:5000/metrics`
  - 验证自定义指标存在:
    - `xwe_nlp_request_seconds`
    - `xwe_nlp_token_count`
    - `xwe_nlp_cache_hit_total`
    - `xwe_context_compression_total`

- [ ] **健康检查端点**
  - 基础健康检查: `curl http://localhost:5000/health`
  - 详细健康检查: `curl http://localhost:5000/health/detailed`

### 4. 性能基准验证

- [ ] **响应时间测试**
  ```bash
  # 单个请求测试
  time curl -X POST http://localhost:5000/api/game/command \
    -H "Content-Type: application/json" \
    -d '{"command": "探索周围环境"}'
  ```
  - 目标: 平均响应时间 < 1秒

- [ ] **并发性能测试**
  ```bash
  # 使用 ab 进行简单压测
  ab -n 100 -c 10 -p test_data.json -T application/json \
    http://localhost:5000/api/game/command
  ```
  - 目标: 支持 50+ QPS

- [ ] **内存使用验证**
  - 启动时内存: < 200MB
  - 运行1小时后: < 500MB
  - 无明显内存泄漏

### 5. 日志配置验证

- [ ] **日志文件位置**
  - 确认日志目录存在: `ls -la logs/`
  - 检查日志轮转配置

- [ ] **日志级别设置**
  - 生产环境: `LOG_LEVEL=INFO`
  - 调试时: `LOG_LEVEL=DEBUG`

- [ ] **日志格式验证**
  - 包含时间戳、级别、模块、消息
  - 示例: `2024-03-14 10:30:45 INFO [xwe.nlp] Processing command: 探索`

### 6. 错误处理验证

- [ ] **API 超时处理**
  - 设置短超时测试: `LLM_TIMEOUT=1`
  - 验证优雅降级

- [ ] **无效输入处理**
  ```bash
  # 测试空输入
  curl -X POST http://localhost:5000/api/game/command \
    -H "Content-Type: application/json" \
    -d '{"command": ""}'
  
  # 测试超长输入
  curl -X POST http://localhost:5000/api/game/command \
    -H "Content-Type: application/json" \
    -d '{"command": "'$(python -c "print('x'*10000)")'"}'
  ```

- [ ] **并发错误处理**
  - 同时发送100个请求
  - 验证无崩溃，错误率 < 5%

### 7. 资源限制设置

- [ ] **进程限制**
  ```bash
  # 设置文件描述符限制
  ulimit -n 65536
  
  # 设置最大进程数
  ulimit -u 4096
  ```

- [ ] **内存限制**
  - 使用 systemd 或 Docker 设置内存上限
  - 建议: 2GB

- [ ] **CPU 限制**
  - 限制 CPU 使用率避免影响其他服务
  - 建议: 80% 最大使用率

### 8. 安全配置

- [ ] **API 密钥保护**
  - 不在代码中硬编码
  - 使用环境变量或密钥管理服务

- [ ] **输入验证**
  - SQL 注入防护
  - XSS 防护
  - 路径遍历防护

- [ ] **访问控制**
  - 限制 /metrics 端点访问
  - API 认证机制

### 9. 监控集成

- [ ] **Prometheus 配置**
  ```yaml
  # prometheus.yml
  scrape_configs:
    - job_name: 'xwe'
      static_configs:
        - targets: ['localhost:5000']
      scrape_interval: 15s
  ```

- [ ] **Grafana 仪表板**
  - 导入提供的仪表板模板
  - 设置告警规则

- [ ] **告警配置**
  - 高延迟告警 (> 5秒)
  - 高错误率告警 (> 10%)
  - 内存使用告警 (> 1GB)

### 10. 回滚方案

- [ ] **备份当前版本**
  ```bash
  # 备份代码
  tar -czf xwe_backup_$(date +%Y%m%d).tar.gz /path/to/xwe
  
  # 备份配置
  cp -r config/ config_backup_$(date +%Y%m%d)/
  ```

- [ ] **数据库备份**
  - 如果使用数据库，确保有备份

- [ ] **快速回滚脚本**
  ```bash
  #!/bin/bash
  # rollback.sh
  systemctl stop xwe
  rm -rf /path/to/xwe
  tar -xzf xwe_backup_latest.tar.gz -C /
  systemctl start xwe
  ```

### 11. 性能优化检查

- [ ] **启用上下文压缩**
  - 验证: `ENABLE_CONTEXT_COMPRESSION=true`
  - 检查压缩率 > 30%

- [ ] **异步处理启用**
  - 验证线程池大小合理
  - 检查队列不会无限增长

- [ ] **缓存配置**
  - NLP 结果缓存启用
  - 缓存命中率 > 20%

### 12. 部署后验证

- [ ] **功能测试**
  ```bash
  # 运行快速功能测试
  pytest tests/integration/test_deployment.py -v
  ```

- [ ] **性能基准对比**
  - 与测试环境基准对比
  - 性能下降 < 10%

- [ ] **监控数据验证**
  - Prometheus 正常收集数据
  - Grafana 图表正常显示

- [ ] **日志审查**
  - 无异常错误日志
  - 无频繁的警告

### 13. 文档更新

- [ ] **部署文档**
  - 记录实际部署步骤
  - 记录遇到的问题和解决方案

- [ ] **运维手册**
  - 常见问题处理
  - 性能调优建议
  - 故障排查步骤

### 14. 培训和交接

- [ ] **运维团队培训**
  - 系统架构说明
  - 监控指标解读
  - 故障处理流程

- [ ] **值班安排**
  - 24/7 值班表
  - 紧急联系方式
  - 升级流程

## 签字确认

| 角色 | 姓名 | 日期 | 签名 |
|------|------|------|------|
| 开发负责人 | | | |
| 测试负责人 | | | |
| 运维负责人 | | | |
| 项目经理 | | | |

---

**注意**: 所有检查项必须通过才能正式上线。如有任何项目未通过，需记录原因并制定解决方案。
