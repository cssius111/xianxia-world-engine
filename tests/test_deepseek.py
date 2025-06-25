import os
import random
import pytest

from run import app


COMMANDS = [
    "探索周围",
    "打开背包",
    "查看状态",
    "修炼",
    "前往城主府",
    "使用回血丹",
    "交谈",
    "帮助",
    "保存",
    "退出",
    "移动 北",
    "去南边",
    "购买丹药",
    "挑战敌人",
    "学习技能",
]


@pytest.mark.skipif(not os.getenv("DEEPSEEK_API_KEY"), reason="DEEPSEEK_API_KEY not set")
def test_deepseek_commands():
    random_commands = [random.choice(COMMANDS) for _ in range(10)]
    with app.test_client() as client:
        for cmd in random_commands:
            resp = client.post("/command", json={"text": cmd}, content_type="application/json")
            assert resp.status_code == 200
            data = resp.get_json()
            assert "parsed_command" in data
            assert data["parsed_command"].get("handler")
