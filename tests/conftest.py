"""Test configuration for pytest."""

import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv
from flask import Flask

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
    app = Flask(__name__)
    app.secret_key = "test_secret"
    app.config.update(TESTING=True, VERSION="1.0.0")
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()
