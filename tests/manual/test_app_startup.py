#!/usr/bin/env python3
"""Test Flask application startup and route registration."""

import sys
import os
from pathlib import Path

# Set up proper path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import pytest


def test_app_startup() -> None:
    """Ensure the Flask application can be created and routes registered."""
    from dotenv import load_dotenv

    load_dotenv()

    from src.xwe.server.app_factory import create_app
    from src.api.routes import register_all_routes

    log_level = 20  # INFO
    app = create_app(log_level=log_level)

    with app.app_context():
        try:
            register_all_routes(app)
        except Exception as exc:  # pragma: no cover - fail test if unexpected
            pytest.fail(f"Route registration failed: {exc}")


