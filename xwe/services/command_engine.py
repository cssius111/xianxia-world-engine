"""
命令引擎服务
负责解析和路由游戏命令到相应的处理器
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import re
import logging

from . import ServiceBase, ServiceContainer
from ..events import GameEvent, publish_event


@dataclass
class CommandContext:
    """命令执行上下文"""
    raw_command: str
    command: str
    args: List[str]
    player_id: Optional[str] = None
    location: Optional[str] = None
    in_combat: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class CommandResult:
    """命令执行结果"""
    success: bool
    output: str
    state_changed: bool = False
    events: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    require_confirmation: bool = False
    confirmation_data: Dict[str, Any] = field(default_factory=dict)


class ICommandHandler(ABC):
    """命令处理器接口"""
    
    @abstractmethod
    def can_handle(self, context: CommandContext) -> bool:
        """判断是否可以处理该命令"""
        pass
        
    @abstractmethod
    def handle(self, context: CommandContext) -> CommandResult:
        """处理命令"""
        pass
        
    @abstractmethod
    def get_help(self) -> str:
        """获取帮助信息"""
        pass


class CommandHandler(ICommandHandler):
    """命令处理器基类"""
    
    def __init__(self, 
                 commands: List[str],
                 aliases: Optional[List[str]] = None,
                 description: str = "",
                 usage: str = "",
                 require_args: int = 0):
        self.commands = commands
        self.aliases = aliases or []
        self.description = description
        self.usage = usage
        self.require_args = require_args
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def can_handle(self, context: CommandContext) -> bool:
        """判断是否可以处理该命令"""
        command = context.command.lower()
        
        # 检查主命令
        if command in [cmd.lower() for cmd in self.commands]:
            return True
            
        # 检查别名
        if command in [alias.lower() for alias in self.aliases]:
            return True
            
        return False
        
    def handle(self, context: CommandContext) -> CommandResult:
        """处理命令"""
        # 检查参数数量
        if len(context.args) < self.require_args:
            return CommandResult(
                success=False,
                output=f"命令格式错误。用法：{self.usage}",
                suggestions=[self.usage]
            )
            
        try:
            return self._do_handle(context)
        except Exception as e:
            self.logger.error(f"Error handling command: {e}")
            return CommandResult(
                success=False,
                output=f"命令执行出错：{str(e)}"
            )
            
    def _do_handle(self, context: CommandContext) -> CommandResult:
        """子类实现的处理逻辑"""
        raise NotImplementedError
        
    def get_help(self) -> str:
        """获取帮助信息"""
        help_text = f"{self.description}\n"
        help_text += f"命令：{', '.join(self.commands)}\n"
        
        if self.aliases:
            help_text += f"别名：{', '.join(self.aliases)}\n"
            
        if self.usage:
            help_text += f"用法：{self.usage}\n"
            
        return help_text


class ICommandEngine(ABC):
    """命令引擎接口"""
    
    @abstractmethod
    def register_handler(self, handler: ICommandHandler) -> None:
        """注册命令处理器"""
        pass
        
    @abstractmethod
    def register_pattern_handler(self, pattern: str, 
                                handler: Callable[[CommandContext], CommandResult]) -> None:
        """注册模式匹配处理器"""
        pass
        
    @abstractmethod
    def process_command(self, command: str, **context_data) -> CommandResult:
        """处理命令"""
        pass
        
    @abstractmethod
    def get_suggestions(self, partial_command: str) -> List[str]:
        """获取命令建议"""
        pass
        
    @abstractmethod
    def get_all_commands(self) -> List[str]:
        """获取所有命令"""
        pass


class CommandEngine(ServiceBase[ICommandEngine], ICommandEngine):
    """命令引擎实现"""
    
    def __init__(self, container: ServiceContainer) -> None:
        super().__init__(container)
        self._handlers: List[ICommandHandler] = []
        self._pattern_handlers: List[Tuple[re.Pattern, Callable]] = []
        self._command_history: List[CommandContext] = []
        self._command_cache: Dict[str, CommandResult] = {}
        
    def _do_initialize(self) -> None:
        """初始化服务"""
        # 注册内置命令处理器
        self._register_builtin_handlers()
        
    def _register_builtin_handlers(self) -> None:
        """注册内置命令处理器"""
        # 帮助命令
        help_handler = HelpCommandHandler(self)
        self.register_handler(help_handler)
        
        # 其他内置命令可以在这里添加
        
    def register_handler(self, handler: ICommandHandler) -> None:
        """注册命令处理器"""
        self._handlers.append(handler)
        self.logger.info(f"Registered command handler: {handler.__class__.__name__}")
        
    def register_pattern_handler(self, pattern: str,
                                handler: Callable[[CommandContext], CommandResult]) -> None:
        """注册模式匹配处理器"""
        compiled_pattern = re.compile(pattern, re.IGNORECASE)
        self._pattern_handlers.append((compiled_pattern, handler))
        self.logger.info(f"Registered pattern handler: {pattern}")
        
    def process_command(self, command: str, **context_data) -> CommandResult:
        """处理命令"""
        # 清理命令
        command = command.strip()
        if not command:
            return CommandResult(
                success=False,
                output="请输入命令",
                suggestions=self.get_suggestions("")
            )
            
        # 解析命令
        parts = command.split()
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # 创建上下文
        context = CommandContext(
            raw_command=command,
            command=cmd,
            args=args,
            **context_data
        )
        
        # 记录命令历史
        self._command_history.append(context)
        if len(self._command_history) > 100:
            self._command_history = self._command_history[-50:]
            
        # 检查缓存
        cache_key = f"{cmd}:{':'.join(args)}"
        if cache_key in self._command_cache and not context.in_combat:
            return self._command_cache[cache_key]
            
        # 查找处理器
        result = None
        
        # 1. 尝试精确匹配处理器
        for handler in self._handlers:
            if handler.can_handle(context):
                result = handler.handle(context)
                break
                
        # 2. 尝试模式匹配处理器
        if not result:
            for pattern, handler in self._pattern_handlers:
                if pattern.match(command):
                    result = handler(context)
                    break
                    
        # 3. 尝试自然语言处理
        if not result:
            result = self._handle_natural_language(context)
            
        # 缓存结果（非战斗命令）
        if result and result.success and not context.in_combat:
            self._command_cache[cache_key] = result
            
        # 发布命令执行事件
        publish_event(GameEvent('command_executed', {
            'command': command,
            'success': result.success if result else False,
            'player_id': context.player_id
        }))
        
        return result or CommandResult(
            success=False,
            output=f"未知命令：{cmd}",
            suggestions=self.get_suggestions(cmd)
        )
        
    def _handle_natural_language(self, context: CommandContext) -> Optional[CommandResult]:
        """处理自然语言命令"""
        # 这里可以集成NLP服务
        # 暂时使用简单的关键词匹配
        
        command_mappings = {
            '攻击': ['攻击', '打', '揍', '击', '斩'],
            '防御': ['防御', '防', '守', '挡'],
            '逃跑': ['逃', '跑', '溜', '撤退'],
            '状态': ['状态', '属性', '信息'],
            '帮助': ['帮助', '怎么', '如何', '教程'],
            '地图': ['地图', '位置', '哪里', '在哪'],
            '探索': ['探索', '查看', '看看', '搜索'],
            '修炼': ['修炼', '修行', '练功', '打坐']
        }
        
        raw_lower = context.raw_command.lower()
        
        for cmd, keywords in command_mappings.items():
            for keyword in keywords:
                if keyword in raw_lower:
                    # 创建新的上下文
                    new_context = CommandContext(
                        raw_command=context.raw_command,
                        command=cmd,
                        args=context.args,
                        player_id=context.player_id,
                        location=context.location,
                        in_combat=context.in_combat,
                        metadata=context.metadata
                    )
                    
                    # 重新处理命令
                    for handler in self._handlers:
                        if handler.can_handle(new_context):
                            return handler.handle(new_context)
                            
        return None
        
    def get_suggestions(self, partial_command: str) -> List[str]:
        """获取命令建议"""
        suggestions = []
        partial_lower = partial_command.lower()
        
        # 从所有命令中查找匹配
        all_commands = self.get_all_commands()
        
        for cmd in all_commands:
            if cmd.lower().startswith(partial_lower):
                suggestions.append(cmd)
                
        # 限制建议数量
        return suggestions[:5]
        
    def get_all_commands(self) -> List[str]:
        """获取所有命令"""
        commands: List[Any] = []
        
        for handler in self._handlers:
            commands.extend(handler.commands)
            commands.extend(handler.aliases)
            
        return sorted(list(set(commands)))


class HelpCommandHandler(CommandHandler):
    """帮助命令处理器"""
    
    def __init__(self, engine: CommandEngine) -> None:
        super().__init__(
            commands=['帮助', 'help'],
            aliases=['?', 'h'],
            description='显示帮助信息',
            usage='帮助 [命令]'
        )
        self.engine = engine
        
    def _do_handle(self, context: CommandContext) -> CommandResult:
        """处理帮助命令"""
        if context.args:
            # 显示特定命令的帮助
            cmd_name = context.args[0]
            
            for handler in self.engine._handlers:
                if (cmd_name.lower() in [c.lower() for c in handler.commands] or
                    cmd_name.lower() in [a.lower() for a in handler.aliases]):
                    return CommandResult(
                        success=True,
                        output=handler.get_help()
                    )
                    
            return CommandResult(
                success=False,
                output=f"未找到命令：{cmd_name}",
                suggestions=self.engine.get_suggestions(cmd_name)
            )
        else:
            # 显示所有命令
            help_text = "=== 游戏命令帮助 ===\n\n"
            
            # 按类别组织命令
            categories = {
                '基础命令': ['帮助', '状态', '地图', '探索'],
                '战斗命令': ['攻击', '防御', '逃跑', '使用'],
                '修炼命令': ['修炼', '突破'],
                '交互命令': ['对话', '交易'],
                '系统命令': ['保存', '退出']
            }
            
            for category, commands in categories.items():
                help_text += f"{category}：\n"
                
                for cmd in commands:
                    # 查找对应的处理器
                    for handler in self.engine._handlers:
                        if cmd in handler.commands:
                            help_text += f"  {cmd} - {handler.description}\n"
                            break
                            
                help_text += "\n"
                
            help_text += "输入 '帮助 [命令]' 查看详细说明"
            
            return CommandResult(
                success=True,
                output=help_text
            )
