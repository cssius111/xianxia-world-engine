import pytest
from xwe.features.narrative_system import (
    NarrativeSystem,
    StoryNode,
    StoryPhase,
)


def create_simple_narrative_system():
    ns = NarrativeSystem()
    ns.story_arcs["test_arc"] = {}
    ns.story_nodes["test_arc_start"] = StoryNode(
        id="test_arc_start",
        phase=StoryPhase.INTRODUCTION,
        content="start",
        choices=[{"text": "go", "next": "next_node"}]
    )
    ns.story_nodes["next_node"] = StoryNode(
        id="next_node",
        phase=StoryPhase.RISING_ACTION,
        content="next"
    )
    return ns


def test_start_story_arc_invalid():
    ns = NarrativeSystem()
    assert ns.start_story_arc("p1", "unknown") is None


def test_story_flow():
    ns = create_simple_narrative_system()
    node = ns.start_story_arc("p1", "test_arc")
    assert node is not None and node.id == "test_arc_start"

    next_node = ns.make_choice("p1", 0)
    assert next_node is not None and next_node.id == "next_node"


def test_dynamic_quest_and_progress():
    ns = NarrativeSystem()
    quest = ns.generate_dynamic_quest(1, "village")
    assert quest.id in ns.quests

    count = quest.objectives[0].get("count", 1)
    assert not ns.update_quest_progress(quest.id, 0, count - 1)
    assert ns.update_quest_progress(quest.id, 0, 1)
    assert ns.quests[quest.id].is_completed


def test_story_summary():
    ns = create_simple_narrative_system()
    ns.start_story_arc("p1", "test_arc")
    ns.make_choice("p1", 0)
    quest = ns.generate_dynamic_quest(1, "village")
    count = quest.objectives[0].get("count", 1)
    ns.update_quest_progress(quest.id, 0, count)

    summary = ns.get_story_summary("p1")
    assert summary["total_choices"] == 1
    assert summary["completed_quests"] >= 1
