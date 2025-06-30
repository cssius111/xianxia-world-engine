#!/usr/bin/env python3
"""测试角色抽卡API，验证返回的数据结构"""

import json
from run import app


def roll_api_request():
    """调用 /api/roll 接口并返回解析后的数据"""
    with app.test_client() as client:
        resp = client.post(
            "/api/roll",
            json={"mode": "random"},
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data.get("success"), f"API返回失败: {data}"
        return data


def test_roll_api():
    data = roll_api_request()
    character = data.get("character", {})

    # 验证必需字段
    for field in ["name", "gender", "background", "attributes"]:
        assert field in character, f"缺少必需字段: {field}"

    # 验证属性
    attrs = character.get("attributes", {})
    for attr in ["constitution", "comprehension", "spirit", "luck"]:
        assert attr in attrs, f"缺少属性: {attr}"
        value = attrs[attr]
        assert isinstance(value, (int, float)) and 1 <= value <= 10

    assert character["gender"] in ["male", "female"]
    assert character["background"] in ["poor", "merchant", "scholar", "martial"]

    destiny = data.get("destiny")
    if destiny:
        assert destiny.get("name"), "命格缺少名称"


def test_multiple_rolls():
    for _ in range(5):
        roll_api_request()
