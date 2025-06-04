"""
视觉和氛围增强系统
- 文字渲染
- ASCII艺术
- 动画效果
"""

import time
import sys
import random
from typing import List, Dict, Optional, Callable
from enum import Enum

class Color:
    """ANSI颜色代码"""
    RESET = '\033[0m'
    
    # 前景色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # 明亮前景色
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # 背景色
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # 样式
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    STRIKETHROUGH = '\033[9m'

class TextRenderer:
    """文字渲染器"""
    
    def __init__(self, enable_color: bool = True):
        self.enable_color = enable_color
        
        # 预定义的颜色方案
        self.color_schemes = {
            "default": {
                "title": Color.BRIGHT_YELLOW + Color.BOLD,
                "subtitle": Color.CYAN,
                "normal": Color.RESET,
                "emphasis": Color.BRIGHT_WHITE + Color.BOLD,
                "success": Color.BRIGHT_GREEN,
                "warning": Color.YELLOW,
                "error": Color.BRIGHT_RED,
                "info": Color.BRIGHT_CYAN,
                "combat": Color.RED,
                "cultivation": Color.BRIGHT_MAGENTA,
                "dialogue": Color.GREEN,
                "system": Color.BRIGHT_BLUE
            },
            "dark": {
                "title": Color.BRIGHT_WHITE + Color.BOLD,
                "subtitle": Color.WHITE,
                "normal": Color.BRIGHT_BLACK,
                "emphasis": Color.WHITE + Color.BOLD,
                "success": Color.GREEN,
                "warning": Color.YELLOW,
                "error": Color.RED,
                "info": Color.CYAN,
                "combat": Color.BRIGHT_RED,
                "cultivation": Color.MAGENTA,
                "dialogue": Color.BRIGHT_GREEN,
                "system": Color.BLUE
            }
        }
        
        self.current_scheme = "default"
    
    def colorize(self, text: str, color_type: str) -> str:
        """给文字添加颜色"""
        if not self.enable_color:
            return text
        
        scheme = self.color_schemes.get(self.current_scheme, self.color_schemes["default"])
        color = scheme.get(color_type, Color.RESET)
        
        return f"{color}{text}{Color.RESET}"
    
    def gradient_text(self, text: str, start_color: str, end_color: str) -> str:
        """渐变色文字（简化版）"""
        if not self.enable_color:
            return text
        
        # 简单实现：前半部分用起始色，后半部分用结束色
        mid = len(text) // 2
        return start_color + text[:mid] + end_color + text[mid:] + Color.RESET
    
    def rainbow_text(self, text: str) -> str:
        """彩虹色文字"""
        if not self.enable_color:
            return text
        
        colors = [
            Color.RED, Color.YELLOW, Color.GREEN, 
            Color.CYAN, Color.BLUE, Color.MAGENTA
        ]
        
        result = ""
        for i, char in enumerate(text):
            if char != ' ':
                color = colors[i % len(colors)]
                result += color + char
            else:
                result += char
        
        return result + Color.RESET
    
    def box(self, text: str, width: int = None, style: str = "single") -> str:
        """文字框"""
        lines = text.split('\n')
        if width is None:
            width = max(len(line) for line in lines)
        
        # 边框样式
        borders = {
            "single": {
                "tl": "┌", "tr": "┐", "bl": "└", "br": "┘",
                "h": "─", "v": "│"
            },
            "double": {
                "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝",
                "h": "═", "v": "║"
            },
            "round": {
                "tl": "╭", "tr": "╮", "bl": "╰", "br": "╯",
                "h": "─", "v": "│"
            }
        }
        
        b = borders.get(style, borders["single"])
        
        # 构建框
        result = []
        result.append(b["tl"] + b["h"] * (width + 2) + b["tr"])
        
        for line in lines:
            padded = line.ljust(width)
            result.append(f"{b['v']} {padded} {b['v']}")
        
        result.append(b["bl"] + b["h"] * (width + 2) + b["br"])
        
        return "\n".join(result)

class ASCIIArt:
    """ASCII艺术"""
    
    def __init__(self):
        self.arts = {
            "sword": [
                "        />",
                "       //",
                "(o)===|[===>",
                "       \\\\",
                "        \\>"
            ],
            "mountain": [
                "      /\\      ",
                "     /  \\     ",
                "    /    \\    ",
                "   /      \\   ",
                "  /        \\  ",
                " /          \\ ",
                "/____________\\"
            ],
            "cultivation": [
                "    _..._    ",
                "  .'     '.  ",
                " /  o   o  \\ ",
                "|     <     |",
                " \\   ___   / ",
                "  '.     .'  ",
                "    '~~~'    "
            ],
            "dragon": [
                "                 __----~~~~~~~~~~~------___",
                "      .  .   ~~//====......          __--~ ~~",
                "  -.            \\_|//     |||\\\\  ~~~~~~::::... /~",
                "___-==_       _-~o~  \\/    |||  \\\\            _/~~-",
                "__---~~~.==~||\=_    -_--~/_-~|-   |\\   \\\\\\\\  /",
                "_-~~     .=~|  \\\\-_    '-~7  /-   /  ||      \\\\\\\\\\\\",
                "  .~       |   \\\\-_    /  /-   /   ||         \\\\\\\\\\\\",
                " /  ____  |     \\\\\\'~ /  /~ ) /  ,||           \\\\\\~",
                "|~~    ~~|--~~~~--_ \\~=/   /_,  ,  -|/           _\\~~",
                "         '         ~-|~~| |~~|  |( <    |         _-~",
                "                     '  '  '  '   \\_\\  '       /~\\\\",
                "                                  ~' ~----~~~~~"
            ],
            "treasure": [
                "     ___________",
                "    /           \\",
                "   /   $$$$$$$   \\",
                "  |  $$$ $$$ $$$  |",
                "  |  $$$ $$$ $$$  |",
                "  |  $$$ $$$ $$$  |",
                "   \\  $$$$$$$$$  /",
                "    \\___________/"
            ],
            "portal": [
                "    .-..-.",
                "  .'     '.",
                " /  _   _  \\",
                "|  (o)-(o)  |",
                "|     <>     |",
                " \\   ___   /",
                "  '.     .'",
                "    '---'"
            ],
            "skull": [
                "     ___",
                "    /   \\",
                "   | o o |",
                "   |  >  |",
                "   | --- |",
                "    \\___/"
            ],
            "potion": [
                "      _",
                "     | |",
                "    /   \\",
                "   |     |",
                "   |  ~  |",
                "   |     |",
                "    \\___/"
            ],
            "book": [
                "   ______",
                "  /      \\",
                " /  修仙  \\",
                "|  秘籍   |",
                "|         |",
                " \\______/"
            ],
            "flame": [
                "     (\\ ",
                "    ( \\\\",
                "   (   ))",
                "  ( )  )",
                " (  ) (",
                "(   )  )",
                " ) (  (",
                "  ) ) )",
                "   ( ("
            ]
        }
    
    def get_art(self, name: str, color: Optional[str] = None) -> str:
        """获取ASCII艺术"""
        if name not in self.arts:
            return ""
        
        art_lines = self.arts[name]
        art_text = "\n".join(art_lines)
        
        if color:
            art_text = color + art_text + Color.RESET
        
        return art_text
    
    def animate_art(self, name: str, duration: float = 1.0, color: Optional[str] = None):
        """动画显示ASCII艺术"""
        art = self.get_art(name, color)
        lines = art.split('\n')
        
        for line in lines:
            print(line)
            time.sleep(duration / len(lines))

class TextAnimation:
    """文字动画效果"""
    
    @staticmethod
    def typewriter(text: str, delay: float = 0.05, color: Optional[str] = None):
        """打字机效果"""
        if color:
            sys.stdout.write(color)
        
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        
        if color:
            sys.stdout.write(Color.RESET)
        sys.stdout.write('\n')
    
    @staticmethod
    def fade_in(text: str, steps: int = 5):
        """淡入效果（通过颜色亮度模拟）"""
        colors = [
            Color.BRIGHT_BLACK,
            Color.BRIGHT_BLACK + Color.BOLD,
            Color.WHITE,
            Color.BRIGHT_WHITE,
            Color.BRIGHT_WHITE + Color.BOLD
        ]
        
        for i in range(min(steps, len(colors))):
            sys.stdout.write(f'\r{colors[i]}{text}{Color.RESET}')
            sys.stdout.flush()
            time.sleep(0.1)
        
        sys.stdout.write('\n')
    
    @staticmethod
    def flash(text: str, times: int = 3, interval: float = 0.3):
        """闪烁效果"""
        for i in range(times):
            sys.stdout.write(f'\r{text}')
            sys.stdout.flush()
            time.sleep(interval)
            sys.stdout.write(f'\r{" " * len(text)}')
            sys.stdout.flush()
            time.sleep(interval)
        
        sys.stdout.write(f'\r{text}\n')
    
    @staticmethod
    def scroll(text: str, width: int = 40, speed: float = 0.1):
        """滚动效果"""
        padded_text = " " * width + text + " " * width
        
        for i in range(len(text) + width):
            display = padded_text[i:i+width]
            sys.stdout.write(f'\r{display}')
            sys.stdout.flush()
            time.sleep(speed)
        
        sys.stdout.write('\n')

class ProgressBar:
    """进度条"""
    
    def __init__(self, total: int, width: int = 40, fill_char: str = "█", empty_char: str = "░"):
        self.total = total
        self.width = width
        self.fill_char = fill_char
        self.empty_char = empty_char
        self.current = 0
    
    def update(self, current: int, prefix: str = "", suffix: str = ""):
        """更新进度条"""
        self.current = min(current, self.total)
        filled = int(self.width * self.current / self.total)
        empty = self.width - filled
        
        bar = self.fill_char * filled + self.empty_char * empty
        percent = self.current / self.total * 100
        
        sys.stdout.write(f'\r{prefix} [{bar}] {percent:.1f}% {suffix}')
        sys.stdout.flush()
        
        if self.current >= self.total:
            sys.stdout.write('\n')
    
    def animate_to(self, target: int, duration: float = 1.0, prefix: str = "", suffix: str = ""):
        """动画到目标值"""
        steps = 20
        step_delay = duration / steps
        step_size = (target - self.current) / steps
        
        for i in range(steps):
            self.update(int(self.current + step_size * (i + 1)), prefix, suffix)
            time.sleep(step_delay)

class VisualTheme:
    """视觉主题"""
    
    def __init__(self):
        self.themes = {
            "default": {
                "primary": Color.BRIGHT_CYAN,
                "secondary": Color.CYAN,
                "accent": Color.BRIGHT_YELLOW,
                "success": Color.BRIGHT_GREEN,
                "warning": Color.YELLOW,
                "error": Color.BRIGHT_RED,
                "text": Color.RESET,
                "dim": Color.BRIGHT_BLACK
            },
            "fire": {
                "primary": Color.BRIGHT_RED,
                "secondary": Color.RED,
                "accent": Color.BRIGHT_YELLOW,
                "success": Color.YELLOW,
                "warning": Color.BRIGHT_YELLOW,
                "error": Color.BRIGHT_MAGENTA,
                "text": Color.BRIGHT_WHITE,
                "dim": Color.RED + Color.DIM
            },
            "ice": {
                "primary": Color.BRIGHT_CYAN,
                "secondary": Color.CYAN,
                "accent": Color.BRIGHT_WHITE,
                "success": Color.BRIGHT_BLUE,
                "warning": Color.BRIGHT_CYAN,
                "error": Color.BRIGHT_WHITE,
                "text": Color.BRIGHT_WHITE,
                "dim": Color.CYAN + Color.DIM
            },
            "nature": {
                "primary": Color.BRIGHT_GREEN,
                "secondary": Color.GREEN,
                "accent": Color.BRIGHT_YELLOW,
                "success": Color.BRIGHT_GREEN,
                "warning": Color.YELLOW,
                "error": Color.BRIGHT_RED,
                "text": Color.BRIGHT_WHITE,
                "dim": Color.GREEN + Color.DIM
            },
            "dark": {
                "primary": Color.BRIGHT_MAGENTA,
                "secondary": Color.MAGENTA,
                "accent": Color.BRIGHT_RED,
                "success": Color.BRIGHT_BLUE,
                "warning": Color.BRIGHT_MAGENTA,
                "error": Color.BRIGHT_RED,
                "text": Color.BRIGHT_BLACK,
                "dim": Color.BLACK
            }
        }
        
        self.current_theme = "default"
    
    def get_color(self, color_type: str) -> str:
        """获取主题颜色"""
        theme = self.themes.get(self.current_theme, self.themes["default"])
        return theme.get(color_type, Color.RESET)
    
    def set_theme(self, theme_name: str):
        """设置主题"""
        if theme_name in self.themes:
            self.current_theme = theme_name

class VisualEffects:
    """视觉效果管理器"""
    
    def __init__(self):
        self.text_renderer = TextRenderer()
        self.ascii_art = ASCIIArt()
        self.theme = VisualTheme()
    
    def display_title(self, title: str, subtitle: str = ""):
        """显示标题"""
        # ASCII艺术边框
        border = "=" * (len(title) + 4)
        
        print(self.text_renderer.colorize(border, "title"))
        print(self.text_renderer.colorize(f"  {title}  ", "title"))
        if subtitle:
            print(self.text_renderer.colorize(f"  {subtitle}  ", "subtitle"))
        print(self.text_renderer.colorize(border, "title"))
        print()
    
    def display_scene_transition(self, from_scene: str, to_scene: str):
        """场景转换效果"""
        print()
        TextAnimation.fade_in(f"离开 {from_scene}...")
        time.sleep(0.5)
        
        # 显示传送门
        portal_art = self.ascii_art.get_art("portal", Color.BRIGHT_MAGENTA)
        print(portal_art)
        time.sleep(0.5)
        
        TextAnimation.fade_in(f"到达 {to_scene}")
        print()
    
    def display_combat_effect(self, attacker: str, target: str, damage: int):
        """战斗效果"""
        # 攻击动画
        print(f"\n{self.text_renderer.colorize(attacker, 'combat')} 发动攻击！")
        
        # 剑的ASCII艺术
        sword_art = self.ascii_art.get_art("sword", Color.BRIGHT_RED)
        print(sword_art)
        
        # 伤害数字
        damage_text = f"-{damage}"
        TextAnimation.flash(
            self.text_renderer.colorize(damage_text, "error"),
            times=2,
            interval=0.2
        )
        
        print(f"{self.text_renderer.colorize(target, 'dialogue')} 受到了伤害！\n")
    
    def display_cultivation_progress(self, current: int, total: int, realm: str):
        """修炼进度"""
        print(f"\n{self.text_renderer.colorize('修炼中...', 'cultivation')}")
        
        # 显示修炼图案
        cultivation_art = self.ascii_art.get_art("cultivation", Color.BRIGHT_MAGENTA)
        print(cultivation_art)
        
        # 进度条
        progress = ProgressBar(total, width=30, fill_char="◆", empty_char="◇")
        progress.animate_to(
            current, 
            duration=1.5,
            prefix=self.text_renderer.colorize(f"{realm}", "cultivation"),
            suffix=f"{current}/{total}"
        )
        print()
    
    def display_item_obtained(self, item_name: str, item_type: str = "common"):
        """获得物品效果"""
        color_map = {
            "common": "normal",
            "rare": "info",
            "epic": "warning",
            "legendary": "accent"
        }
        
        color_type = color_map.get(item_type, "normal")
        
        print()
        TextAnimation.flash(
            self.text_renderer.colorize("获得物品！", "success"),
            times=2
        )
        
        # 显示宝箱
        treasure_art = self.ascii_art.get_art("treasure", self.theme.get_color("accent"))
        print(treasure_art)
        
        item_text = self.text_renderer.colorize(item_name, color_type)
        TextAnimation.typewriter(f"你获得了: {item_text}", delay=0.03)
        print()
    
    def display_dialogue(self, speaker: str, text: str, emotion: str = "normal"):
        """显示对话"""
        # 说话者名称
        speaker_text = self.text_renderer.colorize(f"{speaker}:", "dialogue")
        print(f"\n{speaker_text}")
        
        # 对话内容（打字机效果）
        if emotion == "angry":
            text_color = Color.BRIGHT_RED
        elif emotion == "happy":
            text_color = Color.BRIGHT_YELLOW
        elif emotion == "sad":
            text_color = Color.BRIGHT_BLUE
        else:
            text_color = Color.GREEN
        
        TextAnimation.typewriter(text, delay=0.02, color=text_color)
    
    def display_status_bar(self, hp: int, max_hp: int, mp: int, max_mp: int, exp: int, max_exp: int):
        """显示状态条"""
        # 生命值
        hp_bar = ProgressBar(max_hp, width=20, fill_char="❤", empty_char="♡")
        hp_bar.update(hp, prefix="HP", suffix=f"{hp}/{max_hp}")
        
        # 法力值
        mp_bar = ProgressBar(max_mp, width=20, fill_char="◆", empty_char="◇")
        mp_bar.update(mp, prefix="MP", suffix=f"{mp}/{max_mp}")
        
        # 经验值
        exp_bar = ProgressBar(max_exp, width=20, fill_char="★", empty_char="☆")
        exp_bar.update(exp, prefix="EXP", suffix=f"{exp}/{max_exp}")
    
    def display_menu(self, title: str, options: List[str], selected: int = 0):
        """显示菜单"""
        print(self.text_renderer.box(title, style="double"))
        
        for i, option in enumerate(options):
            if i == selected:
                prefix = self.text_renderer.colorize("▶ ", "accent")
                text = self.text_renderer.colorize(option, "emphasis")
            else:
                prefix = "  "
                text = self.text_renderer.colorize(option, "normal")
            
            print(f"{prefix}{text}")
        
        print()
    
    def display_achievement(self, achievement_name: str, description: str):
        """显示成就"""
        print()
        TextAnimation.flash(
            self.text_renderer.colorize("🏆 成就解锁！", "success"),
            times=3,
            interval=0.3
        )
        
        achievement_box = self.text_renderer.box(
            f"{achievement_name}\n\n{description}",
            style="double"
        )
        
        print(self.text_renderer.colorize(achievement_box, "accent"))
        print()
    
    def clear_screen(self):
        """清屏"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_loading(self, message: str = "加载中", duration: float = 2.0):
        """显示加载动画"""
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        end_time = time.time() + duration
        
        i = 0
        while time.time() < end_time:
            frame = frames[i % len(frames)]
            sys.stdout.write(f'\r{frame} {message}...')
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        
        sys.stdout.write('\r' + ' ' * (len(message) + 10) + '\r')
        sys.stdout.flush()

# 主题化的全局实例
visual_effects = VisualEffects()
