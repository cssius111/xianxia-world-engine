"""
开局 Roll 系统模块

提供角色初始属性的随机生成功能，支持无限重骰。
"""

from .character_roller import CharacterRoller, RollResult
from .roll_data import ROLL_DATA

__all__ = ['CharacterRoller', 'RollResult', 'ROLL_DATA']
