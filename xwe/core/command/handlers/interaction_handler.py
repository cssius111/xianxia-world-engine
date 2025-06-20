"""
交互命令处理器

处理所有交互相关的命令（对话、交易、拾取等）
"""

from typing import List, Optional

from xwe.core.command.command_processor import (
    CommandContext,
    CommandHandler,
    CommandPriority,
    CommandResult,
)
from xwe.core.command_parser import CommandType
from xwe.core.output import MessageType
from xwe.core.state import GameContext


class InteractionHandler(CommandHandler):
    """交互命令基类"""

    def __init__(self, name: str, command_types: List[CommandType]):
        super().__init__(name, command_types, CommandPriority.NORMAL)

    def can_handle(self, context: CommandContext) -> bool:
        """检查是否可以处理"""
        # 战斗中不能进行大部分交互
        if context.game_context == GameContext.COMBAT:
            return False
        return True


class TalkHandler(InteractionHandler):
    """对话命令处理器"""

    def __init__(self):
        super().__init__("talk", [CommandType.TALK])

    def handle(self, context: CommandContext) -> CommandResult:
        """处理对话命令"""
        target_name = context.command.target

        if not target_name:
            context.output_manager.error("请指定对话对象")
            return CommandResult.failure("未指定对话对象")

        # TODO: 从场景中查找NPC
        # location = context.state_manager.get_location()
        # npc = find_npc_in_location(location, target_name)

        # 模拟对话
        context.output_manager.narrative(f"你走向{target_name}。")

        # 进入对话上下文
        context.state_manager.push_context(GameContext.DIALOGUE, {"npc_name": target_name})

        # 模拟NPC对话
        if target_name == "掌门":
            context.output_manager.dialogue(
                target_name, "欢迎来到青云门，年轻的修士。你有什么事吗？"
            )

            # 提供对话选项
            context.output_manager.menu(
                ["请问如何才能提升修为？", "我想接取任务", "告辞"], "选择话题"
            )
        else:
            context.output_manager.dialogue(target_name, "你好，有什么可以帮助你的吗？")

        return CommandResult.success("开始对话", npc=target_name)

    def get_help(self) -> str:
        return """对话命令：和 <NPC名字> 说话

用法：
  和 掌门 说话
  与 商人 交谈
  跟 守卫 对话

说明：
  与NPC进行对话，可以获取信息、接取任务或进行交易。
  对话中会出现选项，输入数字选择对应选项。
"""


class TradeHandler(InteractionHandler):
    """交易命令处理器"""

    def __init__(self):
        super().__init__("trade", [CommandType.TRADE])

    def handle(self, context: CommandContext) -> CommandResult:
        """处理交易命令"""
        target_name = context.command.target

        if not target_name:
            context.output_manager.error("请指定交易对象")
            return CommandResult.failure("未指定交易对象")

        # TODO: 检查是否是商人
        # if not is_merchant(target_name):
        #     context.output_manager.error(f"{target_name}不是商人")
        #     return CommandResult.failure("对方不是商人")

        # 进入交易界面
        context.output_manager.system(f"与{target_name}交易")
        context.output_manager.system("=" * 40)

        # 模拟商品列表
        items = [
            {"名称": "气血药水", "价格": "50灵石", "说明": "恢复100点生命"},
            {"名称": "灵力药水", "价格": "80灵石", "说明": "恢复50点法力"},
            {"名称": "回城符", "价格": "200灵石", "说明": "传送回主城"},
        ]

        context.output_manager.output_table(items, headers=["名称", "价格", "说明"])

        context.output_manager.menu(["购买物品", "出售物品", "结束交易"], "交易选项")

        # 进入交易上下文
        context.state_manager.push_context(GameContext.TRADING, {"merchant": target_name})

        return CommandResult.success("打开交易界面", merchant=target_name)

    def get_help(self) -> str:
        return """交易命令：交易 <商人名字>

用法：
  交易 杂货商

说明：
  与商人进行交易，可以购买或出售物品。
  交易界面会显示商品列表和价格。
"""


class PickUpHandler(InteractionHandler):
    """拾取命令处理器"""

    def __init__(self):
        super().__init__("pickup", [CommandType.PICK_UP])

    def handle(self, context: CommandContext) -> CommandResult:
        """处理拾取命令"""
        item_name = context.command.parameters.get("item")

        if not item_name:
            # 拾取所有物品
            context.output_manager.info("尝试拾取周围的所有物品...")

            # TODO: 获取当前位置的物品列表
            # items = get_items_at_location(context.current_location)

            # 模拟拾取
            items = ["灵石x10", "草药x3"]
            if items:
                for item in items:
                    context.output_manager.success(f"拾取了 {item}")
                return CommandResult.success("拾取成功", items=items)
            else:
                context.output_manager.info("这里没有可以拾取的物品")
                return CommandResult.success("没有物品")
        else:
            # 拾取指定物品
            context.output_manager.info(f"尝试拾取 {item_name}...")

            # TODO: 检查物品是否存在
            # if item_exists_at_location(item_name, context.current_location):
            #     add_to_inventory(context.player, item_name)

            context.output_manager.success(f"拾取了 {item_name}")
            return CommandResult.success("拾取成功", item=item_name)

    def get_help(self) -> str:
        return """拾取命令：拾取 [物品名]

用法：
  拾取          - 拾取周围所有物品
  拾取 灵石      - 拾取指定物品
  捡起 草药      - 同上

说明：
  拾取地上的物品放入背包。如果不指定物品名，会尝试拾取所有物品。
  背包已满时无法拾取更多物品。
"""


# 创建组合处理器
class InteractionCommandHandler(CommandHandler):
    """交互命令组合处理器"""

    def __init__(self):
        super().__init__(
            "interaction_commands",
            [CommandType.TALK, CommandType.TRADE, CommandType.PICK_UP],
            CommandPriority.NORMAL,
        )

        # 子处理器
        self.handlers = {
            CommandType.TALK: TalkHandler(),
            CommandType.TRADE: TradeHandler(),
            CommandType.PICK_UP: PickUpHandler(),
        }

    def can_handle(self, context: CommandContext) -> bool:
        """检查是否可以处理"""
        cmd_type = context.command.command_type
        if cmd_type in self.handlers:
            return self.handlers[cmd_type].can_handle(context)
        return False

    def handle(self, context: CommandContext) -> CommandResult:
        """分发到对应的子处理器"""
        cmd_type = context.command.command_type
        if cmd_type in self.handlers:
            return self.handlers[cmd_type].handle(context)

        return CommandResult.failure("无法处理的交互命令")

    def validate(self, context: CommandContext) -> Optional[str]:
        """验证命令"""
        cmd_type = context.command.command_type
        if cmd_type in self.handlers:
            return self.handlers[cmd_type].validate(context)
        return "未知的交互命令"

    def get_help(self) -> str:
        """获取所有交互命令的帮助"""
        help_text = "=== 交互命令帮助 ===\n\n"
        for handler in self.handlers.values():
            help_text += handler.get_help() + "\n"
        return help_text
