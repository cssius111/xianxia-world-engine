# OutputManager 迁移指南

## 概述

OutputManager 是新的统一输出管理系统，提供了更强大和灵活的游戏输出功能。

## 主要改进

### 1. 多通道输出
- 支持同时输出到多个目标（控制台、文件、HTML、Web API等）
- 每个通道可以独立配置和过滤
- 易于扩展新的输出通道

### 2. 消息类型和优先级
- 明确的消息类型定义（系统、对话、战斗等）
- 优先级系统支持消息过滤
- 更好的语义化输出

### 3. 上下文感知
- 相关消息自动分组
- 战斗序列和对话交流的智能处理
- 保持输出的连贯性

### 4. 格式化支持
- 内置格式化器（表格、状态、进度条等）
- 统一的输出样式
- HTML输出的美化

### 5. 高级功能
- 批处理模式减少IO开销
- 消息历史和搜索
- 线程安全设计
- 输出缓冲管理

## 迁移步骤

### 1. 替换输出方法

旧代码：
```python
class GameCore:
    def output(self, text: str) -> None:
        self.output_buffer.append(text)
```

新代码：
```python
from xwe.core.output import OutputManager, MessageType

class GameCore:
    def __init__(self):
        self.output_manager = OutputManager()
        # 添加需要的输出通道
        self.output_manager.add_channel(ConsoleChannel())

    def output(self, text: str) -> None:
        # 保持向后兼容
        self.output_manager.system(text)
```

### 2. 使用适当的消息类型

旧代码：
```python
# 所有输出都是纯文本
self.output("你遇到了一只妖兽！")
self.output(f"{enemy.name} 发起攻击！")
self.output(f"【{npc.name}】: 你好，少侠。")
```

新代码：
```python
# 使用语义化的输出方法
self.output_manager.narrative("你遇到了一只妖兽！")
self.output_manager.combat(f"{enemy.name} 发起攻击！")
self.output_manager.dialogue(npc.name, "你好，少侠。")
```

### 3. 处理状态显示

旧代码：
```python
def _show_status(self):
    self.output("=== 角色状态 ===")
    self.output(f"姓名: {player.name}")
    self.output(f"等级: {player.level}")
    self.output(f"生命: {player.health}/{player.max_health}")
    # ... 更多状态
```

新代码：
```python
def _show_status(self):
    status_data = {
        "姓名": player.name,
        "等级": player.level,
        "生命": f"{player.health}/{player.max_health}",
        # ... 更多状态
    }
    self.output_manager.output_status(status_data, "角色状态")
```

### 4. 战斗输出优化

旧代码：
```python
def _show_combat_result(self, result):
    self.output(f"你发起了攻击！")
    self.output(f"对 {target.name} 造成了 {damage} 点伤害")
    if target.is_alive:
        self.output(f"{target.name} 剩余生命: {target.health}")
    else:
        self.output(f"{target.name} 被击败了！")
```

新代码：
```python
def _show_combat_result(self, result):
    # 使用战斗序列，相关输出会被组合
    actions = [
        "你发起了攻击！",
        f"对 {target.name} 造成了 {damage} 点伤害"
    ]

    if target.is_alive:
        actions.append(f"{target.name} 剩余生命: {target.health}")
    else:
        actions.append(f"{target.name} 被击败了！")

    self.output_manager.combat_sequence(actions)
```

### 5. 添加文件日志

新功能 - 同时记录到文件：
```python
from xwe.core.output import FileChannel

# 添加文件日志通道
log_channel = FileChannel(Path("logs/game.log"))
self.output_manager.add_channel(log_channel)

# 现在所有输出都会同时写入日志文件
```

### 6. 添加HTML输出

新功能 - 实时HTML显示：
```python
from xwe.core.output import HTMLChannel

# 添加HTML通道
html_channel = HTMLChannel(
    Path("game_output.html"),
    title="仙侠世界",
    auto_refresh=2  # 2秒自动刷新
)
self.output_manager.add_channel(html_channel)

# 更新状态显示
def update_display(self):
    status = {
        "角色": self.game_state.player.name,
        "境界": self.game_state.player.get_realm_info(),
        "位置": self.game_state.current_location,
        # ...
    }
    self.output_manager.update_status(status)
```

## 具体迁移示例

### 示例1：对话系统

旧代码：
```python
def _display_dialogue_node(self, node, npc_name: str):
    if speaker:
        self.output(f"\n{speaker}：{node.text}")
    else:
        self.output(f"\n{node.text}")

    if node.type.value == 'choice':
        self.output("\n请选择：")
        for i, choice in enumerate(choices, 1):
            self.output(f"{i}. {choice.text}")
```

新代码：
```python
def _display_dialogue_node(self, node, npc_name: str):
    # 创建对话上下文
    ctx_id = f"dialogue_{node.id}"
    self.output_manager.create_context(ctx_id, "dialogue")

    # 输出对话
    if speaker:
        self.output_manager.dialogue(speaker, node.text, context_id=ctx_id)
    else:
        self.output_manager.narrative(node.text, context_id=ctx_id)

    # 输出选项
    if node.type.value == 'choice':
        options = [choice.text for choice in choices]
        self.output_manager.menu(options, "请选择", context_id=ctx_id)

    # 结束上下文
    self.output_manager.end_context(ctx_id)
```

### 示例2：探索输出

旧代码：
```python
def _do_explore(self):
    self.output("你仔细探索周围的环境...")
    self.output("")

    if result['discovered_features']:
        self.output("你发现了一些特殊地点：")
        for feature in result['discovered_features']:
            self.output(f"- {feature}")
        self.output("")
```

新代码：
```python
def _do_explore(self):
    # 使用批处理模式优化多行输出
    self.output_manager.enable_batch_mode()

    self.output_manager.narrative("你仔细探索周围的环境...")

    if result['discovered_features']:
        self.output_manager.system("你发现了一些特殊地点：")

        # 使用表格格式化
        features_data = [
            {"发现": feature, "类型": self._get_feature_type(feature)}
            for feature in result['discovered_features']
        ]
        self.output_manager.output_table(features_data)

    # 刷新批处理
    self.output_manager.disable_batch_mode()
```

### 示例3：错误处理

旧代码：
```python
try:
    # 游戏逻辑
except Exception as e:
    self.output(f"发生错误: {e}")
    logger.error(f"游戏错误: {e}")
```

新代码：
```python
try:
    # 游戏逻辑
except Exception as e:
    # 错误会以高优先级输出到所有通道
    self.output_manager.error(f"发生错误: {e}")

    # 调试信息只在开发模式显示
    if self.game_mode == 'dev':
        import traceback
        self.output_manager.debug(traceback.format_exc())
```

## 高级用法

### 1. 自定义输出通道

创建自定义通道（例如：音频播报）：
```python
from xwe.core.output import OutputChannel, MessageType

class AudioChannel(OutputChannel):
    def __init__(self):
        super().__init__("audio")
        self.tts_engine = init_tts()  # 初始化TTS引擎

    def write(self, message: OutputMessage):
        if not self.should_output(message):
            return

        # 只播报重要消息
        if message.priority >= MessagePriority.HIGH:
            if message.type == MessageType.ACHIEVEMENT:
                self.tts_engine.speak(f"恭喜！{message.content}")
            elif message.type == MessageType.ERROR:
                self.tts_engine.speak(f"警告！{message.content}")

    def flush(self):
        self.tts_engine.flush_queue()

# 使用
audio_channel = AudioChannel()
output_manager.add_channel(audio_channel)
```

### 2. 消息过滤

按类型过滤输出：
```python
# 创建一个只记录战斗信息的日志
combat_log = FileChannel(Path("combat.log"))

# 添加过滤器
combat_log.add_filter(lambda msg: msg.type == MessageType.COMBAT)

output_manager.add_channel(combat_log)
```

### 3. 上下文关联

处理复杂的关联输出：
```python
# 任务完成的完整输出
def complete_quest(self, quest_id):
    ctx_id = f"quest_complete_{quest_id}"
    self.output_manager.create_context(ctx_id, "quest")

    # 所有相关输出都使用同一个上下文
    self.output_manager.achievement(
        f"任务完成：{quest.name}",
        context_id=ctx_id
    )

    self.output_manager.success(
        "获得奖励：",
        context_id=ctx_id
    )

    rewards_data = [
        {"物品": item, "数量": count}
        for item, count in quest.rewards.items()
    ]
    self.output_manager.output_table(
        rewards_data,
        context_id=ctx_id
    )

    self.output_manager.narrative(
        quest.completion_text,
        context_id=ctx_id
    )

    self.output_manager.end_context(ctx_id)
```

### 4. Web API 集成

用于前后端分离架构：
```python
from queue import Queue
from xwe.core.output import WebChannel

# 创建消息队列
message_queue = Queue()

# 添加Web通道
web_channel = WebChannel(message_queue)
output_manager.add_channel(web_channel)

# 在Flask路由中获取消息
@app.route('/api/messages')
def get_messages():
    messages = []
    while not message_queue.empty():
        messages.append(message_queue.get())
    return jsonify(messages)
```

## 性能优化建议

1. **使用批处理模式**
   ```python
   # 在大量输出前启用
   output_manager.enable_batch_mode(100)

   # 批量输出
   for item in large_list:
       output_manager.info(f"处理: {item}")

   # 完成后禁用
   output_manager.disable_batch_mode()
   ```

2. **合理设置缓冲大小**
   ```python
   file_channel = FileChannel(log_path)
   file_channel.buffer_size = 200  # 增加缓冲减少IO
   ```

3. **使用消息优先级**
   ```python
   # 低优先级消息可以被某些通道忽略
   output_manager.debug("详细调试信息", priority=MessagePriority.DEBUG)
   ```

## 注意事项

1. **线程安全**：OutputManager 是线程安全的，可以在多线程环境使用

2. **内存管理**：历史记录有大小限制，避免内存泄漏

3. **通道异常**：单个通道的异常不会影响其他通道

4. **编码问题**：所有文本输出使用UTF-8编码

## 总结

OutputManager 提供了更强大和灵活的输出管理功能。通过渐进式迁移，可以在保持兼容性的同时获得新功能的好处。建议先实现基本的类型化输出，然后逐步添加高级功能如多通道、格式化和上下文管理。
