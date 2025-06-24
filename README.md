# 仙侠世界引擎 (XianXia World Engine)

![CI](https://github.com/cssius111/xianxia-world-engine/actions/workflows/python-ci.yml/badge.svg)

本项目是一个基于文本的仙侠世界模拟器，提供控制台和Web界面两种运行方式。核心功能位于`xwe`包中，`api`目录提供REST接口，`entrypoints`目录包含启动脚本。

## 安装与运行

1. 安装依赖

   ```bash
   pip install -r requirements.txt
   ```

2. 安装 Git 钩子（pre-commit）

   ```bash
   pre-commit install
   ```

3. 复制并编辑环境配置

   ```bash
   cp .env.example .env
   # 打开 .env 填写 DEEPSEEK_API_KEY 等变量
   ```

4. 选择运行模式

   - **控制台模式**

     ```bash
     python main_menu.py
     ```

   - **Web界面**

     ```bash
     python entrypoints/run_web_ui_optimized.py
     ```

### 常见问题

**Q: 启动时提示 `DEEPSEEK_API_KEY` 未设置？**

A: 确认 `.env` 文件存在并已填写正确的 API Key。

**Q: Web 页面无法访问或端口冲突？**

A: 默认监听 `5001` 端口，可在 `.env` 中设置 `FLASK_ENV` 为 `development` 并检查防火墙或端口占用情况。

## 目录结构

参考 `PROJECT_STRUCTURE.md` 获取更详细的目录说明。

> **注意**：旧的 `xwe_v2` 目录已移除，相关功能现统一在 `xwe` 下实现。

## 测试

项目使用 [pytest](https://docs.pytest.org/) 进行单元测试：

```bash
pytest
```
