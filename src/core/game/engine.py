from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from src.xwe.core.achievement_system import AchievementSystem
from src.xwe.core.ai import AIController
from src.xwe.core.attributes import AttributeSystem
from src.xwe.core.character import Character, CharacterType
from src.xwe.core.combat import CombatAction, CombatActionType, CombatState, CombatSystem
from src.xwe.core.command_parser import CommandParser, CommandType, ParsedCommand
from src.xwe.core.command_router import CommandPriority, CommandRouter
from src.xwe.core.data_loader import DataLoader
from src.xwe.core.heaven_law_engine import HeavenLawEngine
from src.xwe.core.immersive_event_system import EventType, ImmersiveEventSystem, SpecialEventHandler
from src.xwe.core.inventory import Inventory
from src.xwe.core.item_system import item_system
from src.xwe.core.nlp import NLPProcessor
from src.xwe.core.roll_system import CharacterRoller
from src.xwe.core.skills import SkillSystem
from src.xwe.core.status_manager import StatusDisplayManager
from src.xwe.engine.expression import ExpressionParser
from src.xwe.world import AreaType, EventSystem, LocationManager, TimeSystem, WorldMap

from .state import GameState
from .combat import CombatMixin
from .cultivation import CultivationMixin

logger = logging.getLogger(__name__)


class GameCore(CombatMixin, CultivationMixin):
    """简化版游戏核心，保留必要接口以满足测试。"""

    def __init__(self, data_path: Union[str, Path] | None = None, game_mode: str = "player") -> None:
        if getattr(self, "_initialized", False):
            logger.debug("GameCore 已初始化，跳过")
            return
        self._initialized = True

        self.data_loader = DataLoader(data_path)
        self.parser = ExpressionParser()
        self.attribute_system = AttributeSystem(self.parser)
        self.skill_system = SkillSystem()
        self.heaven_law_engine = HeavenLawEngine()
        self.combat_system = CombatSystem(self.skill_system, self.parser, self.heaven_law_engine)
        self.ai_controller = AIController(self.skill_system)
        self.command_parser = CommandParser()
        self.nlp_processor = NLPProcessor()
        self.world_map = WorldMap()
        self.location_manager = LocationManager(self.world_map)
        self.event_system = EventSystem()
        self.time_system = TimeSystem()
        from src.xwe.npc import DialogueSystem, NPCManager

        self.dialogue_system = DialogueSystem()
        self.npc_manager = NPCManager(self.dialogue_system)
        self.character_roller = CharacterRoller()
        self.status_manager = StatusDisplayManager()
        self.achievement_system = AchievementSystem()
        self.command_router = CommandRouter()
        self.immersive_event_system = ImmersiveEventSystem(self.output)
        self.game_state = GameState(game_mode=game_mode)
        self.game_mode = game_mode
        self.running = False
        self.output_buffer: List[str] = []
        self.current_roll_result = None
        self.stats = {
            "enemies_defeated": 0,
            "win_streak": 0,
            "areas_explored": set(),
            "cultivation_time": 0,
            "gold": 0,
        }
        logger.info("游戏核心初始化完成")

    # --- 简化的方法，仅保留接口 ---

    def start_new_game(self, player_name: str = "无名侠客") -> None:
        self.running = True
        self.game_state.player = Character(name=player_name, character_type=CharacterType.PLAYER)
        self.output("=== 仙侠世界 ===")

    def process_command(self, input_text: str) -> None:  # pragma: no cover - placeholder
        pass

    def output(self, text: str) -> None:
        self.output_buffer.append(text)

    def get_output(self) -> List[str]:
        out = self.output_buffer.copy()
        self.output_buffer.clear()
        return out

    def run(self) -> Any:  # pragma: no cover - placeholder
        self.running = True
        return None


class EnhancedGameCore(GameCore):
    """Placeholder for compatibility."""

    def __init__(self, data_path: Optional[str] = None, game_mode: str = "player"):
        super().__init__(data_path, game_mode)
        self._enhanced_features: Dict[str, bool] = {
            "auto_combat": False,
            "quick_travel": False,
            "enhanced_ui": True,
        }

    def enable_feature(self, feature: str) -> bool:
        if feature in self._enhanced_features:
            self._enhanced_features[feature] = True
            return True
        return False

    def disable_feature(self, feature: str) -> bool:
        if feature in self._enhanced_features:
            self._enhanced_features[feature] = False
            return True
        return False

    def get_feature_status(self, feature: str) -> Optional[bool]:
        return self._enhanced_features.get(feature)


def create_enhanced_game(game_mode: str = "player") -> GameCore:
    game = GameCore(game_mode=game_mode)
    return game
