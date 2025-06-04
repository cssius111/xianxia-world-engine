#!/usr/bin/env python3
"""
修仙世界引擎 2.0 - 增强版
集成了7大功能方向的完整游戏
"""

import os
import sys
import logging
import random
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from xwe.core import GameCore
from xwe.features import (
    enhance_player_experience,
    enhance_with_ai_features,
    integrate_community_features,
    integrate_technical_features,
    narrative_system,
    content_ecosystem,
    visual_effects,
    create_immersive_opening,
    check_and_display_achievements
)
from xwe.features.visual_enhancement import TextAnimation, ProgressBar
from dotenv import load_dotenv
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 减少一些模块的日志输出
logging.getLogger('xwe.core.data_loader').setLevel(logging.WARNING)
logging.getLogger('xwe.engine.expression').setLevel(logging.WARNING)


class EnhancedGameInterface:
    """增强版游戏界面"""
    
    def __init__(self):
        """初始化界面"""
        logging.info("[DEBUG] 初始化增强版游戏界面")
        self.game = GameCore()
        self.running = True
        
        # 初始化所有增强功能
        self._initialize_features()
        
    def _initialize_features(self):
        """初始化所有功能增强"""
        print("正在初始化增强功能...")
        # visual_effects will be used after initialization
        
        # 1. 基础玩家体验
        enhance_player_experience(self.game)
        
        # 2. AI个性化
        enhance_with_ai_features(self.game)
        
        # 3. 社区功能
        integrate_community_features(self.game)
        
        # 4. 技术运营
        integrate_technical_features(self.game)
        
        print("✅ 所有功能初始化完成！")
    
    def start(self):
        """启动游戏"""
        self.show_enhanced_welcome()
        
        # 获取玩家名称
        player_name = self._get_player_name()
        
        # 显示开场剧情
        self._show_opening_story(player_name)
        
        # 开始新游戏
        try:
            self.game.start_new_game(player_name)
            logging.info("[DEBUG] 已调用start_new_game")
        except Exception as e:
            logging.error(f"[DEBUG] start_new_game出错: {e}", exc_info=True)
            raise
        
        # 主循环
        self.main_loop()
    
    def show_enhanced_welcome(self):
        """显示增强版欢迎界面"""
        # 清屏
        visual_effects.clear_screen()
        
        # 显示标题
        visual_effects.display_title(
            "仙侠世界引擎 2.0",
            "XianXia World Engine Enhanced"
        )
        
        # 显示ASCII艺术
        dragon_art = visual_effects.ascii_art.get_art("dragon", visual_effects.theme.get_color("primary"))
        print(dragon_art)
        
        # 显示欢迎词
        welcome_text = """
欢迎来到玄苍界，一个充满机遇与挑战的修仙世界！

这是一个真正的AI驱动游戏：
• 智能命令理解 - 用自然语言交流
• 个性化体验 - 游戏会学习你的风格
• 动态世界 - NPC会主动与你互动
• 社区驱动 - 支持MOD和玩家反馈
"""
        
        TextAnimation.typewriter(
            visual_effects.text_renderer.colorize(welcome_text, "normal"),
            delay=0.02
        )
        
        # 显示提示
        print("\n" + visual_effects.text_renderer.colorize(
            "💡 提示：你可以随时输入 '帮助' 查看可用命令，或用自然语言描述你想做的事。",
            "info"
        ))
    
    def _get_player_name(self):
        """获取玩家名称（增强版）"""
        print("\n" + visual_effects.text_renderer.colorize(
            "请输入你的名字（或直接按回车使用随机名字）: ",
            "emphasis"
        ), end="")
        
        player_name = input().strip()
        
        if not player_name:
            # 生成随机名字
            import random
            surnames = ["云", "风", "雷", "火", "冰", "剑", "刀", "星", "月", "阳"]
            names = ["无痕", "破天", "逍遥", "无极", "凌霄", "傲世", "无双", "绝尘"]
            player_name = random.choice(surnames) + random.choice(names)
            print(visual_effects.text_renderer.colorize(
                f"为你生成了一个名字：{player_name}",
                "info"
            ))
        
        return player_name
    
    def _show_opening_story(self, player_name: str):
        """显示开场剧情"""
        # 使用叙事系统生成开场
        opening_text = create_immersive_opening({
            "player_name": player_name,
            "level": 1
        })
        
        print("\n" + opening_text)
        
        # 触发开局事件
        opening_event = narrative_system.trigger_opening_event({
            "player_name": player_name,
            "level": 1
        })
        
        if opening_event:
            self._handle_opening_event(opening_event)
    
    def _handle_opening_event(self, event_data):
        """处理开局事件"""
        event = event_data["event"]
        choices = event_data["choices"]
        
        print("\n" + visual_effects.text_renderer.colorize("【特殊事件】", "accent"))
        print(visual_effects.text_renderer.colorize(event.name, "emphasis"))
        print(event.description)
        print()
        
        # 显示选项
        for i, choice in enumerate(choices):
            print(f"{i+1}. {choice['text']}")
        
        # 获取玩家选择
        while True:
            try:
                choice_input = input("\n请选择 (输入数字): ").strip()
                choice_index = int(choice_input) - 1
                
                if 0 <= choice_index < len(choices):
                    # 处理选择
                    result = narrative_system.process_event_choice(event.id, choice_index)
                    if result["success"]:
                        print("\n" + visual_effects.text_renderer.colorize(
                            result["text"],
                            "success"
                        ))
                    break
                else:
                    print("无效的选择，请重新输入。")
            except ValueError:
                print("请输入一个数字。")
    
    def main_loop(self):
        """增强版主游戏循环"""
        logging.info("[DEBUG] 进入增强版主循环")
        
        # 游戏开始时的提示
        tips = [
            "记住，你可以用自然语言输入命令",
            "试试输入 '社区' 查看社区链接",
            "如果遇到问题，使用 '反馈：' 命令告诉我们"
        ]
        
        if tips:
            print("\n" + visual_effects.text_renderer.colorize(
                f"💡 {random.choice(tips)}",
                "info"
            ))
        
        command_count = 0
        
        while self.game.is_running() and self.running:
            # 显示游戏输出
            output = self.game.get_output()
            for line in output:
                # 应用颜色增强
                if "战斗" in line or "攻击" in line:
                    print(visual_effects.text_renderer.colorize(line, "combat"))
                elif "获得" in line or "成功" in line:
                    print(visual_effects.text_renderer.colorize(line, "success"))
                elif "失败" in line or "死亡" in line:
                    print(visual_effects.text_renderer.colorize(line, "error"))
                elif "说道" in line or "：" in line:
                    print(visual_effects.text_renderer.colorize(line, "dialogue"))
                else:
                    print(line)
            
            # 检查成就（修复：只有在实际达成条件时才解锁）
            if command_count % 10 == 0 and command_count > 0 and hasattr(self.game.game_state, 'player'):
                player = self.game.game_state.player
                player_stats = {
                    "level": getattr(player, 'level', 1),
                    "kills": getattr(player, 'kill_count', 0),
                    "cultivation_count": getattr(player, 'cultivation_count', 0),
                    "explored_areas": getattr(player, 'explored_areas', 0),
                    # 只传递实际的统计数据
                }
                
                achievement_messages = check_and_display_achievements(player_stats)
                for msg in achievement_messages:
                    print(visual_effects.text_renderer.colorize(msg, "accent"))
            
            # 获取玩家输入
            try:
                # 显示状态条（如果有玩家数据）
                if hasattr(self.game.game_state, 'player') and self.game.game_state.player:
                    player = self.game.game_state.player
                    if hasattr(player.attributes, 'current_health'):
                        visual_effects.display_status_bar(
                            int(player.attributes.current_health),
                            int(player.attributes.max_health),
                            int(player.attributes.current_mana),
                            int(player.attributes.max_mana),
                            0, 100  # 经验值占位
                        )
                
                # 彩色输入提示
                prompt = visual_effects.text_renderer.colorize("> ", "accent")
                command = input(prompt).strip()
                logging.info(f"[DEBUG] 玩家输入命令: {command}")
                
                command_count += 1
                
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
                print(visual_effects.text_renderer.colorize(
                    f"发生错误: {e}",
                    "error"
                ))
                logging.error(f"游戏循环错误: {e}", exc_info=True)
    
    def confirm_quit(self):
        """确认退出（增强版）"""
        print("\n" + visual_effects.text_renderer.colorize(
            "确定要退出游戏吗？(y/n)",
            "warning"
        ))
        
        choice = input("> ").strip().lower()
        
        if choice in ['y', 'yes', '是']:
            # 显示游戏统计
            self._show_game_stats()
            
            print("\n" + visual_effects.text_renderer.colorize(
                "感谢游玩，再见！",
                "success"
            ))
            
            # 播放退出动画
            TextAnimation.fade_in("下次再见...", steps=3)
            
            self.running = False
            self.game.running = False
            logging.info("[DEBUG] 玩家选择退出游戏")
        else:
            print(visual_effects.text_renderer.colorize(
                "继续游戏...",
                "info"
            ))
            logging.info("[DEBUG] 玩家取消退出")
    
    def _show_game_stats(self):
        """显示游戏统计"""
        print("\n" + visual_effects.text_renderer.colorize(
            "=== 游戏统计 ===",
            "emphasis"
        ))
        
        # 获取各种统计数据
        if hasattr(self.game, 'get_system_status'):
            status = self.game.get_system_status()
            
            # 显示性能统计
            if 'performance' in status:
                perf = status['performance']
                print(f"平均CPU使用: {perf.get('average', {}).get('cpu_usage', 0):.1f}%")
                print(f"平均内存使用: {perf.get('average', {}).get('memory_usage', 0):.1f}MB")
            
            # 显示错误统计
            if 'errors' in status:
                errors = status['errors']
                print(f"错误总数: {errors.get('total_errors', 0)}")
        
        # 显示成就统计
        achievement_info = narrative_system.achievement_system.get_achievement_info()
        print(f"解锁成就: {achievement_info['unlocked_count']}/{achievement_info['total_achievements']}")
        print(f"成就点数: {achievement_info['total_points']}")
        
        # 显示AI分析
        if hasattr(self.game, 'get_player_profile'):
            profile = self.game.get_player_profile()
            print(f"玩家风格: {profile.get('primary_style', '未知')}")
            print(f"总行动数: {profile.get('total_actions', 0)}")


def main():
    """主函数"""
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("需要Python 3.8或更高版本")
        return
    
    # 检查依赖
    try:
        import psutil
    except ImportError:
        print("缺少必要的依赖，请运行：")
        print("pip install psutil")
        return
    
    # 检查数据文件
    data_path = project_root / "xwe" / "data"
    if not data_path.exists():
        print(f"错误: 找不到数据目录 {data_path}")
        print("请确保在正确的目录下运行程序")
        return
    
    # 创建必要的目录
    directories = ["saves", "saves/backups", "logs", "logs/crashes", 
                  "feedback", "analytics", "mods"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # 创建并启动游戏
    interface = EnhancedGameInterface()
    
    try:
        logging.info("[DEBUG] 启动增强版游戏界面")
        interface.start()
    except Exception as e:
        logging.error(f"游戏启动失败: {e}", exc_info=True)
        print(visual_effects.text_renderer.colorize(
            f"\n游戏启动失败: {e}",
            "error"
        ))
        print("请检查日志文件获取更多信息")




if __name__ == "__main__":
    logging.info("[DEBUG] 增强版程序开始运行")
    main()
    logging.info("[DEBUG] 增强版程序结束")
