"""
API v1版本模块
"""

from .game import game_bp
from .player import player_bp
from .save import save_bp
from .system import system_bp

__all__ = ["game_bp", "player_bp", "save_bp", "system_bp"]
