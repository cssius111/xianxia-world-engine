# achievement_system_fixed.py
"""
渐进式成就系统
成就根据玩家实际行为逐步解锁，而非一开始全部解锁
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Callable, Any

class Achievement:
    def __init__(self, id: str, name: str, description: str, 
                 icon: str, points: int, hidden: bool = False):
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon
        self.points = points
        self.hidden = hidden
        self.unlocked = False
        self.unlock_time = None
        self.progress = 0
        self.max_progress = 1
        
class AchievementSystem:
    def __init__(self):
        self.achievements = self._init_achievements()
        self.unlock_callbacks = []
        self.total_points = 0
        self.unlock_queue = []  # 解锁队列，避免同时弹出多个
        
    def _init_achievements(self) -> Dict[str, Achievement]:
        """初始化所有成就（未解锁状态）"""
        achievements = {
            # 新手成就
            'first_step': Achievement(
                'first_step', '初入江湖', '完成角色创建',
                '🌟', 10
            ),
            'first_battle': Achievement(
                'first_battle', '初试锋芒', '赢得第一场战斗',
                '⚔️', 20
            ),
            'first_cultivation': Achievement(
                'first_cultivation', '踏上仙途', '第一次修炼',
                '🧘', 15
            ),
            
            # 战斗成就
            'warrior_10': Achievement(
                'warrior_10', '小有所成', '累计战胜10个敌人',
                '🗡️', 30
            ),
            'warrior_50': Achievement(
                'warrior_50', '百战之师', '累计战胜50个敌人',
                '⚔️', 50
            ),
            'no_damage_win': Achievement(
                'no_damage_win', '毫发无伤', '在一场战斗中不受任何伤害并获胜',
                '🛡️', 40
            ),
            'win_streak_10': Achievement(
                'win_streak_10', '连战连捷', '连续赢得10场战斗',
                '🔥', 45
            ),
            
            # 修炼成就
            'breakthrough_qi': Achievement(
                'breakthrough_qi', '筑基成功', '突破至筑基期',
                '💫', 50
            ),
            'breakthrough_golden': Achievement(
                'breakthrough_golden', '金丹大成', '突破至金丹期',
                '🌟', 100
            ),
            'cultivation_100h': Achievement(
                'cultivation_100h', '勤修苦练', '累计修炼100小时',
                '⏰', 60
            ),
            
            # 探索成就
            'explorer_10': Achievement(
                'explorer_10', '游历四方', '探索10个不同地点',
                '🗺️', 25
            ),
            'secret_place': Achievement(
                'secret_place', '机缘巧合', '发现隐藏地点',
                '🎁', 35, hidden=True
            ),
            
            # 社交成就
            'friend_10': Achievement(
                'friend_10', '广结善缘', '与10个NPC建立友好关系',
                '🤝', 30
            ),
            'master_disciple': Achievement(
                'master_disciple', '名师高徒', '拜入师门或收徒',
                '👥', 40
            ),
            
            # 财富成就
            'rich_10000': Achievement(
                'rich_10000', '小有积蓄', '拥有10000金币',
                '💰', 20
            ),
            'rich_100000': Achievement(
                'rich_100000', '富甲一方', '拥有100000金币',
                '💎', 50
            ),
            
            # 特殊成就
            'death_escape': Achievement(
                'death_escape', '大难不死', '从濒死状态恢复',
                '❤️‍🩹', 35
            ),
            'legendary_item': Achievement(
                'legendary_item', '神兵在手', '获得传说级物品',
                '✨', 80, hidden=True
            ),
        }
        
        # 设置进度型成就的最大进度
        achievements['warrior_10'].max_progress = 10
        achievements['warrior_50'].max_progress = 50
        achievements['win_streak_10'].max_progress = 10
        achievements['cultivation_100h'].max_progress = 100
        achievements['explorer_10'].max_progress = 10
        achievements['friend_10'].max_progress = 10
        achievements['rich_10000'].max_progress = 10000
        achievements['rich_100000'].max_progress = 100000
        
        return achievements
        
    def check_achievement(self, achievement_id: str, current_value: Any = None) -> bool:
        """检查并可能解锁成就"""
        if achievement_id not in self.achievements:
            return False
            
        achievement = self.achievements[achievement_id]
        
        # 已解锁的成就不重复解锁
        if achievement.unlocked:
            return False
            
        # 更新进度
        if current_value is not None and achievement.max_progress > 1:
            achievement.progress = min(current_value, achievement.max_progress)
            
        # 检查是否达成
        if achievement.progress >= achievement.max_progress:
            self._unlock_achievement(achievement_id)
            return True
            
        return False
        
    def _unlock_achievement(self, achievement_id: str):
        """解锁成就"""
        achievement = self.achievements[achievement_id]
        achievement.unlocked = True
        achievement.unlock_time = datetime.now()
        self.total_points += achievement.points
        
        # 加入解锁队列
        self.unlock_queue.append(achievement_id)
        
        # 触发回调
        for callback in self.unlock_callbacks:
            callback(achievement)
            
    def check_multiple_achievements(self, checks: Dict[str, Any]):
        """批量检查成就"""
        for achievement_id, value in checks.items():
            self.check_achievement(achievement_id, value)
            
    def get_next_unlock_display(self) -> str:
        """获取下一个待显示的成就解锁信息"""
        if not self.unlock_queue:
            return None
            
        achievement_id = self.unlock_queue.pop(0)
        achievement = self.achievements[achievement_id]
        
        display = f"""
╔═══════════════════════════════════════╗
║        🎉 成就解锁！🎉               
║                                       
║  {achievement.icon} {achievement.name}
║  {achievement.description}
║  获得成就点数：{achievement.points}
║                                       
║  解锁时间：{achievement.unlock_time.strftime('%Y-%m-%d %H:%M')}
╚═══════════════════════════════════════╝
"""
        return display
        
    def get_achievement_progress(self, achievement_id: str) -> tuple:
        """获取成就进度"""
        if achievement_id not in self.achievements:
            return (0, 1)
            
        achievement = self.achievements[achievement_id]
        return (achievement.progress, achievement.max_progress)
        
    def get_unlocked_count(self) -> tuple:
        """获取已解锁成就数量"""
        unlocked = sum(1 for a in self.achievements.values() if a.unlocked)
        total = len(self.achievements)
        return (unlocked, total)
        
    def display_all_achievements(self) -> str:
        """显示所有成就"""
        unlocked_count, total_count = self.get_unlocked_count()
        
        display = f"""
╔═══════════════════════════════════════╗
║          成就系统                     
║  已解锁：{unlocked_count}/{total_count} | 总点数：{self.total_points}
╚═══════════════════════════════════════╝

"""
        
        # 分类显示
        categories = {
            '新手': ['first_step', 'first_battle', 'first_cultivation'],
            '战斗': ['warrior_10', 'warrior_50', 'no_damage_win', 'win_streak_10'],
            '修炼': ['breakthrough_qi', 'breakthrough_golden', 'cultivation_100h'],
            '探索': ['explorer_10', 'secret_place'],
            '社交': ['friend_10', 'master_disciple'],
            '财富': ['rich_10000', 'rich_100000'],
            '特殊': ['death_escape', 'legendary_item']
        }
        
        for category, achievement_ids in categories.items():
            display += f"\n【{category}成就】\n"
            for aid in achievement_ids:
                achievement = self.achievements[aid]
                if achievement.hidden and not achievement.unlocked:
                    continue  # 隐藏成就未解锁时不显示
                    
                status = '✅' if achievement.unlocked else '❌'
                progress_str = ''
                if achievement.max_progress > 1 and not achievement.unlocked:
                    progress_str = f" ({achievement.progress}/{achievement.max_progress})"
                    
                display += f"{status} {achievement.icon} {achievement.name} - {achievement.description}{progress_str}\n"
                
        return display
        
    def add_unlock_callback(self, callback: Callable):
        """添加成就解锁回调函数"""
        self.unlock_callbacks.append(callback)
        
    def save_to_file(self, filepath: str):
        """保存成就数据"""
        data = {
            'total_points': self.total_points,
            'achievements': {}
        }
        
        for aid, achievement in self.achievements.items():
            data['achievements'][aid] = {
                'unlocked': achievement.unlocked,
                'unlock_time': achievement.unlock_time.isoformat() if achievement.unlock_time else None,
                'progress': achievement.progress
            }
            
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    def load_from_file(self, filepath: str):
        """加载成就数据"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.total_points = data.get('total_points', 0)
            
            for aid, adata in data.get('achievements', {}).items():
                if aid in self.achievements:
                    achievement = self.achievements[aid]
                    achievement.unlocked = adata['unlocked']
                    achievement.progress = adata.get('progress', 0)
                    if adata['unlock_time']:
                        achievement.unlock_time = datetime.fromisoformat(adata['unlock_time'])
        except FileNotFoundError:
            pass  # 首次运行，没有存档
