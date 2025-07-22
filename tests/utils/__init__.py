"""测试工具包

提供常用的测试辅助函数和性能/内存分析工具。"""

"""测试工具包

在没有某些可选依赖（如 ``pandas`` 或 ``matplotlib``）时，导入性能或内存
分析模块可能会失败。为避免在测试收集阶段出现 ``ImportError``，这里在
导入这些模块时进行容错处理。如果依赖缺失，将提供空的占位模块，以便
其余测试仍可顺利运行。
"""

from types import ModuleType

from . import test_fixtures, test_helpers

# 尝试导入可选模块，如果依赖缺失则创建空模块
try:  # pragma: no cover - 仅在依赖存在时执行
    from . import memory_profiler  # type: ignore
except Exception:  # pragma: no cover - 忽略导入错误
    memory_profiler = ModuleType("memory_profiler")
    memory_profiler.__all__ = []

try:  # pragma: no cover
    from . import performance_profiler  # type: ignore
except Exception:  # pragma: no cover
    performance_profiler = ModuleType("performance_profiler")
    performance_profiler.__all__ = []

# 导出公共工具
from .test_fixtures import *  # noqa: F401,F403
from .test_helpers import *  # noqa: F401,F403
if memory_profiler.__all__:
    from .memory_profiler import *  # noqa: F401,F403
if performance_profiler.__all__:
    from .performance_profiler import *  # noqa: F401,F403

__all__ = (
    test_helpers.__all__
    + test_fixtures.__all__
    + performance_profiler.__all__
    + memory_profiler.__all__
)
