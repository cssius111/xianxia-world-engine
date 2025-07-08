# 部署验证检查清单

以下内容基于项目文档中提到的配置要求，部署前请逐一确认：

## 1. 环境变量
- [ ] `FLASK_ENV`、`FLASK_DEBUG`、`PORT` 等基础变量已按照 `.env.example` 配置。
- [ ] `SECRET_KEY` 与 `FLASK_SECRET_KEY` 已设置为安全值。
- [ ] `DEEPSEEK_API_KEY` 已填入 `.env`，保证 NLP 功能可用【F:docs/ROADMAP.md†L10-L16】。
- [ ] `ENABLE_PROMETHEUS` 设为 `true`，并确认 `/metrics` 端点可访问【F:src/xwe/metrics/MONITORING.md†L224-L244】。
- [ ] `ENABLE_E2E_API` 开启时，已在测试环境验证【F:docs/development/E2E_COMPLETE_GUIDE.md†L160-L172】。
- [ ] Agent 系统相关变量（如 `ENABLE_NPC_AGENT`、`AGENT_RESPONSE_TIMEOUT` 等）已根据需求设置【F:docs/architecture/agent_system.md†L110-L126】。

## 2. API 密钥
- [ ] 所有外部 API 密钥（如 `DEEPSEEK_API_KEY`）均已安全存储并在环境中读取【F:docs/deepseek_nlp_guide.md†L20-L23】。

## 3. 监控与指标
- [ ] Prometheus 依赖安装完毕，`ENABLE_PROMETHEUS` 为 `true`【F:src/xwe/metrics/PROMETHEUS_README.md†L12-L33】。
- [ ] 访问 `/metrics` 能返回指标数据，用于系统监控【F:src/xwe/metrics/MONITORING.md†L84-L87】。
- [ ] NLP 性能监控端点 `/nlp_monitor` 可正常查看统计信息【F:docs/deepseek_nlp_guide.md†L59-L66】。
- [ ] 部署目录中的 `xwe_prometheus_rules.yml` 已加载到 Prometheus【F:deploy/prometheus/xwe_prometheus_rules.yml†L1-L7】。

确保以上项均通过后，即可安全部署修仙世界引擎。
