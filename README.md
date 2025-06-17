# 仙侠世界引擎 (Xianxia World Engine)

一个模块化、可扩展的文字冒险游戏引擎，专为仙侠题材游戏设计。

## 🎮 快速开始

### 运行游戏
```bash
python run_game.py
```

### 基本命令
```
新游戏 张三      # 创建新角色
继续            # 加载最新存档
帮助            # 查看所有命令
退出            # 退出游戏
```

## 🏗️ 项目结构

```
xianxia_world_engine/
├── xwe/                    # 核心代码
│   ├── core/              # 核心模块
│   │   ├── state/         # 状态管理
│   │   ├── output/        # 输出系统
│   │   ├── command/       # 命令处理
│   │   └── orchestrator.py # 游戏协调器
│   ├── features/          # 游戏功能
│   └── data/             # 游戏数据
├── examples/             # 示例代码
├── tests/               # 测试套件
├── docs/                # 文档
└── run_game.py         # 快速启动脚本
```

## 🚀 特性

### 核心功能
- ✅ 模块化架构，易于扩展
- ✅ 多通道输出（控制台、文件、HTML）
- ✅ 自然语言命令处理
- ✅ 事件驱动的状态管理
- ✅ 自动保存和加载
- ✅ 丰富的游戏命令

### 技术特点
- 🐍 Python 3.8+ 
- 📝 完整的类型注解
- ⚡ 异步支持
- 🧪 全面的单元测试
- 📚 详细的文档

## 💻 开发指南

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行测试
```bash
pytest tests/
```

> **注意**：物品ID建议统一使用複数形式，例如 `spirit_stones`，旧写法
> `spirit_stone` 仍被兼容。

### 创建自定义游戏
```python
from xwe.core.orchestrator import GameConfig, GameOrchestrator

# 配置游戏
config = GameConfig(
    game_name="我的仙侠世界",
    enable_html=True,
    auto_save_enabled=True
)

# 创建并运行游戏
game = GameOrchestrator(config)
game.run_sync()
```

### 添加新命令
```python
from xwe.core.command import CommandHandler, CommandResult

class CustomHandler(CommandHandler):
    def can_handle(self, context):
        return context.raw_input.startswith("自定义")
    
    def handle(self, context):
        context.output_manager.info("执行自定义命令")
        return CommandResult.success()

# 注册处理器
game.command_processor.register_handler(CustomHandler())
```

## 📖 文档

详细文档请查看 `docs/` 目录：
- [架构设计](docs/architecture/modular_design.md)
- [API文档](docs/api/)
- [迁移指南](docs/migration/)
- [示例代码](examples/)

## 🎯 游戏玩法

### 基础命令
- **移动**：`去 <地点>`
- **探索**：`探索`
- **战斗**：`攻击`、`防御`、`逃跑`
- **修炼**：`修炼`、`突破`
- **交互**：`和 <NPC> 说话`、`交易`
- **物品**：`背包`、`使用 <物品>`
- **信息**：`状态`、`地图`、`技能`

### 游戏目标
在仙侠世界中修炼成仙，经历各种冒险，提升境界，最终达到飞升。

## 🛠️ 配置选项

创建 `game_config.json`：
```json
{
    "game_name": "仙侠世界",
    "game_mode": "player",
    "enable_console": true,
    "enable_html": true,
    "console_colored": true,
    "auto_save_enabled": true,
    "auto_save_interval": 300.0
}
```

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

## 📄 许可证

MIT License

## 🙏 致谢

感谢所有为这个项目做出贡献的人。

---

**享受你的仙侠之旅！** 🗡️✨
