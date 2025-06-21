"""
命令路由器
根据优先级和上下文路由命令
"""

from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CommandPriority(Enum):
    """命令优先级"""
    CRITICAL = 1    # 紧急命令（如逃跑）
    HIGH = 2        # 高优先级
    NORMAL = 3      # 普通优先级
    LOW = 4         # 低优先级


@dataclass
class CommandRoute:
    """命令路由"""
    pattern: str
    handler: str
    priority: CommandPriority = CommandPriority.NORMAL
    contexts: List[str] = None  # 适用的上下文
    
    def __post_init__(self):
        if self.contexts is None:
            self.contexts = ["*"]  # 默认所有上下文


class CommandRouter:
    """
    命令路由器
    
    根据当前上下文和优先级路由命令到相应的处理器
    """
    
    def __init__(self):
        self.routes: List[CommandRoute] = []
        self.current_context = "exploration"  # 默认探索模式
        self.nlp_handler: Optional[Callable] = None
        
        # 初始化默认路由
        self._init_default_routes()
        
    def _init_default_routes(self) -> None:
        """初始化默认路由规则"""
        # 战斗上下文的路由
        self.add_route("逃", "flee", CommandPriority.CRITICAL, ["battle"])
        self.add_route("逃跑", "flee", CommandPriority.CRITICAL, ["battle"])
        self.add_route("攻击", "attack", CommandPriority.HIGH, ["battle"])
        self.add_route("防御", "defend", CommandPriority.HIGH, ["battle"])
        self.add_route("技能", "use_skill", CommandPriority.HIGH, ["battle"])
        
        # 探索上下文的路由
        self.add_route("移动", "move", CommandPriority.NORMAL, ["exploration"])
        self.add_route("探索", "explore", CommandPriority.NORMAL, ["exploration"])
        self.add_route("对话", "talk", CommandPriority.NORMAL, ["exploration"])
        self.add_route("交易", "trade", CommandPriority.NORMAL, ["exploration"])
        
        # 通用路由（所有上下文）
        self.add_route("状态", "status", CommandPriority.NORMAL, ["*"])
        self.add_route("背包", "inventory", CommandPriority.NORMAL, ["*"])
        self.add_route("帮助", "help", CommandPriority.LOW, ["*"])
        self.add_route("保存", "save", CommandPriority.LOW, ["*"])
        
        # 修炼相关
        self.add_route("修炼", "cultivate", CommandPriority.NORMAL, ["exploration", "safe_zone"])
        self.add_route("突破", "breakthrough", CommandPriority.HIGH, ["safe_zone"])
        
    def add_route(self, pattern: str, handler: str, 
                  priority: CommandPriority = CommandPriority.NORMAL,
                  contexts: List[str] = None) -> None:
        """
        添加路由规则
        
        Args:
            pattern: 命令模式
            handler: 处理器名称
            priority: 优先级
            contexts: 适用的上下文列表
        """
        route = CommandRoute(pattern, handler, priority, contexts or ["*"])
        self.routes.append(route)
        
        # 按优先级排序
        self.routes.sort(key=lambda r: r.priority.value)
        
    def set_context(self, context: str) -> None:
        """设置当前上下文"""
        self.current_context = context
        logger.debug(f"命令路由器上下文切换到: {context}")
        
    def set_nlp_handler(self, handler: Callable) -> None:
        """设置NLP处理器"""
        self.nlp_handler = handler
        
    def route_command(self, input_text: str) -> Tuple[str, Dict[str, Any]]:
        """
        路由命令
        
        Args:
            input_text: 输入文本
            
        Returns:
            (命令类型, 参数字典)
        """
        # 首先尝试精确匹配路由
        for route in self.routes:
            # 检查上下文
            if "*" not in route.contexts and self.current_context not in route.contexts:
                continue
                
            # 检查模式匹配
            if input_text.lower().startswith(route.pattern.lower()):
                # 提取参数
                params = self._extract_params(input_text, route.pattern)
                return route.handler, params
                
        # 如果没有匹配，使用NLP处理器
        if self.nlp_handler:
            try:
                result = self.nlp_handler(input_text, {"context": self.current_context})
                if isinstance(result, dict):
                    cmd_type = result.get("command_type", "unknown")
                    params = result.get("parameters", {})
                    return cmd_type, params
            except Exception as e:
                logger.error(f"NLP处理器错误: {e}")
                
        # 默认返回未知命令
        return "unknown", {"raw_text": input_text}
        
    def _extract_params(self, input_text: str, pattern: str) -> Dict[str, Any]:
        """提取命令参数"""
        params = {}
        
        # 移除命令部分，剩下的是参数
        remaining = input_text[len(pattern):].strip()
        
        if remaining:
            # 简单处理：第一个词作为目标
            words = remaining.split()
            if words:
                params["target"] = words[0]
                if len(words) > 1:
                    params["extra"] = " ".join(words[1:])
                    
        return params
        
    def get_available_commands(self) -> List[str]:
        """获取当前上下文下可用的命令"""
        available = []
        
        for route in self.routes:
            if "*" in route.contexts or self.current_context in route.contexts:
                if route.pattern not in available:
                    available.append(route.pattern)
                    
        return available
        
    def get_help_text(self) -> str:
        """获取当前上下文的帮助文本"""
        help_lines = ["=== 可用命令 ===\n"]
        
        # 按优先级分组
        priority_groups = {}
        for route in self.routes:
            if "*" in route.contexts or self.current_context in route.contexts:
                priority = route.priority.name
                if priority not in priority_groups:
                    priority_groups[priority] = []
                priority_groups[priority].append(route.pattern)
                
        # 显示各优先级的命令
        priority_names = {
            "CRITICAL": "【紧急命令】",
            "HIGH": "【重要命令】",
            "NORMAL": "【常用命令】",
            "LOW": "【其他命令】"
        }
        
        for priority in ["CRITICAL", "HIGH", "NORMAL", "LOW"]:
            if priority in priority_groups:
                help_lines.append(f"\n{priority_names[priority]}")
                for cmd in priority_groups[priority]:
                    help_lines.append(f"  {cmd}")
                    
        help_lines.append("\n提示：在不同场景下可用的命令会有所不同")
        
        return "\n".join(help_lines)
