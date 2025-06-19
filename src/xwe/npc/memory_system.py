# npc/memory_system.py
"""
NPC记忆系统

管理NPC对事件和交互的记忆。
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """记忆类型"""
    DIALOGUE = "dialogue"      # 对话记忆
    TRADE = "trade"           # 交易记忆
    GIFT = "gift"             # 礼物记忆
    HELP = "help"             # 帮助记忆
    CONFLICT = "conflict"     # 冲突记忆
    QUEST = "quest"           # 任务记忆
    GENERAL = "general"       # 通用记忆


class MemoryImportance(Enum):
    """记忆重要性"""
    TRIVIAL = 1      # 琐碎
    MINOR = 2        # 次要
    MODERATE = 3     # 中等
    MAJOR = 4        # 重要
    CRITICAL = 5     # 关键


@dataclass
class Memory:
    """单个记忆"""
    id: str
    memory_type: MemoryType
    subject: str  # 记忆主体（通常是玩家ID）
    content: Dict[str, Any]
    importance: MemoryImportance
    game_time: int
    real_time: datetime = field(default_factory=datetime.now)
    
    # 记忆强度（随时间衰减）
    strength: float = 1.0
    
    # 情感关联
    emotion_association: Optional[str] = None
    emotion_intensity: float = 0.0
    
    # 关联的其他记忆
    related_memories: List[str] = field(default_factory=list)
    
    def decay(self, time_passed: int, decay_rate: float = 0.01) -> None:
        """
        记忆衰减
        
        Args:
            time_passed: 经过的游戏时间
            decay_rate: 衰减率
        """
        # 重要记忆衰减更慢
        adjusted_rate = decay_rate / self.importance.value
        self.strength = max(0, self.strength - adjusted_rate * time_passed)
    
    def reinforce(self, amount: float = 0.2) -> None:
        """强化记忆"""
        self.strength = min(1.0, self.strength + amount)
    
    def is_forgotten(self) -> bool:
        """是否已遗忘"""
        return self.strength <= 0
    
    def get_summary(self) -> str:
        """获取记忆摘要"""
        type_desc = {
            MemoryType.DIALOGUE: "对话",
            MemoryType.TRADE: "交易",
            MemoryType.GIFT: "礼物",
            MemoryType.HELP: "帮助",
            MemoryType.CONFLICT: "冲突",
            MemoryType.QUEST: "任务",
            MemoryType.GENERAL: "事件"
        }
        
        return f"{type_desc.get(self.memory_type, '未知')}: {self.content.get('summary', '无描述')}"


@dataclass 
class MemoryCluster:
    """记忆簇 - 相关记忆的集合"""
    id: str
    theme: str  # 主题
    memories: List[str] = field(default_factory=list)  # 记忆ID列表
    total_importance: float = 0.0
    last_accessed: int = 0
    
    def add_memory(self, memory_id: str, importance: float) -> None:
        """添加记忆到簇"""
        if memory_id not in self.memories:
            self.memories.append(memory_id)
            self.total_importance += importance
    
    def remove_memory(self, memory_id: str, importance: float) -> None:
        """从簇中移除记忆"""
        if memory_id in self.memories:
            self.memories.remove(memory_id)
            self.total_importance = max(0, self.total_importance - importance)


    def get_memory_profile(self, npc_id: str, target_id: str) -> Dict[str, Any]:
        """获取NPC对目标的记忆概况"""
        memories = self.get_memories(npc_id, target_id)

        if not memories:
            return {
                "has_met": False,
                "relationship": 0,
                "last_interaction": None,
                "interaction_count": 0,
                "important_events": []
            }

        # 统计信息
        interaction_count = len(memories)
        last_memory = memories[-1] if memories else None

        # 计算关系值
        relationship = 0
        important_events = []

        for memory in memories:
            # 根据记忆类型调整关系值
            if memory.memory_type == MemoryType.POSITIVE:
                relationship += memory.importance * 0.1
            elif memory.memory_type == MemoryType.NEGATIVE:
                relationship -= memory.importance * 0.1

            # 收集重要事件
            if memory.importance >= 7:
                important_events.append({
                    "content": memory.content,
                    "timestamp": memory.timestamp,
                    "type": memory.memory_type.value
                })

        return {
            "has_met": True,
            "relationship": round(relationship, 2),
            "last_interaction": last_memory.timestamp if last_memory else None,
            "interaction_count": interaction_count,
            "important_events": important_events[-5:]  # 最近5个重要事件
        }

class MemorySystem:
    """
    记忆系统
    
    管理NPC的长期和短期记忆。
    """
    
    def __init__(self, max_memories_per_npc: int = 100) -> None:
        """
        初始化记忆系统
        
        Args:
            max_memories_per_npc: 每个NPC的最大记忆数
        """
        self.max_memories = max_memories_per_npc
        self.npc_memories: Dict[str, Dict[str, Memory]] = {}  # npc_id -> memory_id -> Memory
        self.memory_clusters: Dict[str, Dict[str, MemoryCluster]] = {}  # npc_id -> cluster_id -> MemoryCluster
        self.memory_counter = 0
        
        logger.info(f"记忆系统初始化 (最大记忆数: {max_memories_per_npc})")
    
    def add_memory(self, npc_id: str, memory_type: MemoryType, 
                  subject: str, content: Dict[str, Any], 
                  importance: MemoryImportance, game_time: int,
                  emotion: Optional[Tuple[str, float]] = None) -> str:
        """
        添加记忆
        
        Args:
            npc_id: NPC ID
            memory_type: 记忆类型
            subject: 记忆主体
            content: 记忆内容
            importance: 重要性
            game_time: 游戏时间
            emotion: 情感关联 (情感类型, 强度)
            
        Returns:
            记忆ID
        """
        # 确保NPC记忆存储存在
        if npc_id not in self.npc_memories:
            self.npc_memories[npc_id] = {}
            self.memory_clusters[npc_id] = {}
        
        # 创建记忆
        memory_id = f"mem_{self.memory_counter}"
        self.memory_counter += 1
        
        memory = Memory(
            id=memory_id,
            memory_type=memory_type,
            subject=subject,
            content=content,
            importance=importance,
            game_time=game_time
        )
        
        # 设置情感关联
        if emotion:
            memory.emotion_association = emotion[0]
            memory.emotion_intensity = emotion[1]
        
        # 查找相关记忆
        related = self._find_related_memories(npc_id, memory)
        memory.related_memories = [m.id for m in related[:3]]  # 最多关联3个
        
        # 存储记忆
        self.npc_memories[npc_id][memory_id] = memory
        
        # 管理记忆容量
        self._manage_memory_capacity(npc_id)
        
        # 更新记忆簇
        self._update_memory_clusters(npc_id, memory)
        
        logger.debug(f"NPC {npc_id} 新增记忆: {memory.get_summary()}")
        
        return memory_id
    
    def _find_related_memories(self, npc_id: str, new_memory: Memory) -> List[Memory]:
        """查找相关记忆"""
        if npc_id not in self.npc_memories:
            return []
        
        related = []
        
        for memory in self.npc_memories[npc_id].values():
            if memory.id == new_memory.id:
                continue
            
            # 相关性评分
            score = 0
            
            # 相同主体
            if memory.subject == new_memory.subject:
                score += 3
            
            # 相同类型
            if memory.memory_type == new_memory.memory_type:
                score += 2
            
            # 时间接近
            time_diff = abs(memory.game_time - new_memory.game_time)
            if time_diff < 10:
                score += 2
            elif time_diff < 50:
                score += 1
            
            # 情感关联
            if (memory.emotion_association and new_memory.emotion_association and
                memory.emotion_association == new_memory.emotion_association):
                score += 2
            
            if score > 3:
                related.append((score, memory))
        
        # 按相关性排序
        related.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in related]
    
    def _manage_memory_capacity(self, npc_id: str) -> None:
        """管理记忆容量"""
        memories = self.npc_memories.get(npc_id, {})
        
        if len(memories) <= self.max_memories:
            return
        
        # 需要遗忘一些记忆
        # 按重要性和强度排序
        memory_list = list(memories.values())
        memory_list.sort(key=lambda m: m.importance.value * m.strength)
        
        # 遗忘最不重要的记忆
        to_forget = memory_list[:len(memories) - self.max_memories + 10]  # 留出一些空间
        
        for memory in to_forget:
            self.forget_memory(npc_id, memory.id)
    
    def _update_memory_clusters(self, npc_id: str, memory: Memory) -> None:
        """更新记忆簇"""
        clusters = self.memory_clusters.get(npc_id, {})
        
        # 查找相关簇
        best_cluster = None
        best_score = 0
        
        for cluster in clusters.values():
            score = 0
            
            # 检查主题相关性
            if memory.subject in cluster.theme:
                score += 3
            if memory.memory_type.value in cluster.theme:
                score += 2
            
            # 检查是否有相关记忆在簇中
            for related_id in memory.related_memories:
                if related_id in cluster.memories:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_cluster = cluster
        
        # 如果找到合适的簇，添加记忆
        if best_cluster and best_score > 2:
            best_cluster.add_memory(memory.id, memory.importance.value)
        else:
            # 创建新簇
            cluster_id = f"cluster_{len(clusters)}"
            theme = f"{memory.subject}_{memory.memory_type.value}"
            
            new_cluster = MemoryCluster(
                id=cluster_id,
                theme=theme,
                last_accessed=memory.game_time
            )
            new_cluster.add_memory(memory.id, memory.importance.value)
            
            clusters[cluster_id] = new_cluster
            self.memory_clusters[npc_id] = clusters
    
    def recall_memories(self, npc_id: str, context: Dict[str, Any], 
                       max_memories: int = 5) -> List[Memory]:
        """
        回忆相关记忆
        
        Args:
            npc_id: NPC ID
            context: 当前上下文
            max_memories: 最大返回记忆数
            
        Returns:
            相关记忆列表
        """
        if npc_id not in self.npc_memories:
            return []
        
        memories = self.npc_memories[npc_id]
        scored_memories = []
        
        # 为每个记忆评分
        for memory in memories.values():
            if memory.strength <= 0:
                continue
            
            score = 0
            
            # 主体匹配
            if context.get('subject') == memory.subject:
                score += 5
            
            # 类型相关
            if context.get('memory_type') == memory.memory_type:
                score += 3
            
            # 时间相关性
            time_diff = abs(context.get('game_time', 0) - memory.game_time)
            if time_diff < 10:
                score += 3
            elif time_diff < 50:
                score += 1
            
            # 情感相关
            if (context.get('emotion') and memory.emotion_association and
                context.get('emotion') == memory.emotion_association):
                score += 2
            
            # 重要性和强度
            score += memory.importance.value * memory.strength
            
            scored_memories.append((score, memory))
        
        # 排序并返回最相关的记忆
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        
        result = []
        for _, memory in scored_memories[:max_memories]:
            # 强化被回忆的记忆
            memory.reinforce(0.1)
            result.append(memory)
        
        return result
    
    def get_memory_summary(self, npc_id: str, subject: str) -> Dict[str, Any]:
        """
        获取关于某个主体的记忆摘要
        
        Args:
            npc_id: NPC ID
            subject: 主体（通常是玩家ID）
            
        Returns:
            记忆摘要
        """
        if npc_id not in self.npc_memories:
            return {
                'total_memories': 0,
                'positive_memories': 0,
                'negative_memories': 0,
                'last_interaction': None,
                'most_important_memory': None
            }
        
        memories = [m for m in self.npc_memories[npc_id].values() 
                   if m.subject == subject and m.strength > 0]
        
        positive = 0
        negative = 0
        last_time = 0
        most_important = None
        
        for memory in memories:
            # 统计正负面记忆
            if memory.emotion_association:
                if memory.emotion_association in ['happy', 'grateful', 'impressed']:
                    positive += 1
                elif memory.emotion_association in ['angry', 'fearful', 'disgusted']:
                    negative += 1
            
            # 最近交互
            if memory.game_time > last_time:
                last_time = memory.game_time
            
            # 最重要记忆
            if not most_important or memory.importance.value > most_important.importance.value:
                most_important = memory
        
        return {
            'total_memories': len(memories),
            'positive_memories': positive,
            'negative_memories': negative,
            'last_interaction': last_time,
            'most_important_memory': most_important.get_summary() if most_important else None
        }
    
    def forget_memory(self, npc_id: str, memory_id: str) -> None:
        """遗忘记忆"""
        if npc_id not in self.npc_memories:
            return
        
        if memory_id in self.npc_memories[npc_id]:
            memory = self.npc_memories[npc_id][memory_id]
            
            # 从记忆簇中移除
            for cluster in self.memory_clusters.get(npc_id, {}).values():
                cluster.remove_memory(memory_id, memory.importance.value)
            
            # 删除记忆
            del self.npc_memories[npc_id][memory_id]
            
            logger.debug(f"NPC {npc_id} 遗忘记忆: {memory.get_summary()}")
    
    def update_memory_strength(self, npc_id: str, current_time: int) -> None:
        """
        更新记忆强度（自然衰减）
        
        Args:
            npc_id: NPC ID
            current_time: 当前游戏时间
        """
        if npc_id not in self.npc_memories:
            return
        
        to_forget = []
        
        for memory_id, memory in self.npc_memories[npc_id].items():
            time_passed = current_time - memory.game_time
            memory.decay(time_passed)
            
            if memory.is_forgotten():
                to_forget.append(memory_id)
        
        # 遗忘强度为0的记忆
        for memory_id in to_forget:
            self.forget_memory(npc_id, memory_id)
    
    def create_dialogue_memory(self, npc_id: str, player_id: str,
                             dialogue_summary: str, game_time: int,
                             importance: MemoryImportance = MemoryImportance.MINOR,
                             emotion: Optional[Tuple[str, float]] = None):
        """创建对话记忆的便捷方法"""
        content = {
            'summary': dialogue_summary,
            'type': 'dialogue'
        }
        
        return self.add_memory(
            npc_id=npc_id,
            memory_type=MemoryType.DIALOGUE,
            subject=player_id,
            content=content,
            importance=importance,
            game_time=game_time,
            emotion=emotion
        )
    
    def create_trade_memory(self, npc_id: str, player_id: str,
                          items_traded: List[str], trade_value: int,
                          game_time: int, successful: bool = True):
        """创建交易记忆的便捷方法"""
        content = {
            'summary': f"交易了{len(items_traded)}件物品，价值{trade_value}灵石",
            'items': items_traded,
            'value': trade_value,
            'successful': successful
        }
        
        importance = MemoryImportance.MINOR
        if trade_value > 1000:
            importance = MemoryImportance.MODERATE
        elif trade_value > 10000:
            importance = MemoryImportance.MAJOR
        
        emotion = None
        if successful:
            emotion = ('happy', 0.3 if trade_value < 1000 else 0.6)
        
        return self.add_memory(
            npc_id=npc_id,
            memory_type=MemoryType.TRADE,
            subject=player_id,
            content=content,
            importance=importance,
            game_time=game_time,
            emotion=emotion
        )

    def get_memory_profile(self, npc_id: str, player_id: str) -> dict:
        """获取NPC对玩家的记忆概况"""
        return {
            "recent_events": [],
            "affinity": 0,
            "total_memories": 0,
            "memory_types": {},
            "first_meeting": None,
            "last_interaction": None,
        }

    def generate_memory_context(self, npc_id: str, player_id: str) -> str:
        """生成NPC记忆上下文摘要"""
        profile = self.get_memory_profile(npc_id, player_id)
        events = profile.get("recent_events", [])
        if events:
            return "; ".join(events)
        return ""

    def create_memory(self, npc_id: str, player_id: str, memory_type: str,
                      game_time: int = 0, **content) -> str:
        """兼容旧接口的创建记忆方法"""
        try:
            mtype = MemoryType(memory_type)
        except Exception:
            mtype = MemoryType.GENERAL
        return self.add_memory(
            npc_id=npc_id,
            memory_type=mtype,
            subject=player_id,
            content=content,
            importance=MemoryImportance.MINOR,
            game_time=game_time,
        )
