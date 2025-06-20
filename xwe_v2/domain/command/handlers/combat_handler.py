"""
战斗命令处理器

处理所有战斗相关的命令
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


class CombatHandler(CommandHandler):
    """战斗命令基类"""

    def __init__(self, name: str, command_types: List[CommandType]):
        super().__init__(name, command_types, CommandPriority.HIGH)

    def can_handle(self, context: CommandContext) -> bool:
        """只在战斗中可以处理"""
        return context.game_context == GameContext.COMBAT

    def validate(self, context: CommandContext) -> Optional[str]:
        """验证战斗状态"""
        if not context.player:
            return "没有玩家角色"

        if not context.player.is_alive:
            return "你已经死亡"

        return None


class AttackHandler(CombatHandler):
    """攻击命令处理器"""

    def __init__(self):
        super().__init__("attack", [CommandType.ATTACK])

    def handle(self, context: CommandContext) -> CommandResult:
        """处理攻击命令"""
        target_name = context.command.target

        if not target_name:
            # 自动选择目标
            context.output_manager.info("自动选择最近的敌人作为目标")
            # TODO: 实现自动目标选择
            target_name = "敌人"

        # 输出攻击信息
        context.output_manager.combat(f"你向{target_name}发起攻击！")

        # TODO: 调用战斗系统执行攻击
        # combat_system = context.metadata.get('combat_system')
        # if combat_system:
        #     damage = combat_system.execute_attack(context.player, target)
        #     context.output_manager.combat(f"造成了 {damage} 点伤害！")

        # 模拟攻击结果
        damage = 50
        context.output_manager.combat(f"造成了 {damage} 点伤害！")

        return CommandResult.success("攻击成功", damage=damage)

    def get_help(self) -> str:
        return """攻击命令：攻击 [目标]

用法：
  攻击 妖兽      - 攻击指定目标
  攻击          - 自动选择最近的敌人

说明：
  在战斗中对目标进行普通攻击。如果不指定目标，会自动选择最近的敌人。
"""


class DefendHandler(CombatHandler):
    """防御命令处理器"""

    def __init__(self):
        super().__init__("defend", [CommandType.DEFEND])

    def handle(self, context: CommandContext) -> CommandResult:
        """处理防御命令"""
        context.output_manager.combat("你摆出防御姿态，准备抵挡攻击。")

        # TODO: 设置防御状态
        # context.player.set_defending(True)

        return CommandResult.success("进入防御状态")

    def get_help(self) -> str:
        return """防御命令：防御

用法：
  防御

说明：
  进入防御姿态，减少接下来受到的伤害。防御状态会在下回合开始时解除。
"""


class FleeHandler(CombatHandler):
    """逃跑命令处理器"""

    def __init__(self):
        super().__init__("flee", [CommandType.FLEE])

    def handle(self, context: CommandContext) -> CommandResult:
        """处理逃跑命令"""
        # 计算逃跑成功率
        flee_chance = 0.5  # TODO: 根据速度等属性计算

        import random

        if random.random() < flee_chance:
            context.output_manager.success("你成功逃离了战斗！")

            # TODO: 结束战斗
            # context.state_manager.end_combat({'fled': True})

            return CommandResult.success("逃跑成功")
        else:
            context.output_manager.warning("逃跑失败！")
            return CommandResult.failure("逃跑失败", continue_processing=True)

    def get_help(self) -> str:
        return """逃跑命令：逃跑

用法：
  逃跑

说明：
  尝试逃离战斗。成功率取决于你和敌人的速度差异。
  逃跑失败会浪费本回合的行动机会。
"""


class UseSkillHandler(CombatHandler):
    """使用技能命令处理器"""

    def __init__(self):
        super().__init__("use_skill", [CommandType.USE_SKILL])

    def handle(self, context: CommandContext) -> CommandResult:
        """处理使用技能命令"""
        skill_name = context.command.parameters.get("skill")
        target_name = context.command.target

        if not skill_name:
            context.output_manager.error("请指定要使用的技能")
            return CommandResult.failure("未指定技能")

        # TODO: 检查技能是否存在
        # skill = context.player.get_skill(skill_name)
        # if not skill:
        #     context.output_manager.error(f"你还没有学会技能：{skill_name}")
        #     return CommandResult.failure("技能不存在")

        # 输出使用技能
        if target_name:
            context.output_manager.combat(f"你对{target_name}使用了{skill_name}！")
        else:
            context.output_manager.combat(f"你使用了{skill_name}！")

        # TODO: 执行技能效果

        return CommandResult.success("技能使用成功", skill=skill_name)

    def validate(self, context: CommandContext) -> Optional[str]:
        """验证技能使用"""
        error = super().validate(context)
        if error:
            return error

        # TODO: 检查法力值
        # if context.player.current_mana < skill.mana_cost:
        #     return "法力值不足"

        # TODO: 检查技能冷却
        # if skill.is_on_cooldown():
        #     return f"技能冷却中，还需等待{skill.cooldown_remaining}回合"

        return None

    def get_help(self) -> str:
        return """使用技能命令：使用 <技能名> [目标]

用法：
  使用 剑气斩 妖兽    - 对指定目标使用技能
  使用 金刚护体       - 使用自身增益技能

说明：
  使用已学会的技能。某些技能需要指定目标，某些技能只能对自己使用。
  使用技能会消耗法力值，部分技能有冷却时间。
"""


# 创建一个组合处理器，可以处理所有战斗命令
class CombatCommandHandler(CommandHandler):
    """战斗命令组合处理器"""

    def __init__(self):
        super().__init__(
            "combat_commands",
            [CommandType.ATTACK, CommandType.DEFEND, CommandType.FLEE, CommandType.USE_SKILL],
            CommandPriority.HIGH,
        )

        # 子处理器
        self.handlers = {
            CommandType.ATTACK: AttackHandler(),
            CommandType.DEFEND: DefendHandler(),
            CommandType.FLEE: FleeHandler(),
            CommandType.USE_SKILL: UseSkillHandler(),
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

        return CommandResult.failure("无法处理的战斗命令")

    def validate(self, context: CommandContext) -> Optional[str]:
        """验证命令"""
        cmd_type = context.command.command_type
        if cmd_type in self.handlers:
            return self.handlers[cmd_type].validate(context)
        return "未知的战斗命令"

    def get_help(self) -> str:
        """获取所有战斗命令的帮助"""
        help_text = "=== 战斗命令帮助 ===\n\n"
        for handler in self.handlers.values():
            help_text += handler.get_help() + "\n"
        return help_text
