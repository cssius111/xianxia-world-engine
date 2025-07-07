import importlib.util
from pathlib import Path
from unittest import mock
from src.xwe.core.combat import CombatResult


def _load_run_module():
    spec = importlib.util.spec_from_file_location("run", Path("scripts/run.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore
    return module


def test_attack_command():
    run = _load_run_module()
    app = run.app
    client = app.test_client()

    mock_res = CombatResult(True, "你对木桩造成了10点伤害")
    with mock.patch("src.xwe.core.combat.CombatSystem.attack", return_value=mock_res):
        resp = client.post("/command", json={"command": "攻击 木桩"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert "木桩" in data["result"]

