# initial_fate.py
"""Determine the starting fate node for a new character."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from xwe.core.character import Character
from xwe.core.nlp import LLMClient

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "event_selector.txt"


def load_prompt() -> str:
    """Load the event selector prompt template."""
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def select_initial_fate(character: Character, events: List[Dict[str, Any]]) -> str:
    """Use DeepSeek to pick the initial fate node.

    The returned string is the selected event id. If the API call fails,
    the first event id from the list will be returned as a fallback.
    """
    prompt_tmpl = load_prompt()
    prompt = prompt_tmpl.replace("{{ character_json }}", json.dumps(character.to_dict(), ensure_ascii=False))
    prompt = prompt.replace("{{ events_json }}", json.dumps(events, ensure_ascii=False))

    llm = LLMClient()
    result = llm.chat(prompt).strip()
    return result if result else events[0]["id"]

