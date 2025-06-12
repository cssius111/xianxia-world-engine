"""
修炼服务接口定义
负责修炼系统的管理，包括修炼、突破、功法、丹药和天劫
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class CultivationRealm(Enum):
    """修炼境界"""
    QI_REFINING = "炼气期"           # 1-9层
    FOUNDATION_BUILDING = "筑基期"    # 前中后期
    GOLDEN_CORE = "金丹期"           # 前中后期
    NASCENT_SOUL = "元婴期"          # 前中后期
    SOUL_FORMATION = "化神期"        # 前中后期
    VOID_REFINING = "炼虚期"         # 前中后期
    INTEGRATION = "合体期"           # 前中后期
    TRIBULATION = "大乘期"           # 前中后期
    ASCENSION = "渡劫期"             # 一到九重天劫


class CultivationType(Enum):
    """修炼类型"""
    MEDITATION = "meditation"      # 打坐修炼
    COMBAT = "combat"              # 战斗修炼
    ENLIGHTENMENT = "enlightenment" # 顿悟
    DUAL = "dual"                  # 双修
    ALCHEMY = "alchemy"            # 炼丹
    ARTIFACT = "artifact"          # 炼器
    FORMATION = "formation"        # 阵法


class SpiritualRoot(Enum):
    """灵根类型"""
    HEAVENLY = "天灵根"      # 单属性，极品
    EXCEPTIONAL = "异灵根"    # 特殊属性
    TRUE = "真灵根"          # 双属性，优秀
    EARTH = "地灵根"         # 三属性，良好
    PSEUDO = "伪灵根"        # 四属性，普通
    MIXED = "杂灵根"         # 五属性，较差
    NONE = "无灵根"          # 无法修炼


@dataclass
class CultivationTechnique:
    """修炼功法"""
    id: str
    name: str
    grade: str  # '黄阶', '玄阶', '地阶', '天阶', '仙阶'
    description: str
    
    # 修炼要求
    min_realm: CultivationRealm
    spiritual_root_requirement: List[str] = field(default_factory=list)
    attribute_requirements: Dict[str, int] = field(default_factory=dict)
    
    # 修炼效果
    cultivation_speed: float = 1.0  # 修炼速度倍率
    attribute_bonus: Dict[str, int] = field(default_factory=dict)
    special_effects: List[str] = field(default_factory=list)
    
    # 进度
    proficiency: int = 0
    max_proficiency: int = 1000
    level: int = 1
    max_level: int = 10


@dataclass
class CultivationResult:
    """修炼结果"""
    success: bool
    cultivation_type: CultivationType
    duration: float  # 修炼时长（秒）
    
    # 收获
    experience_gained: int = 0
    proficiency_gained: int = 0
    enlightenment_gained: int = 0
    
    # 特殊事件
    breakthrough: bool = False
    bottleneck: bool = False
    enlightenment_event: Optional[Dict[str, Any]] = None
    side_effects: List[str] = field(default_factory=list)
    
    # 消耗
    resources_consumed: Dict[str, int] = field(default_factory=dict)
    
    @property
    def message(self) -> str:
        """生成结果消息"""
        if self.breakthrough:
            return "恭喜！你成功突破了境界！"
        elif self.bottleneck:
            return "你遇到了瓶颈，需要特殊机缘才能突破。"
        elif self.enlightenment_event:
            return f"你获得了顿悟！{self.enlightenment_event.get('description', '')}"
        else:
            return f"修炼完成，获得了{self.experience_gained}点经验。"


@dataclass
class BreakthroughInfo:
    """突破信息"""
    current_realm: CultivationRealm
    current_stage: int
    next_realm: CultivationRealm
    next_stage: int
    
    # 突破条件
    experience_required: int
    enlightenment_required: int
    resources_required: Dict[str, int] = field(default_factory=dict)
    special_requirements: List[str] = field(default_factory=list)
    
    # 突破难度
    success_rate: float = 0.5
    tribulation_difficulty: int = 1  # 天劫难度
    
    # 失败后果
    failure_penalty: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Tribulation:
    """天劫"""
    id: str
    name: str
    realm: CultivationRealm
    difficulty: int  # 1-10
    
    # 天劫内容
    waves: int = 1  # 波数
    thunder_power: int = 100  # 雷劫威力
    special_tests: List[str] = field(default_factory=list)  # 特殊考验
    
    # 奖励
    success_rewards: Dict[str, Any] = field(default_factory=dict)
    
    # 状态
    current_wave: int = 0
    is_active: bool = False
    participant_health: int = 100


class ICultivationService(ABC):
    """
    修炼服务接口
    
    主要职责：
    1. 修炼进度管理
    2. 境界突破系统
    3. 功法学习和修炼
    4. 天劫系统
    5. 灵根和体质管理
    6. 丹药炼制和使用
    7. 悟道和机缘
    """
    
    # ========== 基础修炼 ==========
    
    @abstractmethod
    def cultivate(self, cultivation_type: CultivationType = CultivationType.MEDITATION,
                  duration: float = 3600) -> CultivationResult:
        """
        进行修炼
        
        Args:
            cultivation_type: 修炼类型
            duration: 修炼时长（秒）
            
        Returns:
            CultivationResult: 修炼结果
            
        Example:
            >>> result = cultivation_service.cultivate(
            ...     CultivationType.MEDITATION,
            ...     duration=7200  # 2小时
            ... )
            >>> print(result.message)
            "修炼完成，获得了150点经验。"
        """
        pass
        
    @abstractmethod
    def get_cultivation_speed(self) -> float:
        """
        获取修炼速度
        
        Returns:
            float: 修炼速度倍率
        """
        pass
        
    @abstractmethod
    def set_cultivation_location(self, location_id: str) -> bool:
        """
        设置修炼地点
        
        Args:
            location_id: 地点ID
            
        Returns:
            bool: 是否设置成功
        """
        pass
        
    # ========== 境界管理 ==========
    
    @abstractmethod
    def get_current_realm(self) -> Tuple[CultivationRealm, int]:
        """
        获取当前境界
        
        Returns:
            Tuple[CultivationRealm, int]: (境界, 层数/阶段)
        """
        pass
        
    @abstractmethod
    def check_breakthrough_requirements(self) -> BreakthroughInfo:
        """
        检查突破条件
        
        Returns:
            BreakthroughInfo: 突破信息
        """
        pass
        
    @abstractmethod
    def attempt_breakthrough(self) -> Dict[str, Any]:
        """
        尝试突破境界
        
        Returns:
            Dict: 突破结果
                - success: 是否成功
                - new_realm: 新境界
                - tribulation_triggered: 是否触发天劫
                - rewards: 突破奖励
                - message: 结果描述
        """
        pass
        
    @abstractmethod
    def stabilize_realm(self) -> bool:
        """
        稳固境界
        
        Returns:
            bool: 是否成功稳固
        """
        pass
        
    # ========== 功法系统 ==========
    
    @abstractmethod
    def learn_technique(self, technique_id: str) -> bool:
        """
        学习功法
        
        Args:
            technique_id: 功法ID
            
        Returns:
            bool: 是否学习成功
        """
        pass
        
    @abstractmethod
    def practice_technique(self, technique_id: str, duration: float) -> Dict[str, Any]:
        """
        修炼功法
        
        Args:
            technique_id: 功法ID
            duration: 修炼时长
            
        Returns:
            Dict: 修炼结果
        """
        pass
        
    @abstractmethod
    def switch_main_technique(self, technique_id: str) -> bool:
        """
        切换主修功法
        
        Args:
            technique_id: 功法ID
            
        Returns:
            bool: 是否切换成功
        """
        pass
        
    @abstractmethod
    def get_learned_techniques(self) -> List[CultivationTechnique]:
        """
        获取已学功法
        
        Returns:
            List[CultivationTechnique]: 功法列表
        """
        pass
        
    # ========== 天劫系统 ==========
    
    @abstractmethod
    def trigger_tribulation(self, tribulation_type: str = "breakthrough") -> str:
        """
        触发天劫
        
        Args:
            tribulation_type: 天劫类型
            
        Returns:
            str: 天劫ID
        """
        pass
        
    @abstractmethod
    def face_tribulation(self, tribulation_id: str, action: str) -> Dict[str, Any]:
        """
        应对天劫
        
        Args:
            tribulation_id: 天劫ID
            action: 应对方式 ('resist', 'dodge', 'absorb', 'counter')
            
        Returns:
            Dict: 应对结果
        """
        pass
        
    @abstractmethod
    def get_tribulation_status(self, tribulation_id: str) -> Optional[Tribulation]:
        """
        获取天劫状态
        
        Args:
            tribulation_id: 天劫ID
            
        Returns:
            Tribulation: 天劫状态
        """
        pass
        
    # ========== 灵根体质 ==========
    
    @abstractmethod
    def get_spiritual_root(self) -> Dict[str, Any]:
        """
        获取灵根信息
        
        Returns:
            Dict: 灵根信息
                - type: 灵根类型
                - attributes: 属性亲和度
                - quality: 品质
        """
        pass
        
    @abstractmethod
    def improve_spiritual_root(self, method: str) -> bool:
        """
        改善灵根
        
        Args:
            method: 改善方法 ('pill', 'treasure', 'technique')
            
        Returns:
            bool: 是否改善成功
        """
        pass
        
    @abstractmethod
    def get_physique(self) -> Dict[str, Any]:
        """
        获取体质信息
        
        Returns:
            Dict: 体质信息
        """
        pass
        
    @abstractmethod
    def awaken_special_physique(self, physique_type: str) -> bool:
        """
        觉醒特殊体质
        
        Args:
            physique_type: 体质类型
            
        Returns:
            bool: 是否觉醒成功
        """
        pass
        
    # ========== 丹药系统 ==========
    
    @abstractmethod
    def use_cultivation_pill(self, pill_id: str) -> Dict[str, Any]:
        """
        使用修炼丹药
        
        Args:
            pill_id: 丹药ID
            
        Returns:
            Dict: 使用结果
        """
        pass
        
    @abstractmethod
    def refine_pill(self, recipe_id: str, materials: Dict[str, int]) -> Dict[str, Any]:
        """
        炼制丹药
        
        Args:
            recipe_id: 丹方ID
            materials: 材料
            
        Returns:
            Dict: 炼制结果
        """
        pass
        
    @abstractmethod
    def get_pill_toxicity(self) -> int:
        """
        获取丹毒值
        
        Returns:
            int: 当前丹毒值
        """
        pass
        
    @abstractmethod
    def cleanse_pill_toxicity(self, amount: int) -> int:
        """
        清除丹毒
        
        Args:
            amount: 清除量
            
        Returns:
            int: 实际清除量
        """
        pass
        
    # ========== 悟道机缘 ==========
    
    @abstractmethod
    def enter_enlightenment(self) -> bool:
        """
        进入悟道状态
        
        Returns:
            bool: 是否成功进入
        """
        pass
        
    @abstractmethod
    def comprehend_dao(self, dao_type: str) -> Dict[str, Any]:
        """
        参悟大道
        
        Args:
            dao_type: 道的类型 ('sword', 'fire', 'space', 'time', etc.)
            
        Returns:
            Dict: 参悟结果
        """
        pass
        
    @abstractmethod
    def get_dao_comprehension(self) -> Dict[str, float]:
        """
        获取道的领悟程度
        
        Returns:
            Dict[str, float]: 各种道的领悟度（0-1）
        """
        pass
        
    # ========== 修炼环境 ==========
    
    @abstractmethod
    def get_spiritual_energy_density(self) -> float:
        """
        获取当前灵气浓度
        
        Returns:
            float: 灵气浓度倍率
        """
        pass
        
    @abstractmethod
    def find_cultivation_spot(self) -> Optional[str]:
        """
        寻找修炼宝地
        
        Returns:
            str: 宝地位置ID，未找到返回None
        """
        pass
        
    @abstractmethod
    def setup_formation(self, formation_type: str) -> bool:
        """
        布置阵法辅助修炼
        
        Args:
            formation_type: 阵法类型
            
        Returns:
            bool: 是否布置成功
        """
        pass
        
    # ========== 修炼统计 ==========
    
    @abstractmethod
    def get_cultivation_statistics(self) -> Dict[str, Any]:
        """
        获取修炼统计
        
        Returns:
            Dict: 统计信息
                - total_cultivation_time: 总修炼时间
                - breakthroughs: 突破次数
                - tribulations_passed: 渡劫成功次数
                - techniques_mastered: 精通的功法数
        """
        pass
        
    @abstractmethod
    def get_cultivation_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取修炼历史
        
        Args:
            days: 最近N天
            
        Returns:
            List[Dict]: 修炼记录
        """
        pass
