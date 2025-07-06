#!/usr/bin/env python3
"""Simple test to ensure API routes register successfully."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from dotenv import load_dotenv
import pytest


def test_route_registration() -> None:
    """Create the app and ensure important routes return a valid status."""
    load_dotenv()

    from src.xwe.server.app_factory import create_app
    from src.api.routes import register_all_routes

    app = create_app()
    app.config.update(
        TESTING=True,
        VERSION="1.0.0",
        SECRET_KEY="test_secret",
        LOG_PATH="logs",
    )

    app.game_instances = {}
    register_all_routes(app)

    endpoints = [
        "/api/cultivation/status",
        "/api/achievements",
        "/api/map",
        "/api/quests",
        "/api/intel",
        "/api/player/stats/detailed",
        "/api/v1/system/info",
        "/api/v1/game/status",
    ]

    with app.test_client() as client:
        for endpoint in endpoints:
            resp = client.get(endpoint)
            assert resp.status_code < 500


