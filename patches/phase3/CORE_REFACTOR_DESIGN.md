# 第3阶段 - 核心重构设计方案

## 🎯 重构目标

将现有的过程化代码重构为清晰的分层架构，实现关注点分离和依赖倒置。

## 📐 架构设计

### 分层结构
```
┌─────────────────────────────────────┐
│         API Layer (已完成)           │
├─────────────────────────────────────┤
│         Service Layer               │  ← 第3阶段重点
├─────────────────────────────────────┤
│      Domain Model Layer            │  ← 第3阶段重点
├─────────────────────────────────────┤
│     Repository Layer               │
├─────────────────────────────────────┤
│      Data Access Layer             │
└─────────────────────────────────────┘
```

### 核心组件

#### 1. 服务层 (Service Layer)
负责业务逻辑的编排和协调：
- **GameService** - 游戏流程控制
- **PlayerService** - 玩家管理
- **CombatService** - 战斗系统
- **CultivationService** - 修炼系统
- **WorldService** - 世界管理
- **SaveService** - 存档管理

#### 2. 领域模型层 (Domain Model)
核心业务实体和值对象：
- **Player** - 玩家实体
- **Character** - 角色基类
- **Skill** - 技能实体
- **Item** - 物品实体
- **Location** - 地点实体
- **Combat** - 战斗聚合根

#### 3. 事件系统 (Event System)
基于事件的解耦通信：
- **EventBus** - 事件总线
- **DomainEvent** - 领域事件基类
- **EventHandler** - 事件处理器
- **EventStore** - 事件存储

#### 4. 依赖注入 (Dependency Injection)
服务的注册和解析：
- **ServiceContainer** - 服务容器
- **ServiceProvider** - 服务提供者
- **ServiceLifetime** - 生命周期管理

## 🏗️ 实施计划

### Phase 3.1 - 基础架构搭建
1. 创建服务基类和接口
2. 实现服务容器
3. 建立事件总线
4. 定义领域模型基类

### Phase 3.2 - 核心服务实现
1. 重构GameService
2. 重构PlayerService
3. 重构CombatService
4. 实现服务间通信

### Phase 3.3 - 数据模型优化
1. 使用dataclass定义实体
2. 实现值对象
3. 添加模型验证
4. 实现领域事件

### Phase 3.4 - 集成和迁移
1. 更新API层调用
2. 迁移现有代码
3. 保持向后兼容
4. 编写迁移文档

## 📦 代码示例

### 服务接口定义
```python
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class IGameService(ABC):
    """游戏服务接口"""
    
    @abstractmethod
    def initialize_game(self) -> None:
        """初始化游戏"""
        pass
        
    @abstractmethod
    def process_command(self, command: str) -> CommandResult:
        """处理游戏命令"""
        pass
        
    @abstractmethod
    def get_game_state(self) -> GameState:
        """获取游戏状态"""
        pass
```

### 领域模型示例
```python
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class Player:
    """玩家领域模型"""
    id: str
    name: str
    level: int = 1
    experience: int = 0
    realm: str = "炼气期"
    attributes: PlayerAttributes = field(default_factory=PlayerAttributes)
    skills: List[str] = field(default_factory=list)
    inventory: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_experience(self, amount: int) -> List[DomainEvent]:
        """添加经验值"""
        events = []
        self.experience += amount
        events.append(ExperienceGainedEvent(self.id, amount))
        
        # 检查升级
        while self.should_level_up():
            self.level_up()
            events.append(LevelUpEvent(self.id, self.level))
            
        return events
```

### 事件系统示例
```python
class EventBus:
    """事件总线"""
    
    def __init__(self):
        self._handlers = defaultdict(list)
        self._async_handlers = defaultdict(list)
        
    def subscribe(self, event_type: Type[DomainEvent], 
                  handler: EventHandler) -> None:
        """订阅事件"""
        self._handlers[event_type].append(handler)
        
    def publish(self, event: DomainEvent) -> None:
        """发布事件"""
        for handler in self._handlers[type(event)]:
            handler.handle(event)
```

### 依赖注入示例
```python
class ServiceContainer:
    """服务容器"""
    
    def __init__(self):
        self._services = {}
        self._singletons = {}
        
    def register(self, service_type: Type, 
                 implementation: Type,
                 lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT) -> None:
        """注册服务"""
        self._services[service_type] = {
            'implementation': implementation,
            'lifetime': lifetime
        }
        
    def resolve(self, service_type: Type) -> Any:
        """解析服务"""
        if service_type not in self._services:
            raise ServiceNotFoundError(f"Service {service_type} not registered")
            
        service_info = self._services[service_type]
        
        if service_info['lifetime'] == ServiceLifetime.SINGLETON:
            if service_type not in self._singletons:
                self._singletons[service_type] = self._create_instance(service_info)
            return self._singletons[service_type]
        else:
            return self._create_instance(service_info)
```

## 🔄 迁移策略

### 1. 逐步迁移
- 先创建新的服务层
- 逐个功能模块迁移
- 保持旧代码可用
- 完成后移除旧代码

### 2. 向后兼容
- API层保持不变
- 添加适配器模式
- 渐进式更新
- 提供迁移指南

### 3. 测试保障
- 单元测试先行
- 集成测试覆盖
- 性能测试对比
- 回归测试验证

## 📊 预期收益

### 代码质量
- **可维护性**: ⬆️ 80%
- **可测试性**: ⬆️ 90%
- **可扩展性**: ⬆️ 85%
- **耦合度**: ⬇️ 70%

### 开发效率
- 新功能开发时间: ⬇️ 50%
- Bug修复时间: ⬇️ 60%
- 代码理解成本: ⬇️ 70%
- 测试编写时间: ⬇️ 40%

## 🚀 快速开始

1. **安装依赖**
```bash
pip install dataclasses typing-extensions
```

2. **运行示例**
```bash
python -m xwe.services.examples
```

3. **查看文档**
- 服务层文档: `docs/services.md`
- 领域模型文档: `docs/domain.md`
- 事件系统文档: `docs/events.md`

---

第3阶段将彻底改善代码结构，为游戏的长期发展奠定坚实基础。
