# 🤖 修仙世界引擎 - Agent 系统文档

## 概述

本文档描述了修仙世界引擎中的智能Agent系统架构和实现细节。

## 系统架构

### 1. **核心Agent组件**

```
xianxia_world_engine/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py      # 基础Agent类
│   │   ├── npc_agent.py       # NPC智能体
│   │   ├── world_agent.py     # 世界事件智能体
│   │   └── player_agent.py    # 玩家行为分析智能体
│   └── nlp/
│       └── deepseek_integration.py  # DeepSeek NLP集成
```

### 2. **Agent 功能模块**

#### 2.1 NPC Agent（非玩家角色智能体）
- **对话生成**: 基于角色背景和当前情境生成合适的对话
- **行为决策**: 根据玩家行为和世界状态做出反应
- **记忆系统**: 记住与玩家的互动历史
- **情感模拟**: 模拟NPC的情感变化

#### 2.2 World Agent（世界事件智能体）
- **事件生成**: 动态生成世界事件
- **环境变化**: 管理天气、时间、地点变化
- **剧情推进**: 根据玩家进度推进主线剧情
- **随机遭遇**: 生成随机事件和遭遇

#### 2.3 Player Agent（玩家行为分析智能体）
- **意图识别**: 分析玩家输入的真实意图
- **行为预测**: 预测玩家下一步可能的行动
- **个性化推荐**: 基于玩家风格推荐任务和活动
- **难度调整**: 动态调整游戏难度

## 当前状态

### ✅ 已实现功能
1. **基础NLP集成**
   - DeepSeek API接入
   - 自然语言命令解析
   - 基础意图识别

2. **命令系统**
   - 文本命令处理
   - 动作映射
   - 错误处理

### 🚧 开发中功能
1. **高级NPC对话系统**
   - 上下文感知对话
   - 情感状态追踪
   - 长期记忆存储

2. **智能事件生成**
   - 基于玩家历史的事件定制
   - 动态难度调整
   - 剧情分支管理

3. **多Agent协作**
   - Agent间通信协议
   - 协作决策机制
   - 冲突解决策略

## 技术栈

- **NLP引擎**: DeepSeek API
- **框架**: Python asyncio
- **数据存储**: JSON（临时）/ SQLite（计划中）
- **消息队列**: 内存队列（临时）/ Redis（计划中）

## API 接口

### 1. NLP 命令处理
```python
POST /api/command
{
    "text": "向北走并查看周围",
    "context": {
        "location": "青云峰",
        "player_state": "normal"
    }
}
```

### 2. NPC 对话
```python
POST /api/npc/dialogue
{
    "npc_id": "elder_wang",
    "message": "请问如何提升修为？",
    "dialogue_history": []
}
```

### 3. 世界事件查询
```python
GET /api/world/events?location=青云峰&time=morning
```

## 配置说明

### 环境变量
```bash
# DeepSeek API配置
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_MAX_TOKENS=2000

# Agent系统配置
ENABLE_NPC_AGENT=true
ENABLE_WORLD_AGENT=true
ENABLE_PLAYER_AGENT=false  # 实验性功能

# 性能配置
AGENT_RESPONSE_TIMEOUT=5000  # 毫秒
AGENT_CACHE_TTL=3600  # 秒
```

## 使用示例

### 1. 初始化Agent系统
```python
from src.agents import AgentSystem

# 创建Agent系统实例
agent_system = AgentSystem(config)

# 注册各类Agent
agent_system.register_agent('npc', NPCAgent())
agent_system.register_agent('world', WorldAgent())
```

### 2. 处理玩家输入
```python
# 玩家输入自然语言
player_input = "我想找掌门询问关于魔族入侵的事情"

# Agent系统处理
response = await agent_system.process_input(
    player_input,
    context=player_context
)

# 返回结构化响应
{
    "intent": "find_npc_and_ask",
    "parameters": {
        "npc": "掌门",
        "topic": "魔族入侵"
    },
    "actions": [
        {"type": "move", "target": "掌门大殿"},
        {"type": "dialogue", "npc": "掌门", "topic": "魔族入侵"}
    ]
}
```

## 开发路线图

### Phase 1: 基础框架（当前）
- [x] DeepSeek集成
- [x] 基础命令解析
- [ ] NPC对话原型
- [ ] 事件生成原型

### Phase 2: 核心功能
- [ ] 完整NPC对话系统
- [ ] 动态事件生成
- [ ] 玩家行为分析
- [ ] Agent间通信

### Phase 3: 高级特性
- [ ] 多Agent协作
- [ ] 个性化推荐系统
- [ ] 情感计算引擎
- [ ] 剧情生成器

### Phase 4: 优化与扩展
- [ ] 分布式Agent架构
- [ ] 实时学习与适应
- [ ] 多模态输入支持
- [ ] 跨服务器Agent同步

## 性能指标

### 目标性能
- NLP响应时间: < 500ms
- NPC对话延迟: < 1s
- 事件生成频率: 10-30秒/事件
- 内存占用: < 100MB/Agent

### 监控指标
- Agent响应时间
- API调用成功率
- 缓存命中率
- 并发处理能力

## 故障排除

### 常见问题

1. **DeepSeek API连接失败**
   - 检查API密钥配置
   - 确认网络连接
   - 查看API配额

2. **Agent响应缓慢**
   - 检查缓存配置
   - 优化上下文大小
   - 启用异步处理

3. **NPC对话不自然**
   - 调整prompt模板
   - 增加角色背景信息
   - 优化对话历史管理

## 贡献指南

欢迎贡献代码和想法！请遵循以下步骤：

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingAgent`)
3. 提交更改 (`git commit -m 'Add some AmazingAgent'`)
4. 推送到分支 (`git push origin feature/AmazingAgent`)
5. 创建Pull Request

## 相关文档

- [DeepSeek NLP集成指南](./deepseek_nlp_guide.md)
- [游戏架构文档](./architecture/game_architecture.md)
- [API文档](./api/README.md)

## 更新日志

### v0.1.0 (2025-06-30)
- 初始Agent系统框架
- DeepSeek NLP集成
- 基础命令解析功能

---

*本文档持续更新中，最后更新时间：2025-06-30*
