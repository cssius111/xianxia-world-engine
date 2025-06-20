# 事件系统架构文档

## 事件数据结构

### 基础事件格式
```json
{
  "id": "event_uuid",
  "name": "事件名称",
  "description": "事件描述文本",
  "type": "random|fixed|triggered",
  "category": "cultivation|combat|social|exploration|system",
  "effect": {
    "type": "effect_type",
    "payload": {}
  },
  "conditions": {},
  "weight": 100,
  "flags": []
}
```

## Effect 类型详解

### 1. stat_delta (属性变化)
用于修改玩家的基础属性值。

```json
{
  "type": "stat_delta",
  "payload": {
    "strength": 2,
    "agility": -1,
    "intelligence": 3,
    "vitality": 0,
    "luck": 1,
    "charm": 0,
    "physique": -2,
    "move_speed": -1,
    "cultivation_speed": 0.1
  }
}
```

支持的属性：
- `strength`: 力量
- `agility`: 敏捷
- `intelligence`: 智力
- `vitality`: 体质
- `luck`: 幸运
- `charm`: 魅力
- `physique`: 根骨
- `move_speed`: 移动速度
- `cultivation_speed`: 修炼速度倍率

### 2. boolean_flag (布尔标记)
用于设置或清除游戏标记，影响后续事件触发。

```json
{
  "type": "boolean_flag",
  "payload": {
    "action": "set|clear",
    "flags": [
      "childhood_injury",
      "blessed_by_elder",
      "marked_by_demon"
    ]
  }
}
```

标记用途：
- 触发条件检查
- 剧情分支判断
- 成就解锁依据
- NPC态度影响

### 3. item_reward (物品奖励)
给予玩家物品、装备或资源。

```json
{
  "type": "item_reward",
  "payload": {
    "items": [
      {"id": "healing_pill", "count": 3},
      {"id": "spirit_stone", "count": 10},
      {"id": "ancient_sword", "count": 1}
    ],
    "money": 100,
    "exp": 500,
    "contribution": 50
  }
}
```

## 事件触发条件

### 条件结构
```json
{
  "conditions": {
    "level_min": 10,
    "level_max": 30,
    "realm": ["炼气期", "筑基期"],
    "location": ["青云山", "坊市"],
    "time": {
      "hour_min": 6,
      "hour_max": 18,
      "day_type": ["normal", "festival"]
    },
    "flags_required": ["quest_complete_01"],
    "flags_forbidden": ["evil_cultivator"],
    "probability": 0.1
  }
}
```

## 事件分类

### 随机事件 (random)
- 修炼时的意外收获
- 路途中的偶遇
- 天气变化影响
- 灵气潮汐

### 固定事件 (fixed)
- 主线剧情节点
- 宗门定期活动
- 节日庆典
- 系统公告

### 触发事件 (triggered)
- 到达特定地点
- 完成某个任务
- 与NPC互动
- 使用特定物品

## 事件权重系统

权重计算公式：
```
final_weight = base_weight * location_modifier * time_modifier * player_modifier
```

修正因子：
- `location_modifier`: 地点相关性 (0.1 - 2.0)
- `time_modifier`: 时间相关性 (0.5 - 1.5)
- `player_modifier`: 玩家属性影响 (0.8 - 1.2)

## DeepSeek API 集成

### 请求格式
```python
{
  "context": {
    "player_state": {},
    "recent_events": [],
    "current_location": "",
    "current_time": ""
  },
  "event_type": "random",
  "category": "cultivation",
  "constraints": {
    "max_stat_change": 5,
    "item_tier_max": 3,
    "avoid_flags": []
  }
}
```

### 响应验证
生成的事件必须通过以下验证：
1. 结构完整性检查
2. Effect type 合法性
3. 数值范围限制
4. 剧情逻辑一致性

## 事件日志存储

事件执行后记录到 `GameState.event_log`：
```json
{
  "timestamp": "2024-06-13T10:30:00",
  "event_id": "event_uuid",
  "event_name": "幼年摔断腿",
  "effects_applied": {
    "stat_changes": {"physique": -2},
    "flags_set": ["childhood_injury"]
  },
  "player_level": 1,
  "location": "新手村"
}
```
