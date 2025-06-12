# command_router.py
"""
智能指令优先级处理系统
确保核心命令精确匹配，只有无法匹配时才使用NLP
"""

import re
from typing import Dict, Callable, Any, Optional, Tuple, List
from dataclasses import dataclass, field
from enum import Enum


class CommandPriority(Enum):
    """命令优先级枚举"""
    SYSTEM = 1      # 系统命令（最高优先级）
    CORE = 2        # 核心游戏命令
    CONTEXT = 3     # 上下文相关命令
    FUZZY = 4       # 模糊匹配命令
    NLP = 5         # NLP处理（最低优先级）

@dataclass
class CommandDefinition:
    """命令定义"""
    patterns: List[str]      # 匹配模式列表
    handler: Callable       # 处理函数
    priority: CommandPriority  # 优先级
    description: str        # 命令描述
    context_required: Optional[str] = None  # 所需上下文
    aliases: List[str] = field(default_factory=list)  # 别名列表

class CommandRouter:
    def __init__(self):
        self.abbreviations = {}  # 一定要第一行
        self.commands = self._init_commands()
        self.current_context = 'exploration'  # 当前上下文
        self.nlp_handler = None  # NLP处理器
        self.command_history = []  # 命令历史
        
    def _init_commands(self) -> Dict[str, CommandDefinition]:
        """初始化所有命令定义"""
        commands = {
            # 系统命令（最高优先级，必须精确匹配）
            'help': CommandDefinition(
                patterns=['帮助', 'help', '?'],
                handler=lambda cmd: ('help', {}),
                priority=CommandPriority.SYSTEM,
                description='显示帮助信息'
            ),
            'quit': CommandDefinition(
                patterns=['退出', 'quit', 'exit', '退出游戏'],
                handler=lambda cmd: ('quit', {}),
                priority=CommandPriority.SYSTEM,
                description='退出游戏'
            ),
            'save': CommandDefinition(
                patterns=['保存', 'save', '存档'],
                handler=lambda cmd: ('save', {}),
                priority=CommandPriority.SYSTEM,
                description='保存游戏进度'
            ),
            'load': CommandDefinition(
                patterns=['读档', 'load', '载入'],
                handler=lambda cmd: ('load', {}),
                priority=CommandPriority.SYSTEM,
                description='载入游戏进度'
            ),
            
            # 核心游戏命令
            'status': CommandDefinition(
                patterns=['状态', 'status', '查看状态', '属性', '查看属性'],
                handler=lambda cmd: ('status', {}),
                priority=CommandPriority.CORE,
                description='查看角色状态',
                aliases=['stat', 's']
            ),
            'inventory': CommandDefinition(
                patterns=['背包', 'inventory', '物品', '查看背包'],
                handler=lambda cmd: ('inventory', {}),
                priority=CommandPriority.CORE,
                description='查看背包物品',
                aliases=['inv', 'i', 'bag']
            ),
            'map': CommandDefinition(
                patterns=['地图', 'map', '查看地图', '位置'],
                handler=lambda cmd: ('map', {}),
                priority=CommandPriority.CORE,
                description='查看地图和位置',
                aliases=['m', 'where']
            ),
            'cultivate': CommandDefinition(
                patterns=['修炼', 'cultivate', '打坐', '修行'],
                handler=lambda cmd: ('cultivate', {}),
                priority=CommandPriority.CORE,
                description='进行修炼'
            ),
            'skills': CommandDefinition(
                patterns=['技能', 'skills', '查看技能', '技能列表'],
                handler=lambda cmd: ('skills', {}),
                priority=CommandPriority.CORE,
                description='查看技能列表'
            ),
            'explore': CommandDefinition(
                patterns=['探索', 'explore', '查看', '观察'],
                handler=lambda cmd: ('explore', {}),
                priority=CommandPriority.CORE,
                description='探索当前区域'
            ),
            
            # 战斗相关命令（上下文相关）
            'attack': CommandDefinition(
                patterns=['攻击', 'attack', '进攻'],
                handler=lambda cmd: ('attack', {}),
                priority=CommandPriority.CONTEXT,
                description='攻击目标',
                context_required='battle'
            ),
            'defend': CommandDefinition(
                patterns=['防御', 'defend', '防守'],
                handler=lambda cmd: ('defend', {}),
                priority=CommandPriority.CONTEXT,
                description='进入防御姿态',
                context_required='battle'
            ),
            'flee': CommandDefinition(
                patterns=['逃跑', 'flee', '逃走', '撤退'],
                handler=lambda cmd: ('flee', {}),
                priority=CommandPriority.CONTEXT,
                description='逃离战斗',
                context_required='battle'
            ),
        }
        
        # 构建缩写映射
        for cmd_name, cmd_def in commands.items():
            if cmd_def.aliases:
                for alias in cmd_def.aliases:
                    self.abbreviations[alias] = cmd_name
                    
        return commands
        
    def route_command(self, user_input: str) -> Tuple[str, Dict[str, Any]]:
        """
        路由用户命令
        返回: (命令类型, 参数)
        """
        if not user_input:
            return ('unknown', {})
            
        # 清理输入
        cleaned_input = user_input.strip()
        
        # 记录命令历史
        self.command_history.append(cleaned_input)
        if len(self.command_history) > 100:
            self.command_history.pop(0)
            
        # 按优先级尝试匹配
        for priority in CommandPriority:
            result = self._try_match_priority(cleaned_input, priority)
            if result[0] != 'unknown':  # 匹配成功
                return result
                
        # 所有精确匹配都失败，尝试模糊匹配
        fuzzy_result = self._fuzzy_match(cleaned_input)
        if fuzzy_result[0] != 'unknown':
            return fuzzy_result
            
        # 最后尝试NLP
        if self.nlp_handler:
            return self._handle_with_nlp(cleaned_input)
            
        return ('unknown', {'raw': cleaned_input})
        
    def _try_match_priority(self, input_text: str, priority: CommandPriority) -> Tuple[str, Dict]:
        """尝试在指定优先级匹配命令"""
        for cmd_name, cmd_def in self.commands.items():
            if cmd_def.priority != priority:
                continue
                
            # 检查上下文要求
            if cmd_def.context_required and self.current_context != cmd_def.context_required:
                continue
                
            # 尝试匹配模式
            if self._match_patterns(input_text, cmd_def.patterns):
                return cmd_def.handler(input_text)
                
        return ('unknown', {})
        
    def _match_patterns(self, input_text: str, patterns: List[str]) -> bool:
        """精确匹配模式"""
        lower_input = input_text.lower()
        
        # 先检查缩写
        if lower_input in self.abbreviations:
            actual_cmd = self.abbreviations[lower_input]
            if actual_cmd in self.commands:
                patterns = self.commands[actual_cmd].patterns
                
        # 精确匹配
        for pattern in patterns:
            if lower_input == pattern.lower():
                return True
                
        return False
        
    def _fuzzy_match(self, input_text: str) -> Tuple[str, Dict]:
        """模糊匹配（用于处理带参数的命令）"""
        lower_input = input_text.lower()
        
        # 攻击命令模糊匹配
        attack_patterns = [
            r'^(攻击|打|揍|击败)\s*(.+)$',
            r'^(attack|hit|fight)\s+(.+)$'
        ]
        for pattern in attack_patterns:
            match = re.match(pattern, lower_input)
            if match:
                target = match.group(2)
                return ('attack', {'target': target})
                
        # 移动命令模糊匹配
        move_patterns = [
            r'^(去|前往|移动到|走到)\s*(.+)$',
            r'^(go|move|travel)\s+to\s+(.+)$',
            r'^(go|move|travel)\s+(.+)$'
        ]
        for pattern in move_patterns:
            match = re.match(pattern, lower_input)
            if match:
                destination = match.group(2)
                return ('move', {'location': destination})
                
        # 使用技能模糊匹配
        skill_patterns = [
            r'^(使用|施放|释放)\s*(.+)\s*(攻击|对付|打)\s*(.*)$',
            r'^(use|cast)\s+(.+)\s+on\s+(.+)$'
        ]
        for pattern in skill_patterns:
            match = re.match(pattern, lower_input)
            if match:
                skill = match.group(2)
                target = match.group(4) if len(match.groups()) > 3 else None
                return ('use_skill', {'skill': skill, 'target': target})
                
        # 对话命令模糊匹配
        talk_patterns = [
            r'^(和|跟|与)\s*(.+)\s*(说话|聊天|交谈)$',
            r'^(talk|speak|chat)\s+(to|with)\s+(.+)$'
        ]
        for pattern in talk_patterns:
            match = re.match(pattern, lower_input)
            if match:
                target = match.group(2) if '和' in pattern else match.group(3)
                return ('talk', {'target': target})
                
        return ('unknown', {})
        
    def _handle_with_nlp(self, input_text: str) -> Tuple[str, Dict]:
        """使用NLP处理无法精确匹配的输入"""
        try:
            # 调用NLP处理器
            nlp_result = self.nlp_handler(input_text, context={
                'current_context': self.current_context,
                'recent_commands': self.command_history[-5:],
                'available_commands': self._get_context_commands()
            })
            
            if nlp_result:
                return (nlp_result.get('command_type', 'unknown'), 
                       nlp_result.get('parameters', {}))
                       
            return ('unknown', {'raw': input_text})
            
        except Exception as e:
            # NLP处理失败
            return ('unknown', {'raw': input_text, 'error': str(e)})
            
    def _get_context_commands(self) -> List[str]:
        """获取当前上下文可用的命令"""
        available = []
        for cmd_name, cmd_def in self.commands.items():
            if cmd_def.context_required is None or cmd_def.context_required == self.current_context:
                available.extend(cmd_def.patterns)
        return available
        
    def set_context(self, context: str):
        """设置当前上下文"""
        self.current_context = context
        
    def set_nlp_handler(self, handler: Callable):
        """设置NLP处理器"""
        self.nlp_handler = handler
        
    def get_help_text(self) -> str:
        """获取帮助文本"""
        help_text = "【游戏命令列表】\n\n"
        
        # 按优先级分组显示
        priority_groups = {
            CommandPriority.SYSTEM: "系统命令",
            CommandPriority.CORE: "核心命令",
            CommandPriority.CONTEXT: "场景命令"
        }
        
        for priority, group_name in priority_groups.items():
            help_text += f"[{group_name}]\n"
            for cmd_name, cmd_def in self.commands.items():
                if cmd_def.priority == priority:
                    # 检查上下文
                    if cmd_def.context_required and cmd_def.context_required != self.current_context:
                        continue
                        
                    patterns_str = "、".join(cmd_def.patterns[:3])
                    if len(cmd_def.patterns) > 3:
                        patterns_str += "..."
                        
                    help_text += f"  {patterns_str} - {cmd_def.description}\n"
            help_text += "\n"
            
        return help_text
