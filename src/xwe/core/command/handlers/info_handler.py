"""
信息命令处理器

处理所有信息查询相关的命令
"""

from typing import Optional, List, Dict, Any
from xwe.core.command.command_processor import (
    CommandHandler, CommandContext, CommandResult, CommandPriority
)
from xwe.core.command_parser import CommandType
from xwe.core.output import MessageType


class InfoHandler(CommandHandler):
    """信息命令基类"""
    
    def __init__(self, name: str, command_types: List[CommandType]):
        super().__init__(name, command_types, CommandPriority.LOW)
    
    def can_handle(self, context: CommandContext) -> bool:
        """信息命令总是可以处理"""
        return True


class StatusHandler(InfoHandler):
    """状态命令处理器"""
    
    def __init__(self):
        super().__init__("status", [CommandType.STATUS])
    
    def handle(self, context: CommandContext) -> CommandResult:
        """处理状态查看命令"""
        player = context.player
        
        if not player:
            context.output_manager.error("游戏尚未开始")
            return CommandResult.failure("无玩家角色")
        
        # 构建状态数据
        status_data = self._build_status_data(player)
        
        # 输出状态
        context.output_manager.output_status(status_data, "角色状态")
        
        # 输出额外信息
        self._output_additional_info(context, player)
        
        return CommandResult.success("显示状态成功")
    
    def _build_status_data(self, player) -> Dict[str, Any]:
        """构建状态数据"""
        return {
            "姓名": player.name,
            "境界": player.get_realm_info() if hasattr(player, 'get_realm_info') else "未知",
            "等级": player.attributes.cultivation_level if hasattr(player.attributes, 'cultivation_level') else 1,
            "生命": f"{int(player.attributes.current_health)}/{int(player.attributes.max_health)}",
            "灵力": f"{int(player.attributes.current_mana)}/{int(player.attributes.max_mana)}",
            "体力": f"{int(player.attributes.current_stamina)}/{int(player.attributes.max_stamina)}",
            "攻击": int(player.attributes.get('attack_power', 0)),
            "防御": int(player.attributes.get('defense', 0)),
            "速度": int(player.attributes.get('speed', 0)),
        }
    
    def _output_additional_info(self, context: CommandContext, player) -> None:
        """输出额外信息"""
        # 灵根信息
        if hasattr(player, 'spiritual_root') and player.spiritual_root:
            root = player.spiritual_root
            context.output_manager.info(
                f"灵根：{root.get('type', '未知')} - {', '.join(root.get('elements', []))}属性"
            )
        
        # 状态效果
        if hasattr(player, 'status_effects') and player.status_effects:
            if hasattr(player.status_effects, 'effects') and player.status_effects.effects:
                context.output_manager.info("当前状态：")
                for effect in player.status_effects.get_status_summary():
                    context.output_manager.info(f"  - {effect}")
    
    def get_help(self) -> str:
        return """状态命令：状态
        
用法：
  状态
  
说明：
  查看角色的详细状态，包括属性、境界、资源等信息。
"""


class InventoryHandler(InfoHandler):
    """背包命令处理器"""
    
    def __init__(self):
        super().__init__("inventory", [CommandType.INVENTORY])
    
    def handle(self, context: CommandContext) -> CommandResult:
        """处理背包查看命令"""
        player = context.player
        
        if not player:
            context.output_manager.error("游戏尚未开始")
            return CommandResult.failure("无玩家角色")
        
        context.output_manager.system("=== 背包 ===")
        
        if hasattr(player, 'inventory') and len(player.inventory) > 0:
            # 分类显示物品
            items_by_type = self._categorize_items(player.inventory)
            
            for category, items in items_by_type.items():
                if items:
                    context.output_manager.info(f"\n【{category}】")
                    for item_name, quantity in items:
                        context.output_manager.info(f"  {item_name} x{quantity}")
        else:
            context.output_manager.info("背包是空的。")
        
        # 显示装备
        self._show_equipment(context, player)
        
        return CommandResult.success("显示背包成功")
    
    def _categorize_items(self, inventory) -> Dict[str, List[tuple]]:
        """将物品分类"""
        categories = {
            "消耗品": [],
            "材料": [],
            "装备": [],
            "任务物品": [],
            "其他": []
        }
        
        # TODO: 根据物品类型分类
        for item_name, quantity in inventory.list_items():
            categories["其他"].append((item_name, quantity))
        
        return categories
    
    def _show_equipment(self, context: CommandContext, player) -> None:
        """显示装备"""
        if hasattr(player, 'equipment'):
            context.output_manager.info("\n【当前装备】")
            # TODO: 显示装备信息
            context.output_manager.info("  暂无装备")
    
    def get_help(self) -> str:
        return """背包命令：背包
        
用法：
  背包
  
说明：
  查看背包中的物品和当前装备。物品会按类型分类显示。
"""


class SkillsHandler(InfoHandler):
    """技能命令处理器"""
    
    def __init__(self):
        super().__init__("skills", [CommandType.SKILLS])
    
    def handle(self, context: CommandContext) -> CommandResult:
        """处理技能查看命令"""
        player = context.player
        
        if not player:
            context.output_manager.error("游戏尚未开始")
            return CommandResult.failure("无玩家角色")
        
        context.output_manager.system("=== 技能列表 ===")
        
        # TODO: 从技能系统获取技能
        # skill_system = context.metadata.get('skill_system')
        # if skill_system:
        #     skills = skill_system.get_character_skills(player)
        
        # 模拟技能数据
        skills = []
        
        if not skills:
            context.output_manager.info("你还没有学会任何技能。")
        else:
            for skill in skills:
                self._display_skill(context, skill)
        
        return CommandResult.success("显示技能成功")
    
    def _display_skill(self, context: CommandContext, skill) -> None:
        """显示单个技能"""
        status = ""
        if hasattr(skill, 'current_cooldown') and skill.current_cooldown > 0:
            status = f" (冷却: {skill.current_cooldown}回合)"
        
        context.output_manager.info(f"\n{skill.name}{status}")
        context.output_manager.info(f"  {skill.description}")
        context.output_manager.info(f"  消耗: 灵力{skill.mana_cost} 体力{skill.stamina_cost}")
    
    def get_help(self) -> str:
        return """技能命令：技能
        
用法：
  技能
  
说明：
  查看已学会的所有技能，包括技能描述、消耗和冷却状态。
"""


class MapHandler(InfoHandler):
    """地图命令处理器"""
    
    def __init__(self):
        super().__init__("map", [CommandType.MAP])
    
    def handle(self, context: CommandContext) -> CommandResult:
        """处理地图查看命令"""
        player = context.player
        location = context.current_location
        
        if not player:
            context.output_manager.error("游戏尚未开始")
            return CommandResult.failure("无玩家角色")
        
        context.output_manager.system("=== 当前位置 ===")
        context.output_manager.info(f"你在: {location}")
        
        # TODO: 从世界地图系统获取信息
        # world_map = context.metadata.get('world_map')
        # location_manager = context.metadata.get('location_manager')
        
        # 模拟地图信息
        context.output_manager.info("\n【可前往的地点】")
        nearby_locations = [
            ("青云山", "修炼圣地", 1),
            ("妖兽森林", "危险区域", 3),
            ("主城", "繁华都市", 0)
        ]
        
        for name, desc, danger in nearby_locations:
            danger_stars = "★" * danger
            context.output_manager.info(f"  {name} - {desc} [危险: {danger_stars}]")
        
        # 显示探索进度
        context.output_manager.info("\n【探索进度】")
        context.output_manager.output_progress(3, 10, "当前区域")
        
        return CommandResult.success("显示地图成功")
    
    def get_help(self) -> str:
        return """地图命令：地图
        
用法：
  地图
  
说明：
  查看当前位置和周围可以前往的地点。显示各地点的危险等级和探索进度。
"""


# 创建组合处理器
class InfoCommandHandler(CommandHandler):
    """信息命令组合处理器"""
    
    def __init__(self):
        super().__init__(
            "info_commands",
            [CommandType.STATUS, CommandType.INVENTORY, CommandType.SKILLS, CommandType.MAP],
            CommandPriority.LOW
        )
        
        self.handlers = {
            CommandType.STATUS: StatusHandler(),
            CommandType.INVENTORY: InventoryHandler(),
            CommandType.SKILLS: SkillsHandler(),
            CommandType.MAP: MapHandler(),
        }
    
    def can_handle(self, context: CommandContext) -> bool:
        """检查是否可以处理"""
        return context.command.command_type in self.handlers
    
    def handle(self, context: CommandContext) -> CommandResult:
        """分发到对应的子处理器"""
        cmd_type = context.command.command_type
        if cmd_type in self.handlers:
            return self.handlers[cmd_type].handle(context)
        
        return CommandResult.failure("无法处理的信息命令")
    
    def get_help(self) -> str:
        """获取所有信息命令的帮助"""
        help_text = "=== 信息命令帮助 ===\n\n"
        for handler in self.handlers.values():
            help_text += handler.get_help() + "\n"
        return help_text
