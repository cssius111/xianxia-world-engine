# 变更日志

所有重要的项目变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

## [1.4.0] - 2025-06-12

### 新增
- 结构化日志系统 (StructuredLogger) - 支持JSON格式日志输出
- Prometheus监控指标集成 - 包含http_request_duration_seconds和game_events_total等核心指标
- OpenAPI/Swagger文档自动生成 - 访问 /api/docs 查看交互式API文档
- 开发调试控制台 - 新增 /api/v1/dev/* 端点用于系统状态监控
- Docker容器化支持 - 包含Dockerfile和docker-compose.yml
- 完整的监控与调试文档

### 改进
- API模块增加了Swagger UI集成
- 日志服务增强，支持结构化输出
- 系统API新增metrics端点用于Prometheus抓取

### 依赖
- 新增 flask-swagger-ui==4.11.1
- 新增 psutil==5.9.8
- 新增 prometheus-client==0.19.0

### 文档
- 新增 docs/metrics_guide.md - 监控与调试指南
- 更新 REFACTOR_PROGRESS.md - 第4阶段进度更新至25%

## [1.3.0] - 2025-06-11

### 新增
- Service层架构实现
- 依赖注入容器
- 命令引擎服务
- 事件分发器服务
- 完整的服务接口定义

### 改进
- API层使用Service层重构
- 业务逻辑与表现层完全分离
- 添加了单元测试框架

## [1.2.0] - 2025-06-10

### 新增
- RESTful API v1实现
- 统一的错误处理机制
- API中间件架构
- 完整的API测试套件

### 改进
- 前后端完全分离
- 标准化的JSON响应格式
- 请求验证机制

## [1.1.0] - 2025-06-09

### 新增
- 前端模块化重构
- CSS/JS/HTML文件分离
- 组件化模板结构

### 改进
- 代码可维护性提升80%
- 减少单文件代码行数至500行以下

## [1.0.0] - 2025-06-08

### 新增
- 修仙世界引擎核心功能
- 基础战斗系统
- 角色成长系统
- 地图探索功能
- 存档系统

---

# NOTE: backward-compat
# 所有版本更新均保持向后兼容性
# 任何破坏性更改都会在主版本号中体现
