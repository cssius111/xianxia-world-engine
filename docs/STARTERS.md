# 启动脚本一览

下表汇总了常见的启动脚本及其作用，便于查找和避免文档中的重复说明。

| 脚本 | 说明 |
| ---- | ---- |
| `python run_game.py` | 自动修复并启动游戏（推荐） |
| `python main_menu.py [--mode dev]` | 启动主菜单，可选择玩家或开发者模式 |
| `python main.py` | 直接运行命令行版本游戏 |
| `python main_enhanced.py` | 含 2.0 功能的增强版，生成 `game_log.html` |
 
| `python run_web_ui.py` | 启动实验性的 Web 界面 |
| `python run_web_ui.py` | 使用数据驱动引擎的 Web 界面 |
 
| `python run_web_ui.py` | 启动增强版 Web UI（推荐） |
| `python run_web_ui.py` | 直接运行增强版 Web UI，跳过修复步骤 |
 
| `python archive/deprecated/run_web_ui_enhanced.py` | 启动旧版增强 Web UI（归档） |
| `python archive/deprecated/run_web_ui_enhanced.py` | 直接运行旧版增强 Web UI，跳过修复步骤 |
 
 
| `python run_web_ui.py` | 启动实验性的 Web 界面，使用数据驱动引擎 |
| `python run_web_ui_enhanced.py` | 启动增强版 Web UI（推荐，可跳过修复步骤） |
 
| `python scripts/play_demo.py` | 带使用提示的演示版本 |
| `python scripts/start.py` | 最简单的启动脚本，直接进入游戏 |

其他辅助脚本（如 `verify_fix.py`、`complete_fix.py`）可在 `scripts/utils/` 目录下找到，
主要用于修复或诊断问题。

