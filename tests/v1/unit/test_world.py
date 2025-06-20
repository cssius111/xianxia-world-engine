# test_world.py
"""
测试世界系统功能

测试地图、位置管理和事件系统。
"""


# 添加项目根目录到Python路径

from xwe.core import Character
from xwe.world import Area, AreaType, EventSystem, LocationManager, WorldMap


def test_world_map():
    """测试世界地图"""
    print("=== 测试世界地图 ===")

    # 创建地图
    world_map = WorldMap()

    # 添加测试区域
    area1 = Area(
        id="test_city",
        name="测试城",
        type=AreaType.CITY,
        description="一个测试用的城市",
        parent_region="test_region",
        danger_level=1,
        connected_areas=["test_wild"],
    )

    area2 = Area(
        id="test_wild",
        name="测试荒野",
        type=AreaType.WILDERNESS,
        description="城外的荒野",
        parent_region="test_region",
        danger_level=3,
        connected_areas=["test_city"],
    )

    world_map.add_area(area1)
    world_map.add_area(area2)

    # 测试获取区域
    retrieved_area = world_map.get_area("test_city")
    print(f"获取区域: {retrieved_area.name}")
    assert retrieved_area.name == "测试城"

    # 测试相邻区域
    connected = world_map.get_connected_areas("test_city")
    print(f"相邻区域: {[a.name for a in connected]}")
    assert len(connected) == 1
    assert connected[0].name == "测试荒野"

    # 测试移动检查
    can_move, reason = world_map.can_move_to("test_city", "test_wild", player_level=1)
    print(f"可以移动: {can_move}")
    assert can_move is True

    print("✓ 世界地图测试通过\n")


def test_location_manager():
    """测试位置管理器"""
    print("=== 测试位置管理器 ===")

    # 创建地图和位置管理器
    world_map = WorldMap()
    location_manager = LocationManager(world_map)

    # 使用默认地图数据
    from xwe.world.world_map import DEFAULT_MAP_DATA, Area

    for area_data in DEFAULT_MAP_DATA["areas"][:3]:
        area = Area.from_dict(area_data)
        world_map.add_area(area)

    # 创建测试角色
    player = Character(name="测试玩家")
    npc = Character(name="测试NPC")

    # 设置位置
    location_manager.set_location(player.id, "qingyun_city")
    location_manager.set_location(npc.id, "qingyun_city")

    # 测试获取位置
    player_loc = location_manager.get_location(player.id)
    print(f"玩家位置: {player_loc}")
    assert player_loc == "qingyun_city"

    # 测试获取区域内实体
    entities = location_manager.get_entities_in_area("qingyun_city")
    print(f"青云城内实体数: {len(entities)}")
    assert len(entities) == 2

    # 测试移动
    success, message = location_manager.move_entity(player.id, "tiannan_market", player_level=1)
    print(f"移动结果: {success}, {message}")
    assert success is True

    # 测试探索
    result = location_manager.explore_area(player.id)
    print(f"探索成功: {result['success']}")

    print("✓ 位置管理器测试通过\n")


def test_event_system():
    """测试事件系统"""
    print("=== 测试事件系统 ===")

    # 创建事件系统
    event_system = EventSystem()

    # 测试默认事件
    print(f"注册的事件数: {len(event_system.events)}")
    assert len(event_system.events) > 0

    # 构建测试上下文
    context = {
        "game_time": 10,
        "location": "test_wild",
        "location_type": "wilderness",
        "player_level": 5,
        "last_action": "move",
    }

    # 检查触发器
    triggered = event_system.check_triggers(context)
    print(f"可触发事件数: {len(triggered)}")

    # 测试事件触发
    if triggered:
        event = triggered[0]
        result = event_system.trigger_event(event.id, context)
        if result:
            print(f"触发事件: {result['event'].name}")
            print(f"可用选项数: {len(result['choices'])}")

    print("✓ 事件系统测试通过\n")


def test_world_integration():
    """测试世界系统集成"""
    print("=== 测试世界系统集成 ===")

    # 创建完整的世界系统
    world_map = WorldMap()
    location_manager = LocationManager(world_map)
    event_system = EventSystem()

    # 加载默认地图
    from xwe.world.world_map import DEFAULT_MAP_DATA, Area, Region

    for region_data in DEFAULT_MAP_DATA["regions"]:
        region = Region.from_dict(region_data)
        world_map.add_region(region)

    for area_data in DEFAULT_MAP_DATA["areas"]:
        area = Area.from_dict(area_data)
        world_map.add_area(area)

    # 创建玩家
    player = Character(name="测试侠客")
    player.attributes.cultivation_level = 3

    # 设置初始位置
    location_manager.set_location(player.id, "qingyun_city")
    world_map.discover_area("qingyun_city")

    # 测试地区描述
    description = location_manager.get_area_description(player.id)
    print("当前位置描述:")
    print(description[:100] + "...")

    # 测试附近区域
    nearby = location_manager.get_nearby_areas(player.id)
    print(f"\n附近区域数: {len(nearby)}")
    for area in nearby[:3]:
        print(f"- {area['name']} (危险等级: {area['danger_level']})")

    # 测试旅行规划
    travel_info = location_manager.plan_travel(player.id, "ancient_ruins")
    if travel_info:
        print(f"\n到上古遗迹的距离: {travel_info.distance} 个区域")
        print(f"预计体力消耗: {travel_info.stamina_cost}")

    print("\n✓ 世界系统集成测试通过\n")


def main():
    """运行所有测试"""
    print("仙侠世界引擎 - 世界系统测试")
    print("=" * 50)
    print()

    try:
        test_world_map()
        test_location_manager()
        test_event_system()
        test_world_integration()

        print("=" * 50)
        print("所有世界系统测试通过！")
        print("\n提示：世界系统已经可以使用，支持以下功能：")
        print("- 地图导航和区域探索")
        print("- 位置管理和移动")
        print("- 随机事件触发")
        print("- 多区域连接和路径规划")

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
