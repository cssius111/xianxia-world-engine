# test_game_state.py
"""测试 GameState 默认值"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from xwe.core.game_core import GameState


def test_game_state_default_location():
    """GameState.from_dict 默认位置应为 qingyun_city"""
    print("=== 测试 GameState 默认位置 ===")
    state = GameState.from_dict({})
    print(f"默认位置: {state.current_location}")
    assert state.current_location == "qingyun_city"
