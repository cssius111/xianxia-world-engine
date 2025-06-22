# 🔧 项目修复步骤

## 快速修复（推荐）

按以下顺序运行命令：

```bash
# 1. 清理错误的文件和目录
python cleanup.py

# 2. 运行完整修复
python complete_fix.py

# 3. 快速启动测试
python quick_start.py
```

## 修复脚本说明

### cleanup.py
- 删除错误创建的目录
- 清理项目结构

### complete_fix.py
- 清理所有Python缓存
- 创建缺失的模块
- 修复导入问题
- 运行测试验证

### quick_start.py
- 测试所有关键导入
- 如果成功，直接启动Web服务器

## 手动修复步骤

如果自动修复失败，可以手动执行：

### 1. 清理缓存
```bash
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### 2. 检查关键文件
确保以下文件存在：
- `xwe/engine/expression/exceptions.py` - 包含 ValidationError
- `xwe/features/narrative_system.py` - 包含 Achievement 等类
- `xwe/features/content_ecosystem.py`
- `xwe/features/world_building.py`
- `xwe/systems/economy.py`

### 3. 验证导入
```python
# 在Python交互环境中测试
from xwe.engine.expression.exceptions import ValidationError
from xwe.features.narrative_system import Achievement
from xwe.features.content_ecosystem import content_ecosystem
from xwe.metrics import metrics_registry
```

## 常见问题

### Q: 仍然有导入错误
A: 
1. 确保在项目根目录运行脚本
2. 清理所有缓存：`python cleanup.py`
3. 重新运行：`python complete_fix.py`

### Q: Web UI 无法启动
A:
1. 检查端口5000是否被占用
2. 确保安装了所有依赖：`pip install -r requirements.txt`
3. 查看错误日志

### Q: 找不到某个模块
A:
1. 运行 `python scripts/quick_snapshot.py` 生成错误报告
2. 查看 `project_snapshot.json` 了解具体错误
3. 手动创建缺失的文件

## 项目结构

```
xianxia_world_engine/
├── xwe/
│   ├── engine/
│   │   └── expression/
│   │       ├── __init__.py
│   │       ├── exceptions.py    # 包含 ValidationError
│   │       └── parser.py
│   ├── features/
│   │   ├── __init__.py
│   │   ├── narrative_system.py  # 包含 Achievement 等
│   │   ├── content_ecosystem.py
│   │   ├── world_building.py
│   │   └── ...
│   ├── systems/
│   │   ├── __init__.py
│   │   ├── economy.py
│   │   └── ...
│   └── metrics/
│       ├── __init__.py          # 包含 metrics_registry
│       └── prometheus/
├── entrypoints/
│   └── run_web_ui_optimized.py
├── scripts/
│   └── ...
├── cleanup.py
├── complete_fix.py
├── quick_start.py
└── ultimate_fix.py
```

## 启动游戏

修复完成后：

```bash
python entrypoints/run_web_ui_optimized.py
```

或使用快速启动：

```bash
python quick_start.py
```

然后访问：http://localhost:5000
