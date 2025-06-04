# main.py
"""
仙侠世界引擎 - 演示程序

简单的命令行界面，用于测试游戏功能。
"""

import os
import sys
import logging
import time
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()


# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from xwe.core import GameCore
from dotenv import load_dotenv
load_dotenv()  # 默认自动查找项目根目录的 .env 文件并加载

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 减少一些模块的日志输出
logging.getLogger('xwe.core.data_loader').setLevel(logging.WARNING)
logging.getLogger('xwe.engine.expression').setLevel(logging.WARNING)


class SimpleGameInterface:
    """简单的游戏界面"""

    def __init__(self):
        """初始化界面"""
        logging.info("[DEBUG] 初始化SimpleGameInterface")
        self.game = GameCore()
        self.running = True

    def start(self):
        """启动游戏"""
        self.show_welcome()

        # 获取玩家名称
        logging.info("[DEBUG] 等待玩家输入名字")
        player_name = input("请输入你的名字: ").strip()
        if not player_name:
            player_name = "无名侠客"
        logging.info(f"[DEBUG] 玩家名字 = {player_name}")

        # 开始新游戏
        try:
            self.game.start_new_game(player_name)
            logging.info("[DEBUG] 已调用start_new_game")
        except Exception as e:
            logging.error(f"[DEBUG] start_new_game出错: {e}", exc_info=True)
            raise

        # 主循环
        self.main_loop()

    def show_welcome(self):
        """显示欢迎界面"""
        print("=" * 60)
        print("                     仙侠世界引擎")
        print("                   XianXia World Engine")
        print("=" * 60)
        print()
        print("欢迎来到玄苍界，一个充满机遇与挑战的修仙世界！")
        print()

    def main_loop(self):
        """主游戏循环"""
        logging.info("[DEBUG] 进入主循环")
        
        # 调试：检查循环条件
        logging.info(f"[DEBUG] 循环条件检查: self.running={self.running}, game.is_running()={self.game.is_running()}")
        
        if not self.game.is_running():
            logging.warning("[DEBUG] game.is_running()返回False，检查GameCore.start_new_game是否设置了running=True")

        while self.game.is_running() and self.running:
            # 显示游戏输出
            output = self.game.get_output()
            logging.info(f"[DEBUG] 输出内容: {output}")
            for line in output:
                print(line)
            
            # 检查并显示成就
            if hasattr(self.game, 'achievement_system'):
                achievement_display = self.game.achievement_system.get_next_unlock_display()
                if achievement_display:
                    print(achievement_display)
                    time.sleep(2)  # 让玩家有时间阅读成就
                    continue

            # 获取玩家输入
            try:
                command = input("> ").strip()
                logging.info(f"[DEBUG] 玩家输入命令: {command}")

                if command.lower() in ['quit', 'exit', '退出']:
                    self.confirm_quit()
                else:
                    # 处理命令
                    self.game.process_command(command)
                    logging.info("[DEBUG] 已处理命令")

            except KeyboardInterrupt:
                print("\n")
                self.confirm_quit()
            except Exception as e:
                print(f"发生错误: {e}")
                logging.error(f"游戏循环错误: {e}", exc_info=True)

    def confirm_quit(self):
        """确认退出"""
        print("\n确定要退出游戏吗？(y/n)")
        choice = input("> ").strip().lower()

        if choice in ['y', 'yes', '是']:
            print("\n感谢游玩，再见！")
            self.running = False
            self.game.running = False
            logging.info("[DEBUG] 玩家选择退出游戏")
        else:
            print("继续游戏...")
            logging.info("[DEBUG] 玩家取消退出")


def main():
    """主函数"""
    # 检查数据文件是否存在
    data_path = project_root / "xwe" / "data"
    logging.info(f"[DEBUG] 检查数据路径: {data_path}")
    if not data_path.exists():
        print(f"错误: 找不到数据目录 {data_path}")
        print("请确保在正确的目录下运行程序")
        logging.error("[DEBUG] 数据目录不存在，程序终止")
        return

    # 创建并启动游戏
    interface = SimpleGameInterface()

    try:
        logging.info("[DEBUG] 启动游戏界面")
        interface.start()
    except Exception as e:
        logging.error(f"游戏启动失败: {e}", exc_info=True)
        print(f"\n游戏启动失败: {e}")
        print("请检查日志文件获取更多信息")


if __name__ == "__main__":
    logging.info("[DEBUG] 程序开始运行")
    main()
    logging.info("[DEBUG] 程序结束")