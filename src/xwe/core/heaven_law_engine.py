"""Heaven Law Engine - Enforces world-level laws and triggers divine punishment."""

from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Optional, List

from src.world.laws import load_world_laws, WorldLaw

if TYPE_CHECKING:
    from src.xwe.core.character import Character
    from src.xwe.core.game_state import GameState

log = logging.getLogger(__name__)


class ActionContext:
    """Context for action execution with law enforcement."""
    
    def __init__(self):
        self.cancelled: bool = False
        self.events: List[Event] = []
        self.reason: Optional[str] = None
        self.metadata: dict = {}


class Event:
    """Base class for game events."""
    
    def __init__(self, name: str):
        self.name = name
    
    def apply(self) -> str:
        """Apply the event and return a description."""
        return f"Event {self.name} occurred"


class ThunderTribulation(Event):
    """Thunder tribulation event - divine punishment from heaven."""
    
    def __init__(self, actor: "Character", severity: str = "minor"):
        super().__init__("ThunderTribulation")
        self.actor = actor
        self.severity = severity
    
    def apply(self) -> str:
        """Apply thunder damage to the actor."""
        # Damage based on severity
        damage_map = {
            "minor": 100,
            "moderate": 500,
            "severe": 9999,
            "fatal": 99999
        }
        
        dmg = damage_map.get(self.severity, 500)
        
        # Apply damage but don't kill (minimum 1 HP)
        if hasattr(self.actor, 'attributes'):
            old_hp = self.actor.attributes.current_health
            new_hp = max(old_hp - dmg, 1)
            self.actor.attributes.current_health = new_hp
            
            # Add scorched status effect
            if hasattr(self.actor, 'status_effects'):
                from src.xwe.core.status import StatusEffect, StatusType
                scorched_effect = StatusEffect(
                    id='scorched',
                    name='天雷灼伤',
                    description='被天雷击中，全属性降低',
                    status_type=StatusType.DEBUFF,
                    duration=10,
                    modifiers={
                        'attack_power': -0.2,  # -20% attack
                        'defense': -0.2,       # -20% defense
                        'agility': -0.2        # -20% agility
                    }
                )
                self.actor.status_effects.add_effect(scorched_effect)
        
        messages = {
            "minor": f"{self.actor.name}被一道细小的天雷击中！",
            "moderate": f"{self.actor.name}被天雷劈中，浑身焦黑！",
            "severe": f"{self.actor.name}遭受天道惩罚，九道天雷轰然而下！",
            "fatal": f"{self.actor.name}触犯天道，毁灭性的天雷将其笼罩！"
        }
        
        return messages.get(self.severity, f"{self.actor.name} was struck by heavenly lightning!")


class HeavenLawEngine:
    """Central authority that enforces world-level laws before/after actions."""
    
    def __init__(self):
        self.laws = load_world_laws()
        log.info(f"HeavenLawEngine initialized with {len(self.laws)} laws")
    
    def get_realm_index(self, realm_name: str) -> int:
        """Get numerical index for a realm name."""
        realm_order = [
            "凡人", "炼气期", "筑基期", "金丹期", 
            "元婴期", "化神期", "合体期", "大乘期", "渡劫期"
        ]
        
        try:
            return realm_order.index(realm_name)
        except ValueError:
            # Default to 0 if realm not found
            return 0
    
    def enforce(self, actor: "Character", target: Optional["Character"], ctx: ActionContext) -> None:
        """Raise ThunderTribulation or modify ctx according to active laws.
        
        Args:
            actor: The character performing the action
            target: The target of the action (if any)
            ctx: Action context to modify
        """
        # Check CROSS_REALM_KILL law
        law = self.laws.get("CROSS_REALM_KILL")
        if not (law and law.enabled):
            return
        
        if not target:
            return
        
        # Get realm indices
        actor_realm = getattr(actor.attributes, 'realm_name', '炼气期') if hasattr(actor, 'attributes') else '炼气期'
        target_realm = getattr(target.attributes, 'realm_name', '炼气期') if hasattr(target, 'attributes') else '炼气期'
        
        actor_idx = self.get_realm_index(actor_realm)
        target_idx = self.get_realm_index(target_realm)
        
        # Calculate realm difference (positive means actor is higher realm)
        diff = actor_idx - target_idx
        threshold = law.params.get("max_gap", 2)
        
        # Check if violating the law (higher realm attacking much lower realm)
        if diff >= threshold:
            log.info(
                f"HeavenLawEngine: cross-realm kill attempt blocked "
                f"({actor.name}[{actor_realm}] → {target.name}[{target_realm}])"
            )
            
            ctx.cancelled = True
            ctx.reason = f"天道不容！{actor_realm}修士不可肆意斩杀{target_realm}修士！"
            
            # Determine severity based on realm gap
            if diff >= law.params.get("severity_threshold", 3):
                severity = "severe"
            else:
                severity = "moderate"
            
            ctx.events.append(ThunderTribulation(actor=actor, severity=severity))
    
    def check_forbidden_art(self, actor: "Character", skill_name: str, ctx: ActionContext) -> None:
        """Check if a skill is forbidden and apply penalties."""
        law = self.laws.get("FORBIDDEN_ARTS")
        if not (law and law.enabled):
            return
        
        # List of forbidden arts (could be loaded from data)
        forbidden_skills = ["血魔大法", "噬魂术", "九幽冥火", "天魔解体大法"]
        
        if skill_name in forbidden_skills:
            log.info(f"HeavenLawEngine: forbidden art detected - {skill_name}")
            
            # Apply backlash
            ctx.events.append(Event("ForbiddenArtBacklash"))
            
            # Add karma penalty
            if hasattr(actor, 'karma'):
                penalty = law.params.get("karma_penalty", 100)
                actor.karma -= penalty
    
    def check_breakthrough(self, actor: "Character", new_realm: str, ctx: ActionContext) -> None:
        """Check if realm breakthrough requires tribulation."""
        law = self.laws.get("REALM_BREAKTHROUGH")
        if not (law and law.enabled):
            return
        
        major_realms = law.params.get("major_realms", [])
        if new_realm in major_realms:
            difficulty = law.params.get("tribulation_difficulty", {}).get(new_realm, 1)
            log.info(f"HeavenLawEngine: realm breakthrough tribulation required for {new_realm}")
            
            # Create breakthrough tribulation event
            ctx.events.append(Event(f"BreakthroughTribulation_Level{difficulty}"))
