"""
系统命令处理器

处理所有系统相关的命令（保存、加载、帮助、退出等）
"""

import json
import os
from datetime import datetime
from pathlib import Path
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


class SystemHandler(CommandHandler):
    """系统命令基类"""

    def __init__(self, name: str, command_types: List[CommandType]):
        # 系统命令优先级最高
        super().__init__(name, command_types, CommandPriority.SYSTEM)

    def can_handle(self, context: CommandContext) -> bool:
        """系统命令在任何情况下都可以使用"""
        return True


class SaveHandler(SystemHandler):
    """保存命令处理器"""

    def __init__(self):
        super().__init__("save", [CommandType.SAVE])
        self.save_dir = Path("saves")
        self.save_dir.mkdir(exist_ok=True)

    def handle(self, context: CommandContext) -> CommandResult:
        """处理保存命令"""
        # 检查是否可以保存
        if context.game_context == GameContext.COMBAT:
            context.output_manager.warning("战斗中无法保存游戏")
            return CommandResult.failure("战斗中无法保存")

        # 获取存档名称
        save_name = context.command.parameters.get("name")
        if not save_name:
            # 自动生成存档名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_name = f"autosave_{timestamp}"

        # 保存游戏状态
        try:
            save_data = context.state_manager.create_save_data()
            save_path = self.save_dir / f"{save_name}.json"

            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)

            context.output_manager.success(f"游戏已保存到: {save_name}")

            # 更新统计
            context.state_manager.update_statistics("games_saved", 1)

            return CommandResult.success("保存成功", save_name=save_name)

        except Exception as e:
            context.output_manager.error(f"保存失败: {str(e)}")
            return CommandResult.failure(f"保存失败: {str(e)}")

    def get_help(self) -> str:
        return """保存命令：保存 [存档名]

用法：
  保存          - 自动生成存档名保存
  保存 我的存档   - 使用指定名称保存

说明：
  保存当前游戏进度。战斗中无法保存。
  存档文件保存在 saves 目录下。
"""


class LoadHandler(SystemHandler):
    """加载命令处理器"""

    def __init__(self):
        super().__init__("load", [CommandType.LOAD])
        self.save_dir = Path("saves")

    def handle(self, context: CommandContext) -> CommandResult:
        """处理加载命令"""
        # 获取存档名称
        save_name = context.command.parameters.get("name")

        if not save_name:
            # 列出所有存档
            return self._list_saves(context)

        # 加载指定存档
        save_path = self.save_dir / f"{save_name}.json"

        if not save_path.exists():
            context.output_manager.error(f"存档不存在: {save_name}")
            return CommandResult.failure("存档不存在")

        try:
            with open(save_path, "r", encoding="utf-8") as f:
                save_data = json.load(f)

            # 确认是否加载
            context.output_manager.warning("加载存档将丢失当前进度！")
            context.output_manager.menu(["确认加载", "取消"], "是否继续？")

            # TODO: 等待用户确认
            # 这里暂时直接加载

            context.state_manager.load_save_data(save_data)
            context.output_manager.success(f"成功加载存档: {save_name}")

            return CommandResult.success("加载成功", save_name=save_name)

        except Exception as e:
            context.output_manager.error(f"加载失败: {str(e)}")
            return CommandResult.failure(f"加载失败: {str(e)}")

    def _list_saves(self, context: CommandContext) -> CommandResult:
        """列出所有存档"""
        if not self.save_dir.exists():
            context.output_manager.info("没有找到任何存档")
            return CommandResult.success("无存档")

        saves = []
        for save_file in self.save_dir.glob("*.json"):
            try:
                # 读取存档信息
                with open(save_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                save_info = {
                    "存档名": save_file.stem,
                    "角色": data.get("player", {}).get("name", "未知"),
                    "等级": data.get("player", {}).get("level", 0),
                    "游戏时间": f"{data.get('statistics', {}).get('play_time', 0):.1f}小时",
                    "保存时间": datetime.fromtimestamp(save_file.stat().st_mtime).strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                }
                saves.append(save_info)
            except:
                continue

        if saves:
            context.output_manager.system("=== 存档列表 ===")
            context.output_manager.output_table(saves)
            context.output_manager.info("\n使用 '加载 <存档名>' 来加载存档")
        else:
            context.output_manager.info("没有找到有效的存档")

        return CommandResult.success("列出存档", saves=saves)

    def get_help(self) -> str:
        return """加载命令：加载 [存档名]

用法：
  加载          - 显示所有存档
  加载 我的存档   - 加载指定存档

说明：
  加载之前保存的游戏进度。加载会覆盖当前进度，请谨慎操作。
"""


class HelpHandler(SystemHandler):
    """帮助命令处理器"""

    def __init__(self):
        super().__init__("help", [CommandType.HELP])

    def handle(self, context: CommandContext) -> CommandResult:
        """处理帮助命令"""
        # 获取帮助主题
        topic = context.command.parameters.get("topic")

        if topic:
            # 显示特定主题的帮助
            help_text = self._get_topic_help(topic)
        else:
            # 显示总体帮助
            help_text = self._get_general_help()

        context.output_manager.system(help_text)

        return CommandResult.success("显示帮助")

    def _get_general_help(self) -> str:
        """获取总体帮助"""
        return """
=== 修仙世界 游戏帮助 ===

基础命令：
  状态    - 查看角色状态
  背包    - 查看物品
  技能    - 查看技能列表
  地图    - 查看当前地图

探索命令：
  去 <地点>   - 前往指定地点
  探索       - 探索当前区域
  拾取       - 拾取物品

战斗命令：
  攻击 [目标]      - 普通攻击
  使用 <技能> [目标] - 使用技能
  防御           - 防御姿态
  逃跑           - 逃离战斗

交互命令：
  和 <NPC> 说话   - 与NPC对话
  交易 <商人>     - 打开交易

修炼命令：
  修炼          - 进行修炼
  学习 <技能>     - 学习技能
  突破          - 境界突破

系统命令：
  保存 [名称]     - 保存游戏
  加载 [名称]     - 加载存档
  帮助 [主题]     - 显示帮助
  退出          - 退出游戏

输入 '帮助 <命令类型>' 查看详细说明
例如：帮助 战斗
"""

    def _get_topic_help(self, topic: str) -> str:
        """获取特定主题的帮助"""
        topic_helps = {
            "战斗": """
=== 战斗系统帮助 ===

战斗基础：
- 进入战斗后，需要选择行动
- 每回合可以执行一个动作
- 速度决定行动顺序

战斗命令：
1. 攻击 [目标]
   - 进行普通攻击
   - 不指定目标时自动选择

2. 使用 <技能> [目标]
   - 消耗法力使用技能
   - 威力比普通攻击强

3. 防御
   - 减少受到的伤害
   - 下回合开始时解除

4. 逃跑
   - 尝试逃离战斗
   - 成功率取决于速度

战斗技巧：
- 合理使用技能和防御
- 注意法力值管理
- 某些技能有特殊效果
""",
            "修炼": """
=== 修炼系统帮助 ===

境界等级：
1. 炼气期 (1-9层)
2. 筑基期 (1-9层)
3. 金丹期 (1-9层)
4. 元婴期 (1-9层)
5. 化神期 (1-9层)

修炼方法：
- 修炼：增加修为值
- 战斗：获得经验和修为
- 完成任务：大量奖励

突破境界：
- 达到当前境界顶层
- 满足突破条件
- 使用突破命令

提升技巧：
- 找合适的修炼地点
- 使用修炼丹药
- 完成师门任务
""",
            "交易": """
=== 交易系统帮助 ===

交易基础：
- 与商人NPC交易
- 使用灵石作为货币

交易命令：
1. 交易 <商人名>
   - 打开交易界面

2. 购买流程：
   - 查看商品列表
   - 选择要购买的物品
   - 确认交易

3. 出售流程：
   - 选择出售选项
   - 选择要出售的物品
   - 确认价格

交易技巧：
- 不同商人卖不同物品
- 某些物品限量供应
- 商品价格可能变动
""",
        }

        return topic_helps.get(topic, f"没有关于 '{topic}' 的帮助信息")

    def get_help(self) -> str:
        return """帮助命令：帮助 [主题]

用法：
  帮助        - 显示总体帮助
  帮助 战斗    - 显示战斗系统帮助
  帮助 修炼    - 显示修炼系统帮助
  帮助 交易    - 显示交易系统帮助

说明：
  显示游戏帮助信息。可以指定主题查看详细说明。
"""


class QuitHandler(SystemHandler):
    """退出命令处理器"""

    def __init__(self):
        super().__init__("quit", [CommandType.QUIT])

    def handle(self, context: CommandContext) -> CommandResult:
        """处理退出命令"""
        # 检查是否有未保存的进度
        if context.state_manager.has_unsaved_changes():
            context.output_manager.warning("你有未保存的游戏进度！")
            context.output_manager.menu(["保存并退出", "直接退出", "取消"], "选择操作")

            # TODO: 等待用户选择
            # 这里暂时直接退出

        context.output_manager.system("感谢游玩，再见！")

        # 记录游戏时长
        play_time = context.state_manager.get_play_time()
        context.output_manager.info(f"本次游戏时长: {play_time:.1f} 小时")

        return CommandResult.success("退出游戏", should_quit=True)

    def get_help(self) -> str:
        return """退出命令：退出

用法：
  退出

说明：
  退出游戏。如果有未保存的进度，会提示是否保存。
"""


# 创建组合处理器
class SystemCommandHandler(CommandHandler):
    """系统命令组合处理器"""

    def __init__(self):
        super().__init__(
            "system_commands",
            [CommandType.SAVE, CommandType.LOAD, CommandType.HELP, CommandType.QUIT],
            CommandPriority.SYSTEM,
        )

        # 子处理器
        self.handlers = {
            CommandType.SAVE: SaveHandler(),
            CommandType.LOAD: LoadHandler(),
            CommandType.HELP: HelpHandler(),
            CommandType.QUIT: QuitHandler(),
        }

    def can_handle(self, context: CommandContext) -> bool:
        """系统命令总是可以处理"""
        return True

    def handle(self, context: CommandContext) -> CommandResult:
        """分发到对应的子处理器"""
        cmd_type = context.command.command_type
        if cmd_type in self.handlers:
            return self.handlers[cmd_type].handle(context)

        return CommandResult.failure("无法处理的系统命令")

    def validate(self, context: CommandContext) -> Optional[str]:
        """验证命令"""
        cmd_type = context.command.command_type
        if cmd_type in self.handlers:
            return self.handlers[cmd_type].validate(context)
        return "未知的系统命令"

    def get_help(self) -> str:
        """获取所有系统命令的帮助"""
        help_text = "=== 系统命令帮助 ===\n\n"
        for handler in self.handlers.values():
            help_text += handler.get_help() + "\n"
        return help_text
