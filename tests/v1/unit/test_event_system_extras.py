import json

from xwe.core.inventory import Inventory
from xwe.world.event_system import (
    EventChoice,
    EventCondition,
    EventSystem,
    EventTrigger,
    EventType,
    WorldEvent,
)


def test_choice_item_requirement():
    choice = EventChoice(
        id="c1",
        text="need item",
        requirements={"required_items": ["qi_gathering_pill"]},
    )
    inv = Inventory()
    ctx = {"inventory": inv}
    assert not choice.is_available(ctx)
    inv.add("qi_gathering_pill", 1)
    assert choice.is_available(ctx)


def test_load_events_from_file(tmp_path):
    data = {
        "events": [
            {
                "id": "tmp_evt",
                "name": "临时事件",
                "type": "encounter",
                "description": "desc",
                "conditions": [],
                "choices": [{"id": "c", "text": "do", "consequences": {}}],
            }
        ]
    }
    file = tmp_path / "events.json"
    file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    es = EventSystem()
    es.events.clear()
    es.load_events_from_file(str(file))
    assert "tmp_evt" in es.events


def test_random_item_reward(tmp_path):
    es = EventSystem()
    event = WorldEvent(
        id="reward_evt",
        name="奖励",
        type=EventType.ENCOUNTER,
        description="desc",
        choices=[EventChoice(id="open", text="open", consequences={"add_random_item": True})],
    )
    es.register_event(event)
    inv = Inventory()
    ctx = {"inventory": inv}
    res = es.handle_choice("reward_evt", "open", ctx)
    assert res["success"] is True
    assert inv.get_used_slots() == 1
    assert "obtained_item" in res
