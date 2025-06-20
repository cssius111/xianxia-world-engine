#!/usr/bin/env python
"""
增强版NPC对话系统演示

演示情感、记忆和智能对话功能。
"""

import logging

from xwe.core.character import Character
from xwe.npc import (
    DialogueSystem,
    EmotionType,
    NPCBehavior,
    NPCManager,
    NPCProfile,
    PersonalityTrait,
)

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def print_dialogue_state(node, context=None):
    """打印对话状态"""
    print("\n" + "=" * 60)
    if node:
        print(f"[{node.speaker}]: {node.text}")

        # 显示可用选项
        if hasattr(node, "choices") and node.choices:
            print("\n可选回复:")
            for i, choice in enumerate(node.choices):
                print(f"  {i+1}. {choice.text}")

    if context:
        print(f"\n[情绪状态]: {context.current_emotion} (强度: {context.emotion_intensity:.2f})")
        if context.memory_context:
            print(f"[记忆]: {context.memory_context}")
    print("=" * 60)


def demo_enhanced_dialogue():
    """演示增强版对话系统"""
    print("=== 增强版NPC对话系统演示 ===\n")

    # 创建系统
    dialogue_system = DialogueSystem()
    npc_manager = NPCManager(dialogue_system)

    # 创建一个新的NPC - 丹药师
    alchemist_profile = NPCProfile(
        id="npc_zhang_alchemist",
        name="张丹师",
        title="百草堂主管",
        description="一位经验丰富的炼丹师，性格古怪但医术高明。",
        behavior=NPCBehavior.STATIC,
        home_location="baicao_hall",
        is_merchant=True,
        shop_id="zhang_alchemy_shop",
        faction="百草堂",
        default_relationship=30,
        extra_data={"personality_template": "scholar"},
    )

    # 创建自定义对话树
    alchemist_dialogue = {
        "nodes": [
            {
                "id": "start",
                "type": "text",
                "speaker": "张丹师",
                "text": "嗯？又是一个想学炼丹的小子？",
                "next_node": "test",
            },
            {
                "id": "test",
                "type": "choice",
                "speaker": "player",
                "text": "",
                "choices": [
                    {
                        "id": "humble",
                        "text": "晚辈确实想学习炼丹之道，还请前辈指教。",
                        "next_node": "approve",
                        "effects": {"relationship_change": 10},
                    },
                    {
                        "id": "arrogant",
                        "text": "我天赋异禀，学炼丹还不是手到擒来？",
                        "next_node": "disapprove",
                        "effects": {"relationship_change": -10},
                    },
                    {
                        "id": "gift",
                        "text": "这是晚辈的一点心意。（递上千年灵芝）",
                        "next_node": "surprised",
                        "requirements": {"required_items": ["millennium_ganoderma"]},
                        "effects": {"relationship_change": 30},
                    },
                ],
            },
            {
                "id": "approve",
                "type": "text",
                "speaker": "张丹师",
                "text": "嗯，还算有点礼数。炼丹一道，最重要的是耐心和细心。",
                "next_node": "teach",
            },
            {
                "id": "disapprove",
                "type": "text",
                "speaker": "张丹师",
                "text": "哼！年轻人就是狂妄。炼丹岂是你想的那么简单？",
                "next_node": "warn",
            },
            {
                "id": "surprised",
                "type": "text",
                "speaker": "张丹师",
                "text": "哦？千年灵芝！你这小子有心了。罢了，我就教你一些基础。",
                "next_node": "teach_advanced",
                "effects": {"add_flag": "impressed_alchemist"},
            },
            {
                "id": "teach",
                "type": "text",
                "speaker": "张丹师",
                "text": "记住，控火是炼丹的关键。火候差一分，药性就差十分。",
                "effects": {"add_flag": "learned_alchemy_basics"},
            },
            {
                "id": "teach_advanced",
                "type": "text",
                "speaker": "张丹师",
                "text": "你资质不错，我传你一个独门炼丹手法——三转淬灵术。",
                "effects": {"add_flag": "learned_special_technique", "give_item": "alchemy_manual"},
            },
            {
                "id": "warn",
                "type": "text",
                "speaker": "张丹师",
                "text": "等你炸炉几次就知道厉害了。去去去，别打扰我炼丹。",
            },
        ],
        "start_node": "start",
    }

    # 注册NPC
    npc_manager.register_npc_profile(alchemist_profile)
    npc_manager.create_npc_character("npc_zhang_alchemist")
    dialogue_system.load_dialogue("npc_zhang_alchemist", "default", alchemist_dialogue)

    # 创建玩家信息
    player_info = {"level": 5, "faction": "散修", "reputation": 100}

    # 测试场景1：第一次见面
    print("\n### 场景1：第一次见面 ###")
    player_id = "player_001"

    node, context = npc_manager.start_dialogue(player_id, "npc_zhang_alchemist", player_info)
    print_dialogue_state(node, context)

    # 选择谦虚的回答
    node, context = npc_manager.enhanced_dialogue.advance_dialogue(player_id, "humble")
    print_dialogue_state(node, context)

    # 测试场景2：使用自然语言输入
    print("\n\n### 场景2：自然语言对话（再次见面） ###")

    # 模拟时间流逝，情绪衰减
    npc_manager.emotion_system.decay_emotions(10)

    # 再次对话
    node, context = npc_manager.start_dialogue(player_id, "npc_zhang_alchemist", player_info)
    print_dialogue_state(node, context)

    # 使用自然语言
    print("\n玩家输入: 前辈，我想买一些炼丹材料")
    node, context = npc_manager.enhanced_dialogue.process_player_input(
        player_id, "前辈，我想买一些炼丹材料"
    )
    print_dialogue_state(node, context)

    # 测试场景3：情绪变化
    print("\n\n### 场景3：触发不同情绪 ###")

    # 赞美NPC
    print("\n玩家输入: 您的炼丹技术真是太厉害了！")
    npc_manager.emotion_system.trigger_emotion(
        "npc_zhang_alchemist",
        "praise",
        {"relationship": npc_manager.get_relationship(player_id, "npc_zhang_alchemist")},
    )

    node, context = npc_manager.enhanced_dialogue.process_player_input(
        player_id, "您的炼丹技术真是太厉害了！"
    )
    print_dialogue_state(node, context)

    # 测试场景4：记忆系统
    print("\n\n### 场景4：NPC记忆 ###")

    # 创建一些记忆
    npc_manager.memory_system.create_memory(
        "npc_zhang_alchemist", player_id, "helped", game_time=100, player_name="道友"
    )

    # 查看记忆总结
    summary = npc_manager.memory_system.get_relationship_summary("npc_zhang_alchemist", player_id)
    print(f"\nNPC记忆总结:")
    print(f"  总互动次数: {summary['total_interactions']}")
    print(f"  关系类型: {summary['relationship_type']}")
    print(f"  情感倾向: {summary['emotion_tendency']}")

    # 测试场景5：多个NPC
    print("\n\n### 场景5：创建商人NPC ###")

    # 创建王老板
    wang_id = "npc_wang_boss"
    wang_character = npc_manager.create_npc_character(wang_id)

    # 与王老板对话
    node, context = npc_manager.start_dialogue(player_id, wang_id, player_info)
    print_dialogue_state(node, context)

    # 查看可用NPC
    print("\n\n### 当前位置的NPC ###")
    npc_manager.set_npc_location("npc_zhang_alchemist", "tiannan_market")
    npc_manager.set_npc_location(wang_id, "tiannan_market")

    available_npcs = npc_manager.get_available_npcs("tiannan_market", player_id)
    for npc in available_npcs:
        emotion_state = npc_manager.emotion_system.get_emotion_state(npc["id"])
        emotion = emotion_state.current_emotion.value if emotion_state else "未知"
        print(f"\n{npc['name']} - {npc['title']}")
        print(f"  关系度: {npc['relationship']}")
        print(f"  情绪: {emotion}")
        print(f"  描述: {npc['description']}")


def demo_personality_effects():
    """演示性格对对话的影响"""
    print("\n\n=== 性格系统演示 ===\n")

    dialogue_system = DialogueSystem()
    npc_manager = NPCManager(dialogue_system)

    # 创建不同性格的NPC
    personalities = [
        ("李剑客", "warrior", "豪爽的剑客，性格直率"),
        ("苏书生", "scholar", "温文尔雅的书生，喜欢引经据典"),
        ("钱掌柜", "merchant", "精明的商人，总想着赚钱"),
    ]

    player_id = "player_test"
    player_info = {"level": 10}

    for name, template, desc in personalities:
        npc_id = f"npc_{template}"
        profile = NPCProfile(
            id=npc_id, name=name, description=desc, extra_data={"personality_template": template}
        )

        npc_manager.register_npc_profile(profile)
        npc_manager.create_npc_character(npc_id)

        # 对同一句话的反应
        print(f"\n### {name}的反应 ###")
        node, context = npc_manager.start_dialogue(player_id, npc_id, player_info)

        # 触发相同的情绪
        npc_manager.emotion_system.trigger_emotion(npc_id, "gift", {})

        # 查看性格参数
        personality = npc_manager.emotion_system.get_personality(npc_id)
        if personality:
            style = personality.get_dialogue_style()
            print(
                f"对话风格: 正式度={style['formality']:.2f}, "
                f"健谈度={style['verbosity']:.2f}, "
                f"友善度={style['friendliness']:.2f}"
            )


if __name__ == "__main__":
    # 运行演示
    demo_enhanced_dialogue()
    demo_personality_effects()

    print("\n\n演示完成！增强版NPC对话系统展示了：")
    print("1. 情感系统 - NPC有情绪变化")
    print("2. 记忆系统 - NPC记住互动历史")
    print("3. 自然语言理解 - 支持自由输入")
    print("4. 性格系统 - 不同性格有不同对话风格")
    print("5. 动态对话生成 - 根据上下文生成对话")
