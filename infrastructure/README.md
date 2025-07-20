# 基础设施概览

此目录包含部署和监控相关的文件，帮助在生产环境中运行与观测 **修仙世界引擎**。

## 子目录与文件说明

- **deploy/**：存放部署脚本及 Prometheus 规则等配置，另附 `verification_checklist.md` 供上线前检查。
- **monitoring/**：包含 Prometheus、Grafana 与 Alertmanager 的配置文件，用于监控应用状态和告警。
- **Dockerfile**：构建运行游戏引擎的容器镜像。
- **docker-compose.yml**：本地或小规模部署时的 Compose 编排文件，集成了应用及监控组件。

通过阅读本说明，可了解如何快速启动或监控项目。
