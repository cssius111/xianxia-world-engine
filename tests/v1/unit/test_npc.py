# test_npc.py
"""
测试NPC系统功能

测试对话、交易和NPC管理。
"""


# 添加项目根目录到Python路径

from xwe.core import Character
from xwe.npc import DialogueSystem, NPCManager, TradingSystem
from xwe.npc.dialogue_system import (
    DialogueChoice,
    DialogueNode,
    DialogueNodeType,
    DialogueTree,
)


def test_dialogue_system():
    """测试对话系统"""
    print("=== 测试对话系统 ===")

    # 创建对话系统
    dialogue_system = DialogueSystem()

    # 创建简单的对话树
    tree = DialogueTree("test_npc", "test_dialogue")

    # 添加节点
    start_node = DialogueNode(
        id="start",
        type=DialogueNodeType.TEXT,
        speaker="npc",
        text="你好，冒险者！",
        next_node="choice1",
    )
    tree.add_node(start_node)

    choice_node = DialogueNode(
        id="choice1",
        type=DialogueNodeType.CHOICE,
        speaker="player",
        text="",
        choices=[
            DialogueChoice(id="greet", text="你好！", next_node="response1"),
            DialogueChoice(id="ask", text="你是谁？", next_node="response2"),
            DialogueChoice(id="leave", text="再见", next_node="goodbye"),
        ],
    )
    tree.add_node(choice_node)

    response1 = DialogueNode(
        id="response1",
        type=DialogueNodeType.TEXT,
        speaker="npc",
        text="很高兴见到你！",
        effects={"relationship_change": 5},
    )
    tree.add_node(response1)

    response2 = DialogueNode(
        id="response2", type=DialogueNodeType.TEXT, speaker="npc", text="我是这里的守卫。"
    )
    tree.add_node(response2)

    goodbye = DialogueNode(
        id="goodbye", type=DialogueNodeType.TEXT, speaker="npc", text="再见，保重！"
    )
    tree.add_node(goodbye)

    # 加载对话树
    dialogue_system.dialogue_trees["test_npc"] = {"test_dialogue": tree}

    # 测试对话流程
    player_id = "test_player"

    # 开始对话
    first_node = dialogue_system.start_dialogue(player_id, "test_npc", "test_dialogue")
    print(f"第一个节点: {first_node.text}")
    assert first_node.id == "start"

    # 获取选项
    context = {"player_level": 5}
    # 前进到选择节点
    dialogue_system.advance_dialogue(player_id, context)

    choices = dialogue_system.get_active_dialogue(player_id).get_available_choices(context)
    print(f"可用选项数: {len(choices)}")
    assert len(choices) == 3

    # 选择第一个选项
    next_node = dialogue_system.advance_dialogue(player_id, context, "greet")
    print(f"选择后的回应: {next_node.text}")
    assert next_node.id == "response1"

    print("✓ 对话系统测试通过\n")


def test_npc_manager():
    """测试NPC管理器"""
    print("=== 测试NPC管理器 ===")

    # 创建系统
    dialogue_system = DialogueSystem()
    npc_manager = NPCManager(dialogue_system)

    # 测试NPC档案
    print(f"注册的NPC数: {len(npc_manager.npc_profiles)}")
    assert len(npc_manager.npc_profiles) > 0

    # 获取王老板的档案
    wang_profile = npc_manager.get_npc_profile("npc_wang_boss")
    print(f"NPC名称: {wang_profile.name}")
    print(f"是否商人: {wang_profile.is_merchant}")
    assert wang_profile.is_merchant is True

    # 创建NPC角色
    wang_character = npc_manager.create_npc_character("npc_wang_boss")
    print(f"创建角色: {wang_character.name}")
    assert wang_character is not None

    # 测试关系系统
    player_id = "test_player"
    initial_relationship = npc_manager.get_relationship(player_id, "npc_wang_boss")
    print(f"初始关系值: {initial_relationship}")

    # 修改关系
    npc_manager.modify_relationship(player_id, "npc_wang_boss", 10)
    new_relationship = npc_manager.get_relationship(player_id, "npc_wang_boss")
    print(f"修改后关系值: {new_relationship}")
    assert new_relationship == initial_relationship + 10

    # 测试位置
    npc_manager.set_npc_location("npc_wang_boss", "tiannan_market")
    location = npc_manager.get_npc_location("npc_wang_boss")
    print(f"NPC位置: {location}")
    assert location == "tiannan_market"

    # 获取位置的NPC
    npcs_in_market = npc_manager.get_npcs_in_location("tiannan_market")
    print(f"坊市中的NPC数: {len(npcs_in_market)}")
    assert "npc_wang_boss" in npcs_in_market

    print("✓ NPC管理器测试通过\n")


def test_trading_system():
    """测试交易系统"""
    print("=== 测试交易系统 ===")

    # 创建交易系统
    trading_system = TradingSystem()

    # 测试物品
    print(f"注册的物品数: {len(trading_system.items)}")
    assert len(trading_system.items) > 0

    # 获取物品
    healing_pill = trading_system.get_item("healing_pill_low")
    print(f"物品名称: {healing_pill.name}")
    print(f"购买价格: {healing_pill.buy_price}")
    print(f"出售价格: {healing_pill.sell_price}")

    # 测试商店
    wang_shop = trading_system.get_shop("wang_basic_shop")
    print(f"\n商店名称: {wang_shop.name}")
    print(f"商品数量: {len(wang_shop.items)}")

    # 获取商店物品
    player_context = {"player_level": 5, "spirit_stones": 1000, "npc_relationship": 20}

    available_items = trading_system.get_shop_items("wang_basic_shop", player_context)
    print(f"可购买物品数: {len(available_items)}")
    for item in available_items[:3]:
        print(f"- {item['name']}: {item['price']}灵石")

    # 测试购买
    result = trading_system.buy_item("wang_basic_shop", "healing_pill_low", 2, player_context)
    print(f"\n购买结果: {result['message']}")
    print(f"花费: {result['cost']}灵石")
    assert result["success"] is True

    # 测试出售
    sell_result = trading_system.sell_item("wang_basic_shop", "iron_ore", 5)
    print(f"\n出售结果: {sell_result['message']}")
    print(f"收入: {sell_result['income']}灵石")

    print("✓ 交易系统测试通过\n")


def test_dialogue_integration():
    """测试对话集成"""
    print("=== 测试对话集成 ===")

    # 创建完整系统
    dialogue_system = DialogueSystem()
    npc_manager = NPCManager(dialogue_system)

    # 创建王老板
    wang = npc_manager.create_npc_character("npc_wang_boss")
    npc_manager.set_npc_location("npc_wang_boss", "tiannan_market")

    # 开始对话
    player_id = "test_player"
    first_node = npc_manager.start_dialogue(player_id, "npc_wang_boss")

    if first_node:
        print(f"王老板: {first_node.text}")

        # 获取可用选项
        context = {"player_level": 5, "npc_relationship": 20, "flags": {}}

        dialogue = dialogue_system.get_active_dialogue(player_id)
        if dialogue:
            choices = dialogue.get_available_choices(context)
            print(f"\n可选项数: {len(choices)}")
            for i, choice in enumerate(choices, 1):
                print(f"{i}. {choice.text}")

    print("\n✓ 对话集成测试通过\n")


def main():
    """运行所有测试"""
    print("仙侠世界引擎 - NPC系统测试")
    print("=" * 50)
    print()

    try:
        test_dialogue_system()
        test_npc_manager()
        test_trading_system()
        test_dialogue_integration()

        print("=" * 50)
        print("所有NPC系统测试通过！")
        print("\n功能说明：")
        print("- 对话系统：支持分支对话、条件判断、效果应用")
        print("- NPC管理：档案管理、关系系统、位置追踪")
        print("- 交易系统：物品定义、商店管理、买卖交易")
        print("\n在游戏中使用命令：")
        print("- '和王老板说话' 或 'talk to 王老板' 开始对话")
        print("- 输入数字选择对话选项")
        print("- 输入'退出对话'结束对话")

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
