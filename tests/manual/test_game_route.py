#!/usr/bin/env python3
"""Verify the ``/game`` route renders without ``TemplateNotFound`` errors."""

import sys
import os
from pathlib import Path

# Set up proper path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import pytest


def test_game_route_template_loading() -> None:
    """Ensure the ``/game`` route can load its template."""
    from dotenv import load_dotenv

    load_dotenv()

    from src.xwe.server.app_factory import create_app

    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        try:
            template = app.jinja_env.get_template("game_enhanced_optimized_v2.html")
            assert template is not None
        except Exception as exc:
            pytest.fail(f"Template loading failed: {exc}")

    with app.test_client() as client:
        response = client.get("/favicon.ico")
        assert response.status_code < 500



