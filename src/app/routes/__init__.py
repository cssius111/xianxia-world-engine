"""Blueprint registration for app routes."""

from flask import Flask

from .player import player_bp
from .combat import combat_bp
from .status import status_bp


def register_routes(app: Flask) -> None:
    """Register all blueprints with the Flask app."""
    app.register_blueprint(player_bp)
    app.register_blueprint(combat_bp)
    app.register_blueprint(status_bp)
