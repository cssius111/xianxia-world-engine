"""
游戏状态管理模块

负责管理游戏的所有状态，包括玩家状态、世界状态、上下文管理等。
"""

from .game_state_manager import ContextInfo, GameContext, GameState, GameStateManager

__all__ = ["GameStateManager", "GameState", "GameContext", "ContextInfo"]
