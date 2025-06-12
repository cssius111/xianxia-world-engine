# MyPy 错误手动修复指南

基于你的项目实际错误，这里是具体的修复方案。

## 🔧 最常见的错误修复

### 1. **No return value expected** (prometheus.py)
```python
# 错误位置: xwe/metrics/prometheus.py:201
# 原因: 装饰器函数声明了 -> None 但有 return 语句

# 修复前:
def wrapper(*args, **kwargs) -> None:
    # ...
    return result  # 错误！

# 修复后:
def wrapper(*args, **kwargs) -> Any:  # 修改返回类型
    # ...
    return result
```

### 2. **CombatAction 参数错误**
```python
# 错误: Unexpected keyword argument "skill_id" for "CombatAction"
# 位置: xwe/core/ai.py, game_core.py 等

# 修复前:
action = CombatAction(
    action_type=ActionType.SKILL,
    skill_id=skill.id  # 错误的参数名
)

# 修复后:
action = CombatAction(
    action_type=ActionType.SKILL,
    skill=skill.id  # 正确的参数名
)
```

### 3. **ActionType 枚举值错误**
```python
# 错误: "type[ActionType]" has no attribute "SKILL"

# 查找并修复 ActionType 的定义，确保包含所需的值：
class ActionType(Enum):
    ATTACK = "attack"
    SKILL = "skill"     # 添加这个
    DEFEND = "defend"
    WAIT = "wait"       # 添加这个
```

### 4. **Union | None 属性访问**
```python
# 错误: Item "None" of "Character | None" has no attribute "id"

# 修复前:
player = self.game_state.player
player.id  # 可能是 None！

# 修复后:
player = self.game_state.player
if player is not None:
    player.id  # 安全访问
```

### 5. **抽象类实例化错误** (services/)
```python
# 错误: Only concrete class can be given where "type[IGameService]" is expected

# 修复前:
service = IGameService()  # 错误！抽象类不能实例化

# 修复后:
# 方案1: 创建具体实现
class ConcreteGameService(IGameService):
    def create_game(self, config):
        # 实现方法
        pass

service = ConcreteGameService()

# 方案2: 使用类型注解
from typing import Type
service_class: Type[IGameService] = ConcreteGameService
```

### 6. **object 类型的字典操作**
```python
# 错误: Unsupported target for indexed assignment ("object")

# 修复前:
data: object = {}
data['key'] = value  # 错误！

# 修复后:
data: Dict[str, Any] = {}
data['key'] = value  # 正确
```

## 📝 批量修复脚本

创建 `fix_common_errors.py`:

```python
#!/usr/bin/env python3
import re
from pathlib import Path

def fix_combat_action_skill_id(content: str) -> str:
    """修复 CombatAction 的 skill_id 参数"""
    return re.sub(
        r'(CombatAction\([^)]*?)skill_id=',
        r'\1skill=',
        content
    )

def fix_action_type_enums(content: str) -> str:
    """修复 ActionType 枚举引用"""
    # 这需要先确认 ActionType 的定义
    content = content.replace('ActionType.SKILL', 'CombatActionType.SKILL')
    content = content.replace('ActionType.WAIT', 'CombatActionType.WAIT')
    return content

def add_none_checks(content: str) -> str:
    """为常见的 None 检查添加保护"""
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        # 检测 player.xxx 模式
        if 'self.game_state.player.' in line and 'if' not in line:
            indent = len(line) - len(line.lstrip())
            new_lines.append(' ' * indent + 'if self.game_state.player is not None:')
            new_lines.append('    ' + line)
        else:
            new_lines.append(line)
    
    return '\n'.join(new_lines)

# 主函数
project_root = Path('/Users/chenpinle/Desktop/杂/pythonProject/xianxia_world_engine')

# 修复特定文件
files_to_fix = {
    'xwe/core/ai.py': [fix_combat_action_skill_id, fix_action_type_enums],
    'xwe/core/game_core.py': [fix_combat_action_skill_id, fix_action_type_enums, add_none_checks],
}

for file_path, fixes in files_to_fix.items():
    full_path = project_root / file_path
    if full_path.exists():
        with open(full_path, 'r') as f:
            content = f.read()
        
        for fix_func in fixes:
            content = fix_func(content)
        
        with open(full_path, 'w') as f:
            f.write(content)
        
        print(f"修复了: {file_path}")
```

## 🎯 优先修复顺序

1. **修复 ActionType 定义** (xwe/core/combat.py)
   - 确保包含 SKILL, WAIT 等枚举值
   - 或者使用正确的枚举类名 CombatActionType

2. **修复 CombatAction 调用** (多个文件)
   - 全局替换 skill_id= 为 skill=

3. **修复抽象类问题** (xwe/services/)
   - 为每个抽象接口创建具体实现类

4. **添加 None 检查** (xwe/core/game_core.py)
   - 在所有 self.game_state.player 访问前添加检查

5. **修复 prometheus.py** 
   - 将返回值的装饰器函数改为 -> Any

## 🚀 快速修复命令

```bash
# 1. 批量替换 skill_id 为 skill
find xwe -name "*.py" -exec sed -i '' 's/skill_id=/skill=/g' {} \;

# 2. 查找所有需要 None 检查的地方
grep -n "self.game_state.player\." xwe/core/game_core.py

# 3. 查找所有抽象类问题
grep -n "Only concrete class" mypy_output.txt | cut -d: -f1 | sort | uniq

# 4. 检查 ActionType 的使用
grep -r "ActionType\." xwe/ | grep -E "(SKILL|WAIT)"
```

## 💡 长期解决方案

1. **使用 Protocol 而不是抽象基类**
   ```python
   from typing import Protocol
   
   class GameServiceProtocol(Protocol):
       def create_game(self, config: Dict) -> str: ...
   ```

2. **使用 TypeGuard 进行类型缩窄**
   ```python
   from typing import TypeGuard
   
   def is_not_none(obj: Optional[T]) -> TypeGuard[T]:
       return obj is not None
   ```

3. **配置 mypy 更宽松**
   ```ini
   # mypy.ini
   [mypy]
   strict_optional = False  # 减少 None 检查
   allow_untyped_defs = True  # 允许无类型定义
   ```

---

记住：不是所有的 mypy 错误都需要立即修复。优先修复会影响运行的错误，类型注解可以逐步完善。
