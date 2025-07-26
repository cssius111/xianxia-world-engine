# NLP 开发指南

## 目录

- [开发环境搭建](#开发环境搭建)
- [代码规范](#代码规范)
- [核心概念](#核心概念)
- [开发流程](#开发流程)
- [测试指南](#测试指南)
- [调试技巧](#调试技巧)
- [贡献指南](#贡献指南)
- [最佳实践](#最佳实践)

## 开发环境搭建

### 1. 系统要求

- Python 3.8+
- Git
- pip 或 conda
- 推荐使用 VS Code 或 PyCharm

### 2. 克隆项目

```bash
git clone https://github.com/your-org/xianxia_world_engine.git
cd xianxia_world_engine
```

### 3. 创建虚拟环境

```bash
# 使用 venv
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 使用 conda
conda create -n xwe python=3.8
conda activate xwe
```

### 4. 安装依赖

```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt

# 安装 pre-commit hooks
pre-commit install
```

### 5. 配置开发环境

```bash
# 复制环境配置
cp .env.example .env.development

# 编辑配置
vim .env.development
```

必要的环境变量：
```bash
# DeepSeek API（使用测试密钥）
DEEPSEEK_API_KEY=test_key_for_development
# 开发时使用测试密钥

# 调试配置
NLP_DEBUG=true
LOG_LEVEL=DEBUG

# 测试配置
TEST_MODE=true
```

### 6. 验证环境

```bash
# 运行单元测试
python -m pytest tests/test_nlp_processor.py -v

# 运行类型检查
mypy src/xwe/core/nlp/

# 运行代码格式化
black src/xwe/core/nlp/
isort src/xwe/core/nlp/

# 运行代码质量检查
flake8 src/xwe/core/nlp/
```

## 代码规范

### Python 编码规范

遵循 PEP 8 标准，并使用以下工具自动化：

- **Black**: 代码格式化
- **isort**: import 排序
- **flake8**: 代码质量检查
- **mypy**: 类型检查

### 命名约定

```python
# 类名：使用 PascalCase
class NLPProcessor:
    pass

# 函数和方法：使用 snake_case
def parse_command(raw_input: str) -> ParsedCommand:
    pass

# 常量：使用大写字母和下划线
MAX_CACHE_SIZE = 1000
DEFAULT_TIMEOUT = 30

# 私有方法：使用单下划线前缀
def _internal_method(self):
    pass

# 模块级私有变量：使用单下划线前缀
_logger = logging.getLogger(__name__)
```

### 文档字符串

使用 Google 风格的文档字符串：

```python
def parse_command(self, raw_input: str, context: Optional[Dict[str, Any]] = None) -> ParsedCommand:
    """解析自然语言命令。
    
    将用户的自然语言输入转换为结构化的游戏命令。
    
    Args:
        raw_input: 用户的原始输入文本
        context: 可选的游戏上下文信息，包含当前状态、位置等
        
    Returns:
        ParsedCommand: 解析后的命令对象，包含命令类型、参数等
        
    Raises:
        NLPException: 当解析失败或 API 调用出错时
        
    Example:
        >>> nlp = NLPProcessor()
        >>> result = nlp.parse_command("攻击妖兽")
        >>> print(result.intent)
        'combat.attack'
    """
```

### 类型注解

始终使用类型注解：

```python
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass

@dataclass
class ParsedCommand:
    raw: str
    normalized_command: str
    intent: str
    args: Dict[str, Any]
    confidence: float = 1.0
    
def process_commands(
    commands: List[str],
    context: Optional[Dict[str, Any]] = None
) -> List[ParsedCommand]:
    """处理批量命令。"""
    return [parse_command(cmd, context) for cmd in commands]
```

## 核心概念

### 1. 命令解析流程

```python
# 基本流程
raw_input -> 预处理 -> LLM/规则引擎 -> 后处理 -> ParsedCommand
```

### 2. 上下文管理

```python
context = {
    "player": {
        "name": "玩家名",
        "level": 10,
        "location": "青云峰"
    },
    "scene": {
        "type": "combat",
        "enemies": ["妖兽"],
        "available_actions": ["attack", "defend", "flee"]
    },
    "history": [
        {"command": "move", "result": "success"},
        {"command": "explore", "result": "found_enemy"}
    ]
}
```

### 3. 工具系统

```python
@register_tool("custom_action")
def custom_action(payload: Dict[str, Any]) -> Dict[str, Any]:
    """自定义动作的实现。"""
    # 实现逻辑
    return {"success": True, "result": "动作执行成功"}
```

## 开发流程

### 1. 创建新功能

#### Step 1: 创建功能分支

```bash
git checkout -b feature/nlp-enhancement
```

#### Step 2: 实现功能

```python
# src/xwe/core/nlp/enhancements.py
class EnhancedNLPProcessor(DeepSeekNLPProcessor):
    """增强的 NLP 处理器。"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enhancement_enabled = True
        
    def enhance_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """增强上下文信息。"""
        # 实现增强逻辑
        return enhanced_context
```

#### Step 3: 添加测试

```python
# tests/test_nlp_enhancements.py
import pytest
from xwe.core.nlp.enhancements import EnhancedNLPProcessor

class TestEnhancedNLPProcessor:
    def test_context_enhancement(self):
        processor = EnhancedNLPProcessor()
        context = {"player": {"level": 1}}
        enhanced = processor.enhance_context(context)
        assert "enhanced_features" in enhanced
```

#### Step 4: 更新文档

```markdown
# docs/features/nlp_enhancements.md

## NLP 增强功能

### 功能描述
...

### 使用方法
...
```

### 2. 添加新的 LLM 提供商

```python
# src/xwe/core/nlp/providers/new_provider.py
from typing import Dict, Any
from ..base import BaseLLMProvider

class NewLLMProvider(BaseLLMProvider):
    """新的 LLM 提供商实现。"""
    
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.base_url = kwargs.get("base_url", "https://api.newprovider.com")
        
    async def complete(self, prompt: str, **kwargs) -> str:
        """调用 LLM API 完成文本生成。"""
        # 实现 API 调用
        response = await self._call_api(prompt, **kwargs)
        return response["text"]
        
    async def _call_api(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """内部 API 调用方法。"""
        # 实现具体的 HTTP 请求
        pass
```

### 3. 注册新工具

```python
# src/xwe/core/nlp/tools/cultivation.py
from ..tool_router import register_tool

@register_tool("advanced_cultivation")
def advanced_cultivation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """高级修炼功能。
    
    Args:
        payload: 包含修炼参数的字典
            - technique: 修炼功法
            - duration: 修炼时长
            - resources: 消耗的资源
            
    Returns:
        修炼结果
    """
    technique = payload.get("technique", "基础吐纳术")
    duration = payload.get("duration", 60)
    
    # 实现修炼逻辑
    exp_gained = calculate_exp(technique, duration)
    
    return {
        "success": True,
        "exp_gained": exp_gained,
        "message": f"修炼{technique}获得{exp_gained}经验"
    }
```

## 测试指南

### 1. 单元测试

```python
# tests/test_nlp_processor.py
import pytest
from unittest.mock import Mock, patch
from xwe.core.nlp import DeepSeekNLPProcessor

class TestNLPProcessor:
    @pytest.fixture
    def processor(self):
        """创建测试用的处理器实例。"""
        return DeepSeekNLPProcessor(api_key="test_key")
        
    def test_parse_simple_command(self, processor):
        """测试简单命令解析。"""
        result = processor.parse_command("攻击")
        assert result.intent == "combat.attack"
        assert result.normalized_command == "attack"
        
    @patch("xwe.core.nlp.llm_client.LLMClient.complete")
    def test_llm_fallback(self, mock_complete, processor):
        """测试 LLM 调用失败时的回退。"""
        mock_complete.side_effect = Exception("API Error")
        
        result = processor.parse_command("攻击妖兽")
        assert result is not None  # 应该回退到规则引擎
```

### 2. 集成测试

```python
# tests/integration/test_nlp_integration.py
import pytest
import asyncio
from xwe.core.nlp import DeepSeekNLPProcessor

class TestNLPIntegration:
    @pytest.mark.integration
    async def test_real_api_call(self):
        """测试真实的 API 调用（需要有效的 API key）。"""
        processor = DeepSeekNLPProcessor()
        
        result = await processor.parse_command_async(
            "我想去洞府修炼一会儿",
            context={"location": "青云峰"}
        )
        
        assert result.intent in ["exploration.move", "cultivation.cultivate"]
```

### 3. 性能测试

```python
# tests/performance/test_nlp_performance.py
import time
import pytest
from xwe.core.nlp import DeepSeekNLPProcessor

class TestNLPPerformance:
    @pytest.mark.benchmark
    def test_cache_performance(self, benchmark):
        """测试缓存性能。"""
        processor = DeepSeekNLPProcessor()
        
        # 预热缓存
        processor.parse_command("攻击")
        
        # 基准测试
        result = benchmark(processor.parse_command, "攻击")
        assert result is not None
        
    @pytest.mark.slow
    def test_concurrent_requests(self):
        """测试并发请求处理。"""
        processor = DeepSeekNLPProcessor()
        commands = ["攻击", "防御", "逃跑"] * 10
        
        start_time = time.time()
        results = [processor.parse_command(cmd) for cmd in commands]
        end_time = time.time()
        
        assert len(results) == 30
        assert (end_time - start_time) < 5.0  # 应该在5秒内完成
```

### 4. 测试覆盖率

```bash
# 运行测试并生成覆盖率报告
pytest --cov=xwe.core.nlp --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

## 调试技巧

### 1. 启用调试日志

```python
import logging

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("xwe.nlp")

# 在代码中添加调试信息
logger.debug(f"解析命令: {raw_input}")
logger.debug(f"上下文: {context}")
logger.debug(f"LLM 响应: {response}")
```

### 2. 使用断点调试

```python
# 使用 pdb
import pdb

def parse_command(self, raw_input: str):
    pdb.set_trace()  # 设置断点
    # 继续执行代码
    
# 使用 ipdb（增强版）
import ipdb

def complex_logic():
    ipdb.set_trace()
    # 可以使用 IPython 的功能
```

### 3. 监控工具

```python
# 实时监控
from xwe.core.nlp import get_nlp_monitor

monitor = get_nlp_monitor()
monitor.enable_debug_mode()

# 查看详细统计
stats = monitor.get_detailed_stats()
print(json.dumps(stats, indent=2))
```

### 4. 性能分析

```python
# 使用 cProfile
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# 运行要分析的代码
nlp.parse_command("复杂的命令...")

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # 打印前10个最耗时的函数
```

## 贡献指南

### 1. 代码提交流程

1. Fork 项目
2. 创建功能分支
3. 编写代码和测试
4. 确保测试通过
5. 提交 Pull Request

### 2. 提交信息格式

```
类型: 简短描述

详细说明（可选）

相关 Issue: #123
```

类型包括：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建或辅助工具的变动

### 3. Pull Request 检查清单

- [ ] 代码符合项目规范
- [ ] 添加了必要的测试
- [ ] 所有测试通过
- [ ] 更新了相关文档
- [ ] 添加了类型注解
- [ ] 运行了 pre-commit hooks

## 最佳实践

### 1. 错误处理

```python
from typing import Optional
from xwe.core.nlp.exceptions import NLPException, APIException

def safe_parse_command(self, raw_input: str) -> Optional[ParsedCommand]:
    """安全的命令解析，包含完整的错误处理。"""
    try:
        # 尝试使用 LLM
        return self._parse_with_llm(raw_input)
    except APIException as e:
        logger.warning(f"API 调用失败: {e}")
        try:
            # 回退到规则引擎
            return self._parse_with_rules(raw_input)
        except Exception as e:
            logger.error(f"规则引擎也失败: {e}")
            return None
    except Exception as e:
        logger.error(f"未预期的错误: {e}")
        return None
```

### 2. 异步编程

```python
import asyncio
from typing import List

async def batch_parse_async(
    self,
    commands: List[str],
    max_concurrent: int = 10
) -> List[ParsedCommand]:
    """批量异步解析命令。"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def parse_with_limit(cmd: str):
        async with semaphore:
            return await self.parse_command_async(cmd)
    
    tasks = [parse_with_limit(cmd) for cmd in commands]
    return await asyncio.gather(*tasks)
```

### 3. 缓存策略

```python
from functools import lru_cache
import hashlib

class SmartCache:
    """智能缓存实现。"""
    
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
        
    def get_cache_key(self, command: str, context: Dict) -> str:
        """生成缓存键。"""
        # 只使用关键上下文信息
        key_context = {
            "scene_type": context.get("scene", {}).get("type"),
            "player_location": context.get("player", {}).get("location")
        }
        
        key_str = f"{command}:{json.dumps(key_context, sort_keys=True)}"
        return hashlib.md5(key_str.encode()).hexdigest()
```

### 4. 监控和日志

```python
import time
from contextlib import contextmanager

@contextmanager
def monitor_performance(operation_name: str):
    """性能监控上下文管理器。"""
    monitor = get_nlp_monitor()
    start_time = time.time()
    
    try:
        yield
        duration = time.time() - start_time
        monitor.record_success(operation_name, duration)
    except Exception as e:
        duration = time.time() - start_time
        monitor.record_failure(operation_name, duration, str(e))
        raise

# 使用示例
with monitor_performance("parse_command"):
    result = nlp.parse_command("攻击")
```

## 开发工具推荐

### IDE 配置

#### VS Code 推荐插件
- Python
- Pylance
- Python Test Explorer
- GitLens
- Better Comments

#### PyCharm 配置
- 启用类型检查
- 配置代码风格
- 设置测试运行器

### 常用命令别名

```bash
# 添加到 .bashrc 或 .zshrc
alias nlp-test="python -m pytest tests/test_nlp_processor.py -v"
alias nlp-lint="flake8 src/xwe/core/nlp/ && mypy src/xwe/core/nlp/"
alias nlp-format="black src/xwe/core/nlp/ && isort src/xwe/core/nlp/"
alias nlp-run="python -c 'from xwe.core.nlp import DeepSeekNLPProcessor; nlp = DeepSeekNLPProcessor(); print(nlp.parse_command(input(\"命令: \")))'"
```