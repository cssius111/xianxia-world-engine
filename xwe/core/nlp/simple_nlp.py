#!/usr/bin/env python
"""
简单的NLP实现 - 确保基本功能可用
"""

from typing import Any, Optional

from xwe.core.command_parser import CommandType, ParsedCommand


class SimpleNLPProcessor:
    """最简单的NLP处理器实现"""

    def parse(self, text: str, context=None) -> Any:
        """简单的规则解析"""
        text_lower = text.lower()

        # 攻击相关
        if any(word in text_lower for word in ["攻击", "打", "揍", "杀"]):
            return ParsedCommand(
                command_type=CommandType.ATTACK, target="敌人", raw_text=text, confidence=0.7
            )

        # 修炼相关
        elif any(word in text_lower for word in ["修炼", "打坐", "冥想"]):
            return ParsedCommand(command_type=CommandType.CULTIVATE, raw_text=text, confidence=0.8)

        # 状态查看
        elif any(word in text_lower for word in ["状态", "属性", "面板"]):
            return ParsedCommand(command_type=CommandType.STATUS, raw_text=text, confidence=0.9)

        # 技能相关
        elif "技能" in text_lower:
            if any(word in text_lower for word in ["使用", "施放", "释放"]):
                # 提取技能名
                skill_name = self._extract_skill_name(text)
                return ParsedCommand(
                    command_type=CommandType.USE_SKILL,
                    parameters={"skill": skill_name or "未知技能"},
                    raw_text=text,
                    confidence=0.6,
                )
            else:
                return ParsedCommand(command_type=CommandType.SKILLS, raw_text=text, confidence=0.8)

        # 逃跑
        elif any(word in text_lower for word in ["逃", "跑", "撤退"]):
            return ParsedCommand(command_type=CommandType.FLEE, raw_text=text, confidence=0.7)

        # 地图
        elif any(word in text_lower for word in ["地图", "位置", "哪里"]):
            return ParsedCommand(command_type=CommandType.MAP, raw_text=text, confidence=0.8)

        # 移动
        elif any(word in text_lower for word in ["去", "前往", "走到"]):
            location = self._extract_location(text)
            return ParsedCommand(
                command_type=CommandType.MOVE,
                parameters={"location": location or "未知地点"},
                raw_text=text,
                confidence=0.6,
            )

        # 探索
        elif "探索" in text_lower:
            return ParsedCommand(command_type=CommandType.EXPLORE, raw_text=text, confidence=0.7)

        # 默认
        else:
            return ParsedCommand(command_type=CommandType.UNKNOWN, raw_text=text, confidence=0.0)

    def _extract_skill_name(self, text: str) -> Optional[str]:
        """简单的技能名提取"""
        # 这里可以添加更复杂的提取逻辑
        words = ["使用", "施放", "释放"]
        for word in words:
            if word in text:
                parts = text.split(word)
                if len(parts) > 1:
                    return parts[1].strip().split()[0]
        return None

    def _extract_location(self, text: str) -> Optional[str]:
        """简单的地点提取"""
        words = ["去", "前往", "走到"]
        for word in words:
            if word in text:
                parts = text.split(word)
                if len(parts) > 1:
                    return parts[1].strip()
        return None
