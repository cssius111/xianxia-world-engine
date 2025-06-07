# xwe/features/ai_world_events.py

import json
import asyncio
from typing import Dict, List, Optional
from collections import defaultdict
import random

class AIWorldEventGenerator:
    """AI驱动的世界事件生成器"""
    
    def __init__(self, llm_client, world_state):
        self.llm = llm_client
        self.world_state = world_state
        self.event_history = []
        self.pending_events = []
        
    async def generate_world_event(self, 
                                  trigger: str,
                                  severity: str = "minor") -> Dict:
        """生成世界事件"""
        
        # 分析世界状态
        world_context = self._analyze_world_state()
        
        prompt = f"""
基于当前修仙世界的状态，生成一个{severity}级别的世界事件。

触发原因：{trigger}

世界状态：
- 主要门派关系：{world_context.get('faction_relations', '和平')}
- 天地异象：{world_context.get('phenomena', '无')}
- 重要资源分布：{world_context.get('resources', '正常')}
- 近期大事：{self._format_recent_events()}

请生成一个事件，包含：
1. 事件名称（4-8字）
2. 事件描述（50-100字）
3. 影响范围（局部/区域/全局）
4. 持续时间（临时/短期/长期）
5. 玩家选择（2-3个选项）
6. 潜在后果

输出JSON格式。
"""
        
        response = await self.llm.generate(prompt, temperature=0.9)
        
        try:
            event_data = json.loads(response)
        except:
            # 降级处理
            event_data = self._generate_fallback_event(trigger, severity)
            
        # 验证和平衡
        balanced_event = self._balance_event(event_data, severity)
        
        # 注册事件
        self._register_world_event(balanced_event)
        
        return balanced_event
        
    async def evolve_event_chain(self, 
                                event_id: str,
                                player_choice: str) -> List[Dict]:
        """演化事件链"""
        
        original_event = self._get_event(event_id)
        if not original_event:
            return []
        
        prompt = f"""
基于玩家的选择，推演事件的后续发展。

原始事件：{json.dumps(original_event, ensure_ascii=False)}
玩家选择：{player_choice}
世界反应：{self._get_world_reactions(event_id)}

请生成1-3个后续事件，体现：
1. 玩家选择的直接后果
2. 其他势力的反应
3. 可能的连锁反应

保持逻辑连贯性和世界观一致性。
输出JSON数组格式。
"""
        
        response = await self.llm.generate(prompt, temperature=0.85)
        
        # 解析后续事件
        follow_up_events = self._parse_event_chain(response)
        
        # 调度事件
        for event in follow_up_events:
            self._schedule_event(event)
            
        return follow_up_events
        
    def _analyze_world_state(self) -> Dict:
        """分析世界状态"""
        return {
            'faction_relations': self._analyze_faction_relations(),
            'phenomena': self._get_current_phenomena(),
            'resources': self._analyze_resource_distribution(),
            'player_influence': self._calculate_player_influence()
        }
        
    def _analyze_faction_relations(self) -> str:
        """分析门派关系"""
        # 简化的关系分析
        relations = self.world_state.get('faction_relations', {})
        
        hostile_count = sum(1 for r in relations.values() if r < -50)
        friendly_count = sum(1 for r in relations.values() if r > 50)
        
        if hostile_count > 3:
            return "多方敌对，战云密布"
        elif friendly_count > 5:
            return "普遍友好，和平繁荣"
        else:
            return "关系复杂，暗流涌动"
            
    def _get_current_phenomena(self) -> str:
        """获取当前天地异象"""
        phenomena = self.world_state.get('phenomena', [])
        if not phenomena:
            return "天地平静"
            
        return "、".join(phenomena[:3])  # 最多显示3个
        
    def _analyze_resource_distribution(self) -> str:
        """分析资源分布"""
        resources = self.world_state.get('resources', {})
        
        scarcity_count = sum(1 for r in resources.values() if r < 30)
        abundance_count = sum(1 for r in resources.values() if r > 70)
        
        if scarcity_count > abundance_count:
            return "资源匮乏，争夺激烈"
        elif abundance_count > scarcity_count:
            return "资源丰富，发展良好"
        else:
            return "资源分布不均"
            
    def _calculate_player_influence(self) -> float:
        """计算玩家影响力"""
        # 基于玩家的境界、声望、势力等
        player_data = self.world_state.get('player', {})
        
        influence = 0.0
        
        # 境界影响
        realm_level = player_data.get('realm_level', 1)
        influence += realm_level * 10
        
        # 声望影响
        reputation = player_data.get('reputation', 0)
        influence += reputation / 100
        
        # 势力影响
        if player_data.get('faction_leader'):
            influence += 50
            
        return min(100, influence)
        
    def _format_recent_events(self) -> str:
        """格式化近期事件"""
        recent = self.event_history[-5:]  # 最近5个事件
        if not recent:
            return "无重大事件"
            
        return "; ".join([e.get('name', '') for e in recent])
        
    def _generate_fallback_event(self, trigger: str, severity: str) -> Dict:
        """生成降级事件"""
        templates = {
            'minor': [
                {
                    'name': '灵兽迁徙',
                    'description': '大批低阶灵兽开始向南迁徙，似乎在躲避什么。',
                    'scope': 'local',
                    'duration': 'temporary'
                },
                {
                    'name': '灵泉枯竭',
                    'description': '青云山的一处灵泉突然枯竭，引起附近修士关注。',
                    'scope': 'local', 
                    'duration': 'short'
                }
            ],
            'major': [
                {
                    'name': '秘境现世',
                    'description': '一处上古秘境突然出现，各方势力蠢蠢欲动。',
                    'scope': 'regional',
                    'duration': 'short'
                },
                {
                    'name': '天劫异变',
                    'description': '近期渡劫的修士纷纷失败，天劫威力似乎增强了。',
                    'scope': 'global',
                    'duration': 'long'
                }
            ],
            'critical': [
                {
                    'name': '魔族入侵',
                    'description': '北方边境出现空间裂缝，大批魔族涌入人间。',
                    'scope': 'global',
                    'duration': 'long'
                }
            ]
        }
        
        # 选择合适的模板
        severity_templates = templates.get(severity, templates['minor'])
        template = random.choice(severity_templates)
        
        # 添加选项
        template['choices'] = [
            {'id': 1, 'text': '前往调查', 'consequence': 'involvement'},
            {'id': 2, 'text': '静观其变', 'consequence': 'neutral'},
            {'id': 3, 'text': '通知门派', 'consequence': 'reputation'}
        ]
        
        template['event_id'] = f"event_{len(self.event_history) + 1}"
        template['trigger'] = trigger
        template['severity'] = severity
        
        return template
        
    def _balance_event(self, event_data: Dict, severity: str) -> Dict:
        """平衡事件数据"""
        # 确保必要字段存在
        required_fields = ['name', 'description', 'scope', 'duration', 'choices']
        for field in required_fields:
            if field not in event_data:
                if field == 'choices':
                    event_data[field] = [
                        {'id': 1, 'text': '参与', 'consequence': 'active'},
                        {'id': 2, 'text': '观望', 'consequence': 'passive'}
                    ]
                else:
                    event_data[field] = 'unknown'
                    
        # 添加事件ID
        if 'event_id' not in event_data:
            event_data['event_id'] = f"event_{len(self.event_history) + 1}"
            
        # 验证严重程度
        event_data['severity'] = severity
        
        # 确保选项合理
        if len(event_data['choices']) > 5:
            event_data['choices'] = event_data['choices'][:5]
            
        return event_data
        
    def _register_world_event(self, event: Dict):
        """注册世界事件"""
        self.event_history.append(event)
        
        # 更新世界状态
        self._update_world_state(event)
        
        # 触发相关系统
        self._trigger_related_systems(event)
        
    def _update_world_state(self, event: Dict):
        """根据事件更新世界状态"""
        # 根据事件类型和范围更新不同的世界参数
        if event['scope'] == 'global':
            # 全局事件影响所有区域
            self.world_state['global_tension'] = self.world_state.get('global_tension', 0) + 10
            
        elif event['scope'] == 'regional':
            # 区域事件影响特定区域
            affected_region = event.get('region', 'default')
            if 'regional_states' not in self.world_state:
                self.world_state['regional_states'] = {}
            self.world_state['regional_states'][affected_region] = event
            
    def _trigger_related_systems(self, event: Dict):
        """触发相关系统"""
        # 这里可以触发其他系统响应世界事件
        # 例如：NPC反应、市场波动、任务生成等
        pass
        
    def _get_event(self, event_id: str) -> Optional[Dict]:
        """获取事件信息"""
        for event in self.event_history:
            if event.get('event_id') == event_id:
                return event
        return None
        
    def _get_world_reactions(self, event_id: str) -> str:
        """获取世界对事件的反应"""
        # 简化的反应生成
        reactions = [
            "各大门派密切关注事态发展",
            "散修联盟开始聚集",
            "坊市物价出现波动",
            "部分修士开始迁移"
        ]
        
        return "; ".join(random.sample(reactions, 2))
        
    def _parse_event_chain(self, response: str) -> List[Dict]:
        """解析事件链响应"""
        try:
            events = json.loads(response)
            if isinstance(events, list):
                return events
            elif isinstance(events, dict):
                return [events]
        except:
            # 降级处理
            return [self._generate_simple_follow_up()]
            
        return []
        
    def _generate_simple_follow_up(self) -> Dict:
        """生成简单的后续事件"""
        return {
            'name': '余波未平',
            'description': '之前事件的影响还在持续发酵。',
            'scope': 'local',
            'duration': 'temporary',
            'severity': 'minor'
        }
        
    def _schedule_event(self, event: Dict):
        """调度事件发生"""
        # 根据事件的时机安排其发生
        delay = event.get('delay', 0)
        
        if delay == 0:
            # 立即发生
            self._register_world_event(event)
        else:
            # 延迟发生
            self.pending_events.append({
                'event': event,
                'scheduled_time': asyncio.get_event_loop().time() + delay
            })
            
    def process_pending_events(self):
        """处理待发生的事件"""
        current_time = asyncio.get_event_loop().time()
        
        triggered = []
        for pending in self.pending_events:
            if pending['scheduled_time'] <= current_time:
                self._register_world_event(pending['event'])
                triggered.append(pending)
                
        # 移除已触发的事件
        for t in triggered:
            self.pending_events.remove(t)
