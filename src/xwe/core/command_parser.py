"""
命令解析器
解析玩家输入的命令
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class CommandType(Enum):
    """命令类型"""
    # 基础命令
    STATUS = "status"
    INVENTORY = "inventory"
    SKILLS = "skills"
    MAP = "map"
    HELP = "help"
    SAVE = "save"
    QUIT = "quit"
    
    # 移动命令
    MOVE = "move"
    EXPLORE = "explore"
    RETURN = "return"
    
    # 战斗命令
    ATTACK = "attack"
    USE_SKILL = "use_skill"
    DEFEND = "defend"
    FLEE = "flee"
    
    # 社交命令
    TALK = "talk"
    TRADE = "trade"
    GIVE = "give"
    
    # 修炼命令
    CULTIVATE = "cultivate"
    BREAKTHROUGH = "breakthrough"
    LEARN = "learn"
    
    # 其他
    USE_ITEM = "use_item"
    EQUIP = "equip"
    UNEQUIP = "unequip"
    UNKNOWN = "unknown"


@dataclass
class ParsedCommand:
    """解析后的命令"""
    raw_text: str
    command_type: CommandType
    target: Optional[str] = None
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class CommandParser:
    """
    命令解析器
    
    将玩家输入的文本解析为结构化命令
    """
    
    def __init__(self):
        # 初始化同义词表
        self._init_synonyms()
        # 命令别名映射
        self.command_aliases = {
            # 状态
            "状态": CommandType.STATUS,
            "state": CommandType.STATUS,
            "info": CommandType.STATUS,
            "查看状态": CommandType.STATUS,
            "角色信息": CommandType.STATUS,
            
            # 背包
            "背包": CommandType.INVENTORY,
            "inventory": CommandType.INVENTORY,
            "bag": CommandType.INVENTORY,
            "物品": CommandType.INVENTORY,
            "查看背包": CommandType.INVENTORY,
            
            # 技能
            "技能": CommandType.SKILLS,
            "skills": CommandType.SKILLS,
            "skill": CommandType.SKILLS,
            "功法": CommandType.SKILLS,
            "查看技能": CommandType.SKILLS,
            
            # 地图
            "地图": CommandType.MAP,
            "map": CommandType.MAP,
            "位置": CommandType.MAP,
            "查看地图": CommandType.MAP,
            
            # 帮助
            "帮助": CommandType.HELP,
            "help": CommandType.HELP,
            "?": CommandType.HELP,
            "指令": CommandType.HELP,
            
            # 保存
            "保存": CommandType.SAVE,
            "save": CommandType.SAVE,
            "存档": CommandType.SAVE,
            
            # 退出
            "退出": CommandType.QUIT,
            "quit": CommandType.QUIT,
            "exit": CommandType.QUIT,
            "离开": CommandType.QUIT,
            
            # 移动
            "移动": CommandType.MOVE,
            "move": CommandType.MOVE,
            "go": CommandType.MOVE,
            "去": CommandType.MOVE,
            "前往": CommandType.MOVE,
            
            # 探索
            "探索": CommandType.EXPLORE,
            "explore": CommandType.EXPLORE,
            "search": CommandType.EXPLORE,
            "搜索": CommandType.EXPLORE,
            "查看周围": CommandType.EXPLORE,
            "四处游玩": CommandType.EXPLORE,
            "四处闲逛": CommandType.EXPLORE,
            "随便走走": CommandType.EXPLORE,
            "逛逛": CommandType.EXPLORE,
            "转转": CommandType.EXPLORE,
            
            # 攻击
            "攻击": CommandType.ATTACK,
            "attack": CommandType.ATTACK,
            "hit": CommandType.ATTACK,
            "打": CommandType.ATTACK,
            "揍": CommandType.ATTACK,
            
            # 防御
            "防御": CommandType.DEFEND,
            "defend": CommandType.DEFEND,
            "block": CommandType.DEFEND,
            "防守": CommandType.DEFEND,
            "格挡": CommandType.DEFEND,
            
            # 逃跑
            "逃跑": CommandType.FLEE,
            "flee": CommandType.FLEE,
            "run": CommandType.FLEE,
            "逃": CommandType.FLEE,
            "跑": CommandType.FLEE,
            
            # 对话
            "对话": CommandType.TALK,
            "talk": CommandType.TALK,
            "speak": CommandType.TALK,
            "说话": CommandType.TALK,
            "交谈": CommandType.TALK,
            
            # 交易
            "交易": CommandType.TRADE,
            "trade": CommandType.TRADE,
            "shop": CommandType.TRADE,
            "购买": CommandType.TRADE,
            "商店": CommandType.TRADE,
            
            # 修炼
            "修炼": CommandType.CULTIVATE,
            "cultivate": CommandType.CULTIVATE,
            "meditate": CommandType.CULTIVATE,
            "打坐": CommandType.CULTIVATE,
            "练功": CommandType.CULTIVATE,
            
            # 突破
            "突破": CommandType.BREAKTHROUGH,
            "breakthrough": CommandType.BREAKTHROUGH,
            "advance": CommandType.BREAKTHROUGH,
            "进阶": CommandType.BREAKTHROUGH,
        }
        
        # 带参数的命令模式
        self.command_patterns = [
            # 移动到某地
            (r"^(?:去|前往|移动到?)\s*(.+)$", CommandType.MOVE, "location"),
            (r"^move\s+(?:to\s+)?(.+)$", CommandType.MOVE, "location"),
            
            # 攻击目标
            (r"^(?:攻击|打|揍)\s*(.+)$", CommandType.ATTACK, "target"),
            (r"^attack\s+(.+)$", CommandType.ATTACK, "target"),
            
            # 使用技能
            (r"^(?:使用|释放|施展)\s*(.+?)(?:\s*技能)?$", CommandType.USE_SKILL, "skill"),
            (r"^(?:use|cast)\s+(.+)$", CommandType.USE_SKILL, "skill"),
            
            # 与NPC对话
            (r"^(?:和|与|跟)?\s*(.+?)\s*(?:对话|说话|交谈)$", CommandType.TALK, "target"),
            (r"^talk\s+(?:to\s+|with\s+)?(.+)$", CommandType.TALK, "target"),
            
            # 使用物品
            (r"^使用\s*(.+)$", CommandType.USE_ITEM, "item"),
            (r"^use\s+item\s+(.+)$", CommandType.USE_ITEM, "item"),
            
            # 装备物品
            (r"^装备\s*(.+)$", CommandType.EQUIP, "item"),
            (r"^equip\s+(.+)$", CommandType.EQUIP, "item"),
            
            # 赠送物品
            (r"^(?:给|赠送)\s*(.+?)\s*(?:给|到)\s*(.+)$", CommandType.GIVE, ["item", "target"]),
            (r"^give\s+(.+?)\s+to\s+(.+)$", CommandType.GIVE, ["item", "target"]),
        ]
        
    def _init_synonyms(self):
        """初始化同义词表"""
        self.synonyms = {
            "探索": ["探索", "四处游玩", "四处闲逛", "随便走走", "逛逛", "转转", "游玩", "闲逛"],
            "修炼": ["修炼", "打坐", "闭关", "炼功", "修行", "练功"],
            "攻击": ["攻击", "打", "揍", "击打", "出手", "动手"],
            "对话": ["对话", "交谈", "说话", "聊天", "沟通", "聊"],
            "移动": ["移动", "去", "前往", "走", "过去", "进入"],
            "查看": ["查看", "看", "检查", "观察", "察看"],
        }
        
    def normalize_command(self, text: str) -> str:
        """
        归一化命令文本
        
        Args:
            text: 原始命令文本
            
        Returns:
            归一化后的命令
        """
        text = text.strip().lower()
        
        # 查找同义词
        for key, synonyms in self.synonyms.items():
            for synonym in synonyms:
                if synonym in text:
                    # 替换为标准命令
                    text = text.replace(synonym, key)
                    break
                    
        return text
        
    def parse(self, text: str) -> ParsedCommand:
        """
        解析命令文本
        
        Args:
            text: 原始命令文本
            
        Returns:
            解析后的命令对象
        """
        # 清理输入
        text = text.strip().lower()
        
        # 归一化命令
        normalized_text = self.normalize_command(text)
        
        if not text:
            return ParsedCommand(text, CommandType.UNKNOWN)
            
        # 尝试直接匹配命令别名
        for alias, cmd_type in self.command_aliases.items():
            if normalized_text == alias:
                return ParsedCommand(text, cmd_type)
                
        # 尝试匹配带参数的命令模式
        for pattern, cmd_type, param_names in self.command_patterns:
            match = re.match(pattern, normalized_text, re.IGNORECASE)
            if match:
                params = {}
                
                if isinstance(param_names, str):
                    # 单个参数
                    params[param_names] = match.group(1).strip()
                    target = params.get("target") or params.get(param_names)
                else:
                    # 多个参数
                    for i, param_name in enumerate(param_names):
                        params[param_name] = match.group(i + 1).strip()
                    target = params.get("target")
                    
                return ParsedCommand(text, cmd_type, target, params)
                
        # 尝试模糊匹配
        words = text.split()
        if words:
            first_word = words[0]
            
            # 检查第一个词是否是命令
            for alias, cmd_type in self.command_aliases.items():
                if first_word == alias or first_word in alias:
                    # 剩余部分作为参数
                    target = " ".join(words[1:]) if len(words) > 1 else None
                    return ParsedCommand(text, cmd_type, target)
                    
        # 无法识别
        logger.debug(f"无法解析命令: {text}")
        return ParsedCommand(text, CommandType.UNKNOWN)
        
    def get_help_text(self) -> str:
        """获取帮助文本"""
        help_text = """
=== 游戏命令帮助 ===

【基础命令】
状态 - 查看角色状态
背包 - 查看物品栏
技能 - 查看已学技能
地图 - 查看当前地图
帮助 - 显示此帮助
保存 - 保存游戏进度
退出 - 退出游戏

【移动命令】
移动 [地点] - 前往指定地点
探索 - 探索当前区域
返回 - 返回上一个地点

【战斗命令】
攻击 [目标] - 攻击指定目标
使用 [技能] - 使用技能
防御 - 进入防御姿态
逃跑 - 尝试逃离战斗

【社交命令】
对话 [NPC] - 与NPC交谈
交易 - 打开交易界面
赠送 [物品] [NPC] - 赠送物品

【修炼命令】
修炼 - 进行修炼
突破 - 尝试境界突破
学习 [技能] - 学习新技能

【其他命令】
使用 [物品] - 使用物品
装备 [装备] - 装备物品
卸下 [装备] - 卸下装备

提示：命令不区分大小写，可以使用中文或英文
"""
        return help_text
        
    def get_command_suggestions(self, partial: str) -> List[str]:
        """
        获取命令建议
        
        Args:
            partial: 部分输入的命令
            
        Returns:
            可能的命令列表
        """
        suggestions = []
        partial_lower = partial.lower()
        
        # 从别名中查找
        for alias in self.command_aliases.keys():
            if alias.startswith(partial_lower):
                suggestions.append(alias)
                
        # 限制建议数量
        return suggestions[:10]
