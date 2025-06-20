"""
修炼命令处理器

处理所有修炼相关的命令（修炼、学习技能、突破等）
"""

import random
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


class CultivationHandler(CommandHandler):
    """修炼命令基类"""

    def __init__(self, name: str, command_types: List[CommandType]):
        super().__init__(name, command_types, CommandPriority.NORMAL)

    def can_handle(self, context: CommandContext) -> bool:
        """检查是否可以处理"""
        # 战斗和对话中不能修炼
        if context.game_context in [GameContext.COMBAT, GameContext.DIALOGUE]:
            return False
        return True


class CultivateHandler(CultivationHandler):
    """修炼命令处理器"""

    def __init__(self):
        super().__init__("cultivate", [CommandType.CULTIVATE])
        # 不同地点的修炼效率
        self.location_bonuses = {
            "灵气洞府": 2.0,
            "青云峰": 1.5,
            "修炼室": 1.3,
            "普通地点": 1.0,
            "妖兽森林": 0.8,  # 危险地区修炼效率低
        }

    def handle(self, context: CommandContext) -> CommandResult:
        """处理修炼命令"""
        player = context.player

        # 检查体力
        if player.attributes.current_stamina < 20:
            context.output_manager.warning("体力不足，无法修炼")
            return CommandResult.failure("体力不足")

        # 获取地点加成
        location = context.current_location
        bonus = self._get_location_bonus(location)

        # 进入修炼状态
        context.state_manager.push_context(
            GameContext.CULTIVATING, {"start_time": context.state_manager.state.game_time}
        )

        # 描述修炼过程
        context.output_manager.narrative("你盘膝而坐，开始运转功法...")

        if bonus > 1.0:
            context.output_manager.info(f"此地灵气充沛，修炼效率提升{int((bonus-1)*100)}%")

        # 计算修炼成果
        base_exp = random.randint(10, 20)
        actual_exp = int(base_exp * bonus)

        # 消耗体力
        player.attributes.current_stamina -= 20

        # 增加修为
        old_level = player.attributes.cultivation_level
        # TODO: 实际增加修为的逻辑
        # player.add_cultivation_exp(actual_exp)

        # 修炼描述
        cultivation_messages = [
            "灵气在经脉中流转，你感觉修为在缓慢提升。",
            f"获得了 {actual_exp} 点修为。",
        ]

        # 检查是否可以突破
        if self._can_breakthrough(player):
            cultivation_messages.append("你感觉已经达到当前境界的瓶颈，可以尝试突破了！")
            context.output_manager.achievement("已满足突破条件")

        # 批量输出修炼信息
        for msg in cultivation_messages:
            context.output_manager.narrative(msg)

        # 随机事件
        if random.random() < 0.1:
            self._trigger_cultivation_event(context)

        # 退出修炼状态
        context.state_manager.pop_context()

        # 更新统计
        context.state_manager.update_statistics("cultivation_times", 1)
        context.state_manager.update_statistics("total_cultivation_exp", actual_exp)

        return CommandResult.success("修炼完成", exp_gained=actual_exp)

    def _get_location_bonus(self, location: str) -> float:
        """获取地点加成"""
        for loc_type, bonus in self.location_bonuses.items():
            if loc_type in location:
                return bonus
        return 1.0

    def _can_breakthrough(self, player) -> bool:
        """检查是否可以突破"""
        # TODO: 实际的突破条件检查
        # return player.attributes.cultivation_level >= 9
        return player.attributes.cultivation_level >= 5  # 简化版

    def _trigger_cultivation_event(self, context: CommandContext) -> None:
        """触发修炼随机事件"""
        events = [
            ("你突然有所顿悟，修炼效率大增！", 50),
            ("一只灵蝶飞过，带来了浓郁的灵气。", 30),
            ("你回想起师傅的教诲，对功法有了新的理解。", 40),
        ]

        event, bonus_exp = random.choice(events)
        context.output_manager.success(event)
        context.output_manager.success(f"额外获得 {bonus_exp} 点修为！")

    def get_help(self) -> str:
        return """修炼命令：修炼

用法：
  修炼

说明：
  进行打坐修炼，消耗20点体力，获得修为值。
  不同地点的修炼效率不同，灵气充沛的地方效率更高。
  修炼时有几率触发顿悟等特殊事件。
"""


class LearnSkillHandler(CultivationHandler):
    """学习技能命令处理器"""

    def __init__(self):
        super().__init__("learn_skill", [CommandType.LEARN_SKILL])

    def handle(self, context: CommandContext) -> CommandResult:
        """处理学习技能命令"""
        skill_name = context.command.parameters.get("skill")

        if not skill_name:
            context.output_manager.error("请指定要学习的技能")
            return CommandResult.failure("未指定技能")

        # TODO: 检查技能是否存在
        # skill_data = get_skill_data(skill_name)
        # if not skill_data:
        #     context.output_manager.error(f"未知的技能：{skill_name}")
        #     return CommandResult.failure("技能不存在")

        # 模拟技能数据
        skill_requirements = {
            "剑气斩": {"level": 5, "cost": 100},
            "金刚护体": {"level": 10, "cost": 200},
            "御剑术": {"level": 15, "cost": 500},
        }

        if skill_name not in skill_requirements:
            context.output_manager.error(f"未知的技能：{skill_name}")
            return CommandResult.failure("技能不存在")

        req = skill_requirements[skill_name]
        player = context.player

        # 检查等级要求
        if player.attributes.level < req["level"]:
            context.output_manager.error(f"等级不足，需要{req['level']}级")
            return CommandResult.failure("等级不足")

        # 检查技能点
        # TODO: 实际的技能点检查
        # if player.skill_points < req["cost"]:
        #     context.output_manager.error(f"技能点不足，需要{req['cost']}点")
        #     return CommandResult.failure("技能点不足")

        # 学习技能
        context.output_manager.narrative(f"你开始参悟{skill_name}的奥义...")
        context.output_manager.success(f"成功学会了{skill_name}！")

        # TODO: 实际添加技能
        # player.learn_skill(skill_name)

        # 显示技能描述
        skill_descs = {
            "剑气斩": "凝聚剑气进行远程攻击，威力强大",
            "金刚护体": "运转真气护体，大幅提升防御力",
            "御剑术": "御剑飞行，可以快速移动",
        }

        if skill_name in skill_descs:
            context.output_manager.info(skill_descs[skill_name])

        return CommandResult.success("学习成功", skill=skill_name)

    def get_help(self) -> str:
        return """学习技能命令：学习 <技能名>

用法：
  学习 剑气斩
  学习 金刚护体

说明：
  学习新的技能。需要满足等级要求并消耗技能点。
  可以在技能导师处查看可学习的技能列表。
"""


class BreakthroughHandler(CultivationHandler):
    """突破命令处理器"""

    def __init__(self):
        super().__init__("breakthrough", [CommandType.BREAKTHROUGH])
        self.realm_names = ["炼气期", "筑基期", "金丹期", "元婴期", "化神期"]

    def handle(self, context: CommandContext) -> CommandResult:
        """处理突破命令"""
        player = context.player

        # 检查是否满足突破条件
        if not self._check_breakthrough_requirements(player):
            context.output_manager.error("尚未满足突破条件")
            context.output_manager.info("突破需要：")
            context.output_manager.info("- 达到当前境界第9层")
            context.output_manager.info("- 足够的突破材料")
            context.output_manager.info("- 良好的状态（体力>80%）")
            return CommandResult.failure("条件不足")

        # 检查突破材料
        # TODO: 实际的材料检查
        required_items = self._get_breakthrough_items(player)

        # 开始突破
        context.output_manager.narrative("你深吸一口气，开始冲击更高的境界...")
        context.output_manager.warning("突破开始！请不要中断！")

        # 进入突破状态
        context.state_manager.push_context(
            GameContext.BREAKING_THROUGH, {"start_time": context.state_manager.state.game_time}
        )

        # 计算突破成功率
        success_rate = self._calculate_breakthrough_rate(player)
        context.output_manager.info(f"突破成功率：{int(success_rate * 100)}%")

        # 突破过程描述
        breakthrough_messages = [
            "磅礴的灵力在体内奔涌...",
            "你的经脉承受着巨大的压力...",
            "丹田中的真气开始发生质变...",
        ]

        for msg in breakthrough_messages:
            context.output_manager.narrative(msg)

        # 判定突破结果
        if random.random() < success_rate:
            # 突破成功
            self._handle_breakthrough_success(context, player)
        else:
            # 突破失败
            self._handle_breakthrough_failure(context, player)

        # 退出突破状态
        context.state_manager.pop_context()

        return CommandResult.success("突破结束")

    def _check_breakthrough_requirements(self, player) -> bool:
        """检查突破条件"""
        # 必须是第9层
        if player.attributes.cultivation_level < 9:
            return False

        # 体力要充足
        stamina_percent = player.attributes.current_stamina / player.attributes.max_stamina
        if stamina_percent < 0.8:
            return False

        return True

    def _get_breakthrough_items(self, player) -> dict:
        """获取突破所需材料"""
        realm_index = player.attributes.realm
        items = {
            0: {"筑基丹": 1},  # 炼气->筑基
            1: {"凝金丹": 1, "灵石": 100},  # 筑基->金丹
            2: {"结婴丹": 1, "灵石": 500},  # 金丹->元婴
            3: {"化神丹": 1, "灵石": 1000},  # 元婴->化神
        }
        return items.get(realm_index, {})

    def _calculate_breakthrough_rate(self, player) -> float:
        """计算突破成功率"""
        base_rate = 0.6

        # 悟性加成
        comprehension_bonus = player.attributes.get("comprehension", 50) / 200

        # 福缘加成
        luck_bonus = player.attributes.get("luck", 50) / 500

        # 状态加成
        state_bonus = (
            0.1 if player.attributes.current_stamina == player.attributes.max_stamina else 0
        )

        return min(0.95, base_rate + comprehension_bonus + luck_bonus + state_bonus)

    def _handle_breakthrough_success(self, context: CommandContext, player) -> None:
        """处理突破成功"""
        old_realm = self.realm_names[player.attributes.realm]

        # TODO: 实际的境界提升
        # player.attributes.realm += 1
        # player.attributes.cultivation_level = 1

        new_realm = (
            self.realm_names[player.attributes.realm + 1]
            if player.attributes.realm < 4
            else "未知境界"
        )

        context.output_manager.achievement(f"突破成功！从{old_realm}晋升到{new_realm}！")
        context.output_manager.success("你的实力大幅提升！")

        # 属性提升
        context.output_manager.info("属性提升：")
        context.output_manager.info("- 生命上限 +100")
        context.output_manager.info("- 法力上限 +50")
        context.output_manager.info("- 攻击力 +20")
        context.output_manager.info("- 防御力 +15")

        # 恢复状态
        context.output_manager.success("突破后你感觉神清气爽，状态全满！")

        # 更新统计
        context.state_manager.update_statistics("breakthroughs", 1)
        context.state_manager.add_achievement("first_breakthrough")

    def _handle_breakthrough_failure(self, context: CommandContext, player) -> None:
        """处理突破失败"""
        context.output_manager.error("突破失败！")
        context.output_manager.warning("你受到了反噬，损失了部分修为和生命值。")

        # 损失效果
        # TODO: 实际的损失计算
        # player.attributes.current_health *= 0.5
        # player.lose_cultivation_exp(100)

        context.output_manager.info("损失：")
        context.output_manager.info("- 当前生命值减半")
        context.output_manager.info("- 损失100点修为")

        context.output_manager.narrative("失败是成功之母，下次一定能成功！")

    def get_help(self) -> str:
        return """突破命令：突破

用法：
  突破

说明：
  尝试突破到更高的境界。突破需要满足以下条件：
  1. 达到当前境界第9层
  2. 拥有对应的突破丹药
  3. 体力充足（>80%）

  突破成功会大幅提升属性，失败则会受到反噬。
  成功率受悟性、福缘等因素影响。
"""


# 物品使用命令处理器
class UseItemHandler(CommandHandler):
    """使用物品命令处理器"""

    def __init__(self):
        super().__init__("use_item", [CommandType.USE_ITEM], CommandPriority.NORMAL)

    def can_handle(self, context: CommandContext) -> bool:
        """大部分情况下都可以使用物品"""
        # 突破中不能使用物品
        if context.game_context == GameContext.BREAKING_THROUGH:
            return False
        return True

    def handle(self, context: CommandContext) -> CommandResult:
        """处理使用物品命令"""
        item_name = context.command.parameters.get("item")

        if not item_name:
            context.output_manager.error("请指定要使用的物品")
            return CommandResult.failure("未指定物品")

        # TODO: 检查物品是否存在
        # item = player.inventory.get_item(item_name)
        # if not item:
        #     context.output_manager.error(f"你没有{item_name}")
        #     return CommandResult.failure("物品不存在")

        # 模拟物品效果
        item_effects = {
            "气血药水": {"type": "heal", "value": 100},
            "灵力药水": {"type": "mana", "value": 50},
            "体力药剂": {"type": "stamina", "value": 30},
            "修炼丹": {"type": "exp", "value": 200},
        }

        if item_name not in item_effects:
            context.output_manager.error(f"无法使用{item_name}")
            return CommandResult.failure("无法使用")

        effect = item_effects[item_name]
        player = context.player

        # 应用效果
        context.output_manager.info(f"你使用了{item_name}")

        if effect["type"] == "heal":
            # TODO: 实际回复生命
            # player.heal(effect["value"])
            context.output_manager.success(f"恢复了{effect['value']}点生命值")
        elif effect["type"] == "mana":
            # TODO: 实际回复法力
            context.output_manager.success(f"恢复了{effect['value']}点法力值")
        elif effect["type"] == "stamina":
            context.output_manager.success(f"恢复了{effect['value']}点体力值")
        elif effect["type"] == "exp":
            context.output_manager.success(f"获得了{effect['value']}点修为")

        # TODO: 从背包移除物品
        # player.inventory.remove_item(item_name, 1)

        return CommandResult.success("使用成功", item=item_name, effect=effect)

    def get_help(self) -> str:
        return """使用物品命令：使用 <物品名>

用法：
  使用 气血药水
  吃 回春丹
  服用 修炼丹

说明：
  使用背包中的消耗品。不同物品有不同效果：
  - 药水类：恢复生命值、法力值或体力值
  - 丹药类：增加修为或提供临时增益
  - 符咒类：提供各种特殊效果
"""


# 创建组合处理器
class CultivationCommandHandler(CommandHandler):
    """修炼命令组合处理器"""

    def __init__(self):
        super().__init__(
            "cultivation_commands",
            [
                CommandType.CULTIVATE,
                CommandType.LEARN_SKILL,
                CommandType.BREAKTHROUGH,
                CommandType.USE_ITEM,
            ],
            CommandPriority.NORMAL,
        )

        # 子处理器
        self.handlers = {
            CommandType.CULTIVATE: CultivateHandler(),
            CommandType.LEARN_SKILL: LearnSkillHandler(),
            CommandType.BREAKTHROUGH: BreakthroughHandler(),
            CommandType.USE_ITEM: UseItemHandler(),
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

        return CommandResult.failure("无法处理的修炼命令")

    def validate(self, context: CommandContext) -> Optional[str]:
        """验证命令"""
        cmd_type = context.command.command_type
        if cmd_type in self.handlers:
            return self.handlers[cmd_type].validate(context)
        return "未知的修炼命令"

    def get_help(self) -> str:
        """获取所有修炼命令的帮助"""
        help_text = "=== 修炼命令帮助 ===\n\n"
        for handler in self.handlers.values():
            help_text += handler.get_help() + "\n"
        return help_text
