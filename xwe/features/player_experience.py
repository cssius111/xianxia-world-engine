"""
玩家体验优化系统
- 智能提示
- 输入容错
- 新手引导
- 友善反馈
"""

import difflib
import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class CommandAlias:
    """命令别名"""

    primary: str  # 主命令
    aliases: List[str]  # 别名列表
    shortcuts: List[str]  # 快捷键
    description: str  # 描述


class SmartCommandProcessor:
    """智能命令处理器 - 支持模糊匹配、错别字纠正等"""

    def __init__(self) -> None:
        # 命令别名映射
        self.command_aliases = [
            CommandAlias(
                primary="攻击",
                aliases=["打", "杀", "揍", "击", "战斗", "进攻", "出手"],
                shortcuts=["a", "atk"],
                description="对目标发起攻击",
            ),
            CommandAlias(
                primary="使用",
                aliases=["用", "施展", "释放", "发动", "施放"],
                shortcuts=["u", "use"],
                description="使用技能或物品",
            ),
            CommandAlias(
                primary="移动",
                aliases=["去", "走", "前往", "到", "过去", "走到", "走去"],
                shortcuts=["g", "go", "m"],
                description="移动到指定地点",
            ),
            CommandAlias(
                primary="修炼",
                aliases=["修练", "修行", "打坐", "练功", "冥想", "闭关"],
                shortcuts=["c", "cult"],
                description="进行修炼恢复状态",
            ),
            CommandAlias(
                primary="状态",
                aliases=["属性", "信息", "查看", "我的状态", "角色信息"],
                shortcuts=["s", "stat"],
                description="查看角色状态",
            ),
            CommandAlias(
                primary="背包",
                aliases=["物品", "道具", "包裹", "储物袋", "行囊"],
                shortcuts=["b", "bag", "i"],
                description="查看背包物品",
            ),
            CommandAlias(
                primary="技能",
                aliases=["功法", "法术", "招式", "绝招", "技能列表"],
                shortcuts=["sk", "skill"],
                description="查看已学技能",
            ),
            CommandAlias(
                primary="地图",
                aliases=["位置", "在哪", "周围", "附近", "地点"],
                shortcuts=["map", "m"],
                description="查看地图和位置",
            ),
            CommandAlias(
                primary="探索",
                aliases=["搜索", "查看周围", "四处看看", "调查", "察看"],
                shortcuts=["e", "exp"],
                description="探索当前区域",
            ),
            CommandAlias(
                primary="对话",
                aliases=["说话", "交谈", "聊天", "谈话", "和", "跟"],
                shortcuts=["t", "talk"],
                description="与NPC对话",
            ),
            CommandAlias(
                primary="帮助",
                aliases=["救命", "怎么玩", "?", "？", "指令", "命令"],
                shortcuts=["h", "help"],
                description="显示帮助信息",
            ),
            CommandAlias(
                primary="退出",
                aliases=["离开", "结束", "关闭", "再见", "拜拜"],
                shortcuts=["q", "quit", "exit"],
                description="退出游戏",
            ),
        ]

        # 构建快速查找表
        self.alias_map = {}
        self.shortcut_map = {}
        for cmd_alias in self.command_aliases:
            for alias in cmd_alias.aliases:
                self.alias_map[alias] = cmd_alias.primary
            for shortcut in cmd_alias.shortcuts:
                self.shortcut_map[shortcut.lower()] = cmd_alias.primary

        # 常见错别字映射
        self.typo_corrections = {
            "工击": "攻击",
            "公击": "攻击",
            "修连": "修炼",
            "修练": "修炼",
            "背包": "背包",
            "被包": "背包",
            "地土": "地图",
            "底图": "地图",
            "技能": "技能",
            "急能": "技能",
            "击能": "技能",
            "探索": "探索",
            "探所": "探索",
            "谈所": "探索",
            "对话": "对话",
            "对画": "对话",
            "队话": "对话",
            "帮助": "帮助",
            "帮肋": "帮助",
            "邦助": "帮助",
        }

        # 所有可用的命令列表（用于模糊匹配）
        self.all_commands = []
        for cmd_alias in self.command_aliases:
            self.all_commands.append(cmd_alias.primary)
            self.all_commands.extend(cmd_alias.aliases)

    def process_input(self, raw_input: str) -> Tuple[str, float]:
        """
        处理用户输入，返回标准化的命令和置信度

        返回:
            (标准命令, 置信度0-1)
        """
        raw_input = raw_input.strip().lower()

        # 1. 检查快捷键
        if raw_input in self.shortcut_map:
            return self.shortcut_map[raw_input], 1.0

        # 2. 检查完全匹配的别名
        for word in raw_input.split():
            if word in self.alias_map:
                return self.alias_map[word], 0.95

        # 3. 检查错别字
        for typo, correct in self.typo_corrections.items():
            if typo in raw_input:
                raw_input = raw_input.replace(typo, correct)

        # 4. 模糊匹配
        best_match = None
        best_ratio = 0

        for command in self.all_commands:
            # 计算相似度
            ratio = difflib.SequenceMatcher(None, raw_input, command).ratio()

            # 如果输入包含命令关键字，提高权重
            if command in raw_input or raw_input in command:
                ratio += 0.2

            if ratio > best_ratio:
                best_ratio = ratio
                best_match = command

        # 5. 如果找到匹配的别名，转换为主命令
        if best_match and best_match in self.alias_map:
            best_match = self.alias_map[best_match]

        # 如果匹配度太低，返回原始输入
        if best_ratio < 0.4:
            return raw_input, 0.0

        return best_match or raw_input, best_ratio

    def get_suggestions(self, partial_input: str) -> List[str]:
        """获取命令建议"""
        if not partial_input:
            # 返回常用命令
            return ["状态", "地图", "探索", "修炼", "帮助"]

        partial_input = partial_input.lower()
        suggestions = []

        # 查找匹配的命令
        for cmd_alias in self.command_aliases:
            # 检查主命令
            if partial_input in cmd_alias.primary.lower():
                suggestions.append(f"{cmd_alias.primary} - {cmd_alias.description}")
            # 检查别名
            else:
                for alias in cmd_alias.aliases:
                    if partial_input in alias.lower():
                        suggestions.append(f"{alias} - {cmd_alias.description}")
                        break

        return suggestions[:5]  # 最多返回5个建议


class PlayerGuidance:
    """玩家引导系统"""

    def __init__(self) -> None:
        self.tips = {
            "welcome": [
                "提示：输入 '帮助' 可以查看所有可用命令",
                "提示：大部分命令都有简写，比如 's' 代表状态",
                "提示：不确定怎么做？试试 '探索' 看看周围环境",
            ],
            "combat": [
                "战斗提示：使用 '攻击' 进行普通攻击",
                "战斗提示：输入 '技能' 查看可用技能",
                "战斗提示：血量过低时可以 '逃跑'",
            ],
            "exploration": [
                "探索提示：使用 '地图' 查看附近可去的地方",
                "探索提示：和NPC '对话' 可能获得任务或信息",
                "探索提示：定期 '修炼' 可以恢复状态和获得经验",
            ],
            "inventory": [
                "背包提示：使用 '背包' 查看拥有的物品",
                "背包提示：某些物品可以在战斗中使用",
                "背包提示：装备更好的武器防具能提升战斗力",
            ],
            "cultivation": [
                "修炼提示：修炼可以恢复气血值和灵力值",
                "修炼提示：悟性越高，修炼效果越好",
                "修炼提示：某些地点修炼会有额外加成",
            ],
        }

        self.context_tips = {
            "low_health": "你的气血值较低，建议先修炼恢复或使用药品",
            "low_mana": "灵力不足，使用技能前请先恢复灵力",
            "new_area": "到达新区域时，记得先'探索'了解环境",
            "has_enemies": "附近有敌人，小心应对",
            "has_npcs": "这里有其他人，试着和他们'对话'",
            "night_time": "夜晚时分，某些地点可能更加危险",
            "day_time": "白天适合探索和与人交流",
        }

        # 记录已显示的提示，避免重复
        self.shown_tips = set()

    def get_contextual_tip(self, game_context: Dict[str, Any]) -> Optional[str]:
        """根据游戏上下文获取提示"""
        # 检查玩家状态
        if game_context.get("player_health_percent", 1.0) < 0.3:
            return self.context_tips["low_health"]

        if game_context.get("player_mana_percent", 1.0) < 0.2:
            return self.context_tips["low_mana"]

        # 检查环境
        if game_context.get("new_location", False):
            return self.context_tips["new_area"]

        if game_context.get("nearby_enemies", 0) > 0:
            return self.context_tips["has_enemies"]

        if game_context.get("nearby_npcs", 0) > 0:
            tip_key = "has_npcs"
            if tip_key not in self.shown_tips:
                self.shown_tips.add(tip_key)
                return self.context_tips[tip_key]

        return None

    def get_random_tip(self, category: str = "welcome") -> str:
        """获取随机提示"""
        import random

        if category in self.tips:
            return random.choice(self.tips[category])
        return random.choice(self.tips["welcome"])


class FriendlyErrorHandler:
    """友善的错误处理器"""

    def __init__(self) -> None:
        self.error_messages = {
            "unknown_command": [
                "我不太明白你的意思，要不要试试 '{suggestion}'？",
                "这个命令我还不认识呢，你是想 '{suggestion}' 吗？",
                "嗯...要不换个说法试试？比如 '{suggestion}'",
                "我猜你可能想要 '{suggestion}'，对吗？",
            ],
            "invalid_target": [
                "找不到 '{target}'，要不要用 '地图' 看看周围有什么？",
                "这里好像没有 '{target}' 呢，试试 '探索' 看看",
                "'{target}' 不在这里，可能在别的地方？",
            ],
            "not_enough_mana": [
                "灵力不足了，先 '修炼' 恢复一下吧",
                "这个技能需要更多灵力，休息一下再试试？",
                "灵力值不够了，要不要找个安静的地方打坐？",
            ],
            "not_in_combat": [
                "现在没在战斗呢，要去找点刺激吗？",
                "得先遇到敌人才能战斗哦",
                "周围很安全，暂时用不上战斗技能",
            ],
            "already_in_combat": [
                "正在战斗中！先解决眼前的敌人吧",
                "打完这场再说吧，敌人还在呢",
                "战斗还没结束，集中精神！",
            ],
        }

    def get_friendly_error(self, error_type: str, **kwargs) -> str:
        """获取友善的错误信息"""
        import random

        if error_type in self.error_messages:
            template = random.choice(self.error_messages[error_type])
            return template.format(**kwargs)

        return "出了点小问题，要不要试试别的命令？"


class InputHelper:
    """输入辅助器"""

    def __init__(self) -> None:
        self.command_processor = SmartCommandProcessor()
        self.guidance = PlayerGuidance()
        self.error_handler = FriendlyErrorHandler()

        # 命令历史
        self.command_history = []
        self.max_history = 20

    def process_player_input(self, raw_input: str, game_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理玩家输入

        返回:
            {
                "command": str,  # 标准化的命令
                "confidence": float,  # 置信度
                "suggestions": List[str],  # 建议
                "tip": str,  # 提示信息
                "original": str  # 原始输入
            }
        """
        # 保存到历史
        self.command_history.append(raw_input)
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)

        # 处理输入
        command, confidence = self.command_processor.process_input(raw_input)

        # 获取建议
        suggestions = []
        if confidence < 0.7:
            suggestions = self.command_processor.get_suggestions(raw_input)

        # 获取上下文提示
        tip = self.guidance.get_contextual_tip(game_context)

        return {
            "command": command,
            "confidence": confidence,
            "suggestions": suggestions,
            "tip": tip,
            "original": raw_input,
        }

    def get_help_text(self) -> str:
        """获取格式化的帮助文本"""
        lines = ["=== 命令帮助 ===\n"]

        for cmd_alias in self.command_processor.command_aliases:
            # 主命令
            lines.append(f"【{cmd_alias.primary}】 - {cmd_alias.description}")

            # 别名
            if cmd_alias.aliases:
                lines.append(f"  同义词：{', '.join(cmd_alias.aliases)}")

            # 快捷键
            if cmd_alias.shortcuts:
                lines.append(f"  快捷键：{', '.join(cmd_alias.shortcuts)}")

            lines.append("")

        lines.append("提示：")
        lines.append("- 大部分命令都支持模糊输入")
        lines.append("- 可以使用快捷键快速输入命令")
        lines.append("- 输入错误时会自动提供建议")

        return "\n".join(lines)


class GameTipsDisplay:
    """游戏提示显示管理"""

    def __init__(self) -> None:
        self.tip_queue = []
        self.tip_cooldown = {}  # 提示冷却时间
        self.tip_display_count = {}  # 提示显示次数

    def add_tip(self, tip: str, priority: int = 0, category: str = "general") -> None:
        """添加提示到队列"""
        import time

        # 检查冷却
        tip_key = f"{category}:{tip[:20]}"
        if tip_key in self.tip_cooldown:
            if time.time() < self.tip_cooldown[tip_key]:
                return

        # 添加到队列
        self.tip_queue.append(
            {"text": tip, "priority": priority, "category": category, "timestamp": time.time()}
        )

        # 按优先级排序
        self.tip_queue.sort(key=lambda x: x["priority"], reverse=True)

        # 限制队列长度
        if len(self.tip_queue) > 5:
            self.tip_queue = self.tip_queue[:5]

        # 设置冷却（同一提示30秒内不再显示）
        self.tip_cooldown[tip_key] = time.time() + 30

        # 记录显示次数
        self.tip_display_count[tip_key] = self.tip_display_count.get(tip_key, 0) + 1

    def get_next_tip(self) -> Optional[str]:
        """获取下一个要显示的提示"""
        if not self.tip_queue:
            return None

        tip_data = self.tip_queue.pop(0)
        return tip_data["text"]

    def format_tip_display(self, tip: str) -> str:
        """格式化提示显示"""
        # 使用特殊格式显示提示
        border = "─" * (len(tip) + 4)
        return f"\n💡 {tip}\n"


# 导出便捷接口
input_helper = InputHelper()
tips_display = GameTipsDisplay()


def enhance_player_experience(game_core) -> None:
    """增强游戏核心的玩家体验"""
    # 保存原始方法
    original_process_command = game_core.process_command
    original_output = game_core.output

    def enhanced_process_command(input_text: str) -> None:
        """增强的命令处理"""
        # 构建游戏上下文
        context = {
            "player_health_percent": 1.0,
            "player_mana_percent": 1.0,
            "new_location": False,
            "nearby_enemies": 0,
            "nearby_npcs": 0,
        }

        if game_core.game_state.player:
            player = game_core.game_state.player
            context["player_health_percent"] = (
                player.attributes.current_health / player.attributes.max_health
            )
            context["player_mana_percent"] = (
                player.attributes.current_mana / player.attributes.max_mana
            )

        # 处理输入
        processed = input_helper.process_player_input(input_text, context)

        # 如果置信度低，显示建议
        if processed["confidence"] < 0.7 and processed["suggestions"]:
            game_core.output("💭 你是想要：")
            for suggestion in processed["suggestions"]:
                game_core.output(f"  • {suggestion}")

        # 显示上下文提示
        if processed["tip"]:
            tips_display.add_tip(processed["tip"], priority=1)

        # 调用原始处理方法
        original_process_command(processed["command"])

    def enhanced_output(text: str) -> None:
        """增强的输出方法"""
        # 先输出原始内容
        original_output(text)

        # 检查是否需要显示提示
        next_tip = tips_display.get_next_tip()
        if next_tip:
            formatted_tip = tips_display.format_tip_display(next_tip)
            original_output(formatted_tip)

    # 替换方法
    game_core.process_command = enhanced_process_command
    game_core.output = enhanced_output

    # 添加帮助方法
    game_core.show_help = lambda: game_core.output(input_helper.get_help_text())

    logger.info("玩家体验增强已启用")
