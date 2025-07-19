"""Test suite for Stage 3: HeavenLawEngine MVP"""

import pytest
from unittest.mock import MagicMock, patch

from src.xwe.core.heaven_law_engine import HeavenLawEngine, ActionContext, ThunderTribulation
from src.xwe.core.character import Character, CharacterType
from src.xwe.core.attributes import CharacterAttributes
from src.xwe.core.combat import CombatSystem
from src.xwe.world.laws import WorldLaw


def create_character(name: str, realm: str) -> Character:
    """Helper function to create a character with specific realm."""
    character = Character(
        id=f"char_{name}",
        name=name,
        character_type=CharacterType.PLAYER if name == "player" else CharacterType.NPC
    )
    
    character.attributes = CharacterAttributes()
    character.attributes.realm_name = realm
    character.attributes.current_health = 100
    character.attributes.max_health = 100
    
    return character


class TestHeavenLawEngine:
    """Test HeavenLawEngine functionality."""
    
    def test_heaven_law_engine_initialization(self):
        """Test that HeavenLawEngine initializes with laws."""
        engine = HeavenLawEngine()
        
        assert engine.laws is not None
        assert "CROSS_REALM_KILL" in engine.laws
        assert isinstance(engine.laws["CROSS_REALM_KILL"], WorldLaw)
    
    def test_realm_index_calculation(self):
        """Test realm index calculation."""
        engine = HeavenLawEngine()
        
        assert engine.get_realm_index("炼气期") == 1
        assert engine.get_realm_index("筑基期") == 2
        assert engine.get_realm_index("金丹期") == 3
        assert engine.get_realm_index("元婴期") == 4
        assert engine.get_realm_index("化神期") == 5
        assert engine.get_realm_index("合体期") == 6
        assert engine.get_realm_index("大乘期") == 7
        assert engine.get_realm_index("未知境界") == 0
    
    def test_cross_realm_kill_blocked(self):
        """Test that cross-realm kill attempts are blocked."""
        engine = HeavenLawEngine()
        
        # Create high realm attacker and low realm target
        high_realm = create_character("high", "金丹期")  # index 3
        low_realm = create_character("low", "炼气期")     # index 1
        
        ctx = ActionContext()
        
        # Attempt cross-realm kill (3 - 1 = 2, which equals threshold)
        engine.enforce(high_realm, low_realm, ctx)
        
        # Should be blocked
        assert ctx.cancelled is True
        assert ctx.reason is not None
        assert "天道不容" in ctx.reason
        assert len(ctx.events) == 1
        assert isinstance(ctx.events[0], ThunderTribulation)
        assert ctx.events[0].severity == "moderate"
    
    def test_severe_cross_realm_punishment(self):
        """Test severe punishment for large realm gap."""
        engine = HeavenLawEngine()
        
        # Create very high realm attacker
        high_realm = create_character("high", "大乘期")  # index 7
        low_realm = create_character("low", "炼气期")     # index 1
        
        ctx = ActionContext()
        
        # Large gap (7 - 1 = 6)
        engine.enforce(high_realm, low_realm, ctx)
        
        assert ctx.cancelled is True
        assert len(ctx.events) == 1
        assert ctx.events[0].severity == "severe"
    
    def test_allowed_realm_attack(self):
        """Test that attacks within allowed realm gap are not blocked."""
        engine = HeavenLawEngine()
        
        # Small realm difference
        attacker = create_character("attacker", "筑基期")  # index 2
        target = create_character("target", "炼气期")      # index 1
        
        ctx = ActionContext()
        
        # Gap is only 1, below threshold of 2
        engine.enforce(attacker, target, ctx)
        
        assert ctx.cancelled is False
        assert len(ctx.events) == 0
    
    def test_reverse_realm_attack_allowed(self):
        """Test that lower realm attacking higher realm is allowed."""
        engine = HeavenLawEngine()
        
        # Low realm attacks high realm
        low_realm = create_character("low", "炼气期")    # index 1
        high_realm = create_character("high", "金丹期")  # index 3
        
        ctx = ActionContext()
        
        # Negative gap (-2), should be allowed
        engine.enforce(low_realm, high_realm, ctx)
        
        assert ctx.cancelled is False
        assert len(ctx.events) == 0
    
    def test_law_disabled(self):
        """Test that disabled laws are not enforced."""
        engine = HeavenLawEngine()
        
        # Disable the law
        engine.laws["CROSS_REALM_KILL"].enabled = False
        
        high_realm = create_character("high", "金丹期")
        low_realm = create_character("low", "炼气期")
        
        ctx = ActionContext()
        engine.enforce(high_realm, low_realm, ctx)
        
        # Should not be blocked when law is disabled
        assert ctx.cancelled is False
        assert len(ctx.events) == 0
    
    def test_thunder_tribulation_damage(self):
        """Test ThunderTribulation event damage calculation."""
        from src.xwe.core.status import StatusEffectManager
        
        character = create_character("test", "金丹期")
        character.attributes.current_health = 1000
        character.status_effects = StatusEffectManager()
        
        # Test minor tribulation
        minor = ThunderTribulation(character, "minor")
        result = minor.apply()
        assert character.attributes.current_health == 900  # 1000 - 100
        assert "被一道细小的天雷击中" in result
        
        # Test severe tribulation
        character.attributes.current_health = 10000
        severe = ThunderTribulation(character, "severe")
        result = severe.apply()
        assert character.attributes.current_health == 1  # Minimum 1 HP
        assert "九道天雷轰然而下" in result
        
        # Check scorched status
        assert character.status_effects.has_effect('scorched')


class TestCombatSystemIntegration:
    """Test CombatSystem integration with HeavenLawEngine."""
    
    def test_combat_system_blocks_cross_realm_kill(self):
        """Test that CombatSystem properly blocks cross-realm attacks."""
        heaven_law = HeavenLawEngine()
        combat_system = CombatSystem(None, None, heaven_law)
        
        # Create characters
        attacker = create_character("高手", "化神期")  # High realm
        defender = create_character("新手", "炼气期")   # Low realm
        
        # Attempt attack
        result = combat_system.attack(attacker, defender)
        
        # Should be blocked
        assert result.success is False
        assert "天道不容" in result.message
        # The thunder message is in a separate line
        assert "天雷" in result.message or "雷" in result.message
    
    def test_combat_system_allows_normal_attack(self):
        """Test that CombatSystem allows attacks within realm limits."""
        heaven_law = HeavenLawEngine()
        combat_system = CombatSystem(None, None, heaven_law)
        
        # Create characters with small realm gap
        attacker = create_character("player", "筑基期")
        defender = create_character("enemy", "炼气期")
        
        # Mock the _execute_attack method to avoid full combat simulation
        with patch.object(combat_system, '_execute_attack') as mock_execute:
            mock_execute.return_value = MagicMock(
                damage_dealt={defender.id: MagicMock(damage=10, is_evaded=False, is_critical=False)},
                message=""
            )
            
            result = combat_system.attack(attacker, defender)
            
            # Should not be blocked
            assert mock_execute.called
            assert "天道不容" not in result.message


def test_forbidden_art_detection():
    """Test forbidden art detection."""
    engine = HeavenLawEngine()
    character = create_character("player", "金丹期")
    character.karma = 100
    
    ctx = ActionContext()
    
    # Test forbidden art
    engine.check_forbidden_art(character, "血魔大法", ctx)
    
    # Should trigger backlash
    assert len(ctx.events) == 1
    assert ctx.events[0].name == "ForbiddenArtBacklash"
    
    # Should reduce karma if law is enabled
    if engine.laws.get("FORBIDDEN_ARTS", WorldLaw("", enabled=False)).enabled:
        assert character.karma == 0  # 100 - 100 penalty


def test_realm_breakthrough_tribulation():
    """Test realm breakthrough tribulation requirement."""
    engine = HeavenLawEngine()
    character = create_character("player", "炼气期")
    
    ctx = ActionContext()
    
    # Test breakthrough to major realm
    engine.check_breakthrough(character, "筑基期", ctx)
    
    # Should require tribulation if law is enabled
    if engine.laws.get("REALM_BREAKTHROUGH", WorldLaw("", enabled=False)).enabled:
        assert len(ctx.events) == 1
        assert "BreakthroughTribulation" in ctx.events[0].name


@pytest.fixture
def mock_game():
    """Create a mock game instance."""
    from src.xwe.core.game_core import GameCore
    game = GameCore()
    game.heaven_law_engine = HeavenLawEngine()
    return game


def test_full_integration(mock_game):
    """Test full integration with game core."""
    # Create test characters
    low_player = create_character("低境界玩家", "炼气期")
    high_npc = create_character("高境界NPC", "大乘期")
    
    mock_game.game_state.player = low_player
    mock_game.game_state.npcs[high_npc.id] = high_npc
    
    # Low realm attacking high realm should work
    ctx = ActionContext()
    mock_game.heaven_law_engine.enforce(low_player, high_npc, ctx)
    
    assert not ctx.cancelled
    assert len(ctx.events) == 0
    
    # High realm attacking low realm should be blocked
    ctx2 = ActionContext()
    mock_game.heaven_law_engine.enforce(high_npc, low_player, ctx2)
    
    assert ctx2.cancelled
    assert len(ctx2.events) > 0
    assert any(isinstance(e, ThunderTribulation) for e in ctx2.events)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
