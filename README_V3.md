# 修仙世界引擎 V3 - 数据驱动版本

## 🚀 快速开始

### 一键启动
```bash
python run_v3.py
```

### 其他选项
```bash
# 仅运行测试
python run_v3.py --test

# 运行综合示例
python run_v3.py --example

# 跳过测试直接启动
python run_v3.py --skip-tests
```

## 📋 新特性

### 1. 完全数据驱动
- 所有游戏逻辑通过JSON配置
- 无需修改代码即可调整平衡性
- 支持热加载配置

### 2. 智能公式引擎
- 安全的数学表达式解析
- 支持复杂计算公式
- 内置缓存优化性能

### 3. 增强的系统
- **修炼系统**: 境界、突破、顿悟完全配置化
- **战斗系统**: AI行为树、元素克制矩阵化
- **事件系统**: 灵活的触发条件和结果处理
- **NPC系统**: 对话树、关系系统、交易系统

## 📁 项目结构

```
xianxia_world_engine/
├── xwe/
│   ├── core/                    # 核心系统
│   │   ├── data_manager_v3.py  # 数据管理器
│   │   ├── formula_engine.py   # 公式引擎
│   │   ├── cultivation_system.py # 修炼系统
│   │   ├── combat_system_v3.py # 战斗系统
│   │   ├── event_system_v3.py  # 事件系统
│   │   └── npc_system_v3.py    # NPC系统
│   └── data/
│       └── restructured/        # 游戏配置数据
├── run_v3.py                    # 快速启动脚本
├── main_v3_data_driven.py       # 主程序
├── test_data_driven_system.py   # 测试脚本
├── example_v3_comprehensive.py  # 综合示例
└── OPTIMIZATION_SUMMARY_V3.md   # 优化总结
```

## 🔧 配置文件

所有游戏数据存储在 `xwe/data/restructured/` 目录下：

- `formula_library.json` - 所有计算公式
- `cultivation_realm.json` - 境界体系
- `combat_system.json` - 战斗规则
- `event_template.json` - 事件定义
- `npc_template.json` - NPC模板

## 📚 开发指南

### 使用数据管理器
```python
from xwe.core import load_game_data, get_config

# 加载所有数据
load_game_data()

# 获取配置
realms = get_config("cultivation_realm.realms")
```

### 使用公式引擎
```python
from xwe.core import calculate, evaluate_expression

# 使用预定义公式
damage = calculate("physical_damage", 
    attack_power=100,
    weapon_damage=50,
    skill_multiplier=1.5,
    defense=30,
    armor=20
)

# 计算自定义表达式
result = evaluate_expression("health * 0.1 + base_regen", {
    "health": 1000,
    "base_regen": 5
})
```

### 使用游戏系统
```python
from xwe.core import cultivation_system, combat_system, event_system, npc_system

# 修炼
result = cultivation_system.cultivate(player, hours=3)

# 创建战斗
combat = combat_system.create_combat("battle_1", [player, enemy])

# 触发事件
events = event_system.check_and_trigger_events(context)

# 创建NPC
npc = npc_system.create_npc("merchant_wang")
```

## 🐛 问题排查

### 数据加载失败
1. 检查 `xwe/data/restructured/` 目录是否存在
2. 确认所有JSON文件格式正确
3. 查看错误日志了解具体问题

### 公式计算错误
1. 检查公式语法是否正确
2. 确认所有变量都有提供
3. 查看 `formula_library.json` 中的公式定义

### 系统集成问题
1. 确保先调用 `load_game_data()`
2. 检查模块导入是否正确
3. 查看示例代码了解正确用法

## 📞 获取帮助

- 查看 `OPTIMIZATION_SUMMARY_V3.md` 了解详细优化内容
- 运行 `python example_v3_comprehensive.py` 查看使用示例
- 查看 `test_data_driven_system.py` 了解测试方法

## 🎉 开始你的修仙之旅！

现在你可以通过修改JSON配置文件来创造属于自己的修仙世界，无需编写任何代码！

祝你在数据驱动的修仙世界中玩得愉快！ 🗡️✨
