"""
AI个性化和智能玩法系统
- 玩家风格识别
- 自适应引导
- AI驱动NPC
- 动态内容推荐
"""


from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
import random
from collections import defaultdict, Counter
import json
import platform

logger = logging.getLogger(__name__)


class PlayerStyle(Enum):
    """玩家风格类型"""
    WARRIOR = "warrior"  # 战士型 - 喜欢战斗
    EXPLORER = "explorer"  # 探索型 - 喜欢发现新地方
    SOCIALIZER = "socializer"  # 社交型 - 喜欢与NPC互动
    ACHIEVER = "achiever"  # 成就党 - 喜欢收集和完成
    STRATEGIST = "strategist"  # 策略型 - 喜欢规划和优化
    SPEEDRUNNER = "speedrunner"  # 速通型 - 追求效率
    ROLEPLAYER = "roleplayer"  # 角色扮演型 - 重视剧情
    COLLECTOR = "collector"  # 收集型 - 喜欢收集物品


class ContentPreference(Enum):
    """内容偏好"""
    COMBAT = "combat"
    EXPLORATION = "exploration" 
    DIALOGUE = "dialogue"
    CRAFTING = "crafting"
    TRADING = "trading"
    CULTIVATION = "cultivation"
    QUESTS = "quests"
    CHALLENGES = "challenges"


@dataclass
class PlayerBehavior:
    """玩家行为记录"""
    action_type: str
    action_target: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    success: bool = True
    duration: float = 0.0


@dataclass
class PlayerProfile:
    """玩家画像"""
    player_id: str
    primary_style: PlayerStyle = PlayerStyle.EXPLORER
    secondary_style: Optional[PlayerStyle] = None
    style_scores: Dict[PlayerStyle, float] = field(default_factory=dict)
    content_preferences: Dict[ContentPreference, float] = field(default_factory=dict)
    behavior_history: List[PlayerBehavior] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    last_analysis_time: float = 0.0
    
    def add_behavior(self, behavior: PlayerBehavior) -> None:
        """添加行为记录"""
        self.behavior_history.append(behavior)
        # 保留最近1000条记录
        if len(self.behavior_history) > 1000:
            self.behavior_history = self.behavior_history[-1000:]
    
    def get_recent_behaviors(self, time_window: float = 3600) -> List[PlayerBehavior]:
        """获取最近的行为记录"""
        current_time = time.time()
        return [
            b for b in self.behavior_history 
            if current_time - b.timestamp <= time_window
        ]


class PlayerStyleAnalyzer:
    """玩家风格分析器"""
    
    def __init__(self):
        # 行为到风格的映射权重
        self.behavior_style_weights = {
            "attack": {PlayerStyle.WARRIOR: 2.0, PlayerStyle.SPEEDRUNNER: 1.0},
            "defend": {PlayerStyle.STRATEGIST: 1.5, PlayerStyle.WARRIOR: 0.5},
            "flee": {PlayerStyle.SPEEDRUNNER: 1.0, PlayerStyle.STRATEGIST: 0.5},
            "explore": {PlayerStyle.EXPLORER: 2.0, PlayerStyle.COLLECTOR: 1.0},
            "talk": {PlayerStyle.SOCIALIZER: 2.0, PlayerStyle.ROLEPLAYER: 1.5},
            "trade": {PlayerStyle.SOCIALIZER: 1.0, PlayerStyle.COLLECTOR: 1.5},
            "cultivate": {PlayerStyle.ACHIEVER: 1.0, PlayerStyle.STRATEGIST: 1.5},
            "collect_item": {PlayerStyle.COLLECTOR: 2.0, PlayerStyle.ACHIEVER: 1.0},
            "complete_quest": {PlayerStyle.ACHIEVER: 2.0, PlayerStyle.ROLEPLAYER: 1.0},
            "read_lore": {PlayerStyle.ROLEPLAYER: 2.0, PlayerStyle.EXPLORER: 1.0},
            "optimize_build": {PlayerStyle.STRATEGIST: 2.0, PlayerStyle.ACHIEVER: 1.0},
            "speedrun_area": {PlayerStyle.SPEEDRUNNER: 2.0, PlayerStyle.WARRIOR: 1.0}
        }
        
        # 内容偏好映射
        self.content_preference_weights = {
            "attack": ContentPreference.COMBAT,
            "explore": ContentPreference.EXPLORATION,
            "talk": ContentPreference.DIALOGUE,
            "trade": ContentPreference.TRADING,
            "cultivate": ContentPreference.CULTIVATION,
            "accept_quest": ContentPreference.QUESTS,
            "craft": ContentPreference.CRAFTING,
            "challenge": ContentPreference.CHALLENGES
        }
        
        # 分析参数
        self.analysis_interval = 300  # 5分钟分析一次
        self.behavior_decay_factor = 0.95  # 行为影响力衰减
    
    def analyze_player_style(self, profile: PlayerProfile) -> Tuple[PlayerStyle, Optional[PlayerStyle]]:
        """分析玩家风格"""
        current_time = time.time()
        
        # 检查是否需要重新分析
        if current_time - profile.last_analysis_time < self.analysis_interval:
            return profile.primary_style, profile.secondary_style
        
        profile.last_analysis_time = current_time
        
        # 初始化风格分数
        style_scores = defaultdict(float)
        
        # 分析行为历史
        for i, behavior in enumerate(reversed(profile.behavior_history)):
            # 计算时间衰减
            age = current_time - behavior.timestamp
            time_weight = self.behavior_decay_factor ** (age / 3600)  # 每小时衰减
            
            # 获取行为对应的风格权重
            if behavior.action_type in self.behavior_style_weights:
                for style, weight in self.behavior_style_weights[behavior.action_type].items():
                    style_scores[style] += weight * time_weight
        
        # 归一化分数
        total_score = sum(style_scores.values())
        if total_score > 0:
            for style in style_scores:
                style_scores[style] /= total_score
        
        # 更新profile
        profile.style_scores = dict(style_scores)
        
        # 确定主要和次要风格
        sorted_styles = sorted(style_scores.items(), key=lambda x: x[1], reverse=True)
        
        primary_style = sorted_styles[0][0] if sorted_styles else PlayerStyle.EXPLORER
        secondary_style = sorted_styles[1][0] if len(sorted_styles) > 1 and sorted_styles[1][1] > 0.15 else None
        
        profile.primary_style = primary_style
        profile.secondary_style = secondary_style
        
        logger.info(f"玩家风格分析: 主要={primary_style.value}, 次要={secondary_style.value if secondary_style else 'None'}")
        
        return primary_style, secondary_style
    
    def analyze_content_preferences(self, profile: PlayerProfile) -> Dict[ContentPreference, float]:
        """分析内容偏好"""
        preference_counts = defaultdict(int)
        
        # 统计最近的行为
        recent_behaviors = profile.get_recent_behaviors(7200)  # 最近2小时
        
        for behavior in recent_behaviors:
            if behavior.action_type in self.content_preference_weights:
                preference = self.content_preference_weights[behavior.action_type]
                preference_counts[preference] += 1
        
        # 计算偏好分数
        total_count = sum(preference_counts.values())
        if total_count > 0:
            preferences = {
                pref: count / total_count 
                for pref, count in preference_counts.items()
            }
        else:
            # 默认偏好
            preferences = {pref: 1.0 / len(ContentPreference) for pref in ContentPreference}
        
        profile.content_preferences = preferences
        return preferences


class AdaptiveGuideSystem:
    """自适应引导系统"""
    
    def __init__(self):
        self.guide_templates = {
            PlayerStyle.WARRIOR: {
                "tips": [
                    "附近有强大的敌人等待挑战，准备好你的武器！",
                    "听说东边的妖兽峡谷有稀有BOSS出没",
                    "提升战斗技能可以让你在战斗中更加得心应手"
                ],
                "recommendations": [
                    "尝试挑战更高级的敌人获得更好的奖励",
                    "学习连击技能可以大幅提升输出",
                    "别忘了升级你的装备"
                ]
            },
            PlayerStyle.EXPLORER: {
                "tips": [
                    "这个区域还有未发现的秘密等待探索",
                    "传说中的隐藏洞穴就在附近某处",
                    "仔细观察环境，可能会有意外发现"
                ],
                "recommendations": [
                    "试试往地图边缘探索",
                    "某些地点只在特定时间开放",
                    "收集地图碎片可以解锁新区域"
                ]
            },
            PlayerStyle.SOCIALIZER: {
                "tips": [
                    "村里的长老似乎有重要的事情要告诉你",
                    "多和NPC交流可以获得隐藏任务",
                    "提升好感度能解锁特殊对话选项"
                ],
                "recommendations": [
                    "试着帮助村民解决他们的烦恼",
                    "商人那里可能有稀有物品出售",
                    "加入门派可以认识更多朋友"
                ]
            },
            PlayerStyle.ACHIEVER: {
                "tips": [
                    "你距离下一个成就只差一点点了！",
                    "完成全部支线任务有特殊奖励",
                    "收集齐套装可以获得强大加成"
                ],
                "recommendations": [
                    "查看成就列表，规划完成路线",
                    "某些成就有隐藏条件",
                    "首次通关奖励非常丰厚"
                ]
            },
            PlayerStyle.STRATEGIST: {
                "tips": [
                    "合理分配属性点可以让角色更强",
                    "不同技能组合有意想不到的效果",
                    "了解敌人弱点可以事半功倍"
                ],
                "recommendations": [
                    "试试不同的build方案",
                    "计算最优修炼路线",
                    "准备充足再挑战BOSS"
                ]
            }
        }
        
        self.dynamic_events = {
            PlayerStyle.WARRIOR: ["arena_tournament", "boss_spawn", "combat_challenge"],
            PlayerStyle.EXPLORER: ["hidden_area_hint", "treasure_map", "secret_passage"],
            PlayerStyle.SOCIALIZER: ["npc_festival", "merchant_arrival", "faction_event"],
            PlayerStyle.ACHIEVER: ["limited_quest", "collection_event", "achievement_race"],
            PlayerStyle.STRATEGIST: ["puzzle_dungeon", "resource_event", "optimization_challenge"]
        }
    
    def get_personalized_tips(self, profile: PlayerProfile) -> List[str]:
        """获取个性化提示"""
        tips = []
        
        # 主要风格的提示
        if profile.primary_style in self.guide_templates:
            style_tips = self.guide_templates[profile.primary_style]["tips"]
            tips.extend(random.sample(style_tips, min(2, len(style_tips))))
        
        # 次要风格的提示
        if profile.secondary_style and profile.secondary_style in self.guide_templates:
            style_tips = self.guide_templates[profile.secondary_style]["tips"]
            tips.append(random.choice(style_tips))
        
        return tips
    
    def get_content_recommendations(self, profile: PlayerProfile) -> List[Dict[str, Any]]:
        """获取内容推荐"""
        recommendations = []
        
        # 基于主要风格的推荐
        if profile.primary_style in self.guide_templates:
            style_recs = self.guide_templates[profile.primary_style]["recommendations"]
            for rec in random.sample(style_recs, min(2, len(style_recs))):
                recommendations.append({
                    "type": "guide",
                    "content": rec,
                    "priority": "high"
                })
        
        # 基于内容偏好的推荐
        top_preferences = sorted(
            profile.content_preferences.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        for pref, score in top_preferences:
            if score > 0.2:  # 只推荐偏好度高的内容
                recommendations.append({
                    "type": "content",
                    "category": pref.value,
                    "priority": "medium" if score > 0.3 else "low"
                })
        
        return recommendations
    
    def suggest_next_action(self, profile: PlayerProfile, game_context: Dict[str, Any]) -> Optional[str]:
        """建议下一步行动"""
        suggestions = []
        
        # 基于风格的建议
        style_actions = {
            PlayerStyle.WARRIOR: ["寻找强敌", "升级装备", "学习新技能"],
            PlayerStyle.EXPLORER: ["探索新区域", "寻找隐藏地点", "收集地图"],
            PlayerStyle.SOCIALIZER: ["拜访NPC", "完成社交任务", "提升好感度"],
            PlayerStyle.ACHIEVER: ["查看成就进度", "完成收集", "挑战纪录"],
            PlayerStyle.STRATEGIST: ["优化配装", "规划路线", "研究机制"]
        }
        
        if profile.primary_style in style_actions:
            suggestions.extend(style_actions[profile.primary_style])
        
        # 基于游戏状态的建议
        if game_context.get("low_health", False):
            suggestions.insert(0, "恢复气血值")
        
        if game_context.get("new_area", False):
            suggestions.insert(0, "探索周围环境")
        
        if game_context.get("quest_available", False):
            suggestions.append("接受新任务")
        
        return suggestions[0] if suggestions else None


class DynamicNPCBehavior:
    """动态NPC行为系统"""
    
    def __init__(self):
        self.npc_personalities = {
            "friendly": {
                "greeting_style": ["热情", "友好", "亲切"],
                "interaction_frequency": 0.8,
                "help_probability": 0.7,
                "gift_probability": 0.3
            },
            "mysterious": {
                "greeting_style": ["神秘", "深沉", "谜语"],
                "interaction_frequency": 0.3,
                "help_probability": 0.5,
                "gift_probability": 0.1
            },
            "merchant": {
                "greeting_style": ["商业", "精明", "热络"],
                "interaction_frequency": 0.9,
                "help_probability": 0.4,
                "gift_probability": 0.05
            },
            "warrior": {
                "greeting_style": ["豪爽", "直接", "挑战"],
                "interaction_frequency": 0.5,
                "help_probability": 0.6,
                "gift_probability": 0.2
            },
            "scholar": {
                "greeting_style": ["博学", "严谨", "说教"],
                "interaction_frequency": 0.6,
                "help_probability": 0.8,
                "gift_probability": 0.15
            }
        }
        
        self.npc_states = {}  # NPC状态记录
        self.relationship_modifiers = {}  # 关系修正
    
    def generate_npc_dialogue(self, 
                            npc_id: str, 
                            npc_personality: str, 
                            player_profile: PlayerProfile,
                            context: Dict[str, Any]) -> str:
        """生成个性化NPC对话"""
        personality = self.npc_personalities.get(npc_personality, self.npc_personalities["friendly"])
        
        # 获取NPC状态
        npc_state = self.npc_states.get(npc_id, {
            "mood": "neutral",
            "last_interaction": 0,
            "interaction_count": 0,
            "relationship": 0
        })
        
        # 基于玩家风格调整对话
        dialogue_adjustments = {
            PlayerStyle.WARRIOR: "更直接、充满挑战",
            PlayerStyle.EXPLORER: "提供线索和秘密",
            PlayerStyle.SOCIALIZER: "更亲密、个人化",
            PlayerStyle.ACHIEVER: "提供任务和目标",
            PlayerStyle.STRATEGIST: "详细解释和建议"
        }
        
        # 生成对话
        greeting_style = random.choice(personality["greeting_style"])
        
        if player_profile.primary_style == PlayerStyle.SOCIALIZER:
            dialogue = f"（{greeting_style}地）啊，是你！很高兴再次见到你。"
        elif player_profile.primary_style == PlayerStyle.WARRIOR:
            dialogue = f"（{greeting_style}地）又来挑战了吗？我喜欢你的勇气。"
        elif player_profile.primary_style == PlayerStyle.EXPLORER:
            dialogue = f"（{greeting_style}地）你可能会对我知道的一个秘密感兴趣..."
        else:
            dialogue = f"（{greeting_style}地）欢迎，旅行者。"
        
        # 更新NPC状态
        npc_state["interaction_count"] += 1
        npc_state["last_interaction"] = time.time()
        self.npc_states[npc_id] = npc_state
        
        return dialogue
    
    def npc_should_approach_player(self, 
                                 npc_id: str, 
                                 npc_personality: str,
                                 player_profile: PlayerProfile) -> bool:
        """判断NPC是否应该主动接近玩家"""
        personality = self.npc_personalities.get(npc_personality, self.npc_personalities["friendly"])
        base_probability = personality["interaction_frequency"]
        
        # 根据玩家风格调整
        style_modifiers = {
            PlayerStyle.SOCIALIZER: 1.3,
            PlayerStyle.SPEEDRUNNER: 0.5,
            PlayerStyle.ROLEPLAYER: 1.1,
            PlayerStyle.WARRIOR: 0.8
        }
        
        modifier = style_modifiers.get(player_profile.primary_style, 1.0)
        
        # 关系修正
        relationship = self.npc_states.get(npc_id, {}).get("relationship", 0)
        relationship_modifier = 1.0 + (relationship / 100)
        
        final_probability = base_probability * modifier * relationship_modifier
        
        return random.random() < final_probability
    
    def generate_npc_action(self, 
                          npc_id: str,
                          npc_personality: str,
                          player_nearby: bool,
                          player_profile: Optional[PlayerProfile] = None) -> Dict[str, Any]:
        """生成NPC行动"""
        actions: List[Dict[str, Any]] = []
        
        if player_nearby and player_profile:
            # 检查是否应该接近玩家
            if self.npc_should_approach_player(npc_id, npc_personality, player_profile):
                actions.append({
                    "type": "approach_player",
                    "dialogue": self.generate_npc_dialogue(
                        npc_id, npc_personality, player_profile, {}
                    )
                })
            
            # 检查是否应该提供帮助
            personality = self.npc_personalities.get(npc_personality)
            if random.random() < personality["help_probability"]:
                if player_profile.primary_style == PlayerStyle.EXPLORER:
                    actions.append({
                        "type": "offer_information",
                        "content": "我知道一些你可能感兴趣的地方..."
                    })
                elif player_profile.primary_style == PlayerStyle.ACHIEVER:
                    actions.append({
                        "type": "offer_quest",
                        "content": "我这里有个任务，你或许能帮上忙..."
                    })
        else:
            # 日常行为
            daily_actions = ["patrol", "idle", "work", "chat_with_npc", "move_to_location"]
            actions.append({
                "type": random.choice(daily_actions),
                "duration": random.randint(30, 300)
            })
        
        return actions[0] if actions else {"type": "idle", "duration": 60}


class PersonalizationEngine:
    """个性化引擎"""
    
    def __init__(self):
        self.style_analyzer = PlayerStyleAnalyzer()
        self.guide_system = AdaptiveGuideSystem()
        self.npc_behavior = DynamicNPCBehavior()
        
        self.player_profiles: Dict[str, PlayerProfile] = {}
        self.active_recommendations: Dict[str, List[Dict[str, Any]]] = {}
    
    def get_or_create_profile(self, player_id: str) -> PlayerProfile:
        """获取或创建玩家画像"""
        if player_id not in self.player_profiles:
            self.player_profiles[player_id] = PlayerProfile(player_id=player_id)
        return self.player_profiles[player_id]
    
    def record_player_action(self, 
                           player_id: str,
                           action_type: str,
                           action_target: Optional[str] = None,
                           context: Optional[Dict[str, Any]] = None,
                           success: bool = True):
        """记录玩家行为"""
        profile = self.get_or_create_profile(player_id)
        
        behavior = PlayerBehavior(
            action_type=action_type,
            action_target=action_target,
            context=context or {},
            success=success
        )
        
        profile.add_behavior(behavior)
        
        # 更新统计
        if "statistics" not in profile.__dict__:
            profile.statistics = {}
        
        stat_key = f"{action_type}_count"
        profile.statistics[stat_key] = profile.statistics.get(stat_key, 0) + 1
        
        # 每50个行为分析一次
        if len(profile.behavior_history) % 50 == 0:
            self.style_analyzer.analyze_player_style(profile)
            self.style_analyzer.analyze_content_preferences(profile)
    
    def get_personalized_content(self, player_id: str) -> Dict[str, Any]:
        """获取个性化内容"""
        profile = self.get_or_create_profile(player_id)
        
        # 更新分析
        self.style_analyzer.analyze_player_style(profile)
        self.style_analyzer.analyze_content_preferences(profile)
        
        # 获取个性化内容
        tips = self.guide_system.get_personalized_tips(profile)
        recommendations = self.guide_system.get_content_recommendations(profile)
        
        # 存储活跃推荐
        self.active_recommendations[player_id] = recommendations
        
        return {
            "player_style": profile.primary_style.value,
            "secondary_style": profile.secondary_style.value if profile.secondary_style else None,
            "tips": tips,
            "recommendations": recommendations,
            "preferred_content": [
                pref.value for pref, score in profile.content_preferences.items() 
                if score > 0.2
            ]
        }
    
    def get_npc_behavior(self, 
                        npc_id: str,
                        npc_personality: str,
                        player_id: Optional[str] = None,
                        player_nearby: bool = False) -> Dict[str, Any]:
        """获取NPC行为"""
        player_profile = None
        if player_id:
            player_profile = self.get_or_create_profile(player_id)
        
        return self.npc_behavior.generate_npc_action(
            npc_id, npc_personality, player_nearby, player_profile
        )
    
    def generate_adaptive_story(self, player_id: str, story_context: Dict[str, Any]) -> str:
        """生成自适应剧情"""
        profile = self.get_or_create_profile(player_id)
        
        # 基于玩家风格的剧情模板
        story_templates = {
            PlayerStyle.WARRIOR: "一个关于勇气和力量的故事...",
            PlayerStyle.EXPLORER: "一个关于发现和冒险的故事...",
            PlayerStyle.SOCIALIZER: "一个关于友谊和联系的故事...",
            PlayerStyle.ACHIEVER: "一个关于成就和荣耀的故事...",
            PlayerStyle.STRATEGIST: "一个关于智慧和谋略的故事...",
            PlayerStyle.ROLEPLAYER: "一个关于命运和选择的故事..."
        }
        
        base_story = story_templates.get(profile.primary_style, "一个神秘的故事...")
        
        # 根据玩家偏好调整剧情元素
        if ContentPreference.COMBAT in profile.content_preferences and profile.content_preferences[ContentPreference.COMBAT] > 0.3:
            base_story += "\n剧情中包含激烈的战斗场面。"
        
        if ContentPreference.DIALOGUE in profile.content_preferences and profile.content_preferences[ContentPreference.DIALOGUE] > 0.3:
            base_story += "\n剧情中有深入的角色对话。"
        
        return base_story
    
    def export_profile_data(self, player_id: str) -> Dict[str, Any]:
        """导出玩家画像数据"""
        profile = self.get_or_create_profile(player_id)
        
        return {
            "player_id": player_id,
            "primary_style": profile.primary_style.value,
            "secondary_style": profile.secondary_style.value if profile.secondary_style else None,
            "style_scores": {style.value: score for style, score in profile.style_scores.items()},
            "content_preferences": {pref.value: score for pref, score in profile.content_preferences.items()},
            "total_actions": len(profile.behavior_history),
            "statistics": profile.statistics,
            "recommendations_count": len(self.active_recommendations.get(player_id, []))
        }


# 全局实例
personalization_engine = PersonalizationEngine()

# 向后兼容的别名
class AIPersonalization(PersonalizationEngine):
    """`PersonalizationEngine` 的别名, 兼容旧代码"""
    pass

def enhance_with_ai_features(game_core) -> None:
    """为游戏核心添加AI功能"""
    original_process_command = game_core.process_command
    
    def ai_enhanced_process_command(input_text: str) -> None:
        """AI增强的命令处理"""
        player_id = "player_1"  # 简化处理，实际应该从游戏状态获取
        
        # 记录玩家行为
        # 简单解析命令类型
        action_type = "unknown"
        if any(word in input_text for word in ["攻击", "打", "杀"]):
            action_type = "attack"
        elif any(word in input_text for word in ["探索", "查看", "搜索"]):
            action_type = "explore"
        elif any(word in input_text for word in ["说话", "对话", "交谈"]):
            action_type = "talk"
        elif any(word in input_text for word in ["修炼", "打坐", "冥想"]):
            action_type = "cultivate"
        
        personalization_engine.record_player_action(
            player_id=player_id,
            action_type=action_type,
            context={"input": input_text}
        )
        
        # 获取个性化内容
        if random.random() < 0.1:  # 10%概率显示个性化提示
            personalized = personalization_engine.get_personalized_content(player_id)
            if personalized["tips"]:
                game_core.output(f"\n💡 {random.choice(personalized['tips'])}")
        
        # 调用原始方法
        original_process_command(input_text)
    
    # 替换方法
    game_core.process_command = ai_enhanced_process_command
    
    # 添加AI相关方法
    game_core.get_player_profile = lambda: personalization_engine.export_profile_data("player_1")
    game_core.get_ai_recommendation = lambda: personalization_engine.get_personalized_content("player_1")
    
    logger.info("AI个性化功能已启用")

