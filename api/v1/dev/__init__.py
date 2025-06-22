"""
开发者API模块
提供调试和测试功能
"""

"""根据当前环境决定是否导出开发蓝图"""

import os

from .dev_routes import dev_bp as _dev_bp

dev_bp = _dev_bp if os.getenv("FLASK_ENV") == "development" else None

__all__ = ["dev_bp"]
