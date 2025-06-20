import pytest

from xwe.npc import DialogueSystem, NPCBehavior, NPCManager, NPCProfile
from xwe.world import Area, Region, WorldMap
from xwe.world.world_map import DEFAULT_MAP_DATA


def build_world_map():
    wm = WorldMap()
    for r in DEFAULT_MAP_DATA["regions"]:
        wm.add_region(Region.from_dict(r))
    for a in DEFAULT_MAP_DATA["areas"]:
        wm.add_area(Area.from_dict(a))
    return wm


def test_wander_behavior_moves_between_connected_areas():
    dialogue_system = DialogueSystem()
    wm = build_world_map()
    npc_manager = NPCManager(dialogue_system)
    npc_manager.world_map = wm

    profile = NPCProfile(
        id="npc_wander",
        name="游侠",
        behavior=NPCBehavior.WANDER,
        home_location="qingyun_city",
    )
    npc_manager.register_npc_profile(profile)
    npc_manager.create_npc_character("npc_wander")

    npc_manager.update_npc_behavior(game_time=10)
    loc = npc_manager.get_npc_location("npc_wander")
    assert loc in {"tiannan_market", "yellow_maple_valley", "wasteland_entrance"}


def test_schedule_behavior_follows_time_slots():
    dialogue_system = DialogueSystem()
    wm = build_world_map()
    npc_manager = NPCManager(dialogue_system)
    npc_manager.world_map = wm

    schedule = {"8": "tiannan_market", "18": "qingyun_city"}
    profile = NPCProfile(
        id="npc_scheduled",
        name="巡逻者",
        behavior=NPCBehavior.SCHEDULE,
        home_location="qingyun_city",
        extra_data={"schedule": schedule},
    )
    npc_manager.register_npc_profile(profile)
    npc_manager.create_npc_character("npc_scheduled")

    npc_manager.update_npc_behavior(game_time=8)
    assert npc_manager.get_npc_location("npc_scheduled") == "tiannan_market"

    npc_manager.update_npc_behavior(game_time=12)
    assert npc_manager.get_npc_location("npc_scheduled") == "tiannan_market"

    npc_manager.update_npc_behavior(game_time=18)
    assert npc_manager.get_npc_location("npc_scheduled") == "qingyun_city"
