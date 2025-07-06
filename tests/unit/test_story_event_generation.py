import random
import pytest
from src.xwe.features.narrative_system import NarrativeSystem


def choose_highest(events, weights):
    idx = weights.index(max(weights))
    return [events[idx]]


def test_generate_event_by_style(monkeypatch):
    ns = NarrativeSystem()
    monkeypatch.setattr(random, "choices", choose_highest)
    aggressive = ns.generate_story_event({}, player_style="aggressive")
    curious = ns.generate_story_event({}, player_style="curious")
    assert aggressive["id"] == "demon_attack"
    assert curious["id"] == "ancient_ruins"


def test_generate_event_environment(monkeypatch):
    ns = NarrativeSystem()
    monkeypatch.setattr(random, "choices", choose_highest)
    env = {"lingqi": 8, "comprehension": 3}
    event = ns.generate_story_event({}, player_style="aggressive", environment=env)
    assert "灵气充沛" in event["description"]
    assert "悟性受到压制" in event["description"]
