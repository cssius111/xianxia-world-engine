import pytest
from flask import Flask
import importlib.util
from pathlib import Path
import werkzeug

if not hasattr(werkzeug, "__version__"):
    werkzeug.__version__ = "0"

def _load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, Path(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore
    return module

game_bp = _load_module('api/v1/game.py', 'game').game_bp
system_bp = _load_module('api/v1/system.py', 'system').system_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "test_secret"
    app.register_blueprint(game_bp, url_prefix='/api/v1/game')
    app.register_blueprint(system_bp, url_prefix='/api/v1/system')
    app.config.update(TESTING=True)
    return app

@pytest.fixture
def client(app):
    return app.test_client()
