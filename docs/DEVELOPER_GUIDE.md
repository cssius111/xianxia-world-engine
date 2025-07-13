# 修仙世界引擎 开发者指南

## 快速开始

### 环境准备

1. **Python环境**
   ```bash
   python --version  # 需要 Python 3.8+
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate  # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   pre-commit install
   ```

### 开发流程

1. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **编写代码**
   - 遵循PEP 8规范
   - 添加类型注解
   - 编写文档字符串

3. **编写测试**
   ```python
   # tests/unit/test_your_module.py
   import pytest
   from xwe.your_module import YourClass
   
   class TestYourClass:
       def test_functionality(self):
           instance = YourClass()
           assert instance.method() == expected_value
   ```

4. **运行测试**
   ```bash
   pytest tests/unit/test_your_module.py -v
   ```

5. **提交代码**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   ```

## 代码规范

### Python风格指南

1. **命名规范**
   - 类名: `CamelCase`
   - 函数/方法: `snake_case`
   - 常量: `UPPER_SNAKE_CASE`
   - 私有成员: `_leading_underscore`

2. **类型注解**
   ```python
   from typing import List, Dict, Optional
   
   def process_data(items: List[Dict[str, str]]) -> Optional[str]:
       """处理数据"""
       pass
   ```

3. **文档字符串**
   ```python
   def calculate_damage(attacker: Entity, defender: Entity) -> int:
       """
       计算攻击伤害
       
       Args:
           attacker: 攻击者实体
           defender: 防御者实体
           
       Returns:
           int: 计算出的伤害值
           
       Raises:
           InvalidTargetError: 如果目标无效
       """
       pass
   ```

### 测试规范

1. **测试结构**
   - 单元测试: `tests/unit/`
   - 集成测试: `tests/integration/`
   - E2E测试: `tests/e2e/`

2. **测试命名**
   - 测试文件: `test_module_name.py`
   - 测试类: `TestClassName`
   - 测试方法: `test_specific_behavior`

3. **测试覆盖率**
   - 目标覆盖率: 80%+
   - 核心模块: 90%+

## 常见任务

### 添加新的命令

1. **定义命令处理器**
   ```python
   # src/xwe/commands/your_command.py
   from xwe.commands.base import BaseCommand
   
   class YourCommand(BaseCommand):
       def execute(self, game_state, args):
           # 实现命令逻辑
           pass
   ```

2. **注册命令**
   ```python
   # src/xwe/commands/__init__.py
   COMMAND_REGISTRY['your_command'] = YourCommand
   ```

### 添加新的事件

1. **定义事件**
   ```python
   # src/xwe/events/your_event.py
   from xwe.events.base import BaseEvent
   
   class YourEvent(BaseEvent):
       event_type = "your_event_type"
   ```

2. **触发事件**
   ```python
   event_system.emit(YourEvent(data=event_data))
   ```

### 添加新的境界

1. **更新配置**
   ```yaml
   # data/realms.yaml
   realms:
     - name: "新境界"
       level: 10
       requirements:
         cultivation_points: 10000
   ```

## 调试技巧

### 使用日志

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("调试信息: %s", variable)
logger.info("重要信息")
logger.warning("警告信息")
logger.error("错误信息", exc_info=True)
```

### 使用断点

```python
import pdb
pdb.set_trace()  # 设置断点
```

### 性能分析

```bash
python -m cProfile -o profile.stats app.py
python -m pstats profile.stats
```

## 发布流程

1. **更新版本号**
   - 修改 `__version__`
   - 更新 CHANGELOG.md

2. **运行完整测试**
   ```bash
   pytest
   ```

3. **构建发布**
   ```bash
   python setup.py sdist bdist_wheel
   ```

4. **创建标签**
   ```bash
   git tag -a v0.3.4 -m "版本 0.3.4"
   git push origin v0.3.4
   ```

## 获取帮助

- 查看项目Wiki
- 提交Issue
- 加入开发者社区

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交Pull Request
4. 等待代码审查
