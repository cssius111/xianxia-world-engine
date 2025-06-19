"""
扩展命令处理器 - 处理游戏启动相关命令
"""

from typing import Optional
from xwe.core.command import (
    CommandHandler, CommandContext, CommandResult, CommandPriority
)
from xwe.core.command_parser import CommandType, CommandPattern


# 扩展命令类型
class ExtendedCommandType:
    """扩展的命令类型"""
    NEW_GAME = "new_game"
    CONTINUE = "continue"
    OPTIONS = "options"


class NewGameHandler(CommandHandler):
    """新游戏命令处理器"""
    
    def __init__(self, orchestrator):
        # 注意：这里我们不使用标准的CommandType，因为这是扩展命令
        super().__init__("new_game", [], CommandPriority.SYSTEM)
        self.orchestrator = orchestrator
    
    def can_handle(self, context: CommandContext) -> bool:
        """检查是否可以处理"""
        # 检查原始输入
        return context.raw_input.strip().startswith("新游戏")
    
    def handle(self, context: CommandContext) -> CommandResult:
        """处理新游戏命令"""
        # 解析玩家名称
        parts = context.raw_input.strip().split(maxsplit=1)
        
        if len(parts) < 2:
            context.output_manager.error("请指定角色名称")
            context.output_manager.info("用法: 新游戏 <角色名>")
            return CommandResult.failure("未指定角色名")
        
        player_name = parts[1].strip()
        
        # 验证名称
        if len(player_name) < 2:
            context.output_manager.error("角色名至少需要2个字符")
            return CommandResult.failure("角色名太短")
        
        if len(player_name) > 20:
            context.output_manager.error("角色名不能超过20个字符")
            return CommandResult.failure("角色名太长")
        
        # 创建新游戏
        import asyncio
        loop = asyncio.get_event_loop()
        loop.create_task(self.orchestrator.new_game(player_name))
        
        return CommandResult.success("新游戏创建成功")
    
    def get_help(self) -> str:
        return """新游戏命令：新游戏 <角色名>
        
用法：
  新游戏 张三丰
  新游戏 云游道人
  
说明：
  创建一个新的游戏角色并开始游戏。
  角色名长度应在2-20个字符之间。
"""


class ContinueGameHandler(CommandHandler):
    """继续游戏命令处理器"""
    
    def __init__(self, orchestrator):
        super().__init__("continue", [], CommandPriority.SYSTEM)
        self.orchestrator = orchestrator
    
    def can_handle(self, context: CommandContext) -> bool:
        """检查是否可以处理"""
        cmd = context.raw_input.strip().lower()
        return cmd in ["继续", "继续游戏", "continue"]
    
    def handle(self, context: CommandContext) -> CommandResult:
        """处理继续游戏命令"""
        # 查找最新的存档
        save_dir = self.orchestrator.config.save_dir
        
        if not save_dir.exists():
            context.output_manager.error("没有找到任何存档")
            return CommandResult.failure("无存档")
        
        # 获取所有存档文件
        save_files = list(save_dir.glob("*.json"))
        
        if not save_files:
            context.output_manager.error("没有找到任何存档")
            context.output_manager.info("请先创建新游戏")
            return CommandResult.failure("无存档")
        
        # 按修改时间排序，获取最新的
        save_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        latest_save = save_files[0]
        
        # 加载存档
        save_name = latest_save.stem
        context.output_manager.info(f"加载最新存档: {save_name}")
        
        import asyncio
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.orchestrator.load_game(save_name))
        
        return CommandResult.success("继续游戏")
    
    def get_help(self) -> str:
        return """继续游戏命令：继续
        
用法：
  继续
  继续游戏
  
说明：
  加载最新的游戏存档继续游戏。
"""


class OptionsHandler(CommandHandler):
    """选项命令处理器"""
    
    def __init__(self, orchestrator):
        super().__init__("options", [], CommandPriority.SYSTEM)
        self.orchestrator = orchestrator
    
    def can_handle(self, context: CommandContext) -> bool:
        """检查是否可以处理"""
        cmd = context.raw_input.strip().lower()
        return cmd in ["选项", "设置", "options", "config"]
    
    def handle(self, context: CommandContext) -> CommandResult:
        """处理选项命令"""
        config = self.orchestrator.config
        
        # 显示当前配置
        context.output_manager.system("=== 游戏设置 ===")
        
        config_data = {
            "游戏模式": config.game_mode.value,
            "控制台彩色": "开启" if config.console_colored else "关闭",
            "文件日志": "开启" if config.enable_file_log else "关闭",
            "HTML输出": "开启" if config.enable_html else "关闭",
            "自动保存": f"每{config.auto_save_interval/60:.0f}分钟" if config.auto_save_enabled else "关闭",
            "调试模式": "开启" if config.debug_mode else "关闭",
        }
        
        context.output_manager.output_status(config_data, "当前设置")
        
        # 显示可用选项
        context.output_manager.menu([
            "切换彩色输出",
            "切换文件日志",
            "切换HTML输出",
            "切换自动保存",
            "切换调试模式",
            "保存设置",
            "返回"
        ], "设置选项")
        
        return CommandResult.success("显示选项")
    
    def get_help(self) -> str:
        return """选项命令：选项
        
用法：
  选项
  设置
  
说明：
  查看和修改游戏设置。
"""


class GameLauncherHandler(CommandHandler):
    """游戏启动器命令处理器（组合）"""
    
    def __init__(self, orchestrator):
        super().__init__(
            "game_launcher",
            [],  # 不使用标准CommandType
            CommandPriority.SYSTEM
        )
        self.orchestrator = orchestrator
        
        # 子处理器
        self.handlers = {
            'new_game': NewGameHandler(orchestrator),
            'continue': ContinueGameHandler(orchestrator),
            'options': OptionsHandler(orchestrator),
        }
    
    def can_handle(self, context: CommandContext) -> bool:
        """检查是否可以处理"""
        for handler in self.handlers.values():
            if handler.can_handle(context):
                return True
        return False
    
    def handle(self, context: CommandContext) -> CommandResult:
        """分发到对应的子处理器"""
        for handler in self.handlers.values():
            if handler.can_handle(context):
                return handler.handle(context)
        
        return CommandResult.failure("无法处理的启动命令")
    
    def get_help(self) -> str:
        """获取所有启动命令的帮助"""
        help_text = "=== 游戏启动命令 ===\n\n"
        for handler in self.handlers.values():
            help_text += handler.get_help() + "\n"
        return help_text
