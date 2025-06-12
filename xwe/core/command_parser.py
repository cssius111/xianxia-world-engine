# core/command_parser.py
"""
命令解析器模块

解析玩家输入的自然语言命令。
"""

import re
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CommandType(Enum):
    """命令类型"""
    # 战斗命令
    ATTACK = "attack"
    USE_SKILL = "use_skill"
    DEFEND = "defend"
    FLEE = "flee"
    
    # 移动命令
    MOVE = "move"
    EXPLORE = "explore"
    
    # 交互命令
    TALK = "talk"
    TRADE = "trade"
    PICK_UP = "pick_up"
    
    # 修炼命令
    CULTIVATE = "cultivate"
    LEARN_SKILL = "learn_skill"
    BREAKTHROUGH = "breakthrough"
    
    # 物品命令
    USE_ITEM = "use_item"
    EQUIP = "equip"
    UNEQUIP = "unequip"
    
    # 信息命令
    STATUS = "status"
    INVENTORY = "inventory"
    SKILLS = "skills"
    MAP = "map"
    
    # 系统命令
    SAVE = "save"
    LOAD = "load"
    QUIT = "quit"
    HELP = "help"
    
    # 未知命令
    UNKNOWN = "unknown"


@dataclass
class ParsedCommand:
    """解析后的命令"""
    command_type: CommandType
    target: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""
    confidence: float = 1.0
    


class CommandPattern:
    """命令模式"""
    
    def __init__(self, 
                 pattern: str,
                 command_type: CommandType,
                 extractor: Optional[Callable] = None):
        """
        初始化命令模式
        
        Args:
            pattern: 正则表达式模式
            command_type: 命令类型
            extractor: 参数提取函数
        """
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.command_type = command_type
        self.extractor = extractor or self._default_extractor
    
    def _default_extractor(self, match) -> Dict[str, Any]:
        """默认参数提取器"""
        return match.groupdict() if match else {}
    
    def match(self, text: str) -> Optional[Tuple[CommandType, Dict[str, Any]]]:
        """
        匹配文本
        
        Args:
            text: 输入文本
            
        Returns:
            (命令类型, 参数字典) or None
        """
        match = self.pattern.search(text)
        if match:
            params = self.extractor(match)
            return self.command_type, params
        return None


class CommandParser:
    """
    命令解析器
    
    将自然语言转换为游戏命令。
    """
    
    def __init__(self):
        """初始化命令解析器"""
        self.patterns: List[CommandPattern] = []
        self.aliases: Dict[str, str] = {}
        self.command_history: List[ParsedCommand] = []
        
        # 初始化命令模式
        self._init_patterns()
        self._init_aliases()
    
    def _init_patterns(self):
        """初始化命令模式"""
        # 战斗命令
        self.patterns.extend([
            # 攻击
            CommandPattern(
                r'(攻击|打|揍|击杀)\s*(?P<target>.+?)(?:\s|$)',
                CommandType.ATTACK
            ),
            CommandPattern(
                r'(attack|hit|strike)\s+(?P<target>\w+)',
                CommandType.ATTACK
            ),
            
            # 使用技能
            CommandPattern(
                r'(使用|施放|释放)\s*(?P<skill>.+?)\s*(攻击|对付|打击)?\s*(?P<target>.+?)(?:\s|$)',
                CommandType.USE_SKILL
            ),
            CommandPattern(
                r'(use|cast)\s+(?P<skill>[\w\s]+?)(?:\s+on)?\s+(?P<target>\w+)',
                CommandType.USE_SKILL
            ),
            
            # 防御
            CommandPattern(
                r'(防御|防守|格挡|闪避)',
                CommandType.DEFEND
            ),
            CommandPattern(
                r'(defend|block|dodge)',
                CommandType.DEFEND
            ),
            
            # 逃跑
            CommandPattern(
                r'(逃跑|逃走|撤退|跑路)',
                CommandType.FLEE
            ),
            CommandPattern(
                r'(flee|run|escape)',
                CommandType.FLEE
            ),
        ])
        
        # 移动命令
        self.patterns.extend([
            CommandPattern(
                r'(去|前往|移动到)\s*(?P<location>.+?)(?:\s|$)',
                CommandType.MOVE
            ),
            CommandPattern(
                r'(go|move)\s+(?:to\s+)?(?P<location>.+)',
                CommandType.MOVE
            ),
            
            CommandPattern(
                r'(探索|查看|观察)\s*(?P<target>.+?)?(?:\s|$)',
                CommandType.EXPLORE
            ),
        ])
        
        # 交互命令
        self.patterns.extend([
            CommandPattern(
                r'(和|与|跟)\s*(?P<target>.+?)\s*(说话|交谈|对话)',
                CommandType.TALK
            ),
            CommandPattern(
                r'(talk|speak)\s+(?:to\s+)?(?P<target>\w+)',
                CommandType.TALK
            ),
            
            CommandPattern(
                r'(拾取|捡起|获取)\s*(?P<item>.+?)(?:\s|$)',
                CommandType.PICK_UP
            ),
        ])
        
        # 修炼命令
        self.patterns.extend([
            CommandPattern(
                r'(修炼|打坐|练功|修行)',
                CommandType.CULTIVATE
            ),
            CommandPattern(
                r'(cultivate|meditate|practice)',
                CommandType.CULTIVATE
            ),
            
            CommandPattern(
                r'(学习|修习)\s*(?P<skill>.+?)(?:\s|$)',
                CommandType.LEARN_SKILL
            ),
            
            CommandPattern(
                r'(突破|进阶|晋级)',
                CommandType.BREAKTHROUGH
            ),
        ])
        
        # 物品命令
        self.patterns.extend([
            CommandPattern(
                r'(使用|服用|吃)\s*(?P<item>.+?)(?:\s|$)',
                CommandType.USE_ITEM
            ),
            
            CommandPattern(
                r'(装备|穿上|佩戴)\s*(?P<item>.+?)(?:\s|$)',
                CommandType.EQUIP
            ),
            
            CommandPattern(
                r'(卸下|脱下|取下)\s*(?P<item>.+?)(?:\s|$)',
                CommandType.UNEQUIP
            ),
        ])
        
        # 信息命令
        self.patterns.extend([
            CommandPattern(
                r'(状态|属性|信息|info|status)',
                CommandType.STATUS
            ),
            
            CommandPattern(
                r'(背包|物品|inventory|items)',
                CommandType.INVENTORY
            ),
            
            CommandPattern(
                r'(技能|功法|skills)',
                CommandType.SKILLS
            ),
            
            CommandPattern(
                r'(地图|位置|map|location)',
                CommandType.MAP
            ),
        ])
        
        # 系统命令
        self.patterns.extend([
            CommandPattern(
                r'(保存|存档|save)',
                CommandType.SAVE
            ),
            
            CommandPattern(
                r'(读取|载入|load)',
                CommandType.LOAD
            ),
            
            CommandPattern(
                r'(退出|离开|quit|exit)',
                CommandType.QUIT
            ),
            
            CommandPattern(
                r'(帮助|help|\?)',
                CommandType.HELP
            ),
        ])
    
    def _init_aliases(self):
        """初始化别名"""
        # 技能别名
        self.aliases.update({
            '剑气': '剑气斩',
            '火球': '火球术',
            '治疗': '治疗术',
            '疗伤': '治疗术',
        })
        
        # 物品别名
        self.aliases.update({
            '红药': '气血药水',
            '蓝药': '灵力药水',
            '血瓶': '气血药水',
            '蓝瓶': '灵力药水',
        })
        
        # 位置别名
        self.aliases.update({
            '主城': '青云城',
            '城里': '青云城',
            '野外': '城外荒野',
        })
    
    def parse(self, text: str) -> ParsedCommand:
        """
        解析命令
        
        Args:
            text: 输入文本
            
        Returns:
            解析后的命令
        """
        # 清理文本
        text = text.strip()
        if not text:
            return ParsedCommand(
                command_type=CommandType.UNKNOWN,
                raw_text=text,
                confidence=0
            )
        
        # 应用别名
        processed_text = self._apply_aliases(text)
        
        # 尝试匹配所有模式
        matches = []
        for pattern in self.patterns:
            result = pattern.match(processed_text)
            if result:
                command_type, params = result
                matches.append((command_type, params, pattern))
        
        # 选择最佳匹配
        if matches:
            # 简单地选择第一个匹配
            command_type, params, pattern = matches[0]
            
            command = ParsedCommand(
                command_type=command_type,
                parameters=params,
                raw_text=text,
                confidence=0.9
            )
            
            # 提取目标
            if 'target' in params and params['target']:
                command.target = params['target'].strip()
            
            # 记录历史
            self.command_history.append(command)
            
            logger.debug(f"解析命令: {text} -> {command_type.value} {params}")
            
            return command
        
        # 无法识别的命令
        return ParsedCommand(
            command_type=CommandType.UNKNOWN,
            raw_text=text,
            confidence=0
        )
    
    def _apply_aliases(self, text: str) -> str:
        """应用别名替换"""
        for alias, replacement in self.aliases.items():
            text = text.replace(alias, replacement)
        return text
    
    def suggest_command(self, partial_text: str) -> List[str]:
        """
        命令建议
        
        Args:
            partial_text: 部分输入
            
        Returns:
            建议列表
        """
        suggestions = []
        
        # 基础命令建议
        basic_commands = [
            "攻击", "使用", "防御", "逃跑",
            "修炼", "状态", "背包", "技能",
            "地图", "帮助"
        ]
        
        for cmd_str in basic_commands:
            if cmd_str.startswith(partial_text):
                suggestions.append(cmd_str)
        
        # 从历史中学习
        for cmd in self.command_history[-10:]:  # 最近10条
            if cmd.raw_text.startswith(partial_text):
                suggestions.append(cmd.raw_text)
        
        # 去重并限制数量
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                unique_suggestions.append(s)
                if len(unique_suggestions) >= 5:
                    break
        
        return unique_suggestions
    
    def get_help_text(self, command_type: Optional[CommandType] = None) -> str:
        """
        获取帮助文本
        
        Args:
            command_type: 特定命令类型，None表示获取所有
            
        Returns:
            帮助文本
        """
        if command_type:
            return self._get_command_help(command_type)
        
        # 返回所有命令的帮助
        help_text = "=== 游戏命令帮助 ===\n\n"
        
        categories = {
            "战斗命令": [
                ("攻击 <目标>", "对目标进行普通攻击"),
                ("使用 <技能> [目标]", "使用技能"),
                ("防御", "进入防御姿态"),
                ("逃跑", "尝试逃离战斗"),
            ],
            "探索命令": [
                ("去 <地点>", "前往指定地点"),
                ("探索", "探索当前区域"),
                ("拾取 <物品>", "拾取物品"),
            ],
            "修炼命令": [
                ("修炼", "进行修炼"),
                ("学习 <技能>", "学习新技能"),
                ("突破", "尝试境界突破"),
            ],
            "信息命令": [
                ("状态", "查看角色状态"),
                ("背包", "查看物品"),
                ("技能", "查看技能列表"),
                ("地图", "查看地图"),
            ],
            "系统命令": [
                ("保存", "保存游戏"),
                ("读取", "读取存档"),
                ("帮助", "显示帮助"),
                ("退出", "退出游戏"),
            ],
        }
        
        for category, commands in categories.items():
            help_text += f"\n【{category}】\n"
            for cmd, desc in commands:
                help_text += f"  {cmd:<20} - {desc}\n"
        
        help_text += "\n提示：<> 表示必需参数，[] 表示可选参数"
        
        return help_text
    
    def _get_command_help(self, command_type: CommandType) -> str:
        """获取特定命令的帮助"""
        help_map = {
            CommandType.ATTACK: "攻击命令：攻击 <目标>\n例如：攻击 妖兽",
            CommandType.USE_SKILL: "技能命令：使用 <技能名> [目标]\n例如：使用 剑气斩 攻击 妖兽",
            CommandType.DEFEND: "防御命令：防御\n进入防御姿态，减少受到的伤害",
            CommandType.CULTIVATE: "修炼命令：修炼\n进行打坐修炼，恢复灵力并获得修为",
            # ... 更多命令帮助
        }
        
        return help_map.get(command_type, "暂无该命令的详细帮助")
