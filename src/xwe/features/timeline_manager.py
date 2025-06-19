"""Timeline manager for world events."""

from __future__ import annotations

import json
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from xwe.features.intelligence_system import IntelligenceSystem, IntelItem


@dataclass(order=True)
class GameDate:
    """Simple in-game date representation."""

    year: int = 0
    month: int = 0
    day: int = 0

    DAYS_PER_MONTH = 30
    MONTHS_PER_YEAR = 12

    def to_days(self) -> int:
        return self.year * self.MONTHS_PER_YEAR * self.DAYS_PER_MONTH + self.month * self.DAYS_PER_MONTH + self.day

    @classmethod
    def from_days(cls, total: int) -> "GameDate":
        year, rem = divmod(total, cls.MONTHS_PER_YEAR * cls.DAYS_PER_MONTH)
        month, day = divmod(rem, cls.DAYS_PER_MONTH)
        return cls(year=year, month=month, day=day)

    def add_days(self, days: int) -> None:
        total = self.to_days() + days
        new_date = self.from_days(total)
        self.year = new_date.year
        self.month = new_date.month
        self.day = new_date.day

    @classmethod
    def from_string(cls, value: str) -> "GameDate":
        pattern = r"Y\+(?P<y>\d+)\s*M\+(?P<m>\d+)\s*D\+(?P<d>\d+)"
        match = re.match(pattern, value.strip())
        if not match:
            raise ValueError(f"Invalid date format: {value}")
        year = int(match.group("y"))
        month = int(match.group("m"))
        day = int(match.group("d"))
        return cls(year, month, day)


class TimelineManager:
    """Load timeline events and advance in-game time."""

    def __init__(self,
                 events_path: Optional[Path] = None,
                 intelligence_system: Optional[IntelligenceSystem] = None) -> None:
        if events_path is None:
            events_path = Path(__file__).resolve().parents[1] / "data" / "restructured" / "timeline_events.json"
        with open(events_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.events: List[Dict[str, Any]] = data.get("timeline_events", [])
        self.current_date = GameDate()
        self.intelligence_system = intelligence_system

    def advance_time(self, days: int = 1) -> List[Dict[str, Any]]:
        """Advance time and return triggered events."""
        self.current_date.add_days(days)
        triggered: List[Dict[str, Any]] = []
        for event in self.events:
            if event.get("_triggered"):
                continue
            event_date = GameDate.from_string(event["trigger_date"])
            if self.current_date.to_days() >= event_date.to_days():
                event["_triggered"] = True
                triggered.append(event)
                if self.intelligence_system:
                    news = IntelItem(
                        id=event.get("event_id", ""),
                        title=event.get("name", ""),
                        content=event.get("description", ""),
                        ttl=86400,
                        raw_event=event,
                    )
                    self.intelligence_system.add_global_news(news)
        return triggered
