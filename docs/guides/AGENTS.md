# AGENTS.md

本项目使用模块化的智能体架构，控制游戏世界中的主要实体。

## 🎮 Agent 类型

### PlayerAgent
- 代表玩家角色，接受自然语言指令并调用 NLP 处理器。
- 状态数据存储在 `player.json`。

### CombatAIEnemy
- 敌人决策逻辑，依据战场状态选择行动。

### VendorAgent
- 商人或拍卖 NPC，负责交易逻辑并更新玩家库存。

## 🧠 生命周期
1. **初始化**：载入配置或存档。
2. **每回合更新**：`on_turn_start` 调度行为。
3. **事件响应**：`on_event` 处理外部事件。
4. **终止清理**：`terminate` 释放资源。

## ⚙️ 依赖安装
```bash
pip install -r requirements.txt
```

## 🧪 运行测试
```bash
pytest tests/ -v
```

测试环境会加载 `.env` 并禁用交互输入，确保 Flask 等依赖已安装以通过 Web UI 测试。
