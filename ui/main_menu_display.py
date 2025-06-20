import json
import os
from pathlib import Path


def clear_screen() -> None:
    """清屏"""
    os.system("clear" if os.name == "posix" else "cls")


def show_main_menu() -> str:
    """显示主菜单并返回用户选择"""
    print("\n" + "=" * 60)
    print("                   修仙世界引擎")
    print("                XianXia World Engine")
    print("=" * 60)
    print("\n1. 开始新游戏")
    print("2. 开局Roll系统（无限重置角色）")
    print("3. 测试Roll系统")
    print("4. 测试NLP功能")
    print("5. 继续游戏（开发中）")
    print("6. 设置")
    print("7. 退出")
    print("\n" + "=" * 60)
    choice = input("\n请选择 (1-7): ").strip()
    return choice


def test_roll_system() -> None:
    """测试Roll系统"""
    clear_screen()
    from scripts.simple_roll import main as roll_main

    roll_main()


def test_nlp_system() -> None:
    """测试NLP系统"""
    clear_screen()
    from scripts.test_nlp import main as nlp_main

    nlp_main()


def show_settings() -> None:
    """显示设置"""
    print("\n=== 设置 ===")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    print("\nAPI配置状态：")
    print(f"- DeepSeek API: {'已配置' if deepseek_key else '未配置'}")
    print(f"- OpenAI API: {'已配置' if openai_key else '未配置'}")
    config_path = Path(__file__).parent.parent / "xwe/data/interaction/nlp_config.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        print("\n当前NLP配置：")
        print(f"- 提供者: {config.get('llm_provider', 'mock')}")
        print(f"- 启用状态: {config.get('enable_llm', False)}")
    print("\n设置API密钥：")
    print("export DEEPSEEK_API_KEY='your_api_key'")
    print("export OPENAI_API_KEY='your_api_key'")
    input("\n按Enter返回主菜单...")
