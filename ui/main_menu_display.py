import os


def clear_screen() -> None:
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def show_main_menu() -> str:
    """Display the main menu and return user's choice."""
    print("=== \u4e3b\u83dc\u5355 ===")
    print("1. \u65b0\u6e38\u620f")
    print("2. \u4ee5Roll\u5f00\u5c40")
    print("3. \u6d4b\u8bd5Roll\u7cfb\u7edf")
    print("4. \u6d4b\u8bd5NLP\u7cfb\u7edf")
    print("5. \u7ee7\u7eed\u6e38\u620f")
    print("6. \u8bbe\u7f6e")
    print("7. \u9000\u51fa")
    return input("\u8bf7\u9009\u62e9：")


def show_settings() -> None:
    """Placeholder settings screen."""
    print("\u8bbe\u7f6e\u529f\u80fd\u5c1a\u672a\u5b9e\u73b0")
    input("\u6309Enter\u8fd4\u56de...")


def test_nlp_system() -> None:
    """Placeholder NLP system test."""
    print("[NLP]\u6d4b\u8bd5")
    input("\u6309Enter\u8fd4\u56de...")


def test_roll_system() -> None:
    """Placeholder Roll system test."""
    print("[Roll]\u6d4b\u8bd5")
    input("\u6309Enter\u8fd4\u56de...")
