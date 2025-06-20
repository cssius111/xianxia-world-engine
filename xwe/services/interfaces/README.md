# 修仙世界引擎 - 服务接口文档

## 概述

本文档定义了修仙世界引擎的所有核心服务接口。这些接口遵循依赖倒置原则（DIP），使得各个模块之间解耦，便于测试、扩展和维护。

## 接口清单

### 1. IGameService - 游戏服务接口
**位置**: `xwe/services/interfaces/game_service.py`

**主要职责**:
- 游戏生命周期管理（初始化、暂停、恢复、结束）
- 命令处理和路由
- 游戏状态查询和管理
- 事件协调和日志管理
- 存档的保存和加载

**核心方法**:
- `initialize_game()` - 初始化新游戏
- `process_command()` - 处理游戏命令
- `get_game_state()` - 获取游戏状态
- `save_game()` / `load_game()` - 存档管理

---

### 2. IPlayerService - 玩家服务接口
**位置**: `xwe/services/interfaces/player_service.py`

**主要职责**:
- 玩家创建和管理
- 属性查询和修改
- 成长系统（升级、突破）
- 技能和物品管理
- 状态效果管理
- 社交系统

**核心方法**:
- `create_player()` - 创建新玩家
- `add_experience()` - 添加经验值
- `level_up()` - 玩家升级
- `add_skill()` / `add_item()` - 技能和物品管理
- `heal()` / `damage()` - 生命值管理

---

### 3. ISaveService - 存档服务接口
**位置**: `xwe/services/interfaces/save_service.py`

**主要职责**:
- 存档的创建和保存
- 存档的加载和恢复
- 存档的管理（列表、删除、重命名）
- 自动存档和快速存档
- 存档的导入导出
- 云存档同步
- 存档完整性检查

**核心方法**:
- `create_save()` - 创建新存档
- `load_save()` - 加载存档
- `quick_save()` / `quick_load()` - 快速存档
- `sync_to_cloud()` - 云同步
- `verify_save()` - 验证存档完整性

---

### 4. IWorldService - 世界服务接口
**位置**: `xwe/services/interfaces/world_service.py`

**主要职责**:
- 地图和位置管理
- 移动和导航
- 探索系统
- 时间和天气系统
- 世界事件管理
- 资源点管理
- 区域控制

**核心方法**:
- `get_location()` - 获取位置信息
- `move_to()` - 移动到指定位置
- `explore_location()` - 探索位置
- `get_world_time()` - 获取世界时间
- `trigger_event()` - 触发世界事件

---

### 5. ICombatService - 战斗服务接口
**位置**: `xwe/services/interfaces/combat_service.py`

**主要职责**:
- 战斗流程管理
- 伤害计算和效果处理
- 技能系统
- 战斗AI
- 战斗奖励
- 战斗日志

**核心方法**:
- `start_combat()` - 开始战斗
- `execute_action()` - 执行战斗行动
- `calculate_damage()` - 计算伤害
- `get_ai_action()` - 获取AI行动
- `end_combat()` - 结束战斗

---

### 6. ICultivationService - 修炼服务接口
**位置**: `xwe/services/interfaces/cultivation_service.py`

**主要职责**:
- 修炼进度管理
- 境界突破系统
- 功法学习和修炼
- 天劫系统
- 灵根和体质管理
- 丹药炼制和使用
- 悟道和机缘

**核心方法**:
- `cultivate()` - 进行修炼
- `attempt_breakthrough()` - 尝试突破境界
- `learn_technique()` - 学习功法
- `trigger_tribulation()` - 触发天劫
- `use_cultivation_pill()` - 使用丹药

---

### 7. ICommandEngine - 命令引擎接口
**位置**: `xwe/services/command_engine.py`

**主要职责**:
- 命令解析和路由
- 命令处理器注册
- 自然语言理解
- 命令建议和补全

**核心方法**:
- `register_handler()` - 注册命令处理器
- `process_command()` - 处理命令
- `get_suggestions()` - 获取命令建议

---

### 8. IEventDispatcher - 事件分发器接口
**位置**: `xwe/services/event_dispatcher.py`

**主要职责**:
- 事件发布和订阅
- 异步事件处理
- 事件历史记录
- 事件统计分析

**核心方法**:
- `dispatch()` - 分发事件
- `subscribe()` - 订阅事件
- `get_event_history()` - 获取事件历史
- `get_statistics()` - 获取事件统计

---

### 9. ILogService - 日志服务接口
**位置**: `xwe/services/log_service.py`

**主要职责**:
- 日志记录和管理
- 日志查询和过滤
- 日志导出
- 日志统计分析

**核心方法**:
- `log()` - 记录日志
- `get_logs()` - 获取日志
- `export_logs()` - 导出日志
- `get_log_statistics()` - 获取日志统计

## 使用指南

### 1. 导入接口
```python
from xwe.services.interfaces import (
    IGameService,
    IPlayerService,
    ISaveService,
    IWorldService,
    ICombatService,
    ICultivationService,
    ICommandEngine,
    IEventDispatcher,
    ILogService
)
```

### 2. 实现服务
```python
from xwe.services import ServiceBase

class MyPlayerService(ServiceBase[IPlayerService], IPlayerService):
    """玩家服务实现"""

    def create_player(self, name: str, **attributes) -> str:
        # 实现创建玩家逻辑
        pass

    # ... 实现其他接口方法
```

### 3. 注册服务
```python
from xwe.services import ServiceContainer, ServiceLifetime

container = ServiceContainer()
container.register(IPlayerService, MyPlayerService, ServiceLifetime.SINGLETON)
```

### 4. 使用服务
```python
player_service = container.resolve(IPlayerService)
player_id = player_service.create_player("测试玩家")
```

## 设计原则

1. **接口隔离**: 每个接口专注于单一职责领域
2. **依赖倒置**: 高层模块依赖抽象接口，而非具体实现
3. **开闭原则**: 对扩展开放，对修改关闭
4. **里氏替换**: 任何实现都可以替换接口使用
5. **单一职责**: 每个服务只负责一个业务领域

## 扩展建议

1. **新增服务时**:
   - 先定义接口
   - 实现具体服务类
   - 在容器中注册
   - 编写单元测试

2. **修改接口时**:
   - 考虑向后兼容
   - 使用默认参数
   - 添加新方法而非修改旧方法
   - 更新所有实现

3. **集成第三方服务**:
   - 创建适配器实现接口
   - 保持接口稳定
   - 隔离外部依赖

## 最佳实践

1. **异常处理**: 在实现中处理异常，接口定义清晰的错误返回
2. **日志记录**: 在服务实现中记录关键操作
3. **性能优化**: 使用缓存、批处理等技术
4. **事务支持**: 需要时实现事务性操作
5. **并发安全**: 考虑多线程环境下的安全性

## 相关文档

- [服务层架构说明](../../../patches/patch-3.1-services-structure.md)
- [使用示例](usage_examples.py)
- [测试用例](../../../tests/test_services.py)

---

**版本**: 1.0.0
**最后更新**: 2025-06-11
**作者**: 修仙世界引擎开发团队
