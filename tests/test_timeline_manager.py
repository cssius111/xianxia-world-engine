from pathlib import Path

from xwe.features.timeline_manager import TimelineManager
from xwe.features.intelligence_system import IntelligenceSystem


def test_events_trigger_by_date():
    intel = IntelligenceSystem()
    tm = TimelineManager(intelligence_system=intel)

    # Advance one month (30 days)
    triggered = tm.advance_time(30)
    ids = [e["event_id"] for e in triggered]
    assert "sect_recruit_qingyun" in ids
    assert intel.global_news[0].id == "sect_recruit_qingyun"

    # Advance another 45 days to reach 75 days total
    triggered = tm.advance_time(45)
    ids = [e["event_id"] for e in triggered]
    assert "blood_moon_tide" in ids
    assert intel.global_news[-1].id == "blood_moon_tide"
