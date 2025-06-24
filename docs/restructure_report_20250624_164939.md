# 项目重构报告

生成时间: 2025-06-24 16:49:39
模式: 实际执行

## 重构摘要

- 总文件数: 123
- 移动文件: 122
- 需要合并: 38
- 标记废弃: 1

## 新目录结构

```
data/
├── game_configs/      # 游戏配置文件
│   ├── character/     # 角色相关
│   ├── combat/        # 战斗系统
│   ├── cultivation/   # 修炼系统
│   ├── items/         # 物品系统
│   ├── skills/        # 技能系统
│   ├── world/         # 世界设定
│   ├── npc/           # NPC配置
│   └── system/        # 系统配置
├── game_data/         # 游戏数据
│   ├── templates/     # 模板文件
│   ├── formulas/      # 公式配置
│   └── events/        # 事件配置
└── deprecated/        # 废弃文件
```

## 需要手动处理的文件合并

### 1. performance_report.json

需要合并以下文件:
- `logs/performance_report.json`
- `entrypoints/logs/performance_report.json`

建议: 手动审查这些文件的内容，合并有用的配置，删除重复的部分。

### 2. cultivation_realm.json

需要合并以下文件:
- `xwe/data/refactored/cultivation_realm.json`
- `xwe/data/restructured/cultivation_realm.json`
- `data/restructured/cultivation_realm.json`

建议: 手动审查这些文件的内容，合并有用的配置，删除重复的部分。

### 3. spiritual_root.json

需要合并以下文件:
- `xwe/data/refactored/spiritual_root.json`
- `xwe/data/attribute/spiritual_root.json`
- `xwe/data/attribute/spiritual_root_enhanced.json`
- `xwe/data/restructured/spiritual_root.json`
- `data/restructured/spiritual_root.json`

建议: 手动审查这些文件的内容，合并有用的配置，删除重复的部分。

### 4. combat_system.json

需要合并以下文件:
- `xwe/data/refactored/combat_system.json`
- `xwe/data/combat/combat_system_v2.json`
- `xwe/data/combat/combat_system.json`
- `xwe/data/combat/combat_system_optimized.json`
- `xwe/data/restructured/combat_system.json`

建议: 手动审查这些文件的内容，合并有用的配置，删除重复的部分。

### 5. event_template.json

需要合并以下文件:
- `xwe/data/refactored/event_template.json`
- `xwe/data/restructured/event_template.json`

建议: 手动审查这些文件的内容，合并有用的配置，删除重复的部分。

### 6. item_template.json

需要合并以下文件:
- `xwe/data/refactored/item_template.json`
- `xwe/data/restructured/item_template.json`
- `xwe/data/items/item_template.json`

建议: 手动审查这些文件的内容，合并有用的配置，删除重复的部分。

### 7. npc_template.json

需要合并以下文件:
- `xwe/data/character/npc_template.json`
- `xwe/data/restructured/npc_template.json`

建议: 手动审查这些文件的内容，合并有用的配置，删除重复的部分。

### 8. character_creation.json

需要合并以下文件:
- `xwe/data/character/character_creation.json`
- `xwe/data/restructured/character_creation_enhanced.json`

建议: 手动审查这些文件的内容，合并有用的配置，删除重复的部分。

### 9. local_events.json

需要合并以下文件:
- `xwe/data/restructured/local_events.json`
- `xwe/data/restructured/local_events_enhanced.json`

建议: 手动审查这些文件的内容，合并有用的配置，删除重复的部分。

### 10. achievement.json

需要合并以下文件:
- `xwe/data/restructured/achievement.json`
- `data/restructured/achievement.json`

建议: 手动审查这些文件的内容，合并有用的配置，删除重复的部分。

### 11. faction_data.json

需要合并以下文件:
- `xwe/data/restructured/faction_data.json`
- `data/restructured/faction_data.json`

建议: 手动审查这些文件的内容，合并有用的配置，删除重复的部分。

### 12. attribute_model.json

需要合并以下文件:
- `xwe/data/restructured/attribute_model.json`
- `data/restructured/attribute_model.json`

建议: 手动审查这些文件的内容，合并有用的配置，删除重复的部分。

### 13. skill_library.json

需要合并以下文件:
- `xwe/data/restructured/skill_library.json`
- `data/restructured/skill_library.json`

建议: 手动审查这些文件的内容，合并有用的配置，删除重复的部分。

### 14. mod.json

需要合并以下文件:
- `mods/template_mod/mod.json`
- `entrypoints/mods/template_mod/mod.json`

建议: 手动审查这些文件的内容，合并有用的配置，删除重复的部分。

### 15. mysterious_merchant.json

需要合并以下文件:
- `mods/template_mod/npcs/mysterious_merchant.json`
- `entrypoints/mods/template_mod/npcs/mysterious_merchant.json`

建议: 手动审查这些文件的内容，合并有用的配置，删除重复的部分。

## 后续步骤

1. **审查文件合并建议**：手动检查需要合并的文件，确保不丢失重要配置
2. **更新代码引用**：搜索并更新所有引用旧文件路径的代码
3. **清理空目录**：删除移动文件后留下的空目录
4. **建立规范**：制定文件命名和组织规范，避免未来出现类似问题
5. **版本控制**：将这次重构作为一个重要的提交节点

## 代码更新检查清单

需要检查和更新的可能位置:
- [ ] `core/data_loader.py` - 数据加载路径
- [ ] `xwe/core/data_loader.py` - XWE数据加载器
- [ ] 各个Service类中的配置文件路径
- [ ] 测试文件中的数据路径引用
- [ ] 启动脚本中的配置加载
