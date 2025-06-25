# 快速修复指南

## 问题
启动时遇到 `ModuleNotFoundError: No module named 'backoff'` 错误。

## 解决方案

### 方案 1：安装缺失的依赖（推荐）
```bash
pip install backoff
```

### 方案 2：运行安装脚本
```bash
chmod +x install_nlp_deps.sh
./install_nlp_deps.sh
```

### 方案 3：不使用 NLP 功能
系统已经设计为在没有 `backoff` 模块时也能运行。如果您不需要 NLP 功能，系统会自动使用传统命令解析。

## NLP 功能说明

NLP 功能是可选的，需要：
1. 安装 `backoff` 模块（用于 API 重试）
2. 设置 DeepSeek API 密钥

如果没有配置，系统会自动回退到传统的命令解析模式，不影响游戏基本功能。

## 启动游戏

修复后运行：
```bash
python start_web.py
```

游戏将在 http://localhost:5001 启动。
