
# Add project root to path

from xwe.world import WorldMap, LocationManager
from xwe.world.world_map import Area, Region, AreaType


def test_get_area_info_keys_and_string_id():
    wm = WorldMap()
    area = Area.from_dict({
        "id": 1,
        "name": "数字区域",
        "type": "city",
        "description": "测试",
        "connected_areas": [],
        "parent_region": 0
    })
    wm.add_area(area)
    info = wm.get_area_info("1")

    assert all(isinstance(k, str) for k in info.keys())
    assert info["id"] == "1"


def test_get_regions_info_string_id():
    wm = WorldMap()
    region = Region.from_dict({
        "id": 2,
        "name": "数字州",
        "description": "desc",
        "sub_areas": []
    })
    wm.add_region(region)
    info = wm.get_regions_info()[0]

    assert all(isinstance(k, str) for k in info.keys())
    assert info["id"] == "2"


def test_get_nearby_areas_ids_are_strings():
    wm = WorldMap()
    area1 = Area.from_dict({
        "id": 1,
        "name": "A",
        "type": "city",
        "description": "",
        "connected_areas": [2]
    })
    area2 = Area.from_dict({
        "id": 2,
        "name": "B",
        "type": "city",
        "description": "",
        "connected_areas": [1]
    })
    wm.add_area(area1)
    wm.add_area(area2)

    lm = LocationManager(wm)
    lm.set_location("p", "1")
    nearby = lm.get_nearby_areas("p")
    assert nearby
    assert nearby[0]["id"] == "2"
    assert all(isinstance(k, str) for k in nearby[0].keys())

