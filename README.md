# XianXia World Engine - 修仙世界引擎

一个基于Python的AI驱动修仙游戏引擎，支持自然语言交互、动态剧情生成和丰富的游戏系统。

## 🌟 项目特色

- **AI驱动的自然语言交互**: 集成DeepSeek API，理解复杂的中文指令
- **开局Roll系统**: 无限重置角色属性，追求完美开局
- **动态游戏世界**: 随机事件、动态数据、真实的修炼体验
- **完整游戏系统**: 战斗、技能、探索、NPC交互、对话系统
- **模块化架构**: 清晰的代码结构，易于扩展和维护

## ✨ 2.0 更新亮点
- 🐉 中国龙ASCII艺术和彩色输出，营造浓厚氛围
- 📊 智能状态显示与渐进式成就系统
- ⚙️ 命令优先级和智能命令处理，更好理解玩家意图
- 🌟 开局事件及沉浸式剧情系统
- 📦 MOD生态与内容热更新
- 🤖 AI个性化推荐与社区反馈收集
- 🛠️ 自动存档和性能监控


## 📂 项目结构

```
xianxia_world_engine/
├── xwe/                # 游戏引擎核心
│   ├── core/          # 核心系统（角色、战斗、技能、AI等）
│   ├── world/         # 世界系统（地图、事件、位置管理）
│   ├── npc/           # NPC系统（对话、交易、关系）
│   ├── engine/        # 表达式解析引擎
│   └── data/          # 游戏数据配置（JSON）
├── scripts/           # 运行脚本和工具
│   ├── demos/         # 演示脚本
│   ├── tools/         # 实用工具
│   └── utils/         # 辅助脚本
├── tests/             # 测试套件
│   ├── unit/          # 单元测试
│   └── integration/   # 集成测试
├── docs/              # 项目文档
│   └── development/   # 开发文档
├── saves/             # 游戏存档
├── main.py           # 游戏主入口
└── main_menu.py      # 主菜单程序
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip（Python包管理器）

### 安装步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd xianxia_world_engine

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置API密钥（可选，用于AI功能）
export DEEPSEEK_API_KEY="your-api-key"
```

### 运行游戏

```bash
# 方式1：一键启动（推荐）
python run_game.py

# 方式2：主菜单模式
python main_menu.py

# 方式3：直接开始游戏
python main.py

# 方式4：快速启动脚本
python quick_start.py
```

## 🎮 游戏特性

### 开局Roll系统
- 随机生成角色属性、灵根、命格、天赋
- 可无限重置直到满意
- 综合评分系统（D级-SSS级）

### 核心玩法
- **修炼系统**: 从聚气期到合体期的完整境界体系
- **战斗系统**: 回合制战斗，支持技能、防御、逃跑
- **探索系统**: 发现新地点、触发随机事件
- **NPC交互**: 对话、交易、关系系统

### 基础命令
- `状态` - 查看角色信息
- `技能` - 查看技能列表
- `地图` - 查看当前位置
- `探索` - 探索当前区域
- `修炼` - 进行修炼
- `帮助` - 显示所有命令

### 自然语言支持
游戏支持自然语言输入，例如：
- "我想去坊市看看"
- "用剑气斩攻击那个妖兽"
- "和王老板聊聊天"
- "我要修炼一会儿"

## 🛠️ 技术架构

### 核心系统 (xwe/core/)
- **character.py**: 角色属性和状态管理
- **combat.py**: 战斗系统实现
- **skills.py**: 技能系统和效果
- **ai.py**: NPC AI决策
- **nlp/**: 自然语言处理模块
- **roll_system/**: 开局Roll系统

### 世界系统 (xwe/world/)
- **world_map.py**: 地图和区域管理
- **event_system.py**: 事件触发和处理
- **location_manager.py**: 位置和移动管理

### NPC系统 (xwe/npc/)
- **dialogue_system.py**: 对话树和分支
- **npc_manager.py**: NPC档案和行为
- **trading_system.py**: 交易系统

## 📊 开发和测试

### 运行测试
```bash
# 运行所有测试
python scripts/tools/run_tests.py

# 运行单元测试
python -m pytest tests/unit/

# 测试特定功能
python scripts/test_roll.py      # 测试Roll系统
python scripts/test_nlp.py       # 测试NLP系统
```

### 工具脚本
- `scripts/tools/check_status.py` - 检查项目状态
- `scripts/demos/demo_all_features.py` - 功能演示
- `scripts/verify_project.py` - 验证项目完整性
更多文档请参见 `docs/README.md`、`FEATURES_GUIDE.md` 与 `OPTIMIZATION_SUMMARY.md`。

## 🤝 贡献指南

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

## 🙏 致谢

- 感谢所有贡献者
- 特别感谢DeepSeek提供的API支持

---

**项目状态**: 活跃开发中 | **版本**: 2.0.0 | **最后更新**: 2025-06-04

如有问题或建议，欢迎提交Issue或联系开发者。
