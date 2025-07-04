"""Map and location API routes."""

from flask import Blueprint, jsonify

map_bp = Blueprint('map', __name__, url_prefix='/api')


@map_bp.get('/map')
def get_map_data():
    """Get world map data."""
    data = {
        "regions": [
            {
                "id": "region_001",
                "name": "青云山脉",
                "description": "云雾缭绕的仙山",
                "danger_level": 1,
                "locations": [
                    {
                        "id": "loc_001",
                        "name": "青云城",
                        "description": "繁华的修真城市",
                        "discovered": True,
                        "accessible": True,
                        "type": "city"
                    },
                    {
                        "id": "loc_002",
                        "name": "青云峰",
                        "description": "青云宗山门",
                        "discovered": True,
                        "accessible": True,
                        "type": "sect"
                    },
                    {
                        "id": "loc_003",
                        "name": "灵兽森林",
                        "description": "危机四伏的森林",
                        "discovered": False,
                        "accessible": False,
                        "type": "wilderness"
                    }
                ]
            },
            {
                "id": "region_002",
                "name": "血月荒原",
                "description": "妖兽横行的荒芜之地",
                "danger_level": 3,
                "locations": [
                    {
                        "id": "loc_004",
                        "name": "血月城",
                        "description": "魔修聚集地",
                        "discovered": False,
                        "accessible": False,
                        "type": "city"
                    }
                ]
            }
        ],
        "current_location": "loc_001"
    }
    return jsonify({"success": True, "data": data})


@map_bp.get('/map/locations/<location_id>')
def get_location_detail(location_id: str):
    """Get detailed information about a specific location."""
    # TODO: Implement database lookup
    # Mock data for now
    locations = {
        "loc_001": {
            "id": "loc_001",
            "name": "青云城",
            "description": "繁华的修真城市，各路修士云集于此",
            "services": ["shop", "auction", "inn", "teleport"],
            "npcs": ["城主", "灵宝阁掌柜", "神秘商人"],
            "quests_available": 3
        }
    }
    
    location = locations.get(location_id)
    if location:
        return jsonify({"success": True, "location": location})
    
    return jsonify({"success": False, "error": "Location not found"}), 404
