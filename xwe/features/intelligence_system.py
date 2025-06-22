"""
情报系统模块
处理游戏中的情报收集、分析和交易
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set
import random


class IntelType(Enum):
    """情报类型"""
    LOCATION = "location"          # 地点情报
    CHARACTER = "character"        # 人物情报
    TREASURE = "treasure"          # 宝物情报
    TECHNIQUE = "technique"        # 功法情报
    EVENT = "event"               # 事件情报
    SECRET = "secret"             # 秘密情报


class IntelSource(Enum):
    """情报来源"""
    NPC = "npc"                   # NPC对话
    EXPLORATION = "exploration"    # 探索发现
    PURCHASE = "purchase"         # 购买获得
    QUEST = "quest"               # 任务奖励
    EAVESDROP = "eavesdrop"       # 偷听获得
    STEAL = "steal"               # 偷窃获得


class IntelReliability(Enum):
    """情报可靠度"""
    CONFIRMED = "confirmed"        # 已确认
    RELIABLE = "reliable"         # 可靠
    UNCERTAIN = "uncertain"       # 不确定
    DUBIOUS = "dubious"          # 可疑
    FALSE = "false"              # 虚假


@dataclass
class IntelItem:
    """情报项"""
    id: str
    title: str
    content: str
    type: IntelType
    source: IntelSource
    reliability: IntelReliability
    timestamp: datetime
    location: Optional[str] = None
    related_ids: List[str] = None
    value: int = 0
    verified: bool = False
    
    def __post_init__(self):
        if self.related_ids is None:
            self.related_ids = []


class IntelNetwork:
    """情报网络"""
    
    def __init__(self):
        self.contacts: Dict[str, float] = {}  # 联系人ID -> 信任度
        self.reputation: float = 0.0
        self.network_size: int = 0
    
    def add_contact(self, contact_id: str, trust: float = 0.5):
        """添加联系人"""
        self.contacts[contact_id] = max(0.0, min(1.0, trust))
        self.network_size = len(self.contacts)
    
    def improve_trust(self, contact_id: str, amount: float):
        """提升信任度"""
        if contact_id in self.contacts:
            self.contacts[contact_id] = min(1.0, self.contacts[contact_id] + amount)
    
    def get_network_bonus(self) -> float:
        """获取情报网络加成"""
        size_bonus = min(0.3, self.network_size * 0.02)
        trust_bonus = sum(self.contacts.values()) / max(1, len(self.contacts)) * 0.2
        rep_bonus = min(0.3, self.reputation * 0.1)
        return size_bonus + trust_bonus + rep_bonus


class IntelAnalyzer:
    """情报分析器"""
    
    def __init__(self):
        self.analysis_skill = 0.5
        self.verified_intel: Set[str] = set()
    
    def analyze(self, intel: IntelItem) -> Dict:
        """分析情报"""
        # 基础分析
        analysis = {
            "credibility": self._assess_credibility(intel),
            "importance": self._assess_importance(intel),
            "connections": self._find_connections(intel),
            "actionable": self._is_actionable(intel)
        }
        
        # 技能检定
        if random.random() < self.analysis_skill:
            analysis["hidden_info"] = self._extract_hidden_info(intel)
        
        return analysis
    
    def _assess_credibility(self, intel: IntelItem) -> float:
        """评估可信度"""
        base_credibility = {
            IntelReliability.CONFIRMED: 1.0,
            IntelReliability.RELIABLE: 0.8,
            IntelReliability.UNCERTAIN: 0.5,
            IntelReliability.DUBIOUS: 0.3,
            IntelReliability.FALSE: 0.0
        }
        
        credibility = base_credibility.get(intel.reliability, 0.5)
        
        # 已验证的情报可信度提升
        if intel.verified or intel.id in self.verified_intel:
            credibility = min(1.0, credibility + 0.2)
        
        return credibility
    
    def _assess_importance(self, intel: IntelItem) -> int:
        """评估重要性 (1-5)"""
        importance = 2  # 默认重要性
        
        # 根据类型调整
        if intel.type in [IntelType.SECRET, IntelType.TREASURE]:
            importance += 1
        
        # 根据价值调整
        if intel.value > 1000:
            importance += 1
        if intel.value > 5000:
            importance += 1
        
        return min(5, max(1, importance))
    
    def _find_connections(self, intel: IntelItem) -> List[str]:
        """查找关联情报"""
        # 这里简化处理，实际应该从情报库中查找
        return intel.related_ids
    
    def _is_actionable(self, intel: IntelItem) -> bool:
        """判断是否可执行"""
        # 有具体位置的情报通常是可执行的
        if intel.location:
            return True
        
        # 已确认的情报通常是可执行的
        if intel.reliability == IntelReliability.CONFIRMED:
            return True
        
        return False
    
    def _extract_hidden_info(self, intel: IntelItem) -> Optional[str]:
        """提取隐藏信息"""
        hidden_messages = [
            "字里行间似乎暗示着更深的秘密...",
            "这份情报可能只是冰山一角。",
            "某些细节值得进一步调查。",
            "情报来源似乎有意隐瞒了什么。"
        ]
        
        if random.random() < 0.3:
            return random.choice(hidden_messages)
        return None
    
    def verify_intel(self, intel_id: str):
        """验证情报"""
        self.verified_intel.add(intel_id)
        # 验证情报可以提升分析技能
        self.analysis_skill = min(1.0, self.analysis_skill + 0.01)


class IntelligenceSystem:
    """情报系统主类"""
    
    def __init__(self):
        self.intel_database: Dict[str, IntelItem] = {}
        self.player_intel: Set[str] = set()
        self.network = IntelNetwork()
        self.analyzer = IntelAnalyzer()
        self.intel_counter = 0
    
    def create_intel(self, title: str, content: str, intel_type: IntelType,
                    source: IntelSource, reliability: IntelReliability,
                    **kwargs) -> IntelItem:
        """创建情报"""
        self.intel_counter += 1
        intel_id = f"INTEL_{self.intel_counter:04d}"
        
        intel = IntelItem(
            id=intel_id,
            title=title,
            content=content,
            type=intel_type,
            source=source,
            reliability=reliability,
            timestamp=datetime.now(),
            **kwargs
        )
        
        self.intel_database[intel_id] = intel
        return intel
    
    def acquire_intel(self, intel_id: str) -> Optional[IntelItem]:
        """获取情报"""
        if intel_id in self.intel_database:
            self.player_intel.add(intel_id)
            return self.intel_database[intel_id]
        return None
    
    def get_player_intel(self, intel_type: Optional[IntelType] = None) -> List[IntelItem]:
        """获取玩家拥有的情报"""
        player_intels = [
            self.intel_database[intel_id] 
            for intel_id in self.player_intel 
            if intel_id in self.intel_database
        ]
        
        if intel_type:
            player_intels = [
                intel for intel in player_intels 
                if intel.type == intel_type
            ]
        
        return sorted(player_intels, key=lambda x: x.timestamp, reverse=True)
    
    def analyze_intel(self, intel_id: str) -> Optional[Dict]:
        """分析情报"""
        if intel_id in self.player_intel and intel_id in self.intel_database:
            intel = self.intel_database[intel_id]
            return self.analyzer.analyze(intel)
        return None
    
    def trade_intel(self, give_intel_id: str, receive_intel_id: str) -> bool:
        """交易情报"""
        if give_intel_id in self.player_intel and receive_intel_id in self.intel_database:
            self.player_intel.remove(give_intel_id)
            self.player_intel.add(receive_intel_id)
            return True
        return False
    
    def generate_random_intel(self) -> IntelItem:
        """生成随机情报"""
        intel_templates = [
            {
                "title": "神秘洞府的传说",
                "content": "据说在东山深处有一个隐秘的洞府，内有前辈高人留下的传承。",
                "type": IntelType.LOCATION,
                "reliability": IntelReliability.UNCERTAIN
            },
            {
                "title": "失踪弟子的线索",
                "content": "有人在西市看到了失踪已久的青云宗弟子，似乎在寻找什么。",
                "type": IntelType.CHARACTER,
                "reliability": IntelReliability.RELIABLE
            },
            {
                "title": "灵石矿脉的消息",
                "content": "北境发现了新的灵石矿脉，各大势力都在暗中行动。",
                "type": IntelType.TREASURE,
                "reliability": IntelReliability.DUBIOUS
            }
        ]
        
        template = random.choice(intel_templates)
        return self.create_intel(
            title=template["title"],
            content=template["content"],
            intel_type=template["type"],
            source=random.choice(list(IntelSource)),
            reliability=template["reliability"],
            value=random.randint(100, 1000)
        )


# 全局实例
intelligence_system = IntelligenceSystem()


def integrate_intelligence_system(game_core):
    """集成情报系统到游戏核心"""
    # 添加情报相关命令
    def intel_command(args):
        if not args:
            # 显示情报列表
            intels = intelligence_system.get_player_intel()
            if not intels:
                return "你还没有收集到任何情报。"
            
            result = "【情报列表】\n"
            for intel in intels[:10]:  # 只显示最新的10条
                result += f"\n[{intel.id}] {intel.title}"
                result += f"\n类型: {intel.type.value} | 可靠度: {intel.reliability.value}"
            return result
        
        # 查看具体情报
        intel_id = args[0].upper()
        if intel_id.startswith("INTEL_"):
            intel = intelligence_system.intel_database.get(intel_id)
            if intel and intel_id in intelligence_system.player_intel:
                analysis = intelligence_system.analyze_intel(intel_id)
                result = f"【{intel.title}】\n"
                result += f"内容: {intel.content}\n"
                result += f"来源: {intel.source.value}\n"
                result += f"可信度: {analysis['credibility']:.0%}\n"
                result += f"重要性: {'★' * analysis['importance']}"
                
                if analysis.get('hidden_info'):
                    result += f"\n\n{analysis['hidden_info']}"
                
                return result
        
        return "未找到该情报。"
    
    # 注册命令
    if hasattr(game_core, 'register_command'):
        game_core.register_command('intel', intel_command, "查看情报")
        game_core.register_command('情报', intel_command, "查看情报")
