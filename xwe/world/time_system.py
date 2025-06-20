from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class TimeSystem:
    """Game time management based on YAML rules."""

    def __init__(self, rules_path: Optional[Path] = None) -> None:
        if rules_path is None:
            rules_path = (
                Path(__file__).resolve().parents[1] / "data" / "restructured" / "time_rules.yaml"
            )
        with open(rules_path, "r", encoding="utf-8") as f:
            self.rules: Dict[str, Any] = yaml.safe_load(f)

    def get_time_cost(self, action: str, modifiers: Optional[Dict[str, str]] = None) -> float:
        """Calculate time cost for an action with optional modifiers."""
        base_cost = self.rules.get("default_time_cost", {}).get(
            action,
            self.rules.get("deepseek_integration", {})
            .get("fallback_behavior", {})
            .get("default_cost", 1.0),
        )
        if modifiers:
            for mod_type, mod_value in modifiers.items():
                table = self.rules.get("time_modifiers", {}).get(mod_type, {})
                if mod_value in table:
                    base_cost *= table[mod_value]
        return float(base_cost)

    def advance_time(
        self, action: str, game_state: Any, modifiers: Optional[Dict[str, str]] = None
    ) -> float:
        """Advance game time for a given action."""
        cost = self.get_time_cost(action, modifiers)
        fatigue_cfg = self.rules.get("special_rules", {}).get("fatigue_system", {})
        if fatigue_cfg.get("enabled"):
            threshold = fatigue_cfg.get("threshold_hours", 0)
            penalty = fatigue_cfg.get("penalty_multiplier", 1.0)
            if action in {"rest", "meditation"}:
                game_state.active_hours = 0
            else:
                if game_state.active_hours + cost > threshold:
                    cost *= penalty
                game_state.active_hours += cost
        game_state.game_time += cost
        return cost
