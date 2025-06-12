# xianxia_world_engine MyPy 错误修复指南

## 概述

项目当前有 **416 个 MyPy 类型错误**，分布在 **47 个文件**中。本指南将帮助您系统地修复这些错误。

## 快速开始

### 1. 使用自动修复脚本

```bash
# 给脚本添加执行权限
chmod +x fix_mypy_errors.sh

# 运行自动修复脚本
./fix_mypy_errors.sh

# 或使用 Python 版本
python auto_fix_mypy.py
```

### 2. 手动检查单个文件

```bash
# 检查特定文件的错误
mypy xwe/metrics/prometheus.py

# 显示错误代码
mypy xwe/metrics/prometheus.py --show-error-codes
```

## 主要错误类型和修复方法

### 1. 函数缺少返回类型注解 (`return-value`)

**错误示例：**
```
xwe/metrics/prometheus.py:201: error: No return value expected  [return-value]
```

**修复方法：**
```python
# 错误
def time_histogram(self, name: str) -> None:
    return Timer(self, name, labels)  # 实际返回了值

# 正确
def time_histogram(self, name: str) -> Timer:
    return Timer(self, name, labels)
```

### 2. Optional 类型访问错误 (`union-attr`)

**错误示例：**
```
xwe/world/location_manager.py:177: error: Item "None" of "Area | None" has no attribute "name"
```

**修复方法：**
```python
# 错误
area: Optional[Area] = get_area()
print(area.name)  # area 可能是 None

# 正确 - 方法1：添加检查
if area is not None:
    print(area.name)

# 正确 - 方法2：使用断言
assert area is not None
print(area.name)

# 正确 - 方法3：提前返回
if area is None:
    return
print(area.name)
```

### 3. 变量缺少类型注解 (`var-annotated`)

**错误示例：**
```
xwe/features/technical_ops.py:652: error: Need type annotation for "summary"
```

**修复方法：**
```python
# 错误
summary = {}

# 正确
summary: Dict[str, Any] = {}
```

### 4. 参数类型不匹配 (`arg-type`)

**错误示例：**
```
xwe/core/trade_commands.py:29: error: Argument 3 has incompatible type "dict[Any, Any] | None"; expected "dict[str, Any]"
```

**修复方法：**
```python
# 错误
properties: Optional[Dict[Any, Any]] = get_properties()
add_goods("sword", 1, properties)  # properties 可能是 None

# 正确
properties: Optional[Dict[Any, Any]] = get_properties()
if properties is not None:
    add_goods("sword", 1, properties)
# 或者提供默认值
add_goods("sword", 1, properties or {})
```

### 5. 抽象类实例化错误 (`abstract`)

**错误示例：**
```
xwe/services/game_service.py:108: error: Only concrete class can be given where "type[IGameService]" is expected
```

**修复方法：**
```python
# 错误
service = IGameService()  # IGameService 是抽象类

# 正确
service = GameServiceImpl()  # 使用具体实现类
```

### 6. 属性未定义 (`attr-defined`)

**错误示例：**
```
xwe/npc/memory_system.py:139: error: "type[MemoryType]" has no attribute "POSITIVE"
```

**修复方法：**
```python
# 检查枚举定义
class MemoryType(Enum):
    POSITIVE = "positive"  # 确保属性存在
    NEGATIVE = "negative"
```

## 分文件修复优先级

### 高优先级（核心功能）
1. `xwe/services/game_service.py` - 108 个错误
2. `xwe/core/game_core.py` - 多个错误
3. `xwe/core/combat.py` - 战斗系统

### 中优先级（重要模块）
1. `xwe/npc/memory_system.py` - NPC 系统
2. `xwe/features/content_ecosystem.py` - 内容生态
3. `xwe/metrics/prometheus.py` - 监控指标

### 低优先级（辅助功能）
1. `xwe/services/interfaces/usage_examples.py` - 示例代码
2. 测试文件

## 进阶技巧

### 1. 使用类型别名简化复杂类型

```python
from typing import Dict, List, Tuple, Optional

# 定义类型别名
PlayerData = Dict[str, Any]
ItemList = List[Tuple[str, int]]

# 使用别名
def get_player_items(player: PlayerData) -> ItemList:
    return player.get("items", [])
```

### 2. 使用 TypedDict 定义字典结构

```python
from typing import TypedDict

class PlayerStats(TypedDict):
    level: int
    hp: int
    mp: int
    exp: float

def update_stats(stats: PlayerStats) -> None:
    stats["level"] += 1  # 类型安全
```

### 3. 使用 Protocol 定义接口

```python
from typing import Protocol

class Combatant(Protocol):
    hp: int
    def attack(self, target: 'Combatant') -> int: ...
    def take_damage(self, damage: int) -> None: ...
```

### 4. 渐进式类型注解

```python
# 可以逐步添加类型注解
def complex_function(data):  # type: ignore[no-untyped-def]
    # 暂时忽略这个函数的类型检查
    pass
```

## 配置建议

更新 `mypy.ini` 以逐步启用更严格的检查：

```ini
[mypy]
python_version = 3.12
strict_optional = True
no_implicit_optional = True
ignore_missing_imports = True
check_untyped_defs = True
warn_return_any = True
warn_unused_ignores = True

# 针对特定模块的配置
[mypy-xwe.tests.*]
ignore_errors = True  # 暂时忽略测试文件

[mypy-xwe.services.interfaces.usage_examples]
ignore_errors = True  # 忽略示例代码
```

## 常用命令

```bash
# 检查整个项目
mypy xwe --config-file mypy.ini

# 只检查特定文件
mypy xwe/core/game_core.py

# 生成 HTML 报告
mypy xwe --html-report mypy-report

# 显示错误上下文
mypy xwe --show-error-context

# 生成类型存根
stubgen -p xwe -o stubs
```

## 修复进度跟踪

创建一个进度跟踪文件：

```bash
# 统计当前错误
mypy xwe --config-file mypy.ini | grep "error:" | wc -l > mypy_progress.txt

# 按文件统计错误
mypy xwe --config-file mypy.ini | grep "error:" | cut -d: -f1 | sort | uniq -c | sort -rn
```

## 注意事项

1. **备份代码**：在大规模修改前始终备份代码
2. **逐步修复**：不要试图一次修复所有错误
3. **运行测试**：每次修复后运行相关测试
4. **代码审查**：重要修改需要代码审查
5. **文档更新**：更新相关文档和类型注解

## 资源链接

- [MyPy 官方文档](https://mypy.readthedocs.io/)
- [Python 类型注解 PEP 484](https://www.python.org/dev/peps/pep-0484/)
- [类型注解最佳实践](https://github.com/python/typing/blob/master/docs/source/best_practices.rst)

祝您修复顺利！如有问题，请查阅文档或寻求团队帮助。
