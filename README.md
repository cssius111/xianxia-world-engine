# 仙侠世界引擎 (XianXia World Engine)

本项目是一个基于文本的仙侠世界模拟器，提供控制台和Web界面两种运行方式。核心功能位于`xwe`包中，`api`目录提供REST接口，`entrypoints`目录包含启动脚本。

## 运行方式

- **控制台模式**

  ```bash
  python main_menu.py
  ```

- **Web界面**

 ```bash
  python entrypoints/run_web_ui_optimized.py
  ```

运行前请复制 `.env.example` 为 `.env` 并填写 `DEEPSEEK_API_KEY`。

## 目录结构

参考 `PROJECT_STRUCTURE.md` 获取更详细的目录说明。

## 测试

项目使用 [pytest](https://docs.pytest.org/) 进行单元测试：

```bash
pytest
```
