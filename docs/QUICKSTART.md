# 修仙世界引擎3.0 - 快速启动指南

## 🚀 快速开始（5分钟）

### 1. 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd xianxia_world_engine

# 切换到3.0分支
git checkout feature/v3.0-refactor

# 安装依赖
pip install -r requirements-v3.txt
```

### 2. 运行数据迁移
```bash
# 备份原始数据
python scripts/backup_data.py

# 执行数据迁移
python scripts/migrate_to_v3.py

# 验证迁移结果
python scripts/validate_migration.py
```

### 3. 启动游戏
```bash
# 使用新引擎启动
python main_v3.py

# 或使用增强UI
python run_enhanced_v3.py
```

### 4. 运行测试
在开始测试前，请安装依赖：
```bash
pip install -r requirements.txt
pytest tests/ -v
```

## 📚 核心概念速览

### 表达式系统
```python
# 旧方式（文本公式）
damage = "攻击力 * 2 - 防御力"

# 新方式（表达式树）
damage = {
    "operation": "-",
    "operands": [
        {
            "operation": "*",
            "operands": [
                {"attribute": "attacker.attack_power"},
                {"constant": 2}
            ]
        },
        {"attribute": "defender.defense"}
    ]
}
```

### 事件系统
```python
# 发送事件
engine.events.emit('player_level_up', {
    'player_id': player.id,
    'new_level': player.level,
    'rewards': level_rewards
})

# 监听事件
@engine.events.register('player_level_up')
def handle_level_up(event):
    player_id = event.data['player_id']
    # 处理升级逻辑
```

### 模块系统
```python
# 创建自定义模块
class MyCustomModule(GameModule):
    def initialize(self, engine, config):
        super().initialize(engine, config)
        # 初始化逻辑

    def handle_event(self, event):
        if event.type == 'my_custom_event':
            # 处理事件
            pass

# 注册模块
engine.register_module(MyCustomModule())
```

## 🔧 开发者快速参考

### 1. 添加新的计算公式

```python
# 在配置文件中定义
{
  "formulas": {
    "healing_amount": {
      "type": "expression",
      "expression": {
        "operation": "*",
        "operands": [
          {"attribute": "caster.spell_power"},
          {"constant": 0.5},
          {
            "operation": "+",
            "operands": [
              {"constant": 1},
              {"attribute": "skill.level"}
            ]
          }
        ]
      }
    }
  }
}

# 在代码中使用
healing = engine.expressions.evaluate(
    config['formulas']['healing_amount']['expression'],
    context={
        'caster': caster.attributes,
        'skill': skill_data
    }
)
```

### 2. 创建新的游戏内容

```python
# 定义新技能
new_skill = {
    "id": "divine_sword",
    "name": "神剑术",
    "type": "active",
    "cost": {
        "mana": {
            "type": "expression",
            "expression": {
                "operation": "*",
                "operands": [
                    {"constant": 50},
                    {"attribute": "skill.level"}
                ]
            }
        }
    },
    "damage": {
        "type": "expression",
        "expression": {
            "operation": "*",
            "operands": [
                {"attribute": "caster.attack_power"},
                {"constant": 3.5},
                {"attribute": "skill.mastery"}
            ]
        }
    },
    "cooldown": 10,
    "requirements": {
        "realm": "golden_core",
        "sword_mastery": 5
    }
}

# 注册技能
engine.data.set('skills.divine_sword', new_skill)
```

### 3. 处理玩家输入

```python
# 注册命令处理器
@engine.commands.register('cultivate')
def handle_cultivate(player, args):
    # 检查是否可以修炼
    if player.is_in_combat:
        return "无法在战斗中修炼！"

    # 计算修炼收益
    exp_gain = engine.expressions.evaluate(
        config['cultivation']['exp_formula']['expression'],
        context={'player': player.attributes}
    )

    # 应用收益
    player.add_experience(exp_gain)

    # 触发事件
    engine.events.emit('cultivation_completed', {
        'player_id': player.id,
        'exp_gained': exp_gain
    })

    return f"修炼完成，获得 {exp_gain} 点经验！"
```

### 4. 自定义AI行为

```python
# 定义新的AI行为模式
class CautiousAI(AIBehavior):
    def decide_action(self, entity, combat_state):
        # 健康值低于30%时优先治疗或逃跑
        health_ratio = entity.health / entity.max_health

        if health_ratio < 0.3:
            # 检查是否有治疗技能
            heal_skills = [s for s in entity.skills if s.type == 'heal']
            if heal_skills:
                return UseSkillAction(heal_skills[0], entity)
            else:
                return FleeAction()

        # 否则正常攻击
        enemies = combat_state.get_enemies(entity)
        if enemies:
            weakest = min(enemies, key=lambda e: e.health)
            return AttackAction(weakest)

        return DefendAction()

# 注册AI行为
engine.ai.register_behavior('cautious', CautiousAI())
```

## 📋 常用配置模板

### 角色模板
```json
{
  "id": "player_template",
  "attributes": {
    "health": {"base": 100, "growth": 10},
    "mana": {"base": 50, "growth": 5},
    "attack_power": {"base": 10, "growth": 2},
    "defense": {"base": 5, "growth": 1},
    "speed": {"base": 10, "growth": 0.5}
  },
  "spiritual_root": {
    "type": "random",
    "quality_weights": {
      "heavenly": 0.01,
      "excellent": 0.09,
      "good": 0.20,
      "average": 0.40,
      "poor": 0.30
    }
  }
}
```

### 事件模板
```json
{
  "id": "mysterious_encounter",
  "name": "神秘遭遇",
  "trigger": {
    "type": "exploration",
    "probability": 0.05,
    "conditions": {
      "min_realm": "foundation_building",
      "location_type": ["mountain", "forest"]
    }
  },
  "choices": [
    {
      "text": "上前查看",
      "requirements": {"courage": 50},
      "outcomes": [
        {
          "weight": 0.7,
          "type": "treasure",
          "rewards": {"item": "random_rare"}
        },
        {
          "weight": 0.3,
          "type": "combat",
          "enemy": "mysterious_guardian"
        }
      ]
    },
    {
      "text": "谨慎观察",
      "outcomes": [
        {
          "weight": 1.0,
          "type": "information",
          "text": "你发现了一些有用的线索..."
        }
      ]
    }
  ]
}
```

## 🐛 调试技巧

### 1. 启用调试日志
```python
# 在配置中启用
{
  "debug": {
    "log_level": "DEBUG",
    "log_expressions": true,
    "log_events": true,
    "performance_profiling": true
  }
}

# 或在代码中
import logging
logging.getLogger('xwe').setLevel(logging.DEBUG)
```

### 2. 表达式调试
```python
# 测试表达式
from xwe.core.expression import ExpressionEngine

engine = ExpressionEngine()
expr = {
    "operation": "*",
    "operands": [
        {"attribute": "player.level"},
        {"constant": 10}
    ]
}

result = engine.evaluate(expr, {'player': {'level': 5}})
print(f"Result: {result}")  # Result: 50
```

### 3. 事件追踪
```python
# 监听所有事件
@engine.events.register('*')
def debug_event_logger(event):
    print(f"[EVENT] {event.type}: {event.data}")
```

## 🚀 性能优化建议

### 1. 使用缓存
```python
# 对频繁计算的表达式使用缓存
from functools import lru_cache

@lru_cache(maxsize=1000)
def calculate_damage(attacker_id, target_id, skill_id):
    # 复杂的伤害计算
    pass
```

### 2. 批量操作
```python
# 批量更新实体
entities_to_update = [e for e in entities if e.needs_update]
with engine.batch_update():
    for entity in entities_to_update:
        entity.update()
```

### 3. 异步处理
```python
# 对于非关键操作使用异步
import asyncio

async def save_game_async(save_data):
    await asyncio.to_thread(save_to_disk, save_data)
```

## 📦 部署检查清单

- [ ] 所有数据文件已迁移到v3格式
- [ ] 单元测试全部通过
- [ ] 性能测试达标（响应时间<100ms）
- [ ] 日志系统正常工作
- [ ] 备份机制已启用
- [ ] 监控告警已配置
- [ ] 文档已更新
- [ ] 团队培训已完成

## 🆘 故障排除

### 问题：表达式解析错误
```
错误: ExpressionError: Invalid operation 'unknown_op'
解决: 检查表达式中的操作符是否已在ExpressionEngine中注册
```

### 问题：事件处理器未触发
```
检查步骤:
1. 确认事件名称拼写正确
2. 检查事件是否被正确emit
3. 验证handler是否正确注册
4. 查看是否有其他handler阻止了传播
```

### 问题：数据迁移失败
```
解决方案:
1. 检查原始数据格式是否正确
2. 查看migration.log中的详细错误
3. 手动修复问题数据
4. 重新运行迁移脚本
```

## 📞 获取帮助

- **技术文档**: `docs/technical/`
- **API参考**: `docs/api/`
- **示例代码**: `examples/`
- **单元测试**: `tests/`
- **问题追踪**: GitHub Issues
- **开发讨论**: Discord #dev-channel

## 🎯 下一步

1. **探索示例项目**: 查看 `examples/` 目录中的完整示例
2. **阅读架构文档**: 深入了解系统设计理念
3. **参与开发**: 选择一个issue开始贡献代码
4. **反馈建议**: 在Discord或GitHub上分享你的想法

---

**祝你在修仙世界引擎3.0的开发中一切顺利！** 🗡️✨

如有任何问题，请随时查阅文档或联系开发团队。
