#!/usr/bin/env python3
"""Ensure key modules can be imported without circular dependencies."""

import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import pytest


def test_module_imports() -> None:
    """Import important modules and fail the test if any import errors occur."""
    try:
        from src.common.request_utils import is_dev_request
        from src.config.game_config import config
        from src.xwe.core.data_loader import DataLoader
        from src.api.routes import register_all_routes
        from src.api.routes.character import bp
    except Exception as exc:
        pytest.fail(f"Import failed: {exc}")

