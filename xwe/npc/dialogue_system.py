# npc/dialogue_system.py
"""
对话系统

实现NPC对话树和对话管理。
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class DialogueNodeType(Enum):
    """对话节点类型"""
    TEXT = "text"          # 纯文本
    CHOICE = "choice"      # 选择分支
    ACTION = "action"      # 触发动作
    CONDITION = "condition" # 条件分支
    END = "end"           # 结束对话


@dataclass
class DialogueChoice:
    """对话选项"""
    id: str
    text: str
    next_node: str
    requirements: Dict[str, Any] = field(default_factory=dict)
    effects: Dict[str, Any] = field(default_factory=dict)
    
    def is_available(self, context: Dict[str, Any]) -> bool:
        """检查选项是否可用"""
        # 检查等级要求
        if 'min_level' in self.requirements:
            player_level = context.get('player_level', 0)
            if player_level < self.requirements['min_level']:
                return False
        
        # 检查物品要求
        if 'required_items' in self.requirements:
            # TODO: 实现物品检查
            pass
        
        # 检查关系要求
        if 'min_relationship' in self.requirements:
            relationship = context.get('npc_relationship', 0)
            if relationship < self.requirements['min_relationship']:
                return False
        
        # 检查标记要求
        if 'required_flags' in self.requirements:
            flags = context.get('flags', {})
            for flag in self.requirements['required_flags']:
                if not flags.get(flag, False):
                    return False
        
        return True


@dataclass
class DialogueNode:
    """对话节点"""
    id: str
    type: DialogueNodeType
    speaker: str  # "player" 或 NPC名称
    text: str
    
    # 分支选项（用于CHOICE类型）
    choices: List[DialogueChoice] = field(default_factory=list)
    
    # 下一个节点（用于TEXT类型）
    next_node: Optional[str] = None
    
    # 条件（用于CONDITION类型）
    condition: Optional[str] = None
    true_node: Optional[str] = None
    false_node: Optional[str] = None
    
    # 动作（用于ACTION类型）
    action: Optional[str] = None
    action_params: Dict[str, Any] = field(default_factory=dict)
    
    # 效果
    effects: Dict[str, Any] = field(default_factory=dict)
    
    def get_next_node(self, context: Dict[str, Any], choice_id: Optional[str] = None) -> Optional[str]:
        """获取下一个节点ID"""
        if self.type == DialogueNodeType.TEXT:
            return self.next_node
            
        elif self.type == DialogueNodeType.CHOICE:
            if choice_id:
                for choice in self.choices:
                    if choice.id == choice_id and choice.is_available(context):
                        return choice.next_node
            return None
            
        elif self.type == DialogueNodeType.CONDITION:
            # 评估条件
            if self.condition and self._evaluate_condition(self.condition, context):
                return self.true_node
            else:
                return self.false_node
                
        elif self.type == DialogueNodeType.ACTION:
            # 执行动作后继续
            return self.next_node
            
        else:  # END
            return None
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """评估条件"""
        # 简单的条件评估
        # 格式: "player_level >= 5" 或 "has_item:spirit_stone"
        
        if ">=" in condition:
            parts = condition.split(">=")
            if len(parts) == 2:
                key = parts[0].strip()
                value = int(parts[1].strip())
                return context.get(key, 0) >= value
                
        elif ">" in condition:
            parts = condition.split(">")
            if len(parts) == 2:
                key = parts[0].strip()
                value = int(parts[1].strip())
                return context.get(key, 0) > value
                
        elif "has_item:" in condition:
            item_id = condition.replace("has_item:", "").strip()
            items = context.get('player_items', [])
            return item_id in items
            
        elif "has_flag:" in condition:
            flag = condition.replace("has_flag:", "").strip()
            flags = context.get('flags', {})
            return flags.get(flag, False)
            
        return False


class DialogueTree:
    """对话树"""
    
    def __init__(self, npc_id: str, dialogue_id: str):
        """
        初始化对话树
        
        Args:
            npc_id: NPC ID
            dialogue_id: 对话ID
        """
        self.npc_id = npc_id
        self.dialogue_id = dialogue_id
        self.nodes: Dict[str, DialogueNode] = {}
        self.start_node: Optional[str] = None
        self.current_node: Optional[str] = None
        
        # 对话历史
        self.history: List[str] = []
        
        logger.debug(f"创建对话树: {npc_id}/{dialogue_id}")
    
    def add_node(self, node: DialogueNode):
        """添加节点"""
        self.nodes[node.id] = node
        if not self.start_node:
            self.start_node = node.id
    
    def start(self) -> Optional[DialogueNode]:
        """开始对话"""
        if self.start_node:
            self.current_node = self.start_node
            self.history = [self.start_node]
            return self.nodes.get(self.start_node)
        return None
    
    def advance(self, context: Dict[str, Any], choice_id: Optional[str] = None) -> Optional[DialogueNode]:
        """
        推进对话
        
        Args:
            context: 对话上下文
            choice_id: 选择的选项ID
            
        Returns:
            下一个对话节点
        """
        if not self.current_node:
            return None
        
        current = self.nodes.get(self.current_node)
        if not current:
            return None
        
        # 获取下一个节点
        next_node_id = current.get_next_node(context, choice_id)
        
        if next_node_id and next_node_id in self.nodes:
            self.current_node = next_node_id
            self.history.append(next_node_id)
            
            next_node = self.nodes[next_node_id]
            
            # 应用节点效果
            self._apply_effects(next_node.effects, context)
            
            # 如果选择了某个选项，也应用选项效果
            if choice_id and current.type == DialogueNodeType.CHOICE:
                for choice in current.choices:
                    if choice.id == choice_id:
                        self._apply_effects(choice.effects, context)
                        break
            
            return next_node
        
        # 对话结束
        self.current_node = None
        return None
    
    def _apply_effects(self, effects: Dict[str, Any], context: Dict[str, Any]):
        """应用效果"""
        for effect_type, value in effects.items():
            if effect_type == 'relationship_change':
                # 改变关系值
                current = context.get('npc_relationship', 0)
                context['npc_relationship'] = current + value
                
            elif effect_type == 'add_flag':
                # 添加标记
                flags = context.setdefault('flags', {})
                flags[value] = True
                
            elif effect_type == 'give_item':
                # 给予物品（需要物品系统支持）
                context.setdefault('rewards', []).append({
                    'type': 'item',
                    'id': value
                })
                
            elif effect_type == 'give_exp':
                # 给予经验
                context.setdefault('rewards', []).append({
                    'type': 'exp',
                    'amount': value
                })
    
    def get_available_choices(self, context: Dict[str, Any]) -> List[DialogueChoice]:
        """获取当前可用的选项"""
        if not self.current_node:
            return []
        
        current = self.nodes.get(self.current_node)
        if not current or current.type != DialogueNodeType.CHOICE:
            return []
        
        return [choice for choice in current.choices if choice.is_available(context)]
    
    def is_complete(self) -> bool:
        """对话是否结束"""
        return self.current_node is None
    
    @classmethod
    def from_dict(cls, npc_id: str, dialogue_id: str, data: Dict[str, Any]) -> 'DialogueTree':
        """从字典创建对话树"""
        tree = cls(npc_id, dialogue_id)
        
        # 创建所有节点
        for node_data in data.get('nodes', []):
            node_type = DialogueNodeType(node_data.get('type', 'text'))
            
            node = DialogueNode(
                id=node_data['id'],
                type=node_type,
                speaker=node_data.get('speaker', npc_id),
                text=node_data.get('text', ''),
                next_node=node_data.get('next_node'),
                condition=node_data.get('condition'),
                true_node=node_data.get('true_node'),
                false_node=node_data.get('false_node'),
                action=node_data.get('action'),
                action_params=node_data.get('action_params', {}),
                effects=node_data.get('effects', {})
            )
            
            # 添加选项
            if node_type == DialogueNodeType.CHOICE:
                for choice_data in node_data.get('choices', []):
                    choice = DialogueChoice(
                        id=choice_data['id'],
                        text=choice_data['text'],
                        next_node=choice_data['next_node'],
                        requirements=choice_data.get('requirements', {}),
                        effects=choice_data.get('effects', {})
                    )
                    node.choices.append(choice)
            
            tree.add_node(node)
        
        # 设置起始节点
        if 'start_node' in data:
            tree.start_node = data['start_node']
        
        return tree


class DialogueSystem:
    """
    对话系统
    
    管理所有NPC的对话。
    """
    
    def __init__(self):
        """初始化对话系统"""
        self.dialogue_trees: Dict[str, Dict[str, DialogueTree]] = {}  # npc_id -> dialogue_id -> tree
        self.active_dialogues: Dict[str, DialogueTree] = {}  # player_id -> active tree
        self.dialogue_templates: Dict[str, Dict[str, Any]] = {}  # 对话模板
        
        # 动作处理器
        self.action_handlers: Dict[str, Callable] = {}
        
        # 初始化默认对话
        self._init_default_dialogues()
        
        # 加载JSON中的对话数据
        self._load_json_dialogues()
        
        logger.info("对话系统初始化")
    
    def _init_default_dialogues(self):
        """初始化默认对话"""
        # 通用商人对话
        merchant_dialogue = {
            'nodes': [
                {
                    'id': 'start',
                    'type': 'text',
                    'speaker': 'npc',
                    'text': '欢迎光临！需要些什么吗？',
                    'next_node': 'menu'
                },
                {
                    'id': 'menu',
                    'type': 'choice',
                    'speaker': 'player',
                    'text': '',
                    'choices': [
                        {
                            'id': 'buy',
                            'text': '我想买点东西',
                            'next_node': 'show_goods'
                        },
                        {
                            'id': 'sell',
                            'text': '我有些东西要卖',
                            'next_node': 'check_items'
                        },
                        {
                            'id': 'chat',
                            'text': '聊聊最近的消息',
                            'next_node': 'gossip',
                            'requirements': {'min_relationship': 10}
                        },
                        {
                            'id': 'leave',
                            'text': '没什么，告辞',
                            'next_node': 'goodbye'
                        }
                    ]
                },
                {
                    'id': 'show_goods',
                    'type': 'action',
                    'speaker': 'npc',
                    'text': '这是我的商品，请过目。',
                    'action': 'open_shop',
                    'next_node': 'after_trade'
                },
                {
                    'id': 'check_items',
                    'type': 'text',
                    'speaker': 'npc',
                    'text': '让我看看你有什么好东西。',
                    'next_node': 'after_trade'
                },
                {
                    'id': 'gossip',
                    'type': 'text',
                    'speaker': 'npc',
                    'text': '最近听说北方出现了一些异动，有修士在那里失踪了。',
                    'effects': {'add_flag': 'heard_north_rumor'},
                    'next_node': 'menu'
                },
                {
                    'id': 'after_trade',
                    'type': 'text',
                    'speaker': 'npc',
                    'text': '还需要什么吗？',
                    'next_node': 'menu'
                },
                {
                    'id': 'goodbye',
                    'type': 'text',
                    'speaker': 'npc',
                    'text': '欢迎下次光临！',
                    'effects': {'relationship_change': 1}
                }
            ],
            'start_node': 'start'
        }
        
        self.dialogue_templates['merchant_default'] = merchant_dialogue
        
        # 守卫对话
        guard_dialogue = {
            'nodes': [
                {
                    'id': 'start',
                    'type': 'condition',
                    'condition': 'player_level >= 5',
                    'true_node': 'greet_strong',
                    'false_node': 'greet_weak'
                },
                {
                    'id': 'greet_strong',
                    'type': 'text',
                    'speaker': 'npc',
                    'text': '道友好，城中最近太平，请自便。',
                    'next_node': 'ask_strong'
                },
                {
                    'id': 'greet_weak',
                    'type': 'text',
                    'speaker': 'npc',
                    'text': '站住！你是什么人？',
                    'next_node': 'ask_weak'
                },
                {
                    'id': 'ask_strong',
                    'type': 'choice',
                    'speaker': 'player',
                    'text': '',
                    'choices': [
                        {
                            'id': 'ask_news',
                            'text': '最近有什么消息吗？',
                            'next_node': 'tell_news'
                        },
                        {
                            'id': 'leave',
                            'text': '没事，告辞',
                            'next_node': 'goodbye'
                        }
                    ]
                },
                {
                    'id': 'ask_weak',
                    'type': 'choice',
                    'speaker': 'player',
                    'text': '',
                    'choices': [
                        {
                            'id': 'explain',
                            'text': '我是来历练的散修',
                            'next_node': 'warn'
                        },
                        {
                            'id': 'leave',
                            'text': '打扰了，我这就走',
                            'next_node': 'goodbye'
                        }
                    ]
                },
                {
                    'id': 'tell_news',
                    'type': 'text',
                    'speaker': 'npc',
                    'text': '城主府最近在招募护卫，道友若有兴趣可以去看看。',
                    'effects': {'add_flag': 'know_guard_recruit'}
                },
                {
                    'id': 'warn',
                    'type': 'text',
                    'speaker': 'npc',
                    'text': '城中禁止斗法，小心些。',
                    'next_node': 'goodbye'
                },
                {
                    'id': 'goodbye',
                    'type': 'text',
                    'speaker': 'npc',
                    'text': '去吧。'
                }
            ],
            'start_node': 'start'
        }
        
        self.dialogue_templates['guard_default'] = guard_dialogue
    
    def load_dialogue(self, npc_id: str, dialogue_id: str, dialogue_data: Dict[str, Any]):
        """加载对话"""
        tree = DialogueTree.from_dict(npc_id, dialogue_id, dialogue_data)
        
        if npc_id not in self.dialogue_trees:
            self.dialogue_trees[npc_id] = {}
        
        self.dialogue_trees[npc_id][dialogue_id] = tree
        logger.debug(f"加载对话: {npc_id}/{dialogue_id}")
    
    def start_dialogue(self, player_id: str, npc_id: str, 
                      dialogue_id: Optional[str] = None) -> Optional[DialogueNode]:
        """
        开始对话
        
        Args:
            player_id: 玩家ID
            npc_id: NPC ID
            dialogue_id: 指定的对话ID，如果为None则使用默认对话
            
        Returns:
            第一个对话节点
        """
        # 如果没有指定对话ID，使用默认对话
        if not dialogue_id:
            dialogue_id = 'default'
        
        # 查找对话树
        tree = None
        
        # 先查找NPC特定的对话
        if npc_id in self.dialogue_trees and dialogue_id in self.dialogue_trees[npc_id]:
            tree = self.dialogue_trees[npc_id][dialogue_id]
        
        # 如果没找到，尝试使用模板创建
        elif dialogue_id in self.dialogue_templates:
            tree = DialogueTree.from_dict(npc_id, dialogue_id, self.dialogue_templates[dialogue_id])
            self.load_dialogue(npc_id, dialogue_id, self.dialogue_templates[dialogue_id])
        
        if not tree:
            logger.warning(f"找不到对话: {npc_id}/{dialogue_id}")
            return None
        
        # 开始对话
        self.active_dialogues[player_id] = tree
        return tree.start()
    
    def advance_dialogue(self, player_id: str, context: Dict[str, Any], 
                        choice_id: Optional[str] = None) -> Optional[DialogueNode]:
        """
        推进对话
        
        Args:
            player_id: 玩家ID
            context: 对话上下文
            choice_id: 选择的选项ID
            
        Returns:
            下一个对话节点
        """
        tree = self.active_dialogues.get(player_id)
        if not tree:
            return None
        
        next_node = tree.advance(context, choice_id)
        
        # 处理动作节点
        if next_node and next_node.type == DialogueNodeType.ACTION:
            if next_node.action and next_node.action in self.action_handlers:
                handler = self.action_handlers[next_node.action]
                handler(player_id, next_node.action_params, context)
        
        # 如果对话结束，清理
        if tree.is_complete():
            del self.active_dialogues[player_id]
        
        return next_node
    
    def get_active_dialogue(self, player_id: str) -> Optional[DialogueTree]:
        """获取当前活跃的对话"""
        return self.active_dialogues.get(player_id)
    
    def end_dialogue(self, player_id: str):
        """结束对话"""
        if player_id in self.active_dialogues:
            del self.active_dialogues[player_id]
    
    def register_action_handler(self, action: str, handler: Callable):
        """注册动作处理器"""
        self.action_handlers[action] = handler
    
    def create_dialogue_from_template(self, npc_id: str, template_id: str) -> bool:
        """从模板创建对话"""
        if template_id not in self.dialogue_templates:
            return False
        
        template = self.dialogue_templates[template_id]
        self.load_dialogue(npc_id, 'default', template)
        return True
    
    def _load_json_dialogues(self):
        """加载JSON对话数据"""
        import os
        json_path = os.path.join(os.path.dirname(__file__), '../../data/npc/dialogues.json')
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for dialogue_id, dialogue_data in data.get('dialogues', {}).items():
                # 转换为对话系统期望的格式
                nodes = []
                node_dict = dialogue_data.get('nodes', {})
                
                for node_id, node_data in node_dict.items():
                    node_entry = {
                        'id': node_id,
                        'type': node_data.get('type', 'text'),
                        'speaker': node_data.get('speaker', 'npc'),
                        'text': node_data.get('text', '')
                    }
                    
                    if node_data.get('type') == 'choice' and 'choices' in node_data:
                        node_entry['choices'] = [
                            {
                                'id': choice.get('id'),
                                'text': choice.get('text'),
                                'next_node': choice.get('next'),
                                'requirements': choice.get('requirements', {}),
                                'effects': choice.get('effects', {})
                            }
                            for choice in node_data['choices']
                        ]
                    else:
                        node_entry['next_node'] = node_data.get('next')
                    
                    nodes.append(node_entry)
                
                formatted_dialogue = {
                    'nodes': nodes,
                    'start_node': dialogue_data.get('start_node', 'start')
                }
                
                # 加载到test_npc的对话树中
                self.load_dialogue('test_npc', dialogue_id, formatted_dialogue)
                
        except Exception as e:
            logger.warning(f"加载JSON对话失败: {e}")


# 预定义的对话数据
DEFAULT_DIALOGUES = {
    "wang_boss": {
        "default": {
            "nodes": [
                {
                    "id": "start",
                    "type": "text",
                    "speaker": "王老板",
                    "text": "哎呀，这位道友，看你器宇不凡，想必是初入修行之道吧？",
                    "next_node": "introduce"
                },
                {
                    "id": "introduce",
                    "type": "text",
                    "speaker": "王老板",
                    "text": "老夫王某，在这天南坊市经营些小生意，专做修士们的买卖。",
                    "next_node": "menu"
                },
                {
                    "id": "menu",
                    "type": "choice",
                    "speaker": "player",
                    "text": "",
                    "choices": [
                        {
                            "id": "buy",
                            "text": "我需要一些修炼物资",
                            "next_node": "show_goods"
                        },
                        {
                            "id": "ask_cultivation",
                            "text": "前辈可否指点一下修炼之道？",
                            "next_node": "cultivation_advice"
                        },
                        {
                            "id": "ask_news",
                            "text": "最近坊市有什么新鲜事吗？",
                            "next_node": "tell_news",
                            "requirements": {"min_relationship": 5}
                        },
                        {
                            "id": "leave",
                            "text": "多谢前辈，我先走了",
                            "next_node": "goodbye"
                        }
                    ]
                },
                {
                    "id": "show_goods",
                    "type": "text",
                    "speaker": "王老板",
                    "text": "哈哈，来对地方了！我这里有上好的聚气丹，还有一些低阶法器。",
                    "next_node": "trade_action"
                },
                {
                    "id": "trade_action",
                    "type": "action",
                    "speaker": "system",
                    "text": "[交易界面开启]",
                    "action": "open_shop",
                    "action_params": {"shop_id": "wang_basic_shop"},
                    "next_node": "after_trade"
                },
                {
                    "id": "after_trade",
                    "type": "text",
                    "speaker": "王老板",
                    "text": "道友慢走，欢迎下次再来！",
                    "effects": {"relationship_change": 2}
                },
                {
                    "id": "cultivation_advice",
                    "type": "text",
                    "speaker": "王老板",
                    "text": "修炼一途，最重要的是稳扎稳打。初期不要贪功冒进，打好根基最为重要。",
                    "next_node": "cultivation_advice_2"
                },
                {
                    "id": "cultivation_advice_2",
                    "type": "text",
                    "speaker": "王老板",
                    "text": "城外的黄枫谷灵气还算充裕，适合新人修炼，不过要小心妖兽。",
                    "effects": {"add_flag": "know_yellow_maple_valley"},
                    "next_node": "menu"
                },
                {
                    "id": "tell_news",
                    "type": "text",
                    "speaker": "王老板",
                    "text": "说起来，最近坊市确实不太平。有传言说北方的妖兽谷出现了异动...",
                    "next_node": "tell_news_2"
                },
                {
                    "id": "tell_news_2",
                    "type": "text",
                    "speaker": "王老板",
                    "text": "还有啊，青云宗最近在招收外门弟子，道友若是有兴趣，可以去试试。",
                    "effects": {
                        "add_flag": "know_qingyun_recruitment",
                        "relationship_change": 3
                    },
                    "next_node": "menu"
                },
                {
                    "id": "goodbye",
                    "type": "text",
                    "speaker": "王老板",
                    "text": "好好好，年轻人要多历练。有空常来坐坐！",
                    "effects": {"relationship_change": 1}
                }
            ],
            "start_node": "start"
        }
    }
}
