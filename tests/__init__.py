"""Test suite initialization helpers."""

from xwe.utils.dotenv_helper import load_dotenv

load_dotenv()

# 确保测试环境可用 requests
from xwe.utils.requests_helper import ensure_requests

ensure_requests()

# 在测试环境中禁用交互式输入
import builtins
if not hasattr(builtins, "_orig_input"):
    builtins._orig_input = builtins.input
    builtins.input = lambda prompt=None: ""

