"""
GameStateManager 使用示例

展示如何使用新的游戏状态管理器
"""

from xwe.core.state import GameStateManager, GameContext, GameState
from xwe.core.character import Character, CharacterType
from xwe.core.events import EventBus
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic_usage():
    """基础使用示例"""
    print("\n=== 基础使用示例 ===")
    
    # 创建状态管理器
    state_manager = GameStateManager()
    
    # 创建玩家
    player = Character(name="云游侠", character_type=CharacterType.PLAYER)
    state_manager.set_player(player)
    
    # 设置位置
    state_manager.set_location("青云山")
    
    # 设置游戏标记
    state_manager.set_flag("first_visit_qingyun", True)
    state_manager.set_flag("player_level", 1)
    
    # 获取游戏信息
    info = state_manager.get_game_info()
    print(f"玩家: {info['player_name']}")
    print(f"位置: {info['location']}")
    print(f"游戏模式: {info['game_mode']}")


def example_context_management():
    """上下文管理示例"""
    print("\n=== 上下文管理示例 ===")
    
    state_manager = GameStateManager()
    
    # 开始探索
    state_manager.push_context(GameContext.EXPLORATION)
    print(f"当前上下文: {state_manager.get_current_context().name}")
    
    # 进入对话
    state_manager.push_context(GameContext.DIALOGUE, {
        'npc_id': 'elder_wang',
        'dialogue_node': 'greeting'
    })
    print(f"当前上下文: {state_manager.get_current_context().name}")
    print(f"对话数据: {state_manager.get_context_data()}")
    
    # 在对话中进入交易
    state_manager.push_context(GameContext.TRADING, {
        'shop_id': 'elder_wang_shop',
        'discount': 0.9
    })
    print(f"上下文栈深度: {len(state_manager.context_stack)}")
    
    # 退出交易
    state_manager.pop_context()
    print(f"返回到: {state_manager.get_current_context().name}")
    
    # 退出对话
    state_manager.pop_context()
    print(f"返回到: {state_manager.get_current_context().name}")


def example_combat_flow():
    """战斗流程示例"""
    print("\n=== 战斗流程示例 ===")
    
    state_manager = GameStateManager()
    
    # 创建玩家
    player = Character(name="剑侠", character_type=CharacterType.PLAYER)
    state_manager.set_player(player)
    
    # 开始战斗
    print("遭遇妖兽！")
    state_manager.start_combat("combat_001")
    
    print(f"在战斗中: {state_manager.is_in_combat()}")
    print(f"当前上下文: {state_manager.get_current_context().name}")
    
    # 模拟战斗过程
    state_manager.update_statistics("damage_dealt", 150)
    state_manager.update_statistics("damage_taken", 30)
    
    # 结束战斗
    combat_result = {
        'winner': 'player',
        'exp_gained': 100,
        'gold_gained': 50,
        'duration': 5
    }
    state_manager.end_combat(combat_result)
    
    print(f"战斗结束，在战斗中: {state_manager.is_in_combat()}")
    print(f"战斗历史记录数: {len(state_manager.state.combat_history)}")


def example_state_listeners():
    """状态监听器示例"""
    print("\n=== 状态监听器示例 ===")
    
    state_manager = GameStateManager()
    
    # 定义监听器函数
    def on_location_changed(data):
        print(f"[事件] 位置变化: {data['old']} → {data['new']}")
    
    def on_achievement_unlocked(data):
        print(f"[事件] 🎉 成就解锁: {data['achievement']}")
    
    def on_flag_changed(data):
        print(f"[事件] 标记变化: {data['key']} = {data['value']}")
    
    # 注册监听器
    state_manager.add_listener('location_changed', on_location_changed)
    state_manager.add_listener('achievement_unlocked', on_achievement_unlocked)
    state_manager.add_listener('flag_changed', on_flag_changed)
    
    # 触发事件
    state_manager.set_location("神秘森林")
    state_manager.add_achievement("first_exploration")
    state_manager.set_flag("forest_discovered", True)


def example_save_load():
    """存档示例"""
    print("\n=== 存档示例 ===")
    
    # 创建并配置状态
    state_manager = GameStateManager()
    
    player = Character(name="存档测试者", character_type=CharacterType.PLAYER)
    state_manager.set_player(player)
    state_manager.set_location("仙灵湖")
    state_manager.add_achievement("save_master")
    state_manager.push_context(GameContext.CULTIVATION, {'duration': 60})
    
    # 保存状态
    save_path = Path("test_save.json")
    state_manager.save_state(save_path)
    print(f"游戏已保存到: {save_path}")
    
    # 创建新的状态管理器并加载
    new_manager = GameStateManager()
    new_manager.load_state(save_path)
    
    # 验证加载结果
    print(f"加载的玩家: {new_manager.get_player().name}")
    print(f"加载的位置: {new_manager.get_location()}")
    print(f"加载的成就: {new_manager.state.achievements}")
    print(f"加载的上下文: {new_manager.get_current_context().name}")
    
    # 清理测试文件
    save_path.unlink()


def example_snapshots():
    """快照功能示例"""
    print("\n=== 快照功能示例 ===")
    
    state_manager = GameStateManager()
    
    # 设置初始状态
    state_manager.set_location("起始村庄")
    state_manager.set_flag("gold", 100)
    print(f"初始状态 - 位置: {state_manager.get_location()}, 金币: {state_manager.get_flag('gold')}")
    
    # 创建快照
    state_manager.create_snapshot()
    
    # 修改状态
    state_manager.set_location("主城")
    state_manager.set_flag("gold", 50)
    print(f"购物后 - 位置: {state_manager.get_location()}, 金币: {state_manager.get_flag('gold')}")
    
    # 再次创建快照
    state_manager.create_snapshot()
    
    # 继续修改
    state_manager.set_location("野外")
    state_manager.set_flag("gold", 0)
    print(f"被抢劫后 - 位置: {state_manager.get_location()}, 金币: {state_manager.get_flag('gold')}")
    
    # 恢复到上一个快照
    state_manager.restore_snapshot(-1)
    print(f"撤销一步 - 位置: {state_manager.get_location()}, 金币: {state_manager.get_flag('gold')}")
    
    # 恢复到第一个快照
    state_manager.restore_snapshot(0)
    print(f"撤销到开始 - 位置: {state_manager.get_location()}, 金币: {state_manager.get_flag('gold')}")


def example_quest_management():
    """任务管理示例"""
    print("\n=== 任务管理示例 ===")
    
    state_manager = GameStateManager()
    
    # 添加任务
    quest_data = {
        'name': '初出茅庐',
        'description': '击败10只野怪',
        'progress': 0,
        'target': 10,
        'rewards': {'exp': 100, 'gold': 50}
    }
    state_manager.add_quest('newbie_quest', quest_data)
    print(f"接受任务: {quest_data['name']}")
    
    # 更新任务进度
    for i in range(1, 11):
        state_manager.update_quest('newbie_quest', {'progress': i})
        if i % 3 == 0:
            print(f"任务进度: {i}/10")
    
    # 完成任务
    state_manager.complete_quest('newbie_quest')
    quest = state_manager.state.quests['newbie_quest']
    print(f"任务完成: {quest['completed']}")
    print(f"完成时间: {quest.get('completed_at', 'N/A')}")


def example_statistics():
    """统计数据示例"""
    print("\n=== 统计数据示例 ===")
    
    state_manager = GameStateManager()
    
    # 记录各种统计数据
    state_manager.update_statistics('enemies_defeated', 5)
    state_manager.update_statistics('enemies_defeated', 3)
    state_manager.update_statistics('distance_traveled', 100.5)
    state_manager.update_statistics('distance_traveled', 50.3)
    state_manager.update_statistics('play_time', 3600)  # 秒
    state_manager.update_statistics('highest_damage', 999)
    
    # 显示统计
    stats = state_manager.state.statistics
    print("游戏统计:")
    print(f"  击败敌人: {stats.get('enemies_defeated', 0)}")
    print(f"  行走距离: {stats.get('distance_traveled', 0):.1f}米")
    print(f"  游戏时长: {stats.get('play_time', 0) // 60}分钟")
    print(f"  最高伤害: {stats.get('highest_damage', 0)}")


def example_npc_relationships():
    """NPC关系管理示例"""
    print("\n=== NPC关系管理示例 ===")
    
    state_manager = GameStateManager()
    
    # 创建NPC
    npc1 = Character(name="掌门人", character_type=CharacterType.NPC)
    npc1.id = "sect_master"
    npc2 = Character(name="神秘商人", character_type=CharacterType.NPC)
    npc2.id = "merchant"
    
    state_manager.add_npc(npc1)
    state_manager.add_npc(npc2)
    
    # 更新关系值
    print("完成任务，掌门好感度+10")
    state_manager.update_npc_relationship("sect_master", 10)
    
    print("讨价还价失败，商人好感度-5")
    state_manager.update_npc_relationship("merchant", -5)
    
    print("帮助商人，好感度+20")
    state_manager.update_npc_relationship("merchant", 20)
    
    # 显示关系
    relationships = state_manager.state.npc_relationships
    print("\nNPC关系:")
    for npc_id, value in relationships.items():
        npc = state_manager.get_npc(npc_id)
        if npc:
            print(f"  {npc.name}: {value}")


def main():
    """运行所有示例"""
    examples = [
        example_basic_usage,
        example_context_management,
        example_combat_flow,
        example_state_listeners,
        example_save_load,
        example_snapshots,
        example_quest_management,
        example_statistics,
        example_npc_relationships
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"示例 {example.__name__} 出错: {e}")
        print("\n" + "="*50)


if __name__ == "__main__":
    main()
