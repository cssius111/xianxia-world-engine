# NLP系统使用指南

## API版本说明

当前NLP API版本: 2.0

### 标准方法

```python
from xwe.core.nlp import NLPProcessor

nlp = NLPProcessor()
result = nlp.parse(user_input, context=None)
```

### 参数说明

- `user_input` (str): 用户输入的自然语言文本
- `context` (dict, optional): 游戏上下文信息，包括：
  - `location`: 当前位置
  - `in_combat`: 是否在战斗中
  - `enemies`: 敌人列表
  - `skills`: 可用技能

### 返回值

返回 `ParsedCommand` 对象，包含：
- `command_type`: 命令类型（CommandType枚举）
- `target`: 目标（如果有）
- `parameters`: 额外参数
- `confidence`: 置信度（0-1）

### 兼容性说明

⚠️ `process()` 方法已废弃，请使用 `parse()` 方法。
旧代码仍可工作，但会显示废弃警告。

### 示例

```python
# 攻击命令
result = nlp.parse("攻击那个妖兽")
# 返回: CommandType.ATTACK, target="妖兽"

# 使用技能
result = nlp.parse("用剑气斩攻击敌人")
# 返回: CommandType.USE_SKILL, parameters={"skill": "剑气斩"}

# 查看状态
result = nlp.parse("看看我的状态")
# 返回: CommandType.STATUS
```

### 降级保护

如果NLP系统出现问题，会自动降级到简单规则匹配，确保游戏不会崩溃。

### 测试

运行以下命令测试NLP功能：
```bash
python scripts/test_nlp_selfcheck.py
```
