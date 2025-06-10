# 修仙世界引擎 (XianXia World Engine) v3.0

> 一个基于Python的AI驱动修仙游戏引擎，支持自然语言交互、动态剧情生成和丰富的游戏系统。

## 📑 目录

- [项目特色](#项目特色)
- [快速开始](#快速开始)
- [游戏特性](#游戏特性)
- [核心功能](#核心功能)
- [技术架构](#技术架构)
- [开发指南](#开发指南)
- [API文档](#api文档)
- [贡献指南](#贡献指南)
- [世界观概要](#世界观概要)

## 🌟 项目特色

### 核心亮点
- **AI驱动的自然语言交互**: 集成DeepSeek API，理解复杂的中文指令
- **开局Roll系统**: 无限重置角色属性，追求完美开局
- **动态游戏世界**: 随机事件、动态数据、真实的修炼体验
- **完整游戏系统**: 战斗、技能、探索、NPC交互、对话系统
- **模块化架构**: 清晰的代码结构，易于扩展和维护

### 3.0版本新增
- 🐉 中国龙ASCII艺术和彩色输出
- 📊 智能状态显示与渐进式成就系统
- ⚙️ 命令优先级和智能命令处理
- 🌟 开局事件及沉浸式剧情系统
- 📦 MOD生态与内容热更新
- 🤖 AI个性化推荐与社区反馈
- 🛠️ 自动存档和性能监控

## 🚀 快速开始

### 环境要求
- Python 3.8+
- pip（Python包管理器）
- requests 库（已包含在 `requirements.txt` 中）

### 一键启动
```bash
# 推荐方式：自动修复并启动
python run_game.py
```

更多启动脚本和说明请参阅 [docs/STARTERS.md](docs/STARTERS.md)。

### 安装步骤
```bash
# 1. 克隆项目
git clone <repository-url>
cd xianxia_world_engine

# 2. 安装依赖
pip install -r requirements.txt  # 包含 jsonschema 等核心库

# 3. 配置API（可选，用于AI功能）
cp .env.example .env  # 复制示例配置文件
# 然后编辑 `.env` 填入相应的 API 密钥
```

## 🎮 游戏特性

### 开局Roll系统
- 🎲 无限重置角色属性直到满意
- 🌟 11种命格、12种天赋、10种系统、7种身份
- 💎 完整灵根体系（单灵根到五灵根）
- 📊 综合评分系统（D级-SSS级）

### 核心玩法
- **修炼系统**: 从聚气期到合体期的完整境界体系
- **战斗系统**: 回合制战斗，支持技能、防御、逃跑
- **探索系统**: 发现新地点、触发随机事件
- **NPC交互**: 对话、交易、关系系统
- **成就系统**: 6大类14种成就，持续的目标和奖励

### 游戏命令

#### 基础命令
- `状态` - 查看角色信息
- `技能` - 查看技能列表
- `地图` - 查看当前位置
- `探索` - 探索当前区域
- `修炼` - 进行修炼
- `帮助` - 显示所有命令

#### 自然语言支持
游戏支持自然语言输入，例如：
- "我想去坊市看看"
- "用剑气斩攻击那个妖兽"
- "和王老板聊聊天"
- "我要修炼一会儿"

#### 3.0新增命令
- `反馈：[内容]` - 提交游戏反馈
- `社区` - 查看社区链接
- `系统状态` - 查看系统信息

## 🏗️ 核心功能

### 1️⃣ 基础玩家体验
- **智能命令系统**: 模糊匹配、自然语言理解、快捷键支持
- **友善错误引导**: 输错命令时提供智能建议
- **上下文感知**: 根据当前场景提供相关提示

### 2️⃣ 沉浸式叙事
- **开局事件系统**: 5种精心设计的开局（神秘长老、家族传承等）
- **天赋逆转机制**: 废材逆袭、诅咒化福等特殊转折
- **成就系统**: 战斗、修炼、探索、社交等多维度成就

### 3️⃣ 内容生态
- **MOD系统**: 完整的MOD加载器，支持热更新
- **内容类型**: NPC、物品、技能、地点、事件、任务、对话、怪物
- **MOD工具**: 一键创建MOD模板，统一内容管理

### 4️⃣ AI个性化
- **玩家风格识别**: 8种玩家风格（战士型、探索型、社交型等）
- **动态内容推荐**: 根据行为分析推送个性化内容
- **自适应难度**: 根据玩家水平调整游戏难度

### 5️⃣ 社区系统
- **游戏内反馈**: 使用`反馈：[内容]`命令
- **自动分类**: Bug、建议、表扬、问题、投诉
- **社区链接**: Discord、论坛、Wiki、GitHub

### 6️⃣ 技术运营
- **自动存档**: 每5分钟或20个命令自动保存
- **性能监控**: CPU和内存使用监控
- **崩溃保护**: 自动恢复和错误日志

### 7️⃣ 视觉增强
- **彩色输出**: 16种颜色支持
- **ASCII艺术**: 10种图案（剑、山、龙等）
- **文字效果**: 打字机、淡入淡出、进度条

## 📂 技术架构

### 项目结构
```
xianxia_world_engine/
├── xwe/                # 游戏引擎核心
│   ├── core/          # 核心系统
│   ├── world/         # 世界系统
│   ├── npc/           # NPC系统
│   ├── features/      # 3.0功能模块
│   ├── engine/        # 表达式引擎
│   └── data/          # 游戏数据
├── scripts/           # 运行脚本
├── archive/          # 旧版脚本与备份
├── tests/             # 测试套件
├── mods/              # MOD目录
├── saves/             # 存档目录
├── docs/              # 项目文档
└── main.py           # 游戏入口
```
旧版脚本和备份文件已统一放入 `archive/` 目录，保持主目录整洁。

### 核心模块说明

#### core/ - 核心系统
- `character.py` - 角色属性和状态管理
- `combat.py` - 战斗系统实现
- `skills.py` - 技能系统和效果
- `ai.py` - NPC AI决策
- `nlp/` - 自然语言处理模块
- `roll_system/` - 开局Roll系统

#### world/ - 世界系统
- `world_map.py` - 地图和区域管理
- `event_system.py` - 事件触发和处理
- `location_manager.py` - 位置和移动管理

#### npc/ - NPC系统
- `dialogue_system.py` - 对话树和分支
- `npc_manager.py` - NPC档案和行为
- `trading_system.py` - 交易系统

#### features/ - 3.0功能模块
- `player_experience.py` - 玩家体验增强
- `narrative_system.py` - 叙事系统
- `content_ecosystem.py` - 内容生态
- `ai_personalization.py` - AI个性化
- `community_system.py` - 社区系统
- `technical_ops.py` - 技术运营
- `visual_enhancement.py` - 视觉增强
## 世界观概要

本项目采用多位面修仙设定，详细介绍请参见 [docs/WORLD_OVERVIEW.md](docs/WORLD_OVERVIEW.md)。


## 🛠️ 开发指南

### 添加新MOD
1. 运行MOD初始化脚本
```bash
python scripts/init_features.py
```

2. 在`mods/your_mod/`下添加内容
3. 游戏会自动加载新MOD

### 扩展功能
每个功能模块都可扩展：
- 新玩家风格：编辑`ai_personalization.py`
- 新成就：编辑`narrative_system.py`
- 新视觉效果：编辑`visual_enhancement.py`

### 运行测试
```bash
# 运行所有测试（默认使用 mock 模式）
export LLM_PROVIDER=mock
python tests/run_all_tests.py

# 测试特定功能
python test_features.py
python test_optimizations.py

# 运行单元测试
python -m pytest tests/unit/
```

如需使用真实 LLM 进行测试，可在 `.env` 中填入 API 密钥，并将
`LLM_PROVIDER` 设置为实际提供商。

## 📚 API文档

### NLP API v2.0
```python
from xwe.core.nlp import NLPProcessor

nlp = NLPProcessor()
result = nlp.parse(user_input, context=None)
```

**参数说明**:
- `user_input` (str): 用户输入的自然语言文本
- `context` (dict): 游戏上下文信息

**返回值**: `ParsedCommand`对象
- `command_type`: 命令类型
- `target`: 目标（如果有）
- `parameters`: 额外参数
- `confidence`: 置信度（0-1）

### 配置LLM API
```bash
# DeepSeek API
export DEEPSEEK_API_KEY="your-key"

# OpenAI API
export OPENAI_API_KEY="your-key"
```

## 🤝 贡献指南

### 贡献流程
1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

### 贡献重点
- 新的MOD内容
- 更多开局事件
- 新的成就设计
- 视觉效果改进
- Bug修复

### 代码规范
- 遵循PEP 8编码规范
- 添加适当的注释和文档
- 为新功能编写测试
- 保持模块化设计

## 📊 数据收集

游戏会本地收集以下数据用于改进体验：
- 玩家行为模式
- 热门功能使用
- 错误和崩溃信息
- 性能数据

*注：所有数据仅存储在本地，不会上传到任何服务器*

## ❓ 常见问题

**Q: 游戏启动失败？**
A: 检查Python版本（需要3.8+）和依赖安装

**Q: AI功能不工作？**
A: 需要在.env文件中设置API密钥

**Q: 如何关闭彩色输出？**
A: 在设置中关闭视觉增强

**Q: MOD不加载？**
A: 检查MOD目录结构和mod.json格式

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- 感谢所有贡献者
- 特别感谢DeepSeek提供的API支持
- 社区玩家的宝贵反馈

---

**项目状态**: 活跃开发中 | **版本**: 3.0.0 | **最后更新**: 2025-06-04

如有问题或建议，欢迎提交Issue或联系开发者。

祝您在修仙世界中获得精彩的体验！🗡️✨
