# Heaven Law Engine (天道法则引擎)

## 概述

天道法则引擎是修仙世界引擎中的核心系统之一，负责维护游戏世界的基本规则和秩序。它模拟了修仙世界中"天道"的概念，对违反世界法则的行为进行惩罚。

## 核心功能

### 1. 跨境界斩杀限制 (CROSS_REALM_KILL)

防止高境界修士随意斩杀低境界修士，维护世界平衡。

**触发条件：**
- 攻击者境界高于目标境界2个或以上大境界
- 例如：金丹期（3）攻击炼气期（1）会触发

**惩罚机制：**
- 境界差距2-3：中等天雷（500伤害）
- 境界差距3+：严重天雷（9999伤害）

### 2. 禁术反噬 (FORBIDDEN_ARTS)

使用禁术会引发天道反噬。

**禁术列表：**
- 血魔大法
- 噬魂术
- 九幽冥火
- 天魔解体大法

**惩罚：**
- 技能反噬伤害
- 扣除100点业力值

### 3. 境界突破天劫 (REALM_BREAKTHROUGH)

突破大境界时必须渡劫。

**需要渡劫的境界：**
- 炼气期 → 筑基期（难度1）
- 筑基期 → 金丹期（难度2）
- 金丹期 → 元婴期（难度3）
- 元婴期 → 化神期（难度5）
- 化神期 → 合体期（难度7）
- 合体期 → 大乘期（难度9）

## 使用示例

### 基础使用

```python
from src.xwe.core.heaven_law_engine import HeavenLawEngine, ActionContext

# 创建引擎
heaven_law = HeavenLawEngine()

# 创建行动上下文
ctx = ActionContext()

# 执行法则检查
heaven_law.enforce(attacker, defender, ctx)

# 检查是否被阻止
if ctx.cancelled:
    print(f"行动被阻止：{ctx.reason}")
    # 处理触发的事件
    for event in ctx.events:
        result = event.apply()
        print(result)
```

### 在战斗系统中使用

```python
def attack(self, attacker, defender):
    # 创建行动上下文
    ctx = ActionContext()
    
    # 天道审判
    if self.heaven_law_engine:
        self.heaven_law_engine.enforce(attacker, defender, ctx)
        if ctx.cancelled:
            # 处理天雷劫
            result = CombatResult(False, ctx.reason)
            for event in ctx.events:
                if hasattr(event, 'apply'):
                    event_msg = event.apply()
                    result.message += "\n" + event_msg
            return result
    
    # 继续正常攻击流程...
```

## 配置文件

修改 `data/world_laws.json` 来调整法则参数：

```json
{
  "laws": [
    {
      "code": "CROSS_REALM_KILL",
      "enabled": true,
      "params": {
        "max_gap": 2,          // 最大允许境界差
        "severity_threshold": 3 // 严重惩罚的境界差
      }
    }
  ]
}
```

## 事件类型

### ThunderTribulation (天雷劫)

```python
tribulation = ThunderTribulation(character, severity="severe")
result = tribulation.apply()
```

**严重程度：**
- `minor`: 轻微（100伤害）
- `moderate`: 中等（500伤害）
- `severe`: 严重（9999伤害）
- `fatal`: 致命（99999伤害）

**效果：**
- 造成相应伤害（最少保留1点生命）
- 添加"焦痕"状态效果
- 返回描述文本

## 扩展开发

### 添加新法则

1. 在 `world_laws.json` 中添加新法则配置
2. 在 `HeavenLawEngine` 中实现检查逻辑
3. 创建相应的事件类

示例：
```python
def check_treasure_theft(self, actor, target, item, ctx):
    """检查盗取至宝"""
    law = self.laws.get("TREASURE_THEFT")
    if not (law and law.enabled):
        return
    
    if item.rarity >= law.params.get("min_rarity", "legendary"):
        ctx.cancelled = True
        ctx.reason = "此宝有主，强取必遭天谴！"
        ctx.events.append(KarmaEvent(actor, -1000))
```

### 自定义事件

```python
class KarmaEvent(Event):
    def __init__(self, actor, karma_change):
        super().__init__("KarmaEvent")
        self.actor = actor
        self.karma_change = karma_change
    
    def apply(self):
        self.actor.karma += self.karma_change
        if self.karma_change < 0:
            return f"{self.actor.name}因恶行损失{-self.karma_change}点功德！"
        else:
            return f"{self.actor.name}因善行获得{self.karma_change}点功德！"
```

## 注意事项

1. **性能考虑**：每次攻击都会触发法则检查，注意优化
2. **平衡性**：合理设置境界差距阈值，避免游戏体验受损
3. **扩展性**：预留接口以便添加更多法则类型
4. **本地化**：所有提示文本支持多语言

## 调试技巧

启用日志查看详细信息：
```python
import logging
logging.getLogger("HeavenLawEngine").setLevel(logging.DEBUG)
```

## 相关系统

- **Combat System**: 战斗系统集成点
- **Cultivation System**: 境界突破系统
- **Karma System**: 业力系统（开发中）
- **Event System**: 事件处理系统
