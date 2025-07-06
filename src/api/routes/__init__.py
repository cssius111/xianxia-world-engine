"""API routes package initialization."""

# Remove top-level imports to avoid circular dependencies
# All imports are now done lazily within register_all_routes


def register_all_routes(app):
    """Register all API routes with the Flask app."""
    # Lazy-import blueprints to avoid circular dependencies
    from .achievements import achievements_bp
    from .character import bp as character_bp
    from .cultivation import cultivation_bp
    from .intel import bp as intel_bp
    from .intel_api import intel_api_bp, intel_tips_bp
    from .intel_overview import intel_bp as intel_overview_bp
    from .inventory import inventory_bp
    from .lore import bp as lore_bp
    from .map import map_bp
    from .player import player_bp
    from .quests import quests_bp
    from .onboarding import onboarding_bp
    
    # Register all blueprints
    app.register_blueprint(achievements_bp)
    app.register_blueprint(character_bp)
    app.register_blueprint(cultivation_bp)
    app.register_blueprint(intel_bp)
    app.register_blueprint(intel_api_bp)
    app.register_blueprint(intel_tips_bp)
    app.register_blueprint(intel_overview_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(lore_bp)
    app.register_blueprint(map_bp)
    app.register_blueprint(player_bp)
    app.register_blueprint(quests_bp)
    app.register_blueprint(onboarding_bp)
    
    # Register v1 API blueprints
    from ..v1.system import system_bp
    from ..v1.game import game_bp
    from ..v1.player import player_bp as player_v1_bp
    from ..v1.save import save_bp
    
    app.register_blueprint(system_bp, url_prefix='/api/v1/system')
    app.register_blueprint(game_bp, url_prefix='/api/v1/game')
    app.register_blueprint(player_v1_bp, url_prefix='/api/v1/player')
    app.register_blueprint(save_bp, url_prefix='/api/v1/save')
    
    # Store game instances in app context for access in routes
    if hasattr(app, 'game_instances'):
        # Already set, don't override
        pass
    else:
        # Will be set by run.py
        app.game_instances = {}
    
    return app
