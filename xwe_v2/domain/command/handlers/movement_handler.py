"""
移动命令处理器

处理所有移动和探索相关的命令
"""

from typing import List, Optional

from xwe_v2.core.command.command_processor import (
    CommandContext,
    CommandHandler,
    CommandPriority,
    CommandResult,
)
from xwe_v2.core.command_parser import CommandType
from xwe_v2.core.output import MessageType
from xwe_v2.core.state import GameContext


class MovementHandler(CommandHandler):
    """移动命令处理器"""

    def __init__(self):
        super().__init__("movement", [CommandType.MOVE], CommandPriority.NORMAL)

    def can_handle(self, context: CommandContext) -> bool:
        """检查是否可以处理移动命令"""
        # 战斗中不能移动
        if context.game_context == GameContext.COMBAT:
            return False

        # 对话中不能移动
        if context.game_context == GameContext.DIALOGUE:
            return False

        return True

    def handle(self, context: CommandContext) -> CommandResult:
        """处理移动命令"""
        location_name = context.command.parameters.get("location")

        if not location_name:
            context.output_manager.error("请指定要去的地点")
            context.output_manager.info("使用 '地图' 命令查看可去的地点")
            return CommandResult.failure("未指定目的地")

        # TODO: 从位置管理器获取位置信息
        # location_manager = context.metadata.get('location_manager')
        # world_map = context.metadata.get('world_map')

        # 模拟移动
        current_location = context.current_location

        # 检查是否可以移动到目标位置
        if not self._can_move_to(context, location_name):
            context.output_manager.error(f"无法前往 {location_name}")
            return CommandResult.failure("无法到达目的地")

        # 执行移动
        context.output_manager.narrative(f"你离开了{current_location}...")

        # 消耗体力
        stamina_cost = 10
        if context.player and hasattr(context.player, "consume_stamina"):
            context.player.consume_stamina(stamina_cost)
            context.output_manager.system(f"消耗了{stamina_cost}点体力")

        # 更新位置
        context.state_manager.set_location(location_name)

        # 描述新位置
        self._describe_location(context, location_name)

        return CommandResult.success("移动成功", new_location=location_name)

    def _can_move_to(self, context: CommandContext, location: str) -> bool:
        """检查是否可以移动到目标位置"""
        # TODO: 实现实际的位置检查逻辑
        # - 检查位置是否存在
        # - 检查是否相邻
        # - 检查是否满足进入条件

        # 模拟一些基本检查
        valid_locations = ["青云山", "主城", "妖兽森林", "灵药谷"]
        return location in valid_locations

    def _describe_location(self, context: CommandContext, location: str) -> None:
        """描述新位置"""
        descriptions = {
            "青云山": "青山绿水，云雾缭绕，隐约可见山顶的道观。这里灵气充沛，是修炼的绝佳之地。",
            "主城": "人来人往，热闹非凡。街道两旁商铺林立，叫卖声此起彼伏。",
            "妖兽森林": "古木参天，阴森恐怖。不时传来野兽的咆哮声，危机四伏。",
            "灵药谷": "百花齐放，药香扑鼻。这里生长着各种珍贵的灵药。",
        }

        desc = descriptions.get(location, "你来到了一个新的地方。")
        context.output_manager.narrative(desc)

        # 检查是否有特殊事件
        self._check_location_events(context, location)

    def _check_location_events(self, context: CommandContext, location: str) -> None:
        """检查位置事件"""
        # TODO: 从事件系统获取位置事件

        # 模拟一些随机事件
        import random

        if location == "妖兽森林" and random.random() < 0.3:
            context.output_manager.warning("你遇到了一只游荡的妖兽！")
            # TODO: 触发战斗

    def validate(self, context: CommandContext) -> Optional[str]:
        """验证移动命令"""
        if not context.player:
            return "游戏尚未开始"

        # 检查体力
        if hasattr(context.player, "attributes"):
            if context.player.attributes.current_stamina < 10:
                return "体力不足，无法移动"

        return None

    def get_help(self) -> str:
        return """移动命令：去 <地点>

用法：
  去 青云山
  前往 主城
  移动到 妖兽森林

说明：
  移动到指定的地点。移动需要消耗体力，某些地点可能有进入条件。
  使用 '地图' 命令可以查看当前可以前往的地点。
"""


class ExploreHandler(CommandHandler):
    """探索命令处理器"""

    def __init__(self):
        super().__init__("explore", [CommandType.EXPLORE], CommandPriority.NORMAL)

    def can_handle(self, context: CommandContext) -> bool:
        """检查是否可以探索"""
        # 战斗中不能探索
        if context.game_context == GameContext.COMBAT:
            return False

        return True

    def handle(self, context: CommandContext) -> CommandResult:
        """处理探索命令"""
        location = context.current_location

        context.output_manager.narrative("你仔细探索着周围的环境...")

        # TODO: 从位置管理器获取探索结果
        # location_manager = context.metadata.get('location_manager')
        # result = location_manager.explore_area(context.player.id)

        # 模拟探索结果
        import random

        findings = []

        # 随机发现物品
        if random.random() < 0.4:
            items = [
                ("灵草", random.randint(1, 3)),
                ("灵石", random.randint(5, 15)),
                ("神秘卷轴", 1),
            ]
            item, quantity = random.choice(items)
            findings.append(("item", item, quantity))

            context.output_manager.success(f"你找到了 {item} x{quantity}！")

            # TODO: 添加到背包
            # if context.player.inventory:
            #     context.player.inventory.add(item, quantity)

        # 随机发现地点
        if random.random() < 0.3:
            places = ["隐藏的山洞", "废弃的道观", "神秘的祭坛"]
            place = random.choice(places)
            findings.append(("place", place))

            context.output_manager.info(f"你发现了一个{place}！")

        # 随机遭遇
        if random.random() < 0.2:
            encounters = ["游商", "受伤的修士", "神秘老人"]
            encounter = random.choice(encounters)
            findings.append(("encounter", encounter))

            context.output_manager.warning(f"你遇到了一个{encounter}。")

        if not findings:
            context.output_manager.info("你没有发现什么特别的东西。")

        # 消耗体力
        stamina_cost = 5
        if context.player and hasattr(context.player, "consume_stamina"):
            context.player.consume_stamina(stamina_cost)

        # 增加探索进度
        context.state_manager.update_statistics("areas_explored", 0.1)

        return CommandResult.success("探索完成", findings=findings)

    def validate(self, context: CommandContext) -> Optional[str]:
        """验证探索命令"""
        if not context.player:
            return "游戏尚未开始"

        # 检查体力
        if hasattr(context.player, "attributes"):
            if context.player.attributes.current_stamina < 5:
                return "体力不足，无法探索"

        return None

    def get_help(self) -> str:
        return """探索命令：探索

用法：
  探索

说明：
  探索当前区域，可能发现物品、隐藏地点或遭遇NPC。
  探索需要消耗少量体力，但可能带来意外的收获。
"""


# 创建组合处理器
class MovementCommandHandler(CommandHandler):
    """移动命令组合处理器"""

    def __init__(self):
        super().__init__(
            "movement_commands", [CommandType.MOVE, CommandType.EXPLORE], CommandPriority.NORMAL
        )

        self.handlers = {
            CommandType.MOVE: MovementHandler(),
            CommandType.EXPLORE: ExploreHandler(),
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

        return CommandResult.failure("无法处理的移动命令")

    def validate(self, context: CommandContext) -> Optional[str]:
        """验证命令"""
        cmd_type = context.command.command_type
        if cmd_type in self.handlers:
            return self.handlers[cmd_type].validate(context)
        return "未知的移动命令"

    def get_help(self) -> str:
        """获取所有移动命令的帮助"""
        help_text = "=== 移动命令帮助 ===\n\n"
        for handler in self.handlers.values():
            help_text += handler.get_help() + "\n"
        return help_text
