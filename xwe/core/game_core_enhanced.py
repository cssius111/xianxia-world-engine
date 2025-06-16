"""Enhanced game core helpers."""

from .game_core import GameCore
from ..features.html_output import HtmlGameLogger
from ..features.enhanced_output import EnhancedGameOutput

# 可选系统
try:
    from ..features.ai_personalization import AIPersonalization
except Exception:  # pragma: no cover - optional dependency
    AIPersonalization = None  # type: ignore

try:
    from ..features.community_system import CommunitySystem
except Exception:  # pragma: no cover - optional dependency
    CommunitySystem = None  # type: ignore

try:
    from ..features.narrative_system import NarrativeSystem
except Exception:  # pragma: no cover - optional dependency
    NarrativeSystem = None  # type: ignore

try:
    from ..features.technical_ops import TechnicalOps
except Exception:  # pragma: no cover - optional dependency
    TechnicalOps = None  # type: ignore

try:
    from .cultivation_system import CultivationSystem
except Exception:  # pragma: no cover - optional dependency
    CultivationSystem = None  # type: ignore


def create_enhanced_game(log_file: str = "game_log.html", *, game_mode: str = "player") -> GameCore:
    """Create a ``GameCore`` instance with enhanced output and optional systems."""
    game = GameCore(game_mode=game_mode)

    # Integrate enhanced HTML output
    html_logger = HtmlGameLogger(log_file)
    output_handler = EnhancedGameOutput(html_logger)

    def enhanced_print(text: str, category: str = "system", **_kwargs) -> None:
        output_handler.output(str(text), category)

    game.print = enhanced_print  # type: ignore[attr-defined]
    game.output = output_handler  # type: ignore[attr-defined]
    game.html_logger = html_logger  # type: ignore[attr-defined]

    # Attach optional systems if available
    if CultivationSystem:
        game.cultivation_system = CultivationSystem()
    if NarrativeSystem:
        game.narrative_system = NarrativeSystem()
    if AIPersonalization:
        game.ai_personalization = AIPersonalization()
    if CommunitySystem:
        game.community_system = CommunitySystem()
    if TechnicalOps:
        game.technical_ops = TechnicalOps()

    return game
