"""Flask application factory and core utilities."""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
from flask import (
    Blueprint,
    Flask,
    has_request_context,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from src.logging_config import setup_logging

# Load environment variables
load_dotenv()

# Ensure src is on the path
# __file__ is <project_root>/src/app/__init__.py, so parents[2] gives project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from src.config.game_config import config
from src.xwe.core.command_router import CommandRouter, handle_attack
from src.xwe.core.cultivation_system import CultivationSystem
from src.xwe.core.data_loader import DataLoader
from src.xwe.core.game_core import create_enhanced_game
from src.xwe.features import ExplorationSystem, InventorySystem
from src.xwe.features.ai_personalization import AIPersonalization
from src.xwe.features.community_system import CommunitySystem
from src.xwe.features.narrative_system import NarrativeSystem
from src.xwe.features.technical_ops import TechnicalOps
from src.xwe.server.app_factory import create_app as _create_flask_app
from src.common.request_utils import is_dev_request

# Setup logging
verbose_mode = os.getenv("VERBOSE_LOG", "false").lower() == "true"
setup_logging(verbose=verbose_mode)
logger = logging.getLogger("XianxiaEngine")

# Global systems and state
log_level = logging.DEBUG if config.debug_mode else logging.INFO

data_loader = DataLoader()
exploration_system = ExplorationSystem()
inventory_system = InventorySystem()
command_router: CommandRouter | None = None

game_instances: Dict[str, Dict] = {}
status_cache: Dict[str, Dict] = {}


# ---------------- Game instance helpers -----------------

def get_game_instance(session_id: str, initialize_player: bool = True):
    """Get or create a game instance."""
    if session_id not in game_instances:
        game_mode = os.getenv("GAME_MODE", "player")
        game = create_enhanced_game(game_mode=game_mode)

        # 初始化系统
        game.cultivation_system = CultivationSystem()
        game.narrative_system = NarrativeSystem()
        game.ai_personalization = AIPersonalization()
        game.community_system = CommunitySystem()
        game.technical_ops = TechnicalOps()

        # 创建默认玩家（可选）
        if initialize_player and not game.game_state.player:
            from src.xwe.core.attributes import CharacterAttributes
            from src.xwe.core.character import Character, CharacterType

            attrs = CharacterAttributes()
            attrs.realm_name = "炼气期"
            attrs.realm_level = 1
            attrs.level = 1
            attrs.cultivation_level = 0
            attrs.max_cultivation = 100
            attrs.realm_progress = 0
            attrs.faction = "正道"

            attrs.current_health = 100
            attrs.max_health = 100
            attrs.current_mana = 50
            attrs.max_mana = 50
            attrs.current_stamina = 100
            attrs.max_stamina = 100
            attrs.attack_power = 10
            attrs.defense = 5

            player = Character(
                id="player",
                name="无名侠客",
                character_type=CharacterType.PLAYER,
                attributes=attrs,
            )
            game.game_state.player = player
            game.game_state.current_location = "青云城"
            game.game_state.logs = []

            info_dict = {
                "id": player.id,
                "name": player.name,
                "attributes": attrs.to_dict(),
                "spiritual_root": player.spiritual_root,
                "inventory": inventory_system.get_inventory_data(
                    session.get("player_id", player.id)
                    if has_request_context()
                    else player.id
                ),
            }
            logger.debug(f"[PLAYER] Initialized: {info_dict}")

        game_instances[session_id] = {
            "game": game,
            "last_update": time.time(),
            "need_refresh": True,
        }

    return game_instances[session_id]


def cleanup_old_instances() -> None:
    """Clean timed-out game instances."""
    current_time = time.time()
    timeout = 3600

    to_remove = [sid for sid, inst in game_instances.items() if current_time - inst["last_update"] > timeout]
    for sid in to_remove:
        try:
            instance = game_instances[sid]
            if hasattr(instance["game"], "technical_ops"):
                instance["game"].technical_ops.save_game(instance["game"].game_state)
        except Exception:
            pass

        del game_instances[sid]


def build_status_data():
    """Build status dict for the current player."""
    player_id = session.get("player_id", "default")
    inventory_data = inventory_system.get_inventory_data(player_id)

    player_name = session.get("player_name", "无名侠客")
    realm_name = "炼气期"
    realm_level = 1
    current_health = 100
    max_health = 100
    current_mana = 50
    max_mana = 50
    location = session.get("location", "青云城")
    attributes_dict = {
        "realm_name": realm_name,
        "realm_level": realm_level,
        "current_health": current_health,
        "max_health": max_health,
        "current_mana": current_mana,
        "max_mana": max_mana,
    }
    extra_data = {}
    destiny = None
    talents: List[str] = []

    if "session_id" in session:
        try:
            instance = get_game_instance(session["session_id"])
            game = instance["game"]
            player = getattr(game.game_state, "player", None)
            if player:
                player_name = player.name
                realm_name = player.attributes.realm_name
                realm_level = player.attributes.realm_level
                current_health = player.attributes.current_health
                max_health = player.attributes.max_health
                current_mana = player.attributes.current_mana
                max_mana = player.attributes.max_mana
                location = game.game_state.current_location
                try:
                    attributes_dict = player.attributes.to_dict()
                except Exception:
                    attributes_dict = attributes_dict
                extra_data = getattr(player, "extra_data", {})
                destiny = extra_data.get("destiny", destiny)
                talents = extra_data.get("talents", talents)
        except Exception as e:
            logger.error(f"读取游戏状态失败: {e}")

    if destiny is None:
        destiny = session.get("destiny")

    status_dict = {
        "player": {
            "name": player_name,
            "attributes": attributes_dict,
            "extra_data": extra_data,
        },
        "location": location,
        "gold": inventory_data["gold"],
        "inventory": inventory_data,
        "destiny": destiny,
        "talents": talents,
    }
    logger.debug("[STATUS] %s", status_dict)
    return status_dict




main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return redirect(url_for(".game_screen"))


@main_bp.route("/welcome")
def welcome():
    cleanup_old_instances()
    return redirect(url_for(".game_screen"))


@main_bp.route("/intro")
def intro_screen():
    dev_mode = request.args.get("mode") == "dev"
    return render_template("intro_optimized.html", dev_mode=dev_mode)


@main_bp.route("/start")
def start_screen():
    return redirect(url_for(".game_screen"))


@main_bp.route("/game")
def game_screen():
    if "session_id" not in session:
        session["session_id"] = str(time.time())

    instance = get_game_instance(session["session_id"])
    game = instance["game"]

    if game.game_state.player:
        game.game_state.player.name = session.get("player_name", "无名侠客")

    status = build_status_data()

    return render_template(
        "game_enhanced_optimized_v2.html",
        status=status,
        player=status["player"],
        location=status["location"],
        buffs=[],
        special_status=[],
        is_new_session=True,
        dev_mode=request.args.get("mode") == "dev",
    )


@main_bp.route("/roll")
def roll_screen():
    return render_template("screens/roll_screen.html")


@main_bp.route("/choose")
def choose_start():
    return render_template("screens/choose_start.html")


@main_bp.route("/modal/<modal_name>")
def modal(modal_name):
    allowed_modals = [
        "status",
        "inventory",
        "cultivation",
        "achievement",
        "exploration",
        "map",
        "quest",
        "save",
        "load",
        "help",
        "settings",
        "exit",
    ]

    if modal_name not in allowed_modals:
        return "无效的模态框", 404

    try:
        return render_template(f"modals/{modal_name}.html")
    except Exception:
        return f"<h3>{modal_name.title()}</h3><p>功能开发中...</p>"


@main_bp.route("/need_refresh")
def need_refresh():
    return jsonify({"refresh": False, "version": "2025-06-25"})






# Error handlers
@main_bp.errorhandler(404)
def not_found(e):
    logger.warning(f"404错误: {request.path}")
    return "页面未找到", 404


@main_bp.errorhandler(500)
def server_error(e):
    logger.error(f"500错误: {str(e)}")
    return "服务器错误", 500


# ---------------- Application factory -----------------

def create_app(log_level: int = log_level) -> Flask:
    """Create and configure the Flask app."""
    global command_router, app

    app = _create_flask_app(log_level=log_level)
    app.game_instances = game_instances

    try:
        from .routes.lore import bp as lore_bp

        app.register_blueprint(lore_bp)
        logger.info("Lore routes registered")
    except Exception as e:  # pragma: no cover - optional blueprint
        logger.debug(f"Lore routes not loaded: {e}")

    if (
        os.getenv("FLASK_ENV") in ["development", "testing"]
        or os.getenv("ENABLE_E2E_API") == "true"
    ):
        try:
            from .routes.api_e2e import register_e2e_routes

            register_e2e_routes(app)
            logger.info("E2E test API endpoints enabled")
        except Exception as e:  # pragma: no cover - optional blueprint
            logger.debug(f"E2E test routes not loaded: {e}")

    from src.api.routes import register_all_routes

    register_all_routes(app)
    logger.info("All API routes registered")

    for directory in ["saves", "logs"]:
        Path(directory).mkdir(parents=True, exist_ok=True)

    try:
        command_router = CommandRouter(use_nlp=True)
        logger.info("命令路由器初始化成功（NLP模式）")
    except Exception as e:
        logger.warning(f"NLP模式初始化失败: {e}, 使用传统模式")
        command_router = CommandRouter(use_nlp=False)

    if not os.environ.get("DEEPSEEK_API_KEY"):
        logger.warning("DEEPSEEK_API_KEY environment variable not set after loading .env")

    app.register_blueprint(main_bp)

    from .routes import register_routes

    register_routes(app)

    return app
