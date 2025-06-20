# 事件系统架构文档 2.0

## 核心概念

事件系统是游戏的灵魂，负责创造动态、沉浸式的游戏体验。每个事件都可能改变玩家的命运轨迹。

## 事件数据结构（增强版）

### 完整事件格式
```json
{
  "id": "event_uuid",
  "name": "事件名称",
  "description": "事件描述文本（支持动态变量）",
  "type": "random|fixed|triggered|chain|conditional",
  "category": "cultivation|combat|social|exploration|system|fate",
  "rarity": "common|uncommon|rare|epic|legendary",
  "effect": {
    "type": "effect_type",
    "payload": {},
    "duration": "instant|temporary|permanent"
  },
  "conditions": {
    "pre_conditions": {},
    "trigger_conditions": {},
    "success_conditions": {}
  },
  "choices": [],
  "consequences": {},
  "weight": 100,
  "priority": 5,
  "flags": [],
  "tags": [],
  "karma_impact": 0,
  "chain_events": [],
  "achievement_unlock": null
}
```

## Effect 类型详解（扩展版）

### 1. stat_delta (属性变化)
```json
{
  "type": "stat_delta",
  "payload": {
    "attributes": {
      "strength": {"value": 2, "type": "flat|percentage", "cap": 100},
      "cultivation_speed": {"value": 0.1, "type": "percentage"}
    },
    "resources": {
      "health": {"value": -20, "max_change": 50},
      "spiritual_power": {"value": 30, "overflow": "convert_to_exp"}
    }
  },
  "duration": {
    "type": "time|turns|permanent",
    "value": 86400,
    "stack": "replace|add|max"
  }
}
```

### 2. boolean_flag (布尔标记)
```json
{
  "type": "boolean_flag",
  "payload": {
    "action": "set|clear|toggle|check",
    "flags": {
      "childhood_injury": {"value": true, "hidden": false},
      "demon_mark": {"value": true, "timer": 2592000}
    },
    "flag_groups": ["background_flags", "quest_flags"]
  }
}
```

### 3. item_reward (物品奖励)
```json
{
  "type": "item_reward",
  "payload": {
    "items": [
      {
        "id": "breakthrough_pill",
        "count": 1,
        "quality": "random|fixed",
        "bound": true
      }
    ],
    "currency": {
      "spirit_stones": 1000,
      "contribution_points": 500,
      "karma": 10
    },
    "random_pool": {
      "pool_id": "rare_treasures",
      "count": 3,
      "guarantee": "at_least_one_rare"
    }
  }
}
```

### 4. skill_grant (技能授予) - 新增
```json
{
  "type": "skill_grant",
  "payload": {
    "skills": [
      {
        "id": "heaven_splitting_sword",
        "level": 1,
        "mastery": 0,
        "locked": false
      }
    ],
    "skill_points": 5,
    "enlightenment": {
      "type": "sword_dao",
      "level": "initial"
    }
  }
}
```

### 5. relationship_change (关系变化) - 新增
```json
{
  "type": "relationship_change",
  "payload": {
    "npc_id": "elder_wang",
    "change": 20,
    "relationship_type": "respect|friendship|romance|rivalry",
    "triggers_quest": "elder_wang_secret",
    "unlocks_shop": true
  }
}
```

### 6. realm_influence (境界影响) - 新增
```json
{
  "type": "realm_influence",
  "payload": {
    "breakthrough_chance": 0.1,
    "bottleneck_reduction": 0.2,
    "tribulation_power": -0.1,
    "enlightenment_state": {
      "duration": 3600,
      "bonus": 2.0
    }
  }
}
```

### 7. karma_event (因果事件) - 新增
```json
{
  "type": "karma_event",
  "payload": {
    "karma_change": 50,
    "karma_debt": {
      "target": "npc_id",
      "amount": 100,
      "type": "life_saving|revenge|gratitude"
    },
    "future_consequence": {
      "event_id": "karma_payback",
      "delay": "random",
      "condition": "target_alive"
    }
  }
}
```

### 8. world_event (世界事件) - 新增
```json
{
  "type": "world_event",
  "payload": {
    "scope": "regional|global",
    "duration": 604800,
    "effects": {
      "spiritual_energy_density": 1.5,
      "monster_spawn_rate": 2.0,
      "rare_herb_growth": 3.0
    },
    "announcement": {
      "title": "灵气潮汐降临",
      "description": "天地异变，灵气暴涨！"
    }
  }
}
```

## 事件选择系统

### 选择结构
```json
{
  "choices": [
    {
      "id": "choice_1",
      "text": "接受挑战",
      "requirements": {
        "stats": {"courage": 10},
        "items": ["sharp_sword"],
        "skills": ["basic_swordsmanship"]
      },
      "success_rate": {
        "base": 0.6,
        "modifiers": [
          {"stat": "strength", "multiplier": 0.02},
          {"skill": "swordsmanship", "multiplier": 0.05}
        ]
      },
      "outcomes": {
        "success": {
          "effects": ["victory_rewards"],
          "next_event": "hero_reputation"
        },
        "failure": {
          "effects": ["injury", "humiliation"],
          "next_event": "recovery_needed"
        },
        "critical_success": {
          "chance": 0.1,
          "effects": ["legendary_rewards"],
          "achievement": "first_blood"
        }
      }
    }
  ]
}
```

## 高级条件系统

### 复合条件
```json
{
  "conditions": {
    "all_of": [
      {"level": {"min": 10, "max": 30}},
      {"realm": {"in": ["炼气期", "筑基期"]}},
      {"reputation": {"min": 100}}
    ],
    "any_of": [
      {"faction": "青云宗"},
      {"title": "散修"},
      {"achievement": "lone_wolf"}
    ],
    "none_of": [
      {"flag": "evil_cultivator"},
      {"karma": {"max": -100}}
    ],
    "custom_script": "check_special_condition",
    "probability": {
      "base": 0.1,
      "scaling": {
        "luck": 0.01,
        "karma": 0.001
      }
    }
  }
}
```

## 事件链系统

### 连锁事件
```json
{
  "chain_events": [
    {
      "id": "chain_start",
      "name": "神秘老者的考验",
      "branches": [
        {
          "condition": "helped_elder",
          "next": "elder_reward"
        },
        {
          "condition": "refused_help",
          "next": "karma_backlash"
        }
      ]
    },
    {
      "id": "elder_reward",
      "name": "获得传承",
      "unlocks": ["ancient_technique", "hidden_realm_map"]
    }
  ]
}
```

## 动态事件生成

### 模板系统
```json
{
  "event_templates": {
    "encounter_template": {
      "variables": {
        "enemy_type": ["bandit", "rogue_cultivator", "demon_beast"],
        "location": ["mountain_path", "dark_forest", "abandoned_temple"],
        "weather": ["foggy", "rainy", "clear"]
      },
      "description": "在{weather}的{location}，你遇到了{enemy_type}...",
      "dynamic_difficulty": {
        "base": "player_level",
        "variance": 0.2,
        "min_challenge": 0.8,
        "max_challenge": 1.5
      }
    }
  }
}
```

### AI生成规则
```json
{
  "ai_generation": {
    "constraints": {
      "power_level": "appropriate_to_player",
      "theme": "cultivation_world",
      "tone": ["serious", "mysterious", "adventurous"],
      "forbidden_elements": ["modern_technology", "fourth_wall_break"]
    },
    "quality_checks": {
      "coherence": 0.8,
      "lore_consistency": 0.9,
      "balance": 0.85
    },
    "fallback": "use_template_pool"
  }
}
```

## 事件优先级和调度

### 优先级系统
```json
{
  "priority_levels": {
    "critical": {
      "value": 10,
      "examples": ["life_death_situation", "realm_breakthrough"],
      "interrupt_current": true
    },
    "high": {
      "value": 7,
      "examples": ["faction_war", "rare_opportunity"],
      "queue_position": "front"
    },
    "normal": {
      "value": 5,
      "examples": ["random_encounter", "daily_cultivation"],
      "queue_position": "normal"
    },
    "low": {
      "value": 3,
      "examples": ["flavor_text", "minor_discovery"],
      "queue_position": "back"
    }
  }
}
```

## 事件影响力系统

### 涟漪效应
```json
{
  "ripple_effects": {
    "scope": ["personal", "local", "regional", "global"],
    "duration": "1_day|1_week|1_month|permanent",
    "affected_systems": [
      {
        "system": "economy",
        "effect": "prices_increase",
        "magnitude": 0.1
      },
      {
        "system": "faction_relations",
        "effect": "tension_increase",
        "targets": ["righteous_sects", "demonic_sects"]
      }
    ],
    "npc_reactions": {
      "merchant_guild": "opportunity",
      "common_people": "fear",
      "cultivators": "excitement"
    }
  }
}
```

## 成就和里程碑

### 事件成就
```json
{
  "achievements": {
    "first_kill": {
      "name": "初次见血",
      "description": "第一次击杀敌人",
      "rewards": {
        "title": "新手杀手",
        "karma": -10,
        "skill_points": 1
      }
    },
    "pacifist_route": {
      "name": "和平主义者",
      "description": "通过10个战斗事件而未杀一人",
      "rewards": {
        "title": "仁者无敌",
        "karma": 100,
        "special_skill": "化敌为友"
      }
    }
  }
}
```

## 事件日志增强

### 详细记录
```json
{
  "event_log_entry": {
    "timestamp": "2024-06-13T10:30:00",
    "event": {
      "id": "evt_001",
      "name": "奇遇灵泉"
    },
    "player_choice": "drink_spring_water",
    "outcome": "success",
    "changes": {
      "before": {"vitality": 10, "spiritual_power": 50},
      "after": {"vitality": 15, "spiritual_power": 80}
    },
    "unlocks": ["water_affinity"],
    "story_impact": {
      "flags_set": ["blessed_by_spring"],
      "relationship_changes": {"spring_guardian": +50}
    },
    "player_state": {
      "level": 15,
      "realm": "炼气期七层",
      "location": "云梦泽"
    }
  }
}
```

## DeepSeek API 集成增强

### 高级请求格式
```python
{
  "context": {
    "player_profile": {
      "personality": ["cunning", "ambitious"],
      "history": ["killed_bandit_leader", "saved_village"],
      "relationships": {"sect_elder": 80, "rival_disciple": -50}
    },
    "world_state": {
      "current_events": ["demon_invasion", "sect_competition"],
      "regional_mood": "tense",
      "spiritual_energy": "increasing"
    },
    "narrative_arc": {
      "current_chapter": "rise_to_power",
      "completed_arcs": ["humble_beginnings"],
      "foreshadowing": ["ancient_evil_awakening"]
    }
  },
  "requirements": {
    "event_type": "character_development",
    "tone": ["serious", "dramatic"],
    "include_elements": ["moral_choice", "power_temptation"],
    "exclude_elements": ["comedy", "modern_references"]
  },
  "generation_parameters": {
    "creativity": 0.7,
    "consistency": 0.9,
    "surprise_factor": 0.3
  }
}
```

### 智能回退机制
```python
class EventFallbackSystem:
    def __init__(self):
        self.local_events = load_json('local_events.json')
        self.event_history = []
        self.player_preferences = {}

    def get_fallback_event(self, context):
        # 1. 尝试找到最相关的本地事件
        relevant_events = self.filter_by_context(context)

        # 2. 避免重复
        fresh_events = self.remove_recent(relevant_events)

        # 3. 根据玩家偏好调整权重
        weighted_events = self.apply_preferences(fresh_events)

        # 4. 动态调整参数
        selected = self.select_and_customize(weighted_events, context)

        return selected
```

## 事件评分和反馈

### 玩家反馈系统
```json
{
  "feedback_system": {
    "rating_options": ["boring", "okay", "interesting", "amazing"],
    "feedback_impacts": {
      "boring": {
        "weight_modifier": 0.5,
        "similar_events_reduction": 0.3
      },
      "amazing": {
        "weight_modifier": 2.0,
        "unlock_similar": true,
        "developer_notification": true
      }
    },
    "learning_algorithm": {
      "track_choices": true,
      "preference_detection": true,
      "adaptive_generation": true
    }
  }
}
```

## 最佳实践

1. **事件平衡**
   - 正面/负面事件比例 6:4
   - 选择驱动 vs 随机发生 7:3
   - 短期/长期影响 5:5

2. **叙事连贯性**
   - 事件间建立联系
   - 考虑玩家历史
   - 渐进式难度曲线

3. **性能优化**
   - 事件预加载
   - 条件缓存
   - 异步处理

4. **玩家体验**
   - 明确的选择后果
   - 有意义的决策
   - 适度的随机性
