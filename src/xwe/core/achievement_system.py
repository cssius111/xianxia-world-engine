"""
成就系统
跟踪和奖励玩家的各种成就
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AchievementCategory(Enum):
    """成就类别"""
    COMBAT = "战斗"
    EXPLORATION = "探索"
    CULTIVATION = "修炼"
    SOCIAL = "社交"
    COLLECTION = "收集"
    SPECIAL = "特殊"


@dataclass
class Achievement:
    """成就定义"""
    id: str
    name: str
    description: str
    category: AchievementCategory
    points: int = 10
    hidden: bool = False
    icon: str = "⭐"
    
    # 达成条件
    requirement_type: str = "count"  # count, unique, special
    requirement_value: int = 1
    
    # 奖励
    rewards: Dict[str, Any] = field(default_factory=dict)
    
    # 前置成就
    prerequisites: List[str] = field(default_factory=list)


@dataclass
class AchievementProgress:
    """成就进度"""
    achievement_id: str
    current_value: int = 0
    completed: bool = False
    completion_date: Optional[datetime] = None
    claimed: bool = False


class AchievementSystem:
    """
    成就系统管理器
    
    管理所有成就的定义、进度和奖励
    """
    
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.player_progress: Dict[str, AchievementProgress] = {}
        
        # 初始化成就
        self._init_achievements()
        
    def _init_achievements(self) -> None:
        """初始化所有成就"""
        # 战斗成就
        self._add_achievement(Achievement(
            id="first_battle",
            name="初战告捷",
            description="赢得第一场战斗",
            category=AchievementCategory.COMBAT,
            points=10,
            rewards={"exp": 100, "gold": 50}
        ))
        
        self._add_achievement(Achievement(
            id="warrior_10",
            name="小有名气",
            description="击败10个敌人",
            category=AchievementCategory.COMBAT,
            requirement_value=10,
            points=20,
            rewards={"exp": 500, "gold": 200}
        ))
        
        self._add_achievement(Achievement(
            id="warrior_50",
            name="战斗大师",
            description="击败50个敌人",
            category=AchievementCategory.COMBAT,
            requirement_value=50,
            points=50,
            rewards={"exp": 2000, "gold": 1000, "item": "master_sword"}
        ))
        
        self._add_achievement(Achievement(
            id="no_damage_win",
            name="毫发无伤",
            description="在一场战斗中不受任何伤害并获胜",
            category=AchievementCategory.COMBAT,
            requirement_type="special",
            points=30,
            rewards={"title": "无伤大师"}
        ))
        
        self._add_achievement(Achievement(
            id="win_streak_10",
            name="十连胜",
            description="连续赢得10场战斗",
            category=AchievementCategory.COMBAT,
            requirement_value=10,
            points=40,
            hidden=True,
            rewards={"exp": 1500, "buff": "victory_momentum"}
        ))
        
        # 探索成就
        self._add_achievement(Achievement(
            id="first_step",
            name="初入江湖",
            description="开始你的修仙之旅",
            category=AchievementCategory.EXPLORATION,
            points=5,
            rewards={"exp": 50}
        ))
        
        self._add_achievement(Achievement(
            id="explorer_5",
            name="探索者",
            description="发现5个不同的地点",
            category=AchievementCategory.EXPLORATION,
            requirement_type="unique",
            requirement_value=5,
            points=15,
            rewards={"item": "explorer_map"}
        ))
        
        # 修炼成就
        self._add_achievement(Achievement(
            id="first_cultivation",
            name="踏上修仙路",
            description="第一次修炼",
            category=AchievementCategory.CULTIVATION,
            points=10,
            rewards={"exp": 100, "mana": 50}
        ))
        
        self._add_achievement(Achievement(
            id="cultivation_100h",
            name="勤奋修炼",
            description="累计修炼100小时",
            category=AchievementCategory.CULTIVATION,
            requirement_value=100,
            points=30,
            rewards={"exp": 3000, "comprehension": 5}
        ))
        
        self._add_achievement(Achievement(
            id="breakthrough_foundation",
            name="筑基成功",
            description="突破到筑基期",
            category=AchievementCategory.CULTIVATION,
            requirement_type="special",
            points=50,
            rewards={"title": "筑基修士", "item": "foundation_pill"}
        ))
        
        # 社交成就
        self._add_achievement(Achievement(
            id="first_friend",
            name="初识好友",
            description="与一个NPC成为朋友",
            category=AchievementCategory.SOCIAL,
            points=10,
            rewards={"charisma": 5}
        ))
        
        self._add_achievement(Achievement(
            id="popular",
            name="人见人爱",
            description="与10个NPC的好感度达到友善",
            category=AchievementCategory.SOCIAL,
            requirement_value=10,
            points=25,
            rewards={"title": "社交达人", "charisma": 10}
        ))
        
        # 收集成就
        self._add_achievement(Achievement(
            id="collector_10",
            name="初级收藏家",
            description="收集10种不同的物品",
            category=AchievementCategory.COLLECTION,
            requirement_type="unique",
            requirement_value=10,
            points=15,
            rewards={"inventory_space": 10}
        ))
        
        self._add_achievement(Achievement(
            id="rich_1000",
            name="小有积蓄",
            description="拥有1000枚灵石",
            category=AchievementCategory.COLLECTION,
            requirement_value=1000,
            points=20,
            rewards={"gold": 500}
        ))
        
    def _add_achievement(self, achievement: Achievement) -> None:
        """添加成就定义"""
        self.achievements[achievement.id] = achievement
        
    def check_achievement(self, achievement_id: str, value: int = 1) -> bool:
        """
        检查成就进度
        
        Args:
            achievement_id: 成就ID
            value: 进度值
            
        Returns:
            是否新完成该成就
        """
        if achievement_id not in self.achievements:
            return False
            
        achievement = self.achievements[achievement_id]
        
        # 检查前置成就
        for prereq in achievement.prerequisites:
            if prereq not in self.player_progress or not self.player_progress[prereq].completed:
                return False
                
        # 获取或创建进度
        if achievement_id not in self.player_progress:
            self.player_progress[achievement_id] = AchievementProgress(achievement_id)
            
        progress = self.player_progress[achievement_id]
        
        # 如果已完成，不再更新
        if progress.completed:
            return False
            
        # 更新进度
        was_completed = progress.completed
        
        if achievement.requirement_type == "count":
            progress.current_value += value
            if progress.current_value >= achievement.requirement_value:
                progress.completed = True
        elif achievement.requirement_type == "unique":
            progress.current_value = value  # 直接设置为当前唯一值数量
            if progress.current_value >= achievement.requirement_value:
                progress.completed = True
        elif achievement.requirement_type == "special":
            # 特殊成就直接根据传入的value判断
            if value >= achievement.requirement_value:
                progress.completed = True
                
        # 如果新完成
        if not was_completed and progress.completed:
            progress.completion_date = datetime.now()
            logger.info(f"成就达成: {achievement.name}")
            return True
            
        return False
        
    def claim_achievement_rewards(self, achievement_id: str) -> Optional[Dict[str, Any]]:
        """
        领取成就奖励
        
        Args:
            achievement_id: 成就ID
            
        Returns:
            奖励内容，如果无法领取则返回None
        """
        if achievement_id not in self.achievements:
            return None
            
        progress = self.player_progress.get(achievement_id)
        if not progress or not progress.completed or progress.claimed:
            return None
            
        achievement = self.achievements[achievement_id]
        progress.claimed = True
        
        logger.info(f"领取成就奖励: {achievement.name}")
        return achievement.rewards.copy()
        
    def get_achievement_list(self, category: Optional[AchievementCategory] = None,
                           show_hidden: bool = False) -> List[Dict[str, Any]]:
        """
        获取成就列表
        
        Args:
            category: 筛选类别
            show_hidden: 是否显示隐藏成就
            
        Returns:
            成就信息列表
        """
        achievement_list = []
        
        for achievement in self.achievements.values():
            # 过滤类别
            if category and achievement.category != category:
                continue
                
            # 过滤隐藏成就
            if achievement.hidden and not show_hidden:
                progress = self.player_progress.get(achievement.id)
                if not progress or not progress.completed:
                    continue
                    
            # 构建成就信息
            progress = self.player_progress.get(achievement.id, AchievementProgress(achievement.id))
            
            info = {
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "category": achievement.category.value,
                "points": achievement.points,
                "icon": achievement.icon,
                "completed": progress.completed,
                "claimed": progress.claimed,
                "progress": progress.current_value,
                "requirement": achievement.requirement_value,
                "hidden": achievement.hidden
            }
            
            if progress.completion_date:
                info["completion_date"] = progress.completion_date.isoformat()
                
            achievement_list.append(info)
            
        return achievement_list
        
    def get_total_points(self) -> int:
        """获取总成就点数"""
        total = 0
        for achievement_id, progress in self.player_progress.items():
            if progress.completed and achievement_id in self.achievements:
                total += self.achievements[achievement_id].points
        return total
        
    def get_completion_stats(self) -> Dict[str, Any]:
        """获取成就完成统计"""
        total_achievements = len(self.achievements)
        completed_achievements = sum(1 for p in self.player_progress.values() if p.completed)
        
        category_stats = {}
        for category in AchievementCategory:
            category_total = sum(1 for a in self.achievements.values() if a.category == category)
            category_completed = sum(
                1 for a in self.achievements.values()
                if a.category == category and 
                self.player_progress.get(a.id, AchievementProgress(a.id)).completed
            )
            category_stats[category.value] = {
                "total": category_total,
                "completed": category_completed,
                "percentage": (category_completed / category_total * 100) if category_total > 0 else 0
            }
            
        return {
            "total": total_achievements,
            "completed": completed_achievements,
            "percentage": (completed_achievements / total_achievements * 100) if total_achievements > 0 else 0,
            "total_points": self.get_total_points(),
            "category_stats": category_stats
        }
