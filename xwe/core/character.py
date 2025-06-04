# core/character.py
"""
角色系统模块

定义游戏中的角色实体，包括玩家和NPC。
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set
from enum import Enum
import uuid
import logging

from .attributes import CharacterAttributes
from .status import StatusEffectManager
from .inventory import Inventory

logger = logging.getLogger(__name__)


class CharacterType(Enum):
    """角色类型"""
    PLAYER = "player"
    NPC = "npc"
    MONSTER = "monster"
    BOSS = "boss"


class CharacterState(Enum):
    """角色状态"""
    NORMAL = "normal"          # 正常
    COMBAT = "combat"          # 战斗中
    MEDITATING = "meditating"  # 打坐修炼
    DEAD = "dead"              # 死亡
    STUNNED = "stunned"        # 昏迷
    FROZEN = "frozen"          # 冰冻


@dataclass
class Character:
    """
    游戏角色类
    
    表示游戏中的一个角色实体，包括玩家和NPC。
    """
    
    # 基础信息
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "未命名"
    character_type: CharacterType = CharacterType.NPC
    
    # 属性
    attributes: CharacterAttributes = field(default_factory=CharacterAttributes)
    
    # 状态
    state: CharacterState = CharacterState.NORMAL
    status_effects: StatusEffectManager = field(default_factory=StatusEffectManager)
    
    # 修炼相关
    cultivation_path: str = ""  # 修炼路线
    spiritual_root: Dict[str, float] = field(default_factory=dict)  # 灵根
    skills: List[str] = field(default_factory=list)  # 已学技能ID列表
    
    # 装备和物品
    equipment: Dict[str, str] = field(default_factory=dict)  # 装备位置 -> 物品ID
    inventory: Inventory = field(default_factory=Inventory)  # 背包物品
    
    # 社交关系
    faction: str = ""  # 所属门派
    relationships: Dict[str, float] = field(default_factory=dict)  # 角色ID -> 好感度
    
    # 战斗相关
    team_id: Optional[str] = None  # 队伍ID
    combat_position: Optional[int] = None  # 战斗位置
    action_points: int = 0  # 行动点数
    
    # AI相关（仅NPC）
    ai_profile: str = "default"  # AI行为配置
    dialogue_state: Dict[str, Any] = field(default_factory=dict)  # 对话状态
    
    # 其他数据
    extra_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        # 设置默认灵根
        if not self.spiritual_root:
            self.spiritual_root = {
                "金": 20,
                "木": 20,
                "水": 20,
                "火": 20,
                "土": 20
            }
        
        # 初始化资源为最大值
        self.attributes.current_health = self.attributes.max_health
        self.attributes.current_mana = self.attributes.max_mana
        self.attributes.current_stamina = self.attributes.max_stamina
    
    @property
    def is_player(self) -> bool:
        """是否为玩家角色"""
        return self.character_type == CharacterType.PLAYER
    
    @property
    def is_alive(self) -> bool:
        """是否存活"""
        return self.state != CharacterState.DEAD and self.attributes.current_health > 0
    
    @property
    def is_in_combat(self) -> bool:
        """是否在战斗中"""
        return self.state == CharacterState.COMBAT
    
    @property
    def can_act(self) -> bool:
        """是否可以行动"""
        return self.is_alive and self.state not in [
            CharacterState.STUNNED, 
            CharacterState.FROZEN
        ]
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        if self.faction:
            return f"[{self.faction}] {self.name}"
        return self.name
    
    def get_realm_info(self) -> str:
        """获取境界信息"""
        level = self.attributes.cultivation_level
        realm = self.attributes.realm_name
        return f"{realm} {level}层"
    
    def get_status_description(self) -> str:
        """获取状态描述"""
        health_percent = self.attributes.current_health / self.attributes.max_health
        
        if health_percent >= 0.8:
            health_desc = "精神饱满"
        elif health_percent >= 0.6:
            health_desc = "轻微受伤"
        elif health_percent >= 0.4:
            health_desc = "伤势不轻"
        elif health_percent >= 0.2:
            health_desc = "重伤垂危"
        else:
            health_desc = "命悬一线"
        
        mana_percent = self.attributes.current_mana / self.attributes.max_mana
        
        if mana_percent >= 0.8:
            mana_desc = "法力充沛"
        elif mana_percent >= 0.5:
            mana_desc = "法力尚可"
        elif mana_percent >= 0.2:
            mana_desc = "法力不足"
        else:
            mana_desc = "法力枯竭"
        
        return f"{health_desc}，{mana_desc}"
    
    def take_damage(self, damage: float, damage_type: str = "physical"):
        """
        受到伤害
        
        Args:
            damage: 伤害值
            damage_type: 伤害类型
        """
        if damage <= 0:
            return
        
        # 应用伤害
        self.attributes.current_health -= damage
        
        # 检查死亡
        if self.attributes.current_health <= 0:
            self.attributes.current_health = 0
            self.state = CharacterState.DEAD
            logger.info(f"{self.name} 已死亡")
    
    def heal(self, amount: float):
        """
        治疗
        
        Args:
            amount: 治疗量
        """
        if amount <= 0:
            return
        
        self.attributes.current_health = min(
            self.attributes.current_health + amount,
            self.attributes.max_health
        )
    
    def consume_mana(self, amount: float) -> bool:
        """
        消耗法力
        
        Args:
            amount: 消耗量
            
        Returns:
            是否成功消耗
        """
        if self.attributes.current_mana < amount:
            return False
        
        self.attributes.current_mana -= amount
        return True
    
    def restore_mana(self, amount: float):
        """
        恢复法力
        
        Args:
            amount: 恢复量
        """
        if amount <= 0:
            return
        
        self.attributes.current_mana = min(
            self.attributes.current_mana + amount,
            self.attributes.max_mana
        )
    
    def consume_stamina(self, amount: float) -> bool:
        """
        消耗体力
        
        Args:
            amount: 消耗量
            
        Returns:
            是否成功消耗
        """
        if self.attributes.current_stamina < amount:
            return False
        
        self.attributes.current_stamina -= amount
        return True
    
    def restore_stamina(self, amount: float):
        """
        恢复体力
        
        Args:
            amount: 恢复量
        """
        if amount <= 0:
            return
        
        self.attributes.current_stamina = min(
            self.attributes.current_stamina + amount,
            self.attributes.max_stamina
        )
    
    def learn_skill(self, skill_id: str) -> bool:
        """
        学习技能
        
        Args:
            skill_id: 技能ID
            
        Returns:
            是否成功学习
        """
        if skill_id in self.skills:
            return False
        
        self.skills.append(skill_id)
        logger.info(f"{self.name} 学会了技能: {skill_id}")
        return True
    
    def has_skill(self, skill_id: str) -> bool:
        """
        是否拥有技能
        
        Args:
            skill_id: 技能ID
            
        Returns:
            是否拥有
        """
        return skill_id in self.skills
    
    def get_spiritual_root_description(self) -> str:
        """获取灵根描述"""
        if not self.spiritual_root:
            return "无灵根"
        
        # 按值排序
        sorted_roots = sorted(
            self.spiritual_root.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # 计算总纯度
        total_purity = sum(self.spiritual_root.values())
        
        # 生成描述
        if len([v for v in self.spiritual_root.values() if v > 20]) == 1:
            # 单灵根
            main_root = sorted_roots[0][0]
            return f"{main_root}系单灵根（纯度{sorted_roots[0][1]}%）"
        elif len([v for v in self.spiritual_root.values() if v > 15]) == 2:
            # 双灵根
            return f"{sorted_roots[0][0]}{sorted_roots[1][0]}双灵根"
        else:
            # 多灵根
            return "五行杂灵根"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'character_type': self.character_type.value,
            'attributes': self.attributes.to_dict(),
            'state': self.state.value,
            'cultivation_path': self.cultivation_path,
            'spiritual_root': self.spiritual_root,
            'skills': self.skills,
            'equipment': self.equipment,
            'faction': self.faction,
            'ai_profile': self.ai_profile,
        }
    
    @classmethod
    def from_template(cls, template: Dict[str, Any]) -> 'Character':
        """
        从模板创建角色
        
        Args:
            template: 角色模板数据
            
        Returns:
            新建的角色对象
        """
        # 创建属性
        attrs = CharacterAttributes()
        
        # 应用基础属性
        if 'base_attributes' in template:
            for attr, value in template['base_attributes'].items():
                setattr(attrs, attr, value)
        
        # 应用修炼属性
        if 'cultivation' in template:
            cult_data = template['cultivation']
            attrs.realm_name = cult_data.get('realm', '聚气期')
            attrs.realm_level = cult_data.get('realm_level', 1)
            attrs.cultivation_level = cult_data.get('level', 1)
        
        # 重新计算衍生属性
        attrs.calculate_derived_attributes()
        
        # 处理角色类型
        char_type_str = template.get('type', 'npc')
        try:
            char_type = CharacterType(char_type_str)
        except ValueError:
            # 如果值无效，默认为NPC
            char_type = CharacterType.NPC
            logger.warning(f"无效的角色类型: {char_type_str}，使用默认值 NPC")
        
        # 创建角色
        character = cls(
            name=template.get('name', '未命名'),
            character_type=char_type,
            attributes=attrs,
            spiritual_root=template.get('spiritual_root', {}),
            skills=template.get('skills', []),
            faction=template.get('faction', ''),
            ai_profile=template.get('ai_profile', 'default'),
        )
        
        return character
