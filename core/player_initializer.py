from xwe.core import GameCore
from xwe.core.roll_system import CharacterRoller


def start_new_game(game_mode: str) -> None:
    """普通开始游戏"""
    game = GameCore(game_mode=game_mode)
    if game_mode != "player":
        print(f"\n[开发者模式] 当前模式: {game_mode}")

    player_name = input("请输入你的名字: ").strip() or "无名侠客"
    game.start_new_game(player_name)

    while game.is_running():
        output = game.get_output()
        for line in output:
            print(line)

        user_input = input("> ").strip()
        if user_input:
            game.process_command(user_input)

    output = game.get_output()
    for line in output:
        print(line)


def start_with_roll(game_mode: str) -> None:
    """带Roll的新游戏"""
    print("\n=== 开局Roll系统 ===")
    print("你可以无限次重置角色，直到满意为止！")
    if game_mode != "player":
        print(f"[开发者模式] 当前模式: {game_mode}")

    roller = CharacterRoller()
    while True:
        print("\n正在生成角色...")
        character = roller.roll()
        print(character.display())

        choice = input("\n使用这个角色开始游戏吗？(y/n): ").strip().lower()
        if choice == "y":
            print("\n正在准备游戏...")
            print("（提示：Roll系统已集成到主游戏中）")

            player_name = input("\n请输入角色名: ").strip() or character.name
            game = GameCore(game_mode=game_mode)
            game.start_new_game(player_name)

            while game.is_running():
                output = game.get_output()
                for line in output:
                    print(line)

                user_input = input("> ").strip()
                if user_input:
                    game.process_command(user_input)

            output = game.get_output()
            for line in output:
                print(line)
            break
