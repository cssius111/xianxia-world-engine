"""
优化功能测试配置
"""

import pytest
import os
import sys
from pathlib import Path


@pytest.fixture(scope="session")
def project_root():
    """项目根目录"""
    return Path(__file__).parent.parent.parent.parent


@pytest.fixture(autouse=True)
def setup_test_env(project_root):
    """设置测试环境"""
    # 添加 src 目录到 Python 路径
    src_path = str(project_root / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
