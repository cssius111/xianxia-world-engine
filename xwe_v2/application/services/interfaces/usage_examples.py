"""
服务接口使用示例
展示如何使用各个服务接口进行开发
"""

from typing import Any, Dict, List, Optional

from xwe_v2.infrastructure.services import ServiceContainer, ServiceLifetime
from xwe_v2.infrastructure.services.interfaces import *


def example_service_implementation() -> None:
    """服务实现示例"""

    # 1. 实现一个服务
    class MyGameService(IGameService):
        """游戏服务的具体实现"""

        def __init__(self, container: ServiceContainer) -> None:
            self.container = container
            self._initialized = False
            self._game_state = GameState(
                initialized=False, in_combat=False, current_location="起始村", game_time=0.0
            )

        def initialize_game(self, player_name: Optional[str] = None, **options) -> bool:
            """初始化游戏"""
            # 获取玩家服务
            player_service = self.container.resolve(IPlayerService)

            # 创建玩家
            if player_name:
                player_id = player_service.create_player(player_name)
                self._game_state.player_id = player_id

            # 初始化世界
            world_service = self.container.resolve(IWorldService)
            world_service.initialize_world()

            self._initialized = True
            self._game_state.initialized = True

            return True

        def process_command(self, command: str, **context) -> CommandResult:
            """处理命令"""
            # 使用命令引擎
            command_engine = self.container.resolve(ICommandEngine)
            return command_engine.process_command(command, **context)

        # ... 实现其他接口方法 ...


def example_using_services() -> None:
    """使用服务的示例"""

    # 1. 创建服务容器
    container = ServiceContainer()

    # 2. 注册服务
    container.register(IGameService, MyGameService, ServiceLifetime.SINGLETON)
    # ... 注册其他服务 ...

    # 3. 解析并使用服务
    game_service = container.resolve(IGameService)
    player_service = container.resolve(IPlayerService)

    # 4. 初始化游戏
    game_service.initialize_game("测试玩家")

    # 5. 执行游戏操作
    result = game_service.process_command("查看状态")
    print(result.output)


def example_player_service_usage() -> None:
    """玩家服务使用示例"""

    # 假设已经有了服务实例
    player_service: IPlayerService = get_player_service()  # 伪代码

    # 1. 创建玩家
    player_id = player_service.create_player("李逍遥", spiritual_root="天灵根", talent="剑道天才")

    # 2. 获取玩家信息
    player = player_service.get_current_player()
    print(f"玩家：{player.name}，等级：{player.level}")

    # 3. 管理生命值
    damage = player_service.damage(50, "physical")
    print(f"受到{damage}点伤害")

    heal = player_service.heal(30)
    print(f"恢复{heal}点生命")

    # 4. 经验和升级
    result = player_service.add_experience(1000)
    if result["levels_gained"] > 0:
        print(f"升级了！现在是{player.level}级")

    # 5. 技能学习
    if player_service.add_skill("basic_sword"):
        print("学会了基础剑法")

    # 6. 物品管理
    player_service.add_item("healing_potion", 5)
    player_service.use_item("healing_potion")

    # 7. 装备管理
    player_service.equip_item("iron_sword", "weapon")


def example_combat_service_usage() -> None:
    """战斗服务使用示例"""

    combat_service: ICombatService = get_combat_service()  # 伪代码

    # 1. 开始战斗
    combat_id = combat_service.start_combat(
        CombatType.PVE,
        {
            1: [{"id": "player", "type": "player", "name": "勇者", "health": 100, "attack": 20}],
            2: [{"id": "goblin", "type": "monster", "name": "哥布林", "health": 50, "attack": 10}],
        },
    )

    # 2. 执行战斗行动
    # 玩家攻击
    result = combat_service.attack("goblin")
    print(f"造成{result.damage_dealt}点伤害")

    # 使用技能
    result = combat_service.use_skill("fireball", "goblin")
    if result.is_critical:
        print("暴击！")

    # 3. 查询战斗状态
    state = combat_service.get_combat_state()
    for combatant_id, combatant in state.combatants.items():
        print(f"{combatant.name}: {combatant.health}/{combatant.max_health}")

    # 4. AI行动
    ai_action = combat_service.get_ai_action("goblin")
    combat_service.execute_action(ai_action)

    # 5. 结束战斗
    result = combat_service.end_combat(combat_id)
    print(f"战斗结束，获得奖励：{result['rewards']}")


def example_cultivation_service_usage() -> None:
    """修炼服务使用示例"""

    cultivation_service: ICultivationService = get_cultivation_service()  # 伪代码

    # 1. 基础修炼
    result = cultivation_service.cultivate(CultivationType.MEDITATION, duration=3600)  # 1小时
    print(result.message)

    # 2. 检查突破条件
    breakthrough_info = cultivation_service.check_breakthrough_requirements()
    if breakthrough_info.experience_required <= 0:
        print("可以尝试突破了！")

        # 尝试突破
        breakthrough_result = cultivation_service.attempt_breakthrough()
        if breakthrough_result["success"]:
            print(f"突破成功！进入{breakthrough_result['new_realm']}！")

            # 如果触发天劫
            if breakthrough_result["tribulation_triggered"]:
                tribulation_id = cultivation_service.trigger_tribulation()

                # 应对天劫
                result = cultivation_service.face_tribulation(tribulation_id, "resist")
                if result["success"]:
                    print("成功渡过天劫！")

    # 3. 功法修炼
    # 学习功法
    if cultivation_service.learn_technique("basic_qi_cultivation"):
        print("学会了基础练气诀")

    # 修炼功法
    result = cultivation_service.practice_technique("basic_qi_cultivation", duration=1800)
    print(f"功法熟练度提升{result['proficiency_gained']}")

    # 4. 丹药使用
    pill_result = cultivation_service.use_cultivation_pill("qi_gathering_pill")
    print(f"服用丹药，修为提升{pill_result['experience_gained']}")

    # 检查丹毒
    toxicity = cultivation_service.get_pill_toxicity()
    if toxicity > 50:
        print("丹毒过重，需要清理")
        cultivation_service.cleanse_pill_toxicity(30)


def example_world_service_usage() -> None:
    """世界服务使用示例"""

    world_service: IWorldService = get_world_service()  # 伪代码

    # 1. 位置查询
    current = world_service.get_current_location()
    print(f"当前位置：{current.name}")

    # 查看连接的位置
    connections = world_service.get_connected_locations()
    print("可以前往：")
    for loc in connections:
        print(f"- {loc.name} (危险等级：{loc.danger_level})")

    # 2. 移动
    move_result = world_service.move_to("tiannan_city")
    if move_result["success"]:
        print(f"移动成功，耗时{move_result['travel_time']}秒")

        # 路上可能发生事件
        for event in move_result["events"]:
            print(f"遭遇：{event['description']}")

    # 3. 探索
    explore_result = world_service.explore_current_location()
    if explore_result.success:
        print(explore_result.description)

        # 发现新位置
        for discovery in explore_result.discoveries:
            print(f"发现了：{discovery}")

        # 获得资源
        for resource, amount in explore_result.resources_found.items():
            print(f"找到{resource} x{amount}")

    # 4. 时间和天气
    time_info = world_service.get_world_time()
    print(f"游戏时间：第{time_info['day']}天 {time_info['hour']}时")

    weather = world_service.get_weather()
    print(f"天气：{weather.value}")

    # 5. 世界事件
    active_events = world_service.get_active_events()
    for event in active_events:
        print(f"世界事件：{event.name} - {event.description}")

        # 参与事件
        result = world_service.participate_in_event(event.id)
        print(result["message"])


def example_save_service_usage() -> None:
    """存档服务使用示例"""

    save_service: ISaveService = get_save_service()  # 伪代码

    # 1. 创建存档
    save_data = {"game_state": {...}, "player_data": {...}, "world_data": {...}}

    save_id = save_service.create_save("第一章完成", save_data, SaveType.MANUAL)
    print(f"存档创建成功，ID: {save_id}")

    # 2. 快速存档
    quick_save_id = save_service.quick_save(save_data)

    # 3. 自动存档
    auto_save_id = save_service.auto_save(save_data)

    # 4. 列出存档
    saves = save_service.list_saves()
    for save_info in saves:
        print(f"{save_info.name} - {save_info.player_name} Lv.{save_info.player_level}")
        print(f"  游戏时长：{save_info.formatted_play_time}")
        print(f"  创建时间：{save_info.created_at}")

    # 5. 加载存档
    save_data = save_service.load_save(save_id)
    if save_data:
        print("存档加载成功")
        # 恢复游戏状态...

    # 6. 云存档
    if save_service.sync_to_cloud(save_id):
        print("已同步到云端")

    cloud_saves = save_service.list_cloud_saves()
    print(f"云端有{len(cloud_saves)}个存档")


def example_event_driven_architecture() -> None:
    """事件驱动架构示例"""

    event_dispatcher: IEventDispatcher = get_event_dispatcher()  # 伪代码

    # 1. 订阅事件
    def on_player_level_up(event) -> None:
        player_id = event.data["player_id"]
        new_level = event.data["new_level"]
        print(f"玩家{player_id}升到了{new_level}级！")

        # 发放升级奖励
        if new_level % 10 == 0:
            # 每10级给特殊奖励
            event_dispatcher.dispatch_game_event(
                "milestone_reached", {"type": "level", "value": new_level}
            )

    event_dispatcher.subscribe("player_level_up", on_player_level_up)

    # 2. 发布事件
    event_dispatcher.dispatch_player_event(
        "player_level_up", {"new_level": 10}, player_id="player_123"
    )

    # 3. 查看事件历史
    events = event_dispatcher.get_event_history(limit=10)
    for event in events:
        print(f"{event.timestamp}: {event.type}")

    # 4. 事件统计
    stats = event_dispatcher.get_statistics()
    print(f"总事件数：{stats.total_events}")
    print(f"每分钟事件数：{stats.events_per_minute}")


def example_command_pattern() -> None:
    """命令模式示例"""

    from xwe_v2.infrastructure.services.command_engine import (
        CommandContext,
        CommandHandler,
        CommandResult,
    )

    class TeleportCommandHandler(CommandHandler):
        """传送命令处理器"""

        def __init__(self, world_service: IWorldService) -> None:
            super().__init__(
                commands=["传送", "teleport", "tp"],
                aliases=["瞬移"],
                description="传送到指定位置",
                usage="传送 <位置名称>",
                require_args=1,
            )
            self.world_service = world_service

        def _do_handle(self, context: CommandContext) -> CommandResult:
            target_location = context.args[0]

            # 检查是否可以传送
            location = self.world_service.get_location(target_location)
            if not location:
                return CommandResult(
                    success=False,
                    output=f"未知的位置：{target_location}",
                    suggestions=self._get_location_suggestions(target_location),
                )

            # 执行传送
            move_result = self.world_service.move_to(location.id)

            return CommandResult(
                success=move_result["success"],
                output=f"传送到{location.name}",
                state_changed=True,
                events=[{"type": "teleported", "from": context.location, "to": location.id}],
            )

        def _get_location_suggestions(self, partial: str) -> List[str]:
            """获取位置建议"""
            all_locations = self.world_service.list_locations()
            suggestions = []

            for loc in all_locations:
                if partial.lower() in loc.name.lower():
                    suggestions.append(loc.name)

            return suggestions[:5]


def get_player_service() -> IPlayerService:
    """获取玩家服务实例（伪代码）"""
    pass


def get_combat_service() -> ICombatService:
    """获取战斗服务实例（伪代码）"""
    pass


def get_cultivation_service() -> ICultivationService:
    """获取修炼服务实例（伪代码）"""
    pass


def get_world_service() -> IWorldService:
    """获取世界服务实例（伪代码）"""
    pass


def get_save_service() -> ISaveService:
    """获取存档服务实例（伪代码）"""
    pass


def get_event_dispatcher() -> IEventDispatcher:
    """获取事件分发器实例（伪代码）"""
    pass


if __name__ == "__main__":
    print("服务接口使用示例")
    print("=" * 50)
    print("本文件展示了如何使用各个服务接口")
    print("实际使用时需要实现具体的服务类")
