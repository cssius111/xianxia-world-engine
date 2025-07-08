"""Test configuration for pytest."""

import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv
from flask import Flask


def pytest_addoption(parser):
    parser.addoption(
        "--runslow",
        action="store_true",
        default=False,
        help="运行被标记为 slow 的测试",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        return
    skip_slow = pytest.mark.skip(reason="需要 --runslow 才能运行慢速测试")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)

load_dotenv()

# Ensure the src directory is in sys.path so modules can find 'config' and others
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


@pytest.fixture(autouse=True)
def test_env(monkeypatch):
    """Set up test environment."""
    monkeypatch.setenv("FLASK_ENV", "testing")
    monkeypatch.setenv("DEBUG", "false")
    yield


@pytest.fixture
def app():
    """Create test Flask app."""
    # Create a fresh app for testing to avoid conflicts
    from src.xwe.server.app_factory import create_app
    from src.api.routes import register_all_routes
    
    # Create app
    test_app = create_app()
    
    # Configure for testing
    test_app.config.update(
        TESTING=True,
        VERSION="1.0.0",
        SECRET_KEY="test_secret",
        LOG_PATH="logs"
    )
    
    # Initialize game_instances on the app
    test_app.game_instances = {}
    
    # Register all routes
    register_all_routes(test_app)
    
    return test_app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()
