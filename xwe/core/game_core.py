# core/game_core.py
"""
游戏核心模块 - 修改版，集成了Roll系统

管理游戏主循环和状态。
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import json
import os
from datetime import datetime

from ..engine.expression import ExpressionParser
from .data_loader import DataLoader
from .attributes import AttributeSystem
from .character import Character, CharacterType
from .inventory import Inventory
from .skills import SkillSystem
from .combat import CombatSystem, CombatState, CombatAction, CombatActionType
from .ai import AIController
from .command_parser import CommandParser, CommandType, ParsedCommand
from .nlp import NLPProcessor, NLPConfig
from ..world import WorldMap, LocationManager, EventSystem, AreaType
# from ..npc import NPCManager, DialogueSystem, TradingSystem  # 移到使用时导入，避免循环依赖
from .roll_system import CharacterRoller  # 导入Roll系统

# 导入优化系统
from .chinese_dragon_art import get_dragon_art, get_dragon_for_scene
from .status_manager import StatusDisplayManager
from .achievement_system import AchievementSystem
from .command_router import CommandRouter, CommandPriority
from .event_system import ImmersiveEventSystem, EventType, SpecialEventHandler

logger = logging.getLogger(__name__)


@dataclass
class GameState:
    """游戏状态"""
    player: Optional[Character] = None
    current_location: str = "qingyun_city"
    current_combat: Optional[str] = None
    game_time: int = 0  # 游戏时间（回合数）
    flags: Dict[str, Any] = field(default_factory=dict)
    npcs: Dict[str, Character] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为可序列化的字典"""
        return {
            'player': self.player.to_dict() if self.player else None,
            'current_location': self.current_location,
            'current_combat': self.current_combat,
            'game_time': self.game_time,
            'flags': self.flags,
            'npcs': {npc_id: npc.to_dict() for npc_id, npc in self.npcs.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        """从字典创建游戏状态"""
        state = cls()
        
        if data.get('player'):
            # TODO: 实现Character.from_dict
            pass
        
        state.current_location = data.get('current_location', 'qingyun_city')
        state.current_combat = data.get('current_combat')
        state.game_time = data.get('game_time', 0)
        state.flags = data.get('flags', {})
        
        return state


class GameCore:
    """
    游戏核心类
    
    管理所有游戏系统和主循环。
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        初始化游戏核心
        
        Args:
            data_path: 数据文件路径
        """
        # 初始化系统
        self.data_loader = DataLoader(data_path)
        self.parser = ExpressionParser()
        self.attribute_system = AttributeSystem(self.parser)
        self.skill_system = SkillSystem(self.data_loader, self.parser)
        self.combat_system = CombatSystem(self.skill_system, self.parser)
        self.ai_controller = AIController(self.skill_system)
        self.command_parser = CommandParser()
        
        # 初始化NLP处理器
        # 从环境变量获取LLM提供者
        llm_provider = os.getenv('LLM_PROVIDER', 'deepseek')
        
        nlp_config = NLPConfig(
            enable_llm=True,
            llm_provider=llm_provider,  # 使用真实的API
            fallback_to_rules=True,
            confidence_threshold=0.5  # 降低阈值，让更多命令被识别
        )
        self.nlp_processor = NLPProcessor(self.command_parser, nlp_config)
        
        # 初始化世界系统
        self.world_map = WorldMap()
        self.location_manager = LocationManager(self.world_map)
        self.event_system = EventSystem()
        
        # 初始化NPC系统
        # 局部导入避免循环依赖
        from ..npc import NPCManager, DialogueSystem, TradingSystem
        
        self.dialogue_system = DialogueSystem()
        self.npc_manager = NPCManager(self.dialogue_system)
        self.trading_system = TradingSystem()
        
        # 初始化Roll系统
        self.character_roller = CharacterRoller()
        
        # 初始化优化系统
        self.status_manager = StatusDisplayManager()
        self.achievement_system = AchievementSystem()
        self.command_router = CommandRouter()
        self.immersive_event_system = ImmersiveEventSystem(self.output)
        
        # 游戏状态
        self.game_state = GameState()
        self.running = False
        
        # 输出缓冲
        self.output_buffer: List[str] = []
        
        # 临时保存的roll结果
        self.current_roll_result = None
        
        # 游戏统计
        self.stats = {
            'enemies_defeated': 0,
            'win_streak': 0,
            'areas_explored': set(),
            'cultivation_time': 0,
            'gold': 0
        }
        
        logger.info("游戏核心初始化完成")
    
    def start_new_game(self, player_name: str = "无名侠客"):
        """
        开始新游戏 - 集成Roll系统
        
        Args:
            player_name: 玩家名称
        """
        # 设置游戏运行状态（修复主循环退出问题）
        self.running = True
        logger.info("[GameCore] 游戏已启动，进入运行状态")
        
        # 显示开场（使用中国龙艺术）
        self.output(get_dragon_for_scene('welcome'))
        self.output("")
        self.output("=== 仙侠世界 ===")
        self.output(f"欢迎来到玄苍界！")
        self.output("")
        self.output("在踏入这个充满机遇与危险的世界之前，")
        self.output("让我们先看看命运为你准备了什么样的开局...")
        self.output("")
        
        # 进入Roll流程
        self._character_creation_flow(player_name)
    def _character_creation_flow(self, player_name: str):
        """角色创建流程 - 使用Roll系统"""
        self.output("=== 开局Roll ===")
        self.output("你可以无限次重置角色面板，直到获得满意的属性。")
        self.output("每次Roll都会随机生成：灵根、命格、天赋、系统等。")
        self.output("")
        
        confirmed = False
        roll_count = 0
        best_roll = None
        best_score = 0
        
        while not confirmed:
            roll_count += 1
            
            # 执行Roll
            self.output(f"第 {roll_count} 次Roll...")
            self.output("-" * 60)
            
            roll_result = self.character_roller.roll()
            self.current_roll_result = roll_result
            
            # 显示Roll结果
            self._display_roll_result(roll_result)
            
            # 记录最佳结果
            if roll_result.combat_power > best_score:
                best_score = roll_result.combat_power
                best_roll = roll_result
            
            # 询问玩家
            self.output("")
            self.output("选项：")
            self.output("1. 使用这个角色开始游戏")
            self.output("2. 重新Roll")
            if roll_count > 1:
                self.output("3. 使用之前最好的角色")
            self.output("请选择 (输入数字):")
            
            # 等待玩家输入
            self.game_state.flags['waiting_for_roll_choice'] = True
            self.game_state.flags['roll_count'] = roll_count
            self.game_state.flags['best_roll'] = best_roll
            self.game_state.flags['player_name'] = player_name
            
            return  # 返回主循环等待输入
    
    def _display_roll_result(self, roll_result):
        """显示Roll结果"""
        # 基础信息
        self.output(f"姓名：{roll_result.name} ({roll_result.gender})")
        self.output(f"身份：{roll_result.identity} - {roll_result.identity_desc}")
        self.output("")
        
        # 基础属性
        self.output("【基础属性】")
        attrs = roll_result.attributes
        self.output(f"攻击力：{attrs['attack']:<3} 防御力：{attrs['defense']:<3} 气血值：{attrs['health']}")
        self.output(f"灵力值：{attrs['mana']:<3} 速度：{attrs['speed']:<3}   悟性：{attrs['comprehension']}")
        self.output(f"气运：{attrs['luck']:<3}   根骨：{attrs['constitution']:<3} 魅力：{attrs['charm']}")
        self.output("")
        
        # 灵根
        self.output(f"【灵根】{roll_result.spiritual_root_type}")
        self.output(f"属性：{', '.join(roll_result.spiritual_root_elements)}")
        self.output(f"说明：{roll_result.spiritual_root_desc}")
        self.output("")
        
        # 命格
        self.output(f"【命格】{roll_result.destiny} ({roll_result.destiny_rarity})")
        self.output(f"说明：{roll_result.destiny_desc}")
        self.output("")
        
        # 天赋
        self.output("【天赋】")
        for i, talent in enumerate(roll_result.talents, 1):
            self.output(f"{i}. {talent['name']} - {talent['description']}")
        self.output("")
        
        # 系统
        if roll_result.system:
            self.output(f"【系统】{roll_result.system['name']} ({roll_result.system['rarity']})")
            self.output(f"说明：{roll_result.system['description']}")
            self.output("功能：")
            for feature in roll_result.system['features']:
                self.output(f"  • {feature}")
            self.output("")
        
        # 综合评价
        self.output("【综合评价】")
        self.output(f"战斗力评分：{roll_result.combat_power}")
        self.output(f"总体评级：{roll_result.overall_rating}")
        
        if roll_result.special_tags:
            self.output(f"特殊标签：{', '.join(roll_result.special_tags)}")
            
        self.output("-" * 60)
    
    def _create_player_from_roll(self, name: str, roll_result) -> Character:
        """根据Roll结果创建玩家角色"""
        # 获取模板
        player_template = self.data_loader.get_player_template()
        
        # 创建角色
        character = Character.from_template(player_template.get('initial_state', {}))
        character.name = name
        character.character_type = CharacterType.PLAYER
        
        # 设置性别
        character.extra_data['gender'] = roll_result.gender
        character.extra_data['identity'] = roll_result.identity
        
        # 设置属性 - 需要映射Roll系统的属性到游戏系统
        # Roll系统：attack, defense, health, mana, speed, comprehension, luck, constitution, charm
        # 游戏系统：strength, constitution, agility, intelligence, willpower, comprehension, luck
        
        # 映射属性
        character.attributes.strength = roll_result.attributes.get('attack', 10) // 2
        character.attributes.constitution = roll_result.attributes.get('constitution', 10)
        character.attributes.agility = roll_result.attributes.get('speed', 10)
        character.attributes.intelligence = roll_result.attributes.get('mana', 100) // 10
        character.attributes.willpower = roll_result.attributes.get('defense', 10) // 2
        character.attributes.comprehension = roll_result.attributes.get('comprehension', 10)
        character.attributes.luck = roll_result.attributes.get('luck', 10)
        
        # 设置灵根
        character.spiritual_root = {
            'type': roll_result.spiritual_root_type,
            'elements': roll_result.spiritual_root_elements,
            'description': roll_result.spiritual_root_desc
        }
        
        # 设置命格
        character.extra_data['destiny'] = {
            'name': roll_result.destiny,
            'description': roll_result.destiny_desc,
            'rarity': roll_result.destiny_rarity,
            'effects': roll_result.destiny_effects
        }
        
        # 设置天赋
        character.extra_data['talents'] = roll_result.talents
        
        # 设置系统
        if roll_result.system:
            character.extra_data['system'] = roll_result.system
            # TODO: 实现系统功能
        
        # 重新计算衍生属性
        character.attributes.calculate_derived_attributes()
        
        # 添加初始技能
        for skill_id in player_template.get('initial_skills', []):
            character.learn_skill(skill_id)
        
        logger.info(f"根据Roll结果创建玩家角色: {name}")
        return character
    
    def _handle_roll_choice(self, choice: str):
        """处理Roll选择"""
        if not self.game_state.flags.get('waiting_for_roll_choice'):
            return
        
        roll_count = self.game_state.flags.get('roll_count', 0)
        best_roll = self.game_state.flags.get('best_roll')
        player_name = self.game_state.flags.get('player_name', '无名侠客')
        
        if choice == '1':
            # 使用当前角色
            if self.current_roll_result:
                # 使用玩家输入的名字替换Roll的随机名字
                final_name = player_name if player_name != "无名侠客" else self.current_roll_result.name
                
                self.game_state.player = self._create_player_from_roll(final_name, self.current_roll_result)
                self._finalize_character_creation()
                
        elif choice == '2':
            # 重新Roll
            self.game_state.flags['waiting_for_roll_choice'] = False
            self._character_creation_flow(player_name)
            
        elif choice == '3' and roll_count > 1 and best_roll:
            # 使用最佳角色
            final_name = player_name if player_name != "无名侠客" else best_roll.name
            self.game_state.player = self._create_player_from_roll(final_name, best_roll)
            self._finalize_character_creation()
            
        else:
            self.output("无效的选择，请输入对应的数字。")
    
    def _finalize_character_creation(self):
        """完成角色创建"""
        # 清理标志
        self.game_state.flags.pop('waiting_for_roll_choice', None)
        self.game_state.flags.pop('roll_count', None)
        self.game_state.flags.pop('best_roll', None)
        self.game_state.flags.pop('player_name', None)
        
        # 初始化游戏世界
        self._init_world()
        
        # 解锁第一个成就
        self.achievement_system.check_achievement('first_step', 1)
        
        # 显示游戏开始
        self.output("")
        self.output("=== 游戏开始 ===")
        self.output(f"你是{self.game_state.player.extra_data.get('identity', '一名散修')}，")
        self.output("怀着对长生的渴望，踏上了艰难而充满机遇的修仙之路。")
        self.output("")
        self.output("输入 '帮助' 查看可用命令。")
        self.output("")
        
        # 显示初始位置
        self._show_location()
        
        # 触发开局事件
        self.immersive_event_system.start_event("start_journey", {
            'player': self.game_state.player,
            'location': self.game_state.current_location
        })
    
    def _create_player(self, name: str, template: Dict[str, Any]) -> Character:
        """创建玩家角色（旧方法，保留作为备用）"""
        # 使用模板创建角色
        character = Character.from_template(template.get('initial_state', {}))
        character.name = name
        character.character_type = CharacterType.PLAYER
        
        # 添加初始技能
        for skill_id in template.get('initial_skills', []):
            character.learn_skill(skill_id)
        
        logger.info(f"创建玩家角色: {name}")
        return character
    
    def _init_world(self):
        """初始化游戏世界"""
        # 加载世界配置
        world_config = self.data_loader.get_world_config()
        
        # 初始化默认地图
        from ..world.world_map import DEFAULT_MAP_DATA, Region
        for region_data in DEFAULT_MAP_DATA['regions']:
            region = Region.from_dict(region_data)
            self.world_map.add_region(region)
        
        for area_data in DEFAULT_MAP_DATA['areas']:
            from ..world.world_map import Area
            area = Area.from_dict(area_data)
            self.world_map.add_area(area)
        
        # 设置玩家初始位置
        if self.game_state.player:
            self.location_manager.set_location(self.game_state.player.id, "qingyun_city")
            self.game_state.current_location = "qingyun_city"
            self.world_map.discover_area("qingyun_city")
        
        # 创建一些初始NPC
        self._create_initial_npcs()
        
        logger.info("游戏世界初始化完成")
    
    def _create_initial_npcs(self):
        """创建初始NPC"""
        npc_templates = self.data_loader.get_npc_templates()
        
        # 在主城创建一些NPC
        if 'npcs' in npc_templates:
            for npc_data in npc_templates['npcs'][:3]:  # 只创建前3个
                # 检查是否有对应的NPC档案
                npc_name = npc_data.get('name', '')
                npc_id = None
                
                # 根据名称找到对应的NPC ID
                if '王' in npc_name and '板' in npc_name:
                    npc_id = 'npc_wang_boss'
                elif '云梦儿' in npc_name:
                    npc_id = 'npc_yun_menger'
                elif '李太虚' in npc_name:
                    npc_id = 'npc_li_taixu'
                
                if npc_id and npc_id in self.npc_manager.npc_profiles:
                    # 使用NPC管理器创建
                    npc = self.npc_manager.create_npc_character(npc_id, npc_data)
                    if npc:
                        self.game_state.npcs[npc_id] = npc
                        
                        # 设置NPC位置
                        profile = self.npc_manager.get_npc_profile(npc_id)
                        if profile and profile.home_location:
                            self.location_manager.set_location(npc_id, profile.home_location)
                            self.npc_manager.set_npc_location(npc_id, profile.home_location)
                        
                        logger.info(f"创建NPC: {npc.name} 于 {profile.home_location if profile else '未知'}")
                else:
                    # 使用旧方法创建
                    npc = Character.from_template(npc_data)
                    self.game_state.npcs[npc.id] = npc
                    
                    # 设置NPC位置
                    npc_location = npc.extra_data.get('location', 'qingyun_city')
                    if npc_location == '青云城':
                        npc_location = 'qingyun_city'  # 转换为区域ID
                    self.location_manager.set_location(npc.id, npc_location)
                    
                    logger.info(f"创建NPC: {npc.name} 于 {npc_location}")
    
    def process_command(self, input_text: str):
        """
        处理玩家命令
        
        Args:
            input_text: 玩家输入
        """
        if not self.running:
            return
        
        # 如果在等待Roll选择
        if self.game_state.flags.get('waiting_for_roll_choice'):
            self._handle_roll_choice(input_text.strip())
            return
        
        # 检查是否在对话中
        if self.game_state.flags.get('in_dialogue', False):
            # 处理对话选择
            if input_text.isdigit():
                choice_index = int(input_text) - 1
                dialogue_choices = self.game_state.flags.get('dialogue_choices', [])
                
                if 0 <= choice_index < len(dialogue_choices):
                    self._process_dialogue_choice(dialogue_choices[choice_index])
                else:
                    self.output("无效的选择。")
                return
            elif input_text.lower() in ['quit', 'exit', '退出对话', '结束对话']:
                self._end_dialogue()
                return
        
        # 使用命令路由器（优先级系统）
        # 设置NLP处理器
        def nlp_handler(text, context):
            parsed = self.nlp_processor.parse(text, context)
            return {
                'command_type': parsed.command_type.value if parsed.command_type != CommandType.UNKNOWN else 'unknown',
                'parameters': {
                    'target': parsed.target,
                    'skill': parsed.parameters.get('skill'),
                    'location': parsed.parameters.get('location'),
                    **parsed.parameters
                }
            }
        
        self.command_router.set_nlp_handler(nlp_handler)
        
        # 设置当前上下文
        if self.game_state.current_combat:
            self.command_router.set_context('battle')
        else:
            self.command_router.set_context('exploration')
        
        # 路由命令
        cmd_type, params = self.command_router.route_command(input_text)
        
        # 如果命令不明确
        if cmd_type == 'unknown':
            self.output("我不太明白你的意思。")
            self.output("你可以说：")
            context = self._build_command_context()
            suggestions = self.nlp_processor.get_suggestions("", context)
            for suggestion in suggestions[:5]:
                self.output(f"  - {suggestion}")
            self.output("输入 '帮助' 查看所有命令。")
            return
        
        # 根据游戏状态处理命令
        if self.game_state.current_combat:
            self._process_combat_command_v2(cmd_type, params)
        else:
            self._process_normal_command_v2(cmd_type, params)
        
        # 更新游戏时间
        self.game_state.game_time += 1
    
    def _build_command_context(self) -> Dict[str, Any]:
        """构建命令上下文"""
        context = {
            'current_location': self.game_state.current_location,
            'in_combat': bool(self.game_state.current_combat),
            'game_time': self.game_state.game_time
        }
        
        # 添加战斗上下文
        if self.game_state.current_combat:
            combat_state = self.combat_system.get_combat(self.game_state.current_combat)
            if combat_state:
                player = self.game_state.player
                enemies = combat_state.get_enemies(player)
                context['enemies'] = [
                    {'id': e.id, 'name': e.name, 'health_percent': e.attributes.current_health / e.attributes.max_health}
                    for e in enemies if e.is_alive
                ]
        
        # 添加可用技能
        if self.game_state.player:
            skills = self.skill_system.get_character_skills(self.game_state.player)
            context['available_skills'] = [skill.name for skill in skills]
        
        # 添加周围NPC
        npcs_here = [
            npc.name for npc in self.game_state.npcs.values()
            if npc.extra_data.get('location') == self.game_state.current_location
        ]
        if npcs_here:
            context['nearby_npcs'] = npcs_here
        
        return context
    
    def _process_normal_command(self, command: ParsedCommand):
        """处理非战斗状态的命令"""
        if command.command_type == CommandType.STATUS:
            self._show_status()
            
        elif command.command_type == CommandType.INVENTORY:
            self._show_inventory()
            
        elif command.command_type == CommandType.SKILLS:
            self._show_skills()
            
        elif command.command_type == CommandType.MAP:
            self._show_map()
            
        elif command.command_type == CommandType.CULTIVATE:
            self._do_cultivate()
            
        elif command.command_type == CommandType.ATTACK:
            if command.target:
                self._start_combat(command.target)
            else:
                self.output("攻击谁？")
                
        elif command.command_type == CommandType.EXPLORE:
            self._do_explore()
            
        elif command.command_type == CommandType.MOVE:
            if command.parameters.get('location'):
                self._do_move(command.parameters['location'])
            else:
                self.output("要去哪里？")
            
        elif command.command_type == CommandType.TALK:
            if command.target:
                self._do_talk(command.target)
            else:
                self.output("要和谁说话？")
            
        elif command.command_type == CommandType.HELP:
            self.output(self.command_parser.get_help_text())
            
        elif command.command_type == CommandType.SAVE:
            self._save_game()
            
        elif command.command_type == CommandType.QUIT:
            self._quit_game()
            
        else:
            self.output("无法理解的命令。输入 '帮助' 查看可用命令。")
    
    def _process_combat_command(self, command: ParsedCommand):
        """处理战斗状态的命令"""
        combat_state = self.combat_system.get_combat(self.game_state.current_combat)
        if not combat_state:
            return
        
        player = self.game_state.player
        
        # 构建战斗行动
        action = None
        
        if command.command_type == CommandType.ATTACK:
            # 普通攻击
            if command.target:
                target = self._find_combat_target(combat_state, command.target)
                if target:
                    action = CombatAction(
                        action_type=CombatActionType.ATTACK,
                        actor_id=player.id,
                        target_ids=[target.id]
                    )
                else:
                    self.output(f"找不到目标: {command.target}")
            else:
                # 自动选择目标
                enemies = combat_state.get_enemies(player)
                if enemies:
                    action = CombatAction(
                        action_type=CombatActionType.ATTACK,
                        actor_id=player.id,
                        target_ids=[enemies[0].id]
                    )
                    
        elif command.command_type == CommandType.USE_SKILL:
            # 使用技能
            skill_name = command.parameters.get('skill', '')
            skill = self._find_skill_by_name(skill_name)
            
            if skill and player.has_skill(skill.id):
                target = None
                if command.target:
                    target = self._find_combat_target(combat_state, command.target)
                
                if skill.target_type.value == 'self':
                    target_ids = [player.id]
                elif skill.target_type.value == 'single_enemy' and target:
                    target_ids = [target.id]
                elif skill.target_type.value == 'all_enemies':
                    enemies = combat_state.get_enemies(player)
                    target_ids = [e.id for e in enemies[:skill.max_targets]]
                else:
                    target_ids = []
                
                if target_ids or skill.target_type.value in ['self', 'all_enemies']:
                    action = CombatAction(
                        action_type=CombatActionType.SKILL,
                        actor_id=player.id,
                        target_ids=target_ids,
                        skill_id=skill.id
                    )
                else:
                    self.output(f"无法确定技能目标")
            else:
                self.output(f"你还没有学会技能: {skill_name}")
                
        elif command.command_type == CommandType.DEFEND:
            # 防御
            action = CombatAction(
                action_type=CombatActionType.DEFEND,
                actor_id=player.id
            )
            
        elif command.command_type == CommandType.FLEE:
            # 逃跑
            if self._try_flee():
                return
            else:
                self.output("逃跑失败！")
                action = CombatAction(
                    action_type=CombatActionType.WAIT,
                    actor_id=player.id
                )
        
        # 执行玩家行动
        if action:
            result = self.combat_system.execute_action(
                self.game_state.current_combat,
                action
            )
            
            # 显示结果
            self._show_combat_result(result)
            
            # NPC行动
            self._process_npc_turns(combat_state)
            
            # 检查战斗是否结束
            if combat_state.is_combat_over():
                self._end_combat(combat_state)
    
    def _find_combat_target(self, 
                            combat_state: CombatState, 
                            target_name: str) -> Optional[Character]:
        """在战斗中查找目标"""
        for char in combat_state.participants.values():
            if target_name in char.name and char.is_alive:
                return char
        return None
    
    def _find_skill_by_name(self, skill_name: str):
        """通过名称查找技能"""
        for skill_id, skill in self.skill_system.skills.items():
            if skill_name in skill.name:
                return skill
        return None
    
    def _show_status(self):
        """显示角色状态"""
        player = self.game_state.player
        
        self.output("=== 角色状态 ===")
        self.output(f"姓名: {player.name}")
        self.output(f"性别: {player.extra_data.get('gender', '未知')}")
        self.output(f"身份: {player.extra_data.get('identity', '散修')}")
        self.output(f"境界: {player.get_realm_info()}")
        
        # 显示灵根
        if hasattr(player, 'spiritual_root') and player.spiritual_root:
            root = player.spiritual_root
            self.output(f"灵根: {root.get('type', '未知')} - {', '.join(root.get('elements', []))}属性")
        else:
            self.output(f"灵根: {player.get_spiritual_root_description()}")
        
        # 显示命格
        destiny = player.extra_data.get('destiny')
        if destiny:
            self.output(f"命格: {destiny['name']} ({destiny['rarity']})")
        
        # 显示系统
        system = player.extra_data.get('system')
        if system:
            self.output(f"系统: {system['name']} ({system['rarity']})")
        
        self.output("")
        
        # 资源状态
        self.output(f"气血: {player.attributes.current_health:.0f}/{player.attributes.max_health:.0f}")
        self.output(f"灵力: {player.attributes.current_mana:.0f}/{player.attributes.max_mana:.0f}")
        self.output(f"体力: {player.attributes.current_stamina:.0f}/{player.attributes.max_stamina:.0f}")
        self.output("")
        
        # 属性
        self.output("【基础属性】")
        self.output(f"力量: {player.attributes.strength}")
        self.output(f"体质: {player.attributes.constitution}")
        self.output(f"敏捷: {player.attributes.agility}")
        self.output(f"智力: {player.attributes.intelligence}")
        self.output(f"意志: {player.attributes.willpower}")
        self.output(f"悟性: {player.attributes.comprehension}")
        self.output(f"福缘: {player.attributes.luck}")
        self.output("")
        
        # 战斗属性
        self.output("【战斗属性】")
        self.output(f"攻击力: {player.attributes.get('attack_power'):.0f}")
        self.output(f"法术威力: {player.attributes.get('spell_power'):.0f}")
        self.output(f"防御力: {player.attributes.get('defense'):.0f}")
        self.output(f"法术抗性: {player.attributes.get('magic_resistance'):.0f}")
        
        # 天赋
        talents = player.extra_data.get('talents', [])
        if talents:
            self.output("")
            self.output("【天赋】")
            for talent in talents:
                self.output(f"- {talent['name']}: {talent['description']}")
        
        # 状态效果
        if player.status_effects.effects:
            self.output("")
            self.output("【状态效果】")
            for status in player.status_effects.get_status_summary():
                self.output(f"- {status}")
    
    def _show_inventory(self):
        """显示背包"""
        player = self.game_state.player
        
        self.output("=== 背包 ===")
        
        if len(player.inventory) == 0:
            self.output("背包是空的。")
        else:
            for name, qty in player.inventory.list_items():
                self.output(f"- {name} x{qty}")
    
    def _show_skills(self):
        """显示技能列表"""
        player = self.game_state.player
        skills = self.skill_system.get_character_skills(player)
        
        self.output("=== 技能列表 ===")
        
        if not skills:
            self.output("你还没有学会任何技能。")
        else:
            for skill in skills:
                status = ""
                if skill.current_cooldown > 0:
                    status = f" (冷却: {skill.current_cooldown}回合)"
                
                self.output(f"{skill.name}{status}")
                self.output(f"  {skill.description}")
                self.output(f"  消耗: 灵力{skill.mana_cost} 体力{skill.stamina_cost}")
                self.output("")
    
    def _show_map(self):
        """显示地图"""
        player = self.game_state.player
        if not player:
            return
            
        current_area_id = self.location_manager.get_location(player.id)
        if not current_area_id:
            self.output("你不知道自己在哪里。")
            return
            
        current_area = self.world_map.get_area(current_area_id)
        if not current_area:
            return
            
        self.output("=== 当前位置 ===")
        self.output(f"你在: {current_area.name}")
        self.output(f"危险等级: {'★' * current_area.danger_level}")
        self.output("")
        
        # 显示已发现的大区域
        regions_info = self.world_map.get_regions_info()
        if regions_info:
            self.output("【已知大区域】")
            for region in regions_info:
                if region['discovered_areas'] > 0:
                    self.output(f"- {region['name']} "
                              f"(探索度: {region['discovered_areas']}/{region['total_areas']})")
            self.output("")
        
        # 显示附近区域
        nearby_areas = self.location_manager.get_nearby_areas(player.id)
        if nearby_areas:
            self.output("【可前往的地点】")
            for area_info in nearby_areas:
                status = "已探索" if area_info['discovered'] else "未探索"
                danger = '★' * area_info['danger_level']
                self.output(f"- {area_info['name']} ({area_info['type']}) "
                          f"[危险: {danger}] [{status}]")
    
    def _show_location(self):
        """显示当前位置"""
        player = self.game_state.player
        if not player:
            return
            
        # 获取区域描述
        description = self.location_manager.get_area_description(player.id)
        self.output(description)
        
        # 显示可交互的NPC
        current_location = self.location_manager.get_location(player.id)
        if current_location:
            available_npcs = self.npc_manager.get_available_npcs(current_location, player.id)
            if available_npcs:
                self.output("\n可交互的人物：")
                for npc_info in available_npcs:
                    title = f" ({npc_info['title']})" if npc_info.get('title') else ""
                    merchant = " [商人]" if npc_info.get('is_merchant') else ""
                    self.output(f"- {npc_info['name']}{title}{merchant}")
    
    def _do_cultivate(self):
        """修炼"""
        player = self.game_state.player
        
        # 进入修炼场景
        self.status_manager.enter_context('cultivation')
        
        # 使用事件系统处理修炼
        duration = 1  # 默认修炼1天
        exp_gained = SpecialEventHandler.handle_cultivation_event(
            self.immersive_event_system,
            {'attributes': player.attributes},
            duration
        )
        
        # 恢复资源
        mana_recovery = player.attributes.max_mana * 0.3
        stamina_recovery = player.attributes.max_stamina * 0.5
        
        player.restore_mana(mana_recovery)
        player.restore_stamina(stamina_recovery)
        
        self.output(f"同时恢复了 {mana_recovery:.0f} 点灵力和 {stamina_recovery:.0f} 点体力")
        
        # 更新统计
        self.stats['cultivation_time'] += 1
        
        # 检查成就
        if self.stats['cultivation_time'] == 1:
            self.achievement_system.check_achievement('first_cultivation', 1)
        self.achievement_system.check_achievement('cultivation_100h', self.stats['cultivation_time'])
        
        # 退出修炼场景
        self.status_manager.exit_context()
    
    def _do_explore(self):
        """探索"""
        player = self.game_state.player
        if not player:
            return
            
        self.output("你仔细探索周围的环境...")
        self.output("")
        
        # 使用位置管理器探索
        result = self.location_manager.explore_area(player.id)
        
        if not result['success']:
            self.output(result['message'])
            return
        
        # 显示探索结果
        if result['discovered_features']:
            self.output("你发现了一些特殊地点：")
            for feature in result['discovered_features']:
                self.output(f"- {feature}")
            self.output("")
        
        if result['found_items']:
            self.output("你找到了一些物品：")
            for item in result['found_items']:
                self.output(f"- {item['quantity']}份{item['type']}")
                player.inventory.add(item['type'], item['quantity'])
            self.output("")
        
        if result['found_npcs']:
            self.output("你遇到了：")
            for npc_id in result['found_npcs']:
                npc = self.game_state.npcs.get(npc_id)
                if npc:
                    self.output(f"- {npc.name}")
            self.output("")
        
        if result['triggered_events']:
            # 处理触发的事件
            for event_name in result['triggered_events']:
                if event_name == "遭遇低阶妖兽":
                    self.output("你遇到了一只低阶妖兽！")
                    self._start_combat("低阶妖兽")
                    return
        
        if not any([result['discovered_features'], result['found_items'], 
                   result['found_npcs'], result['triggered_events']]):
            self.output("你没有发现什么特别的东西。")
    
    def _do_move(self, location_name: str):
        """移动到新位置"""
        player = self.game_state.player
        if not player:
            return
        
        # 查找目标区域
        target_area_id = None
        current_area_id = self.location_manager.get_location(player.id)
        
        if current_area_id:
            # 在附近区域中查找
            nearby_areas = self.location_manager.get_nearby_areas(player.id)
            for area_info in nearby_areas:
                if location_name in area_info['name']:
                    target_area_id = area_info['id']
                    break
        
        if not target_area_id:
            # 在所有区域中查找
            for area_id, area in self.world_map.areas.items():
                if location_name in area.name:
                    target_area_id = area_id
                    break
        
        if not target_area_id:
            self.output(f"找不到地点：{location_name}")
            self.output("使用 '地图' 命令查看可去的地点。")
            return
        
        # 检查是否可以直接移动
        current_area = self.world_map.get_area(current_area_id)
        target_area = self.world_map.get_area(target_area_id)
        
        if target_area_id in current_area.connected_areas:
            # 直接移动
            success, message = self.location_manager.move_entity(
                player.id, target_area_id, player.attributes.cultivation_level
            )
            
            if success:
                self.output(message)
                # 更新游戏状态
                # store区域ID保持一致
                self.game_state.current_location = target_area_id
                logger.debug(f"玩家移动到 {target_area.name} (ID: {target_area_id})")
                
                # 消耗体力
                stamina_cost = 10  # 基础体力消耗
                player.consume_stamina(stamina_cost)
                self.output(f"消耗了{stamina_cost}点体力")
                
                # 显示新位置
                self.output("")
                self._show_location()
                
                # 检查事件
                self._check_area_events()
            else:
                self.output(message)
        else:
            # 需要规划路线
            travel_info = self.location_manager.plan_travel(player.id, target_area_id)
            if travel_info:
                self.output(f"{target_area.name}不在附近，需要经过{travel_info.distance}个区域。")
                self.output(f"预计消耗{travel_info.stamina_cost}点体力。")
                # TODO: 实现长途旅行
            else:
                self.output(f"无法到达{target_area.name}，可能需要特殊条件。")
    
    def _check_area_events(self):
        """检查区域事件"""
        player = self.game_state.player
        if not player:
            return
            
        current_area_id = self.location_manager.get_location(player.id)
        current_area = self.world_map.get_area(current_area_id)
        
        if not current_area:
            return
        
        # 构建事件上下文
        event_context = {
            'game_time': self.game_state.game_time,
            'location': current_area_id,
            'location_type': current_area.type.value,
            'player_level': player.attributes.cultivation_level,
            'last_action': 'move'
        }
        
        # 检查可触发的事件
        triggered_events = self.event_system.check_triggers(event_context)
        
        if triggered_events:
            # 触发第一个事件
            event = triggered_events[0]
            result = self.event_system.trigger_event(event.id, event_context)
            
            if result:
                self.output("")
                self.output("=== 事件 ===")
                self.output(result['intro_text'])
                # TODO: 处理事件选项
    
    def _do_talk(self, target_name: str):
        """与NPC对话"""
        player = self.game_state.player
        if not player:
            return
        
        # 获取当前位置
        current_location = self.location_manager.get_location(player.id)
        if not current_location:
            self.output("你不知道自己在哪里。")
            return
        
        # 查找NPC
        npc_found = None
        npc_id = None
        
        # 在当前位置的NPC中查找
        available_npcs = self.npc_manager.get_available_npcs(current_location, player.id)
        for npc_info in available_npcs:
            if target_name in npc_info['name']:
                npc_id = npc_info['id']
                npc_found = npc_info
                break
        
        if not npc_found:
            self.output(f"这里没有叫{target_name}的人。")
            return
        
        # 检查是否已经在对话中
        active_dialogue = self.dialogue_system.get_active_dialogue(player.id)
        if active_dialogue:
            self.output("你正在与其他人对话。")
            return
        
        # 开始对话
        self.output(f"\n你走向{npc_found['name']}。")
        
        # 构建对话上下文
        dialogue_context = {
            'player_id': player.id,
            'player_level': player.attributes.cultivation_level,
            'player_faction': player.extra_data.get('faction', ''),
            'npc_relationship': npc_found.get('relationship', 0),
            'flags': self.game_state.flags,
            'spirit_stones': 1000  # TODO: 实现物品系统后从背包获取
        }
        
        # 开始对话
        first_node = self.npc_manager.start_dialogue(player.id, npc_id)
        if first_node:
            self._display_dialogue_node(first_node, npc_found['name'])
        else:
            self.output(f"{npc_found['name']}似乎不想说话。")
    
    def _display_dialogue_node(self, node, npc_name: str):
        """显示对话节点"""
        if not node:
            return
        
        # 显示说话者和内容
        if node.speaker == 'player':
            speaker = self.game_state.player.name
        elif node.speaker == 'system':
            speaker = ''
        else:
            speaker = node.speaker if node.speaker != 'npc' else npc_name
        
        if speaker:
            self.output(f"\n{speaker}：{node.text}")
        else:
            self.output(f"\n{node.text}")
        
        # 如果是选择节点，显示选项
        if node.type.value == 'choice':
            player = self.game_state.player
            context = {
                'player_level': player.attributes.cultivation_level,
                'npc_relationship': self.npc_manager.get_relationship(player.id, node.id),
                'flags': self.game_state.flags
            }
            
            choices = self.dialogue_system.get_active_dialogue(player.id).get_available_choices(context)
            if choices:
                self.output("\n请选择：")
                for i, choice in enumerate(choices, 1):
                    self.output(f"{i}. {choice.text}")
                
                # 设置游戏状态为对话模式
                self.game_state.flags['in_dialogue'] = True
                self.game_state.flags['dialogue_choices'] = [c.id for c in choices]
        
        # 如果是文本节点，自动继续
        elif node.type.value == 'text' and node.next_node:
            dialogue = self.dialogue_system.get_active_dialogue(player.id)
            if dialogue:
                context = {
                    'player_id': player.id,
                    'player_level': player.attributes.cultivation_level
                }
                next_node = dialogue.advance(context)
                if next_node:
                    self._display_dialogue_node(next_node, npc_name)
                else:
                    self._end_dialogue()
    
    def _end_dialogue(self):
        """结束对话"""
        player = self.game_state.player
        if player:
            self.dialogue_system.end_dialogue(player.id)
        
        # 清除对话状态
        if 'in_dialogue' in self.game_state.flags:
            del self.game_state.flags['in_dialogue']
        if 'dialogue_choices' in self.game_state.flags:
            del self.game_state.flags['dialogue_choices']
        
        self.output("\n[对话结束]")
    
    def _process_dialogue_choice(self, choice_id: str):
        """处理对话选择"""
        player = self.game_state.player
        if not player:
            return
        
        # 获取当前对话
        dialogue = self.dialogue_system.get_active_dialogue(player.id)
        if not dialogue:
            self._end_dialogue()
            return
        
        # 构建上下文
        context = {
            'player_id': player.id,
            'player_level': player.attributes.cultivation_level,
            'npc_relationship': self.npc_manager.get_relationship(player.id, dialogue.npc_id),
            'flags': self.game_state.flags,
            'spirit_stones': 1000  # TODO: 从背包获取
        }
        
        # 处理选择
        next_node = self.dialogue_system.advance_dialogue(player.id, context, choice_id)
        
        # 处理对话结果
        if 'rewards' in context:
            for reward in context['rewards']:
                if reward['type'] == 'exp':
                    self.output(f"\n获得了{reward['amount']}点修为！")
                elif reward['type'] == 'item':
                    self.output(f"\n获得了物品！")  # TODO: 显示物品名称
        
        # 如果关系变化
        if 'npc_relationship' in context:
            self.npc_manager.npc_relationships[player.id][dialogue.npc_id] = context['npc_relationship']
        
        # 如果有动作
        if next_node and next_node.action == 'open_shop':
            # TODO: 打开商店
            self.output("\n[商店功能尚未完全实现]")
            # 继续对话
            context['shop_closed'] = True
            next_node = self.dialogue_system.advance_dialogue(player.id, context)
        
        # 显示下一个节点
        if next_node:
            # 获取NPC名称
            npc_profile = self.npc_manager.get_npc_profile(dialogue.npc_id)
            npc_name = npc_profile.name if npc_profile else '未知'
            self._display_dialogue_node(next_node, npc_name)
        else:
            self._end_dialogue()
    
    def _start_combat(self, target_name: str):
        """开始战斗"""
        # 创建战斗
        combat_id = f"combat_{self.game_state.game_time}"
        combat_state = self.combat_system.create_combat(combat_id)
        
        # 添加玩家
        player = self.game_state.player
        combat_state.add_participant(player, "player_team")
        
        # 查找或创建敌人
        enemy = None
        
        # 先从已有NPC中查找
        for npc in self.game_state.npcs.values():
            if target_name in npc.name:
                enemy = npc
                break
        
        # 如果没找到，创建一个临时敌人
        if not enemy:
            if target_name == "低阶妖兽":
                enemy = self._create_monster("低阶妖兽", level=1)
            else:
                self.output(f"找不到目标: {target_name}")
                self.combat_system.end_combat(combat_id)
                return
        
        # 添加敌人
        combat_state.add_participant(enemy, "enemy_team")
        
        # 设置当前战斗
        self.game_state.current_combat = combat_id
        
        # 进入战斗场景
        self.status_manager.enter_context('battle')
        
        # 显示战斗开始（使用中国龙）
        self.output("")
        self.output(get_dragon_for_scene('battle'))
        self.output("")
        self.output("=== 战斗开始 ===")
        self.output(f"{player.name} VS {enemy.name}")
        self.output("")
        
        # 显示敌人信息
        self.output(f"{enemy.name} - {enemy.get_realm_info()}")
        self.output(f"状态: {enemy.get_status_description()}")
        self.output("")
        
        # 如果敌人先手
        if enemy.attributes.get('speed') > player.attributes.get('speed'):
            self.output(f"{enemy.name} 速度更快，先发制人！")
            self._process_npc_turns(combat_state)
    
    def _create_monster(self, name: str, level: int) -> Character:
        """创建怪物"""
        monster = Character(
            name=name,
            character_type=CharacterType.MONSTER
        )
        
        # 设置属性
        monster.attributes.cultivation_level = level
        monster.attributes.strength = 8 + level * 2
        monster.attributes.constitution = 10 + level * 2
        monster.attributes.agility = 6 + level
        
        # 重新计算衍生属性
        monster.attributes.calculate_derived_attributes()
        
        # 设置AI
        monster.ai_profile = 'aggressive'
        
        # 添加基础技能
        monster.learn_skill('basic_attack')
        
        return monster
    
    def _process_npc_turns(self, combat_state: CombatState):
        """处理NPC回合"""
        player = self.game_state.player
        
        for character in combat_state.participants.values():
            if character.id == player.id or not character.is_alive:
                continue
            
            # AI决策
            action = self.ai_controller.decide_action(character, combat_state)
            
            # 执行行动
            result = self.combat_system.execute_action(
                self.game_state.current_combat,
                action
            )
            
            # 显示结果
            self._show_combat_result(result, is_player=False)
            
            # 检查玩家是否死亡
            if not player.is_alive:
                self.output("")
                self.output("你被击败了！")
                self._game_over()
                break
    
    def _show_combat_result(self, result, is_player: bool = True):
        """显示战斗结果"""
        if not result.success:
            self.output(f"行动失败: {result.message}")
            return
        
        # 显示伤害
        for target_id, damage_info in result.damage_dealt.items():
            target = self.combat_system.get_combat(
                self.game_state.current_combat
            ).participants.get(target_id)
            
            if target:
                if damage_info.is_evaded:
                    self.output(f"{target.name} 闪避了攻击！")
                else:
                    damage_text = f"{damage_info.damage:.0f}"
                    if damage_info.is_critical:
                        damage_text = f"暴击！{damage_text}"
                    
                    self.output(f"对 {target.name} 造成了 {damage_text} 点伤害")
                    
                    # 显示目标状态
                    if target.is_alive:
                        health_percent = target.attributes.current_health / target.attributes.max_health
                        if health_percent < 0.3:
                            self.output(f"{target.name} 已经岌岌可危！")
                    else:
                        self.output(f"{target.name} 被击败了！")
        
        # 显示治疗
        for target_id, heal_amount in result.healing_done.items():
            target = self.combat_system.get_combat(
                self.game_state.current_combat
            ).participants.get(target_id)
            
            if target:
                self.output(f"{target.name} 恢复了 {heal_amount:.0f} 点生命")
        
        # 显示效果
        for effect in result.effects_applied:
            self.output(f"施加了效果: {effect.name}")
        
        self.output("")
    
    def _try_flee(self) -> bool:
        """尝试逃跑"""
        import random
        
        player = self.game_state.player
        combat_state = self.combat_system.get_combat(self.game_state.current_combat)
        
        # 基于速度计算逃跑成功率
        enemies = combat_state.get_enemies(player)
        if not enemies:
            return True
        
        avg_enemy_speed = sum(e.attributes.get('speed') for e in enemies) / len(enemies)
        player_speed = player.attributes.get('speed')
        
        flee_chance = min(0.9, max(0.1, player_speed / (player_speed + avg_enemy_speed)))
        
        if random.random() < flee_chance:
            self.output("你成功逃离了战斗！")
            self._end_combat(combat_state, fled=True)
            return True
        
        return False
    
    def _end_combat(self, combat_state: CombatState, fled: bool = False):
        """结束战斗"""
        if not fled:
            # 战斗胜利
            winner = combat_state.get_winning_team()
            if winner == "player_team":
                self.output("")
                self.output("=== 战斗胜利 ===")
                
                # 更新统计
                self.stats['enemies_defeated'] += 1
                self.stats['win_streak'] += 1
                
                # 检查成就
                if self.stats['enemies_defeated'] == 1:
                    self.achievement_system.check_achievement('first_battle', 1)
                self.achievement_system.check_achievement('warrior_10', self.stats['enemies_defeated'])
                self.achievement_system.check_achievement('warrior_50', self.stats['enemies_defeated'])
                self.achievement_system.check_achievement('win_streak_10', self.stats['win_streak'])
                
                # 检查是否无伤胜利
                player = self.game_state.player
                if player.attributes.current_health == player.attributes.max_health:
                    self.achievement_system.check_achievement('no_damage_win', 1)
                
                # 获得奖励
                # TODO: 实现战利品系统
                self.output("获得了一些修为和物品！")
            else:
                self.output("")
                self.output("=== 战斗失败 ===")
                self.stats['win_streak'] = 0  # 重置连胜
        else:
            self.stats['win_streak'] = 0  # 逃跑也重置连胜
        
        # 退出战斗场景
        self.status_manager.exit_context()
        
        # 清理战斗状态
        self.combat_system.end_combat(self.game_state.current_combat)
        self.game_state.current_combat = None
        
        self.output("")
        self._show_location()
    
    def _save_game(self):
        """保存游戏"""
        try:
            # 创建存档目录
            save_dir = "saves"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # 生成存档文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{save_dir}/save_{timestamp}.json"
            
            # 保存游戏状态
            save_data = {
                'version': '1.0.0',
                'timestamp': timestamp,
                'game_state': self.game_state.to_dict()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            self.output(f"游戏已保存: {filename}")
            
        except Exception as e:
            self.output(f"保存失败: {e}")
            logger.error(f"保存游戏失败: {e}")
    
    def _quit_game(self):
        """退出游戏"""
        self.output("是否保存游戏？(y/n)")
        # TODO: 实现确认机制
        
        self.running = False
        self.output("感谢游戏，再见！")
    
    def _game_over(self):
        """游戏结束"""
        self.running = False
        self.output("")
        self.output("=== 游戏结束 ===")
        self.output("你的修仙之路到此为止...")
    
    def output(self, text: str):
        """
        输出文本
        
        Args:
            text: 要输出的文本
        """
        self.output_buffer.append(text)
    
    def get_output(self) -> List[str]:
        """
        获取并清空输出缓冲
        
        Returns:
            输出文本列表
        """
        output = self.output_buffer.copy()
        self.output_buffer.clear()
        return output
    
    def is_running(self) -> bool:
        """游戏是否在运行"""
        return self.running

    def run(self):
        """运行游戏"""
        return self.main_loop()
    
    def _process_normal_command_v2(self, cmd_type: str, params: Dict[str, Any]):
        """处理非战斗状态的命令（新版）"""
        if cmd_type == 'status':
            self._show_status()
            
        elif cmd_type == 'inventory':
            self._show_inventory()
            
        elif cmd_type == 'skills':
            self._show_skills()
            
        elif cmd_type == 'map':
            self._show_map()
            
        elif cmd_type == 'cultivate':
            self._do_cultivate()
            
        elif cmd_type == 'attack':
            if params.get('target'):
                self._start_combat(params['target'])
            else:
                self.output("攻击谁？")
                
        elif cmd_type == 'explore':
            self._do_explore()
            
        elif cmd_type == 'move':
            if params.get('location'):
                self._do_move(params['location'])
            else:
                self.output("要去哪里？")
            
        elif cmd_type == 'talk':
            if params.get('target'):
                self._do_talk(params['target'])
            else:
                self.output("要和谁说话？")
            
        elif cmd_type == 'help':
            self._show_help()
            
        elif cmd_type == 'save':
            self._save_game()
            
        elif cmd_type == 'quit':
            self._quit_game()
            
        else:
            self.output("无法理解的命令。输入 '帮助' 查看可用命令。")
    
    def _process_combat_command_v2(self, cmd_type: str, params: Dict[str, Any]):
        """处理战斗状态的命令（新版）"""
        combat_state = self.combat_system.get_combat(self.game_state.current_combat)
        if not combat_state:
            return
        
        player = self.game_state.player
        
        # 构建战斗行动
        action = None
        
        if cmd_type == 'attack':
            # 普通攻击
            if params.get('target'):
                target = self._find_combat_target(combat_state, params['target'])
                if target:
                    action = CombatAction(
                        action_type=CombatActionType.ATTACK,
                        actor_id=player.id,
                        target_ids=[target.id]
                    )
                else:
                    self.output(f"找不到目标: {params['target']}")
            else:
                # 自动选择目标
                enemies = combat_state.get_enemies(player)
                if enemies:
                    action = CombatAction(
                        action_type=CombatActionType.ATTACK,
                        actor_id=player.id,
                        target_ids=[enemies[0].id]
                    )
                    
        elif cmd_type == 'use_skill':
            # 使用技能
            skill_name = params.get('skill', '')
            skill = self._find_skill_by_name(skill_name)
            
            if skill and player.has_skill(skill.id):
                target = None
                if params.get('target'):
                    target = self._find_combat_target(combat_state, params['target'])
                
                if skill.target_type.value == 'self':
                    target_ids = [player.id]
                elif skill.target_type.value == 'single_enemy' and target:
                    target_ids = [target.id]
                elif skill.target_type.value == 'all_enemies':
                    enemies = combat_state.get_enemies(player)
                    target_ids = [e.id for e in enemies[:skill.max_targets]]
                else:
                    target_ids = []
                
                if target_ids or skill.target_type.value in ['self', 'all_enemies']:
                    action = CombatAction(
                        action_type=CombatActionType.SKILL,
                        actor_id=player.id,
                        target_ids=target_ids,
                        skill_id=skill.id
                    )
                else:
                    self.output(f"无法确定技能目标")
            else:
                self.output(f"你还没有学会技能: {skill_name}")
                
        elif cmd_type == 'defend':
            # 防御
            action = CombatAction(
                action_type=CombatActionType.DEFEND,
                actor_id=player.id
            )
            
        elif cmd_type == 'flee':
            # 逃跑
            if self._try_flee():
                return
            else:
                self.output("逃跑失败！")
                action = CombatAction(
                    action_type=CombatActionType.WAIT,
                    actor_id=player.id
                )
        
        # 执行玩家行动
        if action:
            result = self.combat_system.execute_action(
                self.game_state.current_combat,
                action
            )
            
            # 显示结果
            self._show_combat_result(result)
            
            # NPC行动
            self._process_npc_turns(combat_state)
            
            # 检查战斗是否结束
            if combat_state.is_combat_over():
                self._end_combat(combat_state)
    
    def _show_help(self):
        """显示帮助（使用中国龙和优先级系统）"""
        self.output(get_dragon_for_scene('help'))
        self.output("")
        self.output(self.command_router.get_help_text())
