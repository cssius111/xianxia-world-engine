# npc/npc_manager.py
"""
NPC管理器

管理NPC的行为、状态和互动。
"""

import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random

from ..core.character import Character, CharacterType
from .dialogue_system import DialogueSystem, DialogueNode, DEFAULT_DIALOGUES
from .emotion_system import EmotionSystem
from .memory_system import MemorySystem, MemoryType
from .enhanced_dialogue import EnhancedDialogueSystem

logger = logging.getLogger(__name__)


class NPCBehavior(Enum):
    """NPC行为类型"""
    STATIC = "static"        # 静态（始终在同一位置）
    PATROL = "patrol"        # 巡逻（在几个位置间移动）
    WANDER = "wander"        # 漫游（随机移动）
    FOLLOW = "follow"        # 跟随（跟随玩家或其他NPC）
    SCHEDULE = "schedule"    # 日程（按时间表行动）


@dataclass
class NPCProfile:
    """NPC档案"""
    id: str
    name: str
    title: str = ""
    description: str = ""
    
    # 行为设置
    behavior: NPCBehavior = NPCBehavior.STATIC
    home_location: str = ""
    patrol_routes: List[str] = field(default_factory=list)
    
    # 对话设置
    dialogue_id: str = "default"
    dialogue_template: str = ""  # 使用的对话模板
    
    # 交易设置
    is_merchant: bool = False
    shop_id: Optional[str] = None
    
    # 任务相关
    quest_giver: bool = False
    quest_ids: List[str] = field(default_factory=list)
    
    # 关系设置
    faction: str = ""
    default_relationship: int = 0
    relationship_modifiers: Dict[str, int] = field(default_factory=dict)
    
    # 额外数据
    extra_data: Dict[str, Any] = field(default_factory=dict)


class NPCManager:
    """
    NPC管理器
    
    管理所有NPC的行为和状态。
    """
    
    def __init__(self, dialogue_system: DialogueSystem, nlp_processor=None):
        """
        初始化NPC管理器
        
        Args:
            dialogue_system: 对话系统实例
            nlp_processor: NLP处理器（可选）
        """
        self.dialogue_system = dialogue_system
        self.npc_profiles: Dict[str, NPCProfile] = {}
        self.npc_characters: Dict[str, Character] = {}
        self.npc_relationships: Dict[str, Dict[str, int]] = {}  # player_id -> npc_id -> relationship
        
        # NPC位置（由LocationManager管理，这里只记录）
        self.npc_locations: Dict[str, str] = {}
        
        # 行为计时器
        self.behavior_timers: Dict[str, int] = {}
        
        # 初始化增强系统
        self.emotion_system = EmotionSystem()
        self.memory_system = MemorySystem()
        self.enhanced_dialogue = EnhancedDialogueSystem(
            dialogue_system=dialogue_system,
            emotion_system=self.emotion_system,
            memory_system=self.memory_system,
            nlp_processor=nlp_processor
        )
        
        # 初始化默认NPC
        self._init_default_npcs()
        
        logger.info("NPC管理器初始化")
    
    def _init_default_npcs(self):
        """初始化默认NPC档案"""
        # 王老板 - 商人
        wang_profile = NPCProfile(
            id="npc_wang_boss",
            name="王老板",
            title="坊市管事",
            description="一位精明的商人，在天南坊市经营着一家小店铺。",
            behavior=NPCBehavior.STATIC,
            home_location="tiannan_market",
            is_merchant=True,
            shop_id="wang_basic_shop",
            dialogue_template="merchant_default",
            faction="天南商会",
            default_relationship=20
        )
        self.register_npc_profile(wang_profile)
        
        # 云梦儿 - 天才修士
        yun_profile = NPCProfile(
            id="npc_yun_menger",
            name="云梦儿",
            title="云霞宗弟子",
            description="云霞宗的天才弟子，年纪轻轻就已经是筑基期修为。",
            behavior=NPCBehavior.PATROL,
            home_location="qingyun_city",
            patrol_routes=["qingyun_city", "tiannan_market", "yellow_maple_valley"],
            dialogue_template="cultivator_default",
            faction="云霞宗",
            default_relationship=0,
            relationship_modifiers={"same_faction": 20, "high_level": -10}
        )
        self.register_npc_profile(yun_profile)
        
        # 李太虚 - 宗门长老
        li_profile = NPCProfile(
            id="npc_li_taixu",
            name="李太虚",
            title="青云宗外门长老",
            description="青云宗的外门长老，负责招收和指导新弟子。",
            behavior=NPCBehavior.SCHEDULE,
            home_location="qingyun_city",
            quest_giver=True,
            quest_ids=["join_qingyun_sect"],
            dialogue_template="elder_default",
            faction="青云宗",
            default_relationship=10
        )
        self.register_npc_profile(li_profile)
        
        # 加载对话
        for npc_id, dialogues in DEFAULT_DIALOGUES.items():
            for dialogue_id, dialogue_data in dialogues.items():
                self.dialogue_system.load_dialogue(f"npc_{npc_id}", dialogue_id, dialogue_data)
    
    def register_npc_profile(self, profile: NPCProfile):
        """注册NPC档案"""
        self.npc_profiles[profile.id] = profile
        logger.debug(f"注册NPC档案: {profile.name}")
    
    def create_npc_character(self, npc_id: str, template_data: Optional[Dict[str, Any]] = None) -> Optional[Character]:
        """
        创建NPC角色实例
        
        Args:
            npc_id: NPC ID
            template_data: 角色模板数据
            
        Returns:
            创建的角色实例
        """
        profile = self.npc_profiles.get(npc_id)
        if not profile:
            logger.error(f"NPC档案不存在: {npc_id}")
            return None
        
        # 创建角色
        if template_data:
            character = Character.from_template(template_data)
        else:
            character = Character(name=profile.name, character_type=CharacterType.NPC)
        
        # 设置基本信息
        character.id = npc_id
        character.extra_data['title'] = profile.title
        character.extra_data['faction'] = profile.faction
        character.extra_data['profile_id'] = profile.id
        
        # 保存角色实例
        self.npc_characters[npc_id] = character
        
        # 设置初始位置
        if profile.home_location:
            self.npc_locations[npc_id] = profile.home_location
        
        # 创建对话（如果使用模板）
        if profile.dialogue_template:
            self.dialogue_system.create_dialogue_from_template(npc_id, profile.dialogue_template)
        
        # 注册到增强系统
        personality_template = None
        if profile.extra_data.get('personality_template'):
            personality_template = profile.extra_data['personality_template']
        elif 'merchant' in profile.id or profile.is_merchant:
            personality_template = 'merchant'
        elif 'elder' in profile.title.lower() or '长老' in profile.title:
            personality_template = 'elder'
        
        self.emotion_system.register_npc(npc_id, personality_template)
        
        logger.info(f"创建NPC角色: {profile.name}")
        return character
    
    def get_npc_character(self, npc_id: str) -> Optional[Character]:
        """获取NPC角色实例"""
        return self.npc_characters.get(npc_id)
    
    def get_npc_profile(self, npc_id: str) -> Optional[NPCProfile]:
        """获取NPC档案"""
        return self.npc_profiles.get(npc_id)
    
    def update_npc_behavior(self, game_time: int):
        """
        更新NPC行为
        
        Args:
            game_time: 游戏时间
        """
        for npc_id, profile in self.npc_profiles.items():
            if profile.behavior == NPCBehavior.PATROL:
                self._update_patrol_behavior(npc_id, profile, game_time)
            elif profile.behavior == NPCBehavior.WANDER:
                self._update_wander_behavior(npc_id, profile, game_time)
            elif profile.behavior == NPCBehavior.SCHEDULE:
                self._update_schedule_behavior(npc_id, profile, game_time)
    
    def _update_patrol_behavior(self, npc_id: str, profile: NPCProfile, game_time: int):
        """更新巡逻行为"""
        if not profile.patrol_routes:
            return
        
        # 检查计时器
        last_move = self.behavior_timers.get(npc_id, 0)
        if game_time - last_move < 10:  # 每10回合移动一次
            return
        
        # 获取当前位置
        current_location = self.npc_locations.get(npc_id, profile.home_location)
        
        # 找到下一个位置
        if current_location in profile.patrol_routes:
            current_index = profile.patrol_routes.index(current_location)
            next_index = (current_index + 1) % len(profile.patrol_routes)
            next_location = profile.patrol_routes[next_index]
        else:
            next_location = profile.patrol_routes[0]
        
        # 更新位置
        self.npc_locations[npc_id] = next_location
        self.behavior_timers[npc_id] = game_time
        
        logger.debug(f"NPC {profile.name} 巡逻到 {next_location}")
    
    def _update_wander_behavior(self, npc_id: str, profile: NPCProfile, game_time: int):
        """更新漫游行为"""
        # TODO: 实现漫游逻辑
        pass
    
    def _update_schedule_behavior(self, npc_id: str, profile: NPCProfile, game_time: int):
        """更新日程行为"""
        # TODO: 实现日程逻辑（根据时间决定位置）
        pass
    
    def get_npc_location(self, npc_id: str) -> Optional[str]:
        """获取NPC位置"""
        return self.npc_locations.get(npc_id)
    
    def set_npc_location(self, npc_id: str, location: str):
        """设置NPC位置"""
        self.npc_locations[npc_id] = location
    
    def get_relationship(self, player_id: str, npc_id: str) -> int:
        """
        获取玩家与NPC的关系值
        
        Args:
            player_id: 玩家ID
            npc_id: NPC ID
            
        Returns:
            关系值（-100到100）
        """
        if player_id not in self.npc_relationships:
            self.npc_relationships[player_id] = {}
        
        if npc_id not in self.npc_relationships[player_id]:
            # 使用默认关系值
            profile = self.npc_profiles.get(npc_id)
            if profile:
                self.npc_relationships[player_id][npc_id] = profile.default_relationship
            else:
                self.npc_relationships[player_id][npc_id] = 0
        
        return self.npc_relationships[player_id][npc_id]
    
    def modify_relationship(self, player_id: str, npc_id: str, change: int):
        """
        修改关系值
        
        Args:
            player_id: 玩家ID
            npc_id: NPC ID
            change: 变化量
        """
        current = self.get_relationship(player_id, npc_id)
        new_value = max(-100, min(100, current + change))
        
        if player_id not in self.npc_relationships:
            self.npc_relationships[player_id] = {}
        
        self.npc_relationships[player_id][npc_id] = new_value
        
        logger.info(f"关系变化: {player_id} 与 {npc_id} 的关系 {current} -> {new_value}")
    
    def get_npcs_in_location(self, location: str) -> List[str]:
        """获取某个位置的所有NPC"""
        return [npc_id for npc_id, loc in self.npc_locations.items() if loc == location]
    
    def start_dialogue(self, player_id: str, npc_id: str, player_info: Dict[str, Any] = None,
                      use_enhanced: bool = True) -> Tuple[Optional[DialogueNode], Optional[Any]]:
        """
        开始与NPC对话
        
        Args:
            player_id: 玩家ID
            npc_id: NPC ID
            player_info: 玩家信息
            use_enhanced: 是否使用增强版对话系统
            
        Returns:
            (第一个对话节点, 对话上下文)
        """
        profile = self.npc_profiles.get(npc_id)
        if not profile:
            return None, None
        
        # 构建NPC信息
        npc_info = self.get_npc_info(npc_id)
        npc_info['relationship'] = self.get_relationship(player_id, npc_id)
        
        # 构建玩家信息
        if not player_info:
            player_info = {
                'level': 1,
                'faction': '',
                'reputation': 0
            }
        
        if use_enhanced:
            # 使用增强版对话系统
            node, context = self.enhanced_dialogue.start_dialogue(
                player_id, npc_id, npc_info, player_info
            )
            return node, context
        else:
            # 使用基础对话系统
            character = self.npc_characters.get(npc_id)
            context = {
                'npc_id': npc_id,
                'npc_name': profile.name,
                'npc_relationship': self.get_relationship(player_id, npc_id),
                'player_id': player_id
            }
            
            # 添加角色信息
            if character:
                context['npc_level'] = character.attributes.cultivation_level
                context['npc_faction'] = profile.faction
            
            # 开始对话
            node = self.dialogue_system.start_dialogue(player_id, npc_id, profile.dialogue_id)
            return node, context
    
    def get_npc_info(self, npc_id: str) -> Dict[str, Any]:
        """
        获取NPC信息
        
        Returns:
            NPC信息字典
        """
        profile = self.npc_profiles.get(npc_id)
        character = self.npc_characters.get(npc_id)
        
        if not profile:
            return {}
        
        info = {
            'id': npc_id,
            'name': profile.name,
            'title': profile.title,
            'description': profile.description,
            'faction': profile.faction,
            'location': self.npc_locations.get(npc_id, ''),
            'is_merchant': profile.is_merchant,
            'quest_giver': profile.quest_giver
        }
        
        if character:
            info['level'] = character.attributes.cultivation_level
            info['realm'] = character.get_realm_info()
        
        return info
    
    def get_available_npcs(self, location: str, player_id: str) -> List[Dict[str, Any]]:
        """
        获取某个位置可交互的NPC列表
        
        Args:
            location: 位置ID
            player_id: 玩家ID
            
        Returns:
            NPC信息列表
        """
        available_npcs = []
        
        for npc_id in self.get_npcs_in_location(location):
            npc_info = self.get_npc_info(npc_id)
            if npc_info:
                # 添加关系信息
                npc_info['relationship'] = self.get_relationship(player_id, npc_id)
                available_npcs.append(npc_info)
        
        return available_npcs
