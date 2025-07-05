from app import create_app, get_game_instance as _get_game_instance

app = create_app()

# DEPRECATED – will be removed in v1.0
from app import create_app as _create_app

# Re-export for backward compatibility
get_game_instance = _get_game_instance

if __name__ == "__main__":
    app.run()
