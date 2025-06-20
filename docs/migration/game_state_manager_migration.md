# GameStateManager 迁移指南

## 概述

GameStateManager 是重构后的核心状态管理模块，提供了更强大和灵活的游戏状态管理功能。

## 主要改进

### 1. 上下文栈管理
- 支持多层上下文嵌套（探索→对话→交易）
- 自动管理游戏模式切换
- 上下文相关数据存储

### 2. 状态变化通知
- 基于事件的状态变化通知
- 支持自定义监听器
- 解耦状态管理和UI更新

### 3. 状态持久化
- 改进的存档系统
- 支持状态快照和回滚
- 自动保存功能

### 4. 更好的类型安全
- 使用枚举定义游戏上下文
- 数据类提供清晰的结构
- 完整的类型注解

## 迁移步骤

### 1. 替换 GameState 导入

旧代码：
```python
from xwe.core.game_core import GameState
```

新代码：
```python
from xwe.core.state import GameState, GameStateManager, GameContext
```

### 2. 初始化 GameStateManager

旧代码：
```python
class GameCore:
    def __init__(self):
        self.game_state = GameState()
```

新代码：
```python
class GameCore:
    def __init__(self):
        self.state_manager = GameStateManager(self.event_bus)
        self.game_state = self.state_manager.state  # 向后兼容
```

### 3. 使用上下文管理

旧代码：
```python
# 开始战斗
self.game_state.current_combat = combat_id

# 检查是否在战斗中
if self.game_state.current_combat:
    # 战斗逻辑
```

新代码：
```python
# 开始战斗
self.state_manager.start_combat(combat_id)

# 检查是否在战斗中
if self.state_manager.is_in_combat():
    # 战斗逻辑

# 或使用上下文
if self.state_manager.get_current_context() == GameContext.COMBAT:
    # 战斗逻辑
```

### 4. 管理游戏标记

旧代码：
```python
# 设置标记
self.game_state.flags['quest_completed'] = True

# 获取标记
if self.game_state.flags.get('quest_completed', False):
    # 处理
```

新代码：
```python
# 设置标记
self.state_manager.set_flag('quest_completed', True)

# 获取标记
if self.state_manager.get_flag('quest_completed', False):
    # 处理
```

### 5. 保存和加载游戏

旧代码：
```python
# 保存
save_data = {
    'game_state': self.game_state.to_dict()
}
with open(filename, 'w') as f:
    json.dump(save_data, f)

# 加载
with open(filename, 'r') as f:
    save_data = json.load(f)
self.game_state = GameState.from_dict(save_data['game_state'])
```

新代码：
```python
# 保存
self.state_manager.save_state(Path(filename))

# 加载
self.state_manager.load_state(Path(filename))
```

### 6. 使用状态监听器

新功能 - 监听状态变化：
```python
# 添加位置变化监听器
def on_location_changed(data):
    old_location = data['old']
    new_location = data['new']
    print(f"玩家从 {old_location} 移动到 {new_location}")

self.state_manager.add_listener('location_changed', on_location_changed)

# 添加战斗结束监听器
def on_combat_ended(result):
    if result['winner'] == 'player':
        print("战斗胜利！")
    else:
        print("战斗失败...")

self.state_manager.add_listener('combat_ended', on_combat_ended)
```

## 具体迁移示例

### 示例1：处理对话状态

旧代码：
```python
def _do_talk(self, target_name: str):
    # 检查是否已经在对话中
    if self.game_state.flags.get('in_dialogue', False):
        self.output("你正在与其他人对话。")
        return

    # 开始对话
    self.game_state.flags['in_dialogue'] = True
    self.game_state.flags['dialogue_npc'] = target_name

def _end_dialogue(self):
    # 清除对话状态
    if 'in_dialogue' in self.game_state.flags:
        del self.game_state.flags['in_dialogue']
    if 'dialogue_npc' in self.game_state.flags:
        del self.game_state.flags['dialogue_npc']
```

新代码：
```python
def _do_talk(self, target_name: str):
    # 检查是否已经在对话中
    if self.state_manager.is_in_context(GameContext.DIALOGUE):
        self.output("你正在与其他人对话。")
        return

    # 开始对话
    self.state_manager.push_context(GameContext.DIALOGUE, {
        'npc_id': target_name,
        'start_time': datetime.now()
    })

def _end_dialogue(self):
    # 结束对话
    if self.state_manager.get_current_context() == GameContext.DIALOGUE:
        context_data = self.state_manager.get_context_data()
        dialogue_duration = datetime.now() - context_data['start_time']

        # 可以记录对话时长等统计信息
        self.state_manager.update_statistics('dialogue_time', dialogue_duration.total_seconds())

        self.state_manager.pop_context()
```

### 示例2：管理战斗流程

旧代码：
```python
def _start_combat(self, target_name: str):
    combat_id = f"combat_{self.game_state.game_time}"
    combat_state = self.combat_system.create_combat(combat_id)

    # 设置当前战斗
    self.game_state.current_combat = combat_id

def _end_combat(self, combat_state: CombatState, fled: bool = False):
    # 清理战斗状态
    self.combat_system.end_combat(self.game_state.current_combat)
    self.game_state.current_combat = None
```

新代码：
```python
def _start_combat(self, target_name: str):
    combat_id = f"combat_{self.state_manager.state.game_time}"
    combat_state = self.combat_system.create_combat(combat_id)

    # 使用状态管理器开始战斗
    self.state_manager.start_combat(combat_id)

def _end_combat(self, combat_state: CombatState, fled: bool = False):
    result = {
        'fled': fled,
        'winner': combat_state.get_winning_team() if not fled else None,
        'duration': combat_state.round_count,
        'exp_gained': self._calculate_exp_reward(combat_state)
    }

    # 使用状态管理器结束战斗
    self.state_manager.end_combat(result)

    # 清理战斗系统
    self.combat_system.end_combat(combat_state.id)
```

### 示例3：使用快照功能

新功能 - 在关键时刻创建快照：
```python
def process_command(self, input_text: str):
    # 在处理命令前创建快照（用于撤销功能）
    if input_text.lower() not in ['undo', 'help', 'save', 'load']:
        self.state_manager.create_snapshot()

    # 处理撤销命令
    if input_text.lower() == 'undo':
        if self.state_manager.restore_snapshot():
            self.output("已撤销上一步操作。")
        else:
            self.output("无法撤销。")
        return

    # 正常处理命令...
```

## 完整迁移示例

这里是一个简化的 GameCore 类，展示如何集成 GameStateManager：

```python
from xwe.core.state import GameStateManager, GameContext

class GameCore:
    def __init__(self):
        # 初始化事件系统
        self.event_bus = EventBus()

        # 初始化状态管理器
        self.state_manager = GameStateManager(self.event_bus)

        # 向后兼容
        @property
        def game_state(self):
            return self.state_manager.state

        # 设置状态监听器
        self._setup_state_listeners()

    def _setup_state_listeners(self):
        """设置状态监听器"""
        # 监听位置变化
        self.state_manager.add_listener('location_changed', self._on_location_changed)

        # 监听战斗开始/结束
        self.state_manager.add_listener('combat_started', self._on_combat_started)
        self.state_manager.add_listener('combat_ended', self._on_combat_ended)

        # 监听成就解锁
        self.state_manager.add_listener('achievement_unlocked', self._on_achievement_unlocked)

    def _on_location_changed(self, data):
        """处理位置变化"""
        # 更新地图显示
        # 检查区域事件
        # 等等...

    def _on_combat_started(self, data):
        """处理战斗开始"""
        # 播放战斗音乐
        # 显示战斗UI
        # 等等...

    def _on_combat_ended(self, data):
        """处理战斗结束"""
        # 显示战斗结果
        # 发放奖励
        # 更新统计
        # 等等...

    def _on_achievement_unlocked(self, data):
        """处理成就解锁"""
        achievement_id = data['achievement']
        self.output(f"🎉 成就解锁：{achievement_id}")
```

## 最佳实践

1. **使用上下文而不是标记**
   - 用上下文栈管理游戏模式
   - 减少对 flags 的依赖

2. **利用状态监听器**
   - UI更新
   - 成就检查
   - 统计追踪

3. **定期创建快照**
   - 在重要操作前
   - 支持撤销功能

4. **使用自动保存**
   - 减少数据丢失
   - 提升用户体验

5. **验证状态完整性**
   - 加载存档后验证
   - 定期检查状态一致性

## 注意事项

1. GameStateManager 是线程安全的，但建议在主线程中使用
2. 监听器中的异常会被捕获并记录，不会影响主流程
3. 自动保存默认启用，间隔为5分钟
4. 状态快照数量有限制（默认10个）

## 总结

GameStateManager 提供了更强大和灵活的状态管理功能，通过渐进式迁移，可以在保持兼容性的同时获得新功能的好处。建议先迁移核心功能，然后逐步利用高级特性如状态监听器和快照功能。
