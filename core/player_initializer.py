from xwe.core.game_core import create_enhanced_game


def start_new_game(game_mode: str = "player") -> None:
    """Start a new game in console mode."""
    game = create_enhanced_game(game_mode=game_mode)
    player_name = input("\u8bf7\u8f93\u5165\u89d2\u8272\u540d\u79f0：")
    game.start_new_game(player_name)
    _game_loop(game)


def start_with_roll(game_mode: str = "player") -> None:
    """Start a game and immediately enter the roll system."""
    start_new_game(game_mode=game_mode)


def _game_loop(game) -> None:
    """Simple command loop interacting with the GameCore instance."""
    while game.is_running():
        for line in game.get_output():
            print(line)
        cmd = input("\u8bf7\u8f93\u5165\u547d\u4ee4：")
        game.process_command(cmd)
        for line in game.get_output():
            print(line)
