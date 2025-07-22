---
title: 修仙世界引擎 (Xianxia World Engine)
author: 修仙世界引擎团队
date: 2025-07-01
tags: [模块]
---

# 修仙世界引擎 (Xianxia World Engine)

一个基于文本的修仙世界模拟游戏引擎，让玩家体验修仙之旅。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
pre-commit install
```

### 2. 启动游戏

```bash
# 使用提供的脚本
./scripts/start.sh

# 或手动运行
python -m xwe.cli.run_server
# 如需指定存档或日志目录：
# python -m xwe.cli.run_server --save-dir my_saves --log-dir my_logs
```

`scripts/start.sh` 仅负责启动应用，运行前请先完成依赖安装。
旧的 `scripts/run.py` 启动脚本仍然可用，但已不再推荐。

### 3. 访问游戏

打开浏览器访问：http://localhost:5001

### 4. 运行测试

在首次运行测试前，请确保安装所有依赖：

```bash
pip install -r requirements.txt
```

然后执行：

```bash
python scripts/maintenance/run_tests.py all
# 运行 DeepSeek 异步单元测试
python scripts/run_async_tests.py
```

运行测试时，`tests/conftest.py` 会自动设置以下环境变量：

- `USE_MOCK_LLM=true`：使用模拟的 LLM 客户端
- `ENABLE_PROMETHEUS=true`：启用 Prometheus 指标
- `ENABLE_CONTEXT_COMPRESSION=true`：启用上下文压缩

若需要执行依赖真实 DeepSeek API 的测试，请额外设置 `DEEPSEEK_API_KEY`。
某些基准测试依赖 `pandas` 与 `matplotlib`，在缺少这些依赖的环境下会被自动跳过。

### 5. 启用异步模式（可选）

```bash
export USE_ASYNC_DEEPSEEK=1
export FLASK_ASYNC_ENABLED=1
```

详见 [异步模式快速指南](docs/DEEPSEEK_ASYNC_QUICKSTART.md)。

### 文档构建/预览

项目文档使用 [MkDocs](https://www.mkdocs.org/) 与 `mkdocs-material` 主题。若要在本地查看文档，可执行：

```bash
pip install mkdocs-material  # 如未安装
mkdocs serve                 # 本地预览
# 或生成静态站点
mkdocs build
```

预览地址默认是 <http://localhost:8000>。

## Recent Architecture Changes (v0.3.0)

- **API Consolidation**: Merged `api_fixes.py` into main route handlers
- **Module Restructuring**: Removed empty `deepseek/__init__.py`, moved AI integration to `src/ai/deepseek_client.py`
- **Improved Code Organization**: All API routes now follow RESTful conventions under `src/api/routes/`
- **DeepSeek Route Unification**: Deprecated `/api/v1/deepseek` blueprint. All
  DeepSeek endpoints are served from `/api/llm`.

These changes improve maintainability and reduce code duplication. For migration details,
see [CHANGELOG.md](./CHANGELOG.md).

## 游戏流程

1. **开始页面** - 选择"开始新游戏"
2. **欢迎页面** - 了解游戏背景
3. **角色创建** - 创建你的角色
4. **世界介绍** - 了解游戏世界
5. **游戏主界面** - 开始你的修仙之旅

## 游戏命令

- `探索` - 探索当前区域
- `修炼` - 进行修炼
- `查看状态` - 查看角色状态
- `背包` - 打开背包
- `地图` - 查看地图
- `任务` - 查看任务列表
- `帮助` - 显示帮助信息

## 开发模式

### 启用开发模式

1. 在开始页面点击"开发者模式"
2. 输入在 `DEV_PASSWORD` 中设置的密码
3. 或在地址栏添加 `?dev=true`
4. 也可以在浏览器控制台执行 `localStorage.setItem('dev', 'true')`

### 开发模式快捷键

- `Ctrl+Shift+S` - 跳过到角色创建
- `Ctrl+Shift+W` - 跳过到世界介绍
- `Ctrl+Shift+G` - 直接进入游戏
- `ESC` - 关闭当前面板
- `Ctrl+S` - 快速保存（游戏内）

## 项目结构

```
xianxia_world_engine/
├── scripts/run.py          # 兼容旧路径的启动脚本（已不推荐）
├── src/                    # 迁移后的源代码
│   └── xwe/                # 游戏引擎核心模块
├── infrastructure/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── deploy/             # 部署脚本和配置
│   └── monitoring/         # 监控配置
├── tests/                  # 单元测试
│   └── performance/        # k6 压力测试
└── docs/                   # 项目文档
```

## 功能特点

- 🎮 文本命令式游戏玩法
- 🎭 角色属性自定义系统
- 🗺️ 开放世界探索
- ⚔️ 修炼系统
- 📦 背包物品管理
- 📜 任务系统
- 💾 存档功能（开发中）
- 🌍 丰富的世界观设定
- 🤖 智能NLP命令解析系统

## 技术栈

- **后端**: Python Flask
- **前端**: HTML5, CSS3, JavaScript
- **数据**: JSON文件存储
- **样式**: 自定义水墨风格主题
- **AI**: DeepSeek API (NLP处理)

## NLP 智能命令系统

### 功能概述

修仙世界引擎集成了先进的自然语言处理（NLP）系统，让玩家可以使用自然语言与游戏交互，而不仅限于固定的命令格式。

#### 核心特性

- **智能意图识别**: 理解玩家的自然语言输入，自动转换为游戏命令
- **上下文感知**: 根据游戏状态智能解析命令含义
- **多语言支持**: 支持中文自然语言输入
- **容错能力**: 自动纠正拼写错误和语法变化
- **缓存优化**: 智能缓存常用命令，提高响应速度
- **离线回退**: API不可用时自动切换到规则引擎

### 快速开始

1. **配置 API 密钥**
   ```bash
   # 在 .env 文件中设置
   DEEPSEEK_API_KEY=your_api_key_here
   ```

2. **启用 NLP 功能**
   ```python
   # 默认已启用，可在配置中调整
   nlp_config.json: "enable_llm": true
   ```

3. **使用自然语言命令**
   ```
   # 传统命令
   > 攻击 妖兽

   # 自然语言
   > 我要攻击那只妖兽
   > 用剑砍它
   > 快跑，这里太危险了
   ```

### 配置说明

NLP系统配置文件位于 `src/xwe/data/interaction/nlp_config.json`，主要配置项：

- `enable_llm`: 是否启用LLM解析
- `llm_provider`: LLM提供商（deepseek/openai/mock）
- `confidence_threshold`: 命令识别置信度阈值
- `cache_size`: 缓存大小
- `fallback_to_rules`: 是否启用规则引擎回退

详细配置说明请参考 [NLP配置文档](docs/api/nlp_api.md#配置)

### API 参考

完整的 NLP API 文档请参考：[docs/api/nlp_api.md](docs/api/nlp_api.md)

## 缓存与 TTL 设置

`config/game_config.py` 提供以下可调参数：

- `data_cache_ttl`：数据文件缓存时间，默认 `300` 秒
- `smart_cache_ttl`：`SmartCache` 的默认 TTL，默认 `300` 秒
- `smart_cache_size`：`SmartCache` 缓存上限，默认 `128`

可在代码中修改这些值，例如：

```python
from config.game_config import config

config.data_cache_ttl = 600
config.smart_cache_ttl = 60
config.smart_cache_size = 256
```

修改后重启游戏即可生效。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue。

更多文档见 [docs/INDEX.md](docs/INDEX.md)。
项目结构详见 [docs/architecture/project_structure.md](docs/architecture/project_structure.md)，
开发环境搭建见 [docs/development/setup_guide.md](docs/development/setup_guide.md)。
部署与监控指南见 [infrastructure/README.md](infrastructure/README.md)。

历史修复总结文档已移动至 [docs/reports](docs/reports)。
