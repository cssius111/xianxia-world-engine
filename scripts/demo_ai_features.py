# demo_ai_features.py

"""
AI功能演示脚本
"""

import asyncio
import os
from typing import Dict, Any
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from xwe.core.nlp.llm_client import LLMClient
from xwe.core.nlp.advanced import AdvancedPromptEngine, ResponseType, GameContext
from xwe.features.ai_dialogue import AIDialogueManager
from xwe.features.narrative_generator import DynamicNarrativeGenerator
from xwe.features.ai_world_events import AIWorldEventGenerator


async def demo_ai_dialogue():
    """演示AI对话系统"""
    print("\n=== AI对话系统演示 ===")
    
    # 检查API密钥
    if not os.getenv('DEEPSEEK_API_KEY'):
        print("警告：未设置DEEPSEEK_API_KEY，将使用模拟响应")
        return demo_dialogue_mock()
        
    # 创建组件
    llm_client = LLMClient()
    prompt_engine = AdvancedPromptEngine()
    dialogue_manager = AIDialogueManager(llm_client, prompt_engine)
    
    # 模拟游戏上下文
    context = {
        'player': {
            'name': '道友',
            'realm': '筑基期',
            'health': 100,
            'max_health': 100,
            'level': 10
        },
        'location': {
            'id': 'tiannan_market',
            'name': '天南坊市',
            'description': '繁华的修仙者交易市场'
        },
        'npc': {
            'id': 'merchant_wang',
            'name': '王老板',
            'personality': '精明商人，友善但爱讨价还价',
            'occupation': '灵药商人'
        },
        'recent_events': [],
        'world': {}
    }
    
    # 测试对话
    test_conversations = [
        "你好，有什么好东西吗？",
        "这个回灵丹怎么卖？",
        "能便宜点吗？我是老顾客了。",
        "好吧，我买10颗。"
    ]
    
    print(f"\n与{context['npc']['name']}的对话：")
    print("-" * 50)
    
    for player_input in test_conversations:
        print(f"\n玩家: {player_input}")
        
        try:
            # 生成AI对话
            result = await dialogue_manager.generate_npc_dialogue(
                context['npc']['id'],
                player_input,
                context
            )
            
            # 显示结果
            print(f"{context['npc']['name']}: {result['text']}")
            
            if result.get('choices'):
                print("\n选项:")
                for choice in result['choices']:
                    print(f"  {choice['id']}. {choice['text']}")
                    
            if result.get('effects'):
                print("\n效果:")
                for effect in result['effects']:
                    print(f"  - {effect.get('description', effect)}")
                    
        except Exception as e:
            print(f"错误: {e}")
            
        await asyncio.sleep(1)  # 避免API限流
        
    # 显示关系变化
    relationship = dialogue_manager.get_relationship_level(context['npc']['id'])
    print(f"\n与{context['npc']['name']}的关系: {relationship} ({dialogue_manager._get_relationship_status(context['npc']['id'])})")


def demo_dialogue_mock():
    """模拟对话演示（无API）"""
    print("\n模拟对话响应：")
    print("-" * 50)
    
    responses = [
        {
            'text': '道友好！老夫这里有上好的回灵丹、培元丹，还有一些稀有的灵草种子。',
            'emotion': 'friendly',
            'choices': [
                {'id': 1, 'text': '我想看看回灵丹'},
                {'id': 2, 'text': '灵草种子是什么品种？'}
            ]
        },
        {
            'text': '这回灵丹可是老夫亲手炼制，药效比市面上的要好三成！一颗50灵石。',
            'emotion': 'proud'
        },
        {
            'text': '哈哈，道友真会说话。看在你是熟客的份上，45灵石一颗，不能再少了！',
            'emotion': 'happy',
            'effects': [{'type': 'relationship', 'value': 5}]
        },
        {
            'text': '好嘞！10颗回灵丹，一共450灵石。道友慢走，下次再来！',
            'emotion': 'satisfied'
        }
    ]
    
    conversations = [
        "你好，有什么好东西吗？",
        "这个回灵丹怎么卖？",
        "能便宜点吗？我是老顾客了。",
        "好吧，我买10颗。"
    ]
    
    for i, player_input in enumerate(conversations):
        print(f"\n玩家: {player_input}")
        
        if i < len(responses):
            result = responses[i]
            print(f"王老板: {result['text']}")
            
            if result.get('choices'):
                print("\n选项:")
                for choice in result['choices']:
                    print(f"  {choice['id']}. {choice['text']}")
                    
            if result.get('effects'):
                print("\n效果:")
                for effect in result['effects']:
                    if effect['type'] == 'relationship':
                        print(f"  - 好感度+{effect['value']}")


async def demo_narrative_generation():
    """演示叙事生成"""
    print("\n=== 动态叙事生成演示 ===")
    
    if not os.getenv('DEEPSEEK_API_KEY'):
        print("警告：未设置DEEPSEEK_API_KEY，将使用预设叙事")
        return demo_narrative_mock()
        
    # 创建叙事生成器
    llm_client = LLMClient()
    narrator = DynamicNarrativeGenerator(llm_client)
    
    # 战斗叙事
    print("\n1. 战斗叙事：")
    print("-" * 50)
    
    combat_events = [
        {'type': 'start', 'attacker': '你', 'defender': '火灵兽'},
        {'type': 'attack', 'attacker': '你', 'skill': '青莲剑诀', 'damage': 150, 'critical': True},
        {'type': 'attack', 'attacker': '火灵兽', 'skill': '烈焰吐息', 'damage': 80},
        {'type': 'skill', 'caster': '你', 'skill_name': '玄冰护盾', 'effect': '减少50%火系伤害'},
        {'type': 'defeat', 'loser': '火灵兽', 'winner': '你'}
    ]
    
    context = {
        'location': {'name': '熔岩洞穴'},
        'player': {'name': '道友', 'realm': '筑基期'}
    }
    
    try:
        narrative = await narrator.generate_combat_narrative(combat_events, context)
        print(narrative)
    except Exception as e:
        print(f"错误: {e}")
        
    # 探索叙事
    print("\n\n2. 探索叙事：")
    print("-" * 50)
    
    try:
        # 有发现的探索
        discovery = {
            'type': '灵药',
            'description': '千年雪莲',
            'value': '珍稀'
        }
        
        narrative = await narrator.generate_exploration_narrative(
            '仔细搜索洞穴深处',
            discovery,
            context
        )
        print(narrative)
        
    except Exception as e:
        print(f"错误: {e}")


def demo_narrative_mock():
    """模拟叙事演示"""
    
    combat_narrative = """
剑光如虹，你施展青莲剑诀，凌厉的剑气化作青色莲花向火灵兽席卷而去。火灵兽察觉到致命威胁，
怒吼一声，烈焰吐息如岩浆般喷涌而出。千钧一发之际，你掐诀念咒，玄冰护盾应声而起，
将炽热的火焰尽数挡下。趁着火灵兽气息未稳，你剑指一引，青莲绽放，剑气透体而过。
火灵兽哀鸣一声，庞大的身躯轰然倒地，化作点点灵光消散。

最终，你取得了这场激烈战斗的胜利。
"""
    
    exploration_narrative = """
你小心翼翼地深入洞穴，灵识全开，不放过任何蛛丝马迹。忽然，一股清冷的药香传来，
你循着香味在一处隐秘的石缝中发现了一株雪白的灵药。定睛一看，竟是传说中的千年雪莲！
这等天材地宝，足以让筑基期修士突破瓶颈。你压抑住内心的激动，小心地将雪莲连根采下，
收入储物袋中。
"""
    
    print("\n1. 战斗叙事：")
    print("-" * 50)
    print(combat_narrative)
    
    print("\n\n2. 探索叙事：")
    print("-" * 50)
    print(exploration_narrative)


async def demo_world_events():
    """演示世界事件生成"""
    print("\n=== AI世界事件生成演示 ===")
    
    if not os.getenv('DEEPSEEK_API_KEY'):
        print("警告：未设置DEEPSEEK_API_KEY，将使用预设事件")
        return demo_world_events_mock()
        
    # 创建世界事件生成器
    llm_client = LLMClient()
    world_state = {
        'faction_relations': {'正道': 50, '魔道': -30},
        'phenomena': ['灵气潮汐', '天火陨落'],
        'resources': {'灵石矿': 30, '灵药': 60},
        'player': {'realm_level': 5, 'reputation': 200}
    }
    
    event_generator = AIWorldEventGenerator(llm_client, world_state)
    
    # 生成不同级别的事件
    for severity in ['minor', 'major']:
        print(f"\n{severity.upper()}级事件：")
        print("-" * 50)
        
        try:
            event = await event_generator.generate_world_event(
                f"定期{severity}事件",
                severity
            )
            
            print(f"事件名称: {event.get('name', '未知')}")
            print(f"描述: {event.get('description', '')}")
            print(f"影响范围: {event.get('scope', '未知')}")
            print(f"持续时间: {event.get('duration', '未知')}")
            
            if event.get('choices'):
                print("\n玩家选择:")
                for choice in event['choices']:
                    print(f"  {choice['id']}. {choice['text']}")
                    
        except Exception as e:
            print(f"错误: {e}")
            
        await asyncio.sleep(1)


def demo_world_events_mock():
    """模拟世界事件"""
    
    events = {
        'minor': {
            'name': '灵泉枯竭',
            'description': '青云山脉的一处灵泉突然枯竭，附近的修士纷纷议论纷纷，有人说是地脉变动所致。',
            'scope': '局部',
            'duration': '短期',
            'choices': [
                {'id': 1, 'text': '前往调查原因'},
                {'id': 2, 'text': '向门派汇报此事'},
                {'id': 3, 'text': '静观其变'}
            ]
        },
        'major': {
            'name': '上古秘境现世',
            'description': '天南州边境突然出现空间波动，一座尘封万年的上古秘境重现人间。各大势力蠢蠢欲动，一场腥风血雨即将来临。',
            'scope': '区域',
            'duration': '长期',
            'choices': [
                {'id': 1, 'text': '立即前往探索'},
                {'id': 2, 'text': '等待时机成熟'},
                {'id': 3, 'text': '联络盟友共同行动'},
                {'id': 4, 'text': '将消息卖给其他势力'}
            ]
        }
    }
    
    for severity, event in events.items():
        print(f"\n{severity.upper()}级事件：")
        print("-" * 50)
        print(f"事件名称: {event['name']}")
        print(f"描述: {event['description']}")
        print(f"影响范围: {event['scope']}")
        print(f"持续时间: {event['duration']}")
        
        print("\n玩家选择:")
        for choice in event['choices']:
            print(f"  {choice['id']}. {choice['text']}")


async def main():
    """主演示函数"""
    print("=== 修仙世界引擎 AI功能演示 ===")
    print(f"API密钥状态: {'已设置' if os.getenv('DEEPSEEK_API_KEY') else '未设置'}")
    
    # 演示各项AI功能
    await demo_ai_dialogue()
    await demo_narrative_generation()
    await demo_world_events()
    
    print("\n=== 演示完成 ===")
    print("\n提示：")
    print("1. 设置DEEPSEEK_API_KEY环境变量可以体验真实的AI生成效果")
    print("2. 未设置API密钥时将显示预设的演示内容")
    print("3. 这些AI功能可以集成到游戏中，提供动态的游戏体验")


if __name__ == '__main__':
    asyncio.run(main())
