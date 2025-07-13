"""
版本信息
"""
__version__ = "0.3.4"
__author__ = "XianXia World Engine Team"
__email__ = "dev@xianxia-engine.com"
__license__ = "MIT"
__copyright__ = "Copyright 2025 XianXia World Engine Team"

VERSION_INFO = {
    "major": 0,
    "minor": 3,
    "patch": 4,
    "release": "stable",
    "build": "20250113"
}

def get_version_string():
    """获取完整版本字符串"""
    return f"{__version__}-{VERSION_INFO['release']}"
