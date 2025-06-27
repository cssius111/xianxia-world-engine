# 修仙世界引擎 (Xianxia World Engine)

一个基于文本的修仙世界模拟游戏引擎，让玩家体验修仙之旅。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动游戏

```bash
python run.py
```

### 3. 访问游戏

打开浏览器访问：http://localhost:5001

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
2. 输入密码：`dev123`
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
├── run.py                  # 主程序入口
├── templates/              # HTML模板
│   ├── base.html          # 基础模板
│   ├── intro_optimized.html    # 角色创建流程
│   ├── game_enhanced_optimized_v2.html  # 游戏主界面
│   ├── screens/           # 页面模板
│   └── components/        # 组件模板
├── static/                # 静态资源
│   ├── css/              # 样式文件
│   └── js/               # JavaScript文件
├── xwe/                   # 核心模块
├── saves/                 # 存档文件
└── logs/                  # 日志文件，自动轮转并生成 `.gz` 压缩包
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

## 技术栈

- **后端**: Python Flask
- **前端**: HTML5, CSS3, JavaScript
- **数据**: JSON文件存储
- **样式**: 自定义水墨风格主题

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
