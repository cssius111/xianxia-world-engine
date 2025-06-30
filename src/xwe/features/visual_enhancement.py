"""
视觉增强模块
提供文本动画、颜色、ASCII艺术等视觉效果
"""

import os
import sys
import time
import random
from enum import Enum
from typing import Dict, List, Optional, Tuple


class Color:
    """ANSI颜色代码"""
    RESET = '\033[0m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # 亮色版本
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


class VisualTheme(Enum):
    """视觉主题"""
    CLASSIC = "classic"      # 经典主题
    MYSTIC = "mystic"       # 神秘主题
    NATURE = "nature"       # 自然主题
    TECH = "tech"           # 科技主题
    MINIMAL = "minimal"     # 极简主题


class TextRenderer:
    """文本渲染器"""
    
    def __init__(self):
        self.current_theme = VisualTheme.CLASSIC
        self.color_enabled = self._check_color_support()
        self.theme_colors = {
            VisualTheme.CLASSIC: {
                "primary": Color.CYAN,
                "secondary": Color.YELLOW,
                "accent": Color.MAGENTA,
                "info": Color.BLUE,
                "success": Color.GREEN,
                "warning": Color.YELLOW,
                "error": Color.RED
            },
            VisualTheme.MYSTIC: {
                "primary": Color.MAGENTA,
                "secondary": Color.CYAN,
                "accent": Color.BRIGHT_MAGENTA,
                "info": Color.BRIGHT_BLUE,
                "success": Color.BRIGHT_GREEN,
                "warning": Color.BRIGHT_YELLOW,
                "error": Color.BRIGHT_RED
            },
            VisualTheme.NATURE: {
                "primary": Color.GREEN,
                "secondary": Color.YELLOW,
                "accent": Color.BRIGHT_GREEN,
                "info": Color.CYAN,
                "success": Color.BRIGHT_GREEN,
                "warning": Color.YELLOW,
                "error": Color.RED
            }
        }
    
    def _check_color_support(self) -> bool:
        """检查终端是否支持颜色"""
        # Windows终端颜色支持
        if sys.platform == "win32":
            return os.environ.get("ANSICON") is not None or "WT_SESSION" in os.environ
        
        # Unix-like系统
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    
    def set_theme(self, theme: VisualTheme):
        """设置主题"""
        self.current_theme = theme
    
    def colorize(self, text: str, color_type: str = "primary") -> str:
        """给文本着色"""
        if not self.color_enabled:
            return text
        
        colors = self.theme_colors.get(self.current_theme, self.theme_colors[VisualTheme.CLASSIC])
        color = colors.get(color_type, Color.WHITE)
        
        return f"{color}{text}{Color.RESET}"
    
    def gradient_text(self, text: str, start_color: str, end_color: str) -> str:
        """渐变文本效果（简化版）"""
        if not self.color_enabled:
            return text
        
        # 简化实现：交替使用两种颜色
        result = ""
        colors = [start_color, end_color]
        for i, char in enumerate(text):
            if char == ' ':
                result += char
            else:
                result += f"{colors[i % 2]}{char}"
        
        return result + Color.RESET
    
    def box(self, content: str, title: Optional[str] = None, 
            width: Optional[int] = None, padding: int = 1) -> str:
        """创建文本框"""
        lines = content.split('\n')
        
        # 计算宽度
        if width is None:
            width = max(len(line) for line in lines) + padding * 2
            if title:
                width = max(width, len(title) + 4)
        
        # 边框字符
        chars = {
            'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
            'h': '─', 'v': '│', 'cross': '┼'
        }
        
        # 构建框架
        result = []
        
        # 顶部
        if title:
            title_line = chars['tl'] + chars['h'] + f" {title} "
            title_line += chars['h'] * (width - len(title) - 3) + chars['tr']
            result.append(self.colorize(title_line, "primary"))
        else:
            result.append(self.colorize(
                chars['tl'] + chars['h'] * width + chars['tr'], 
                "primary"
            ))
        
        # 内容
        for line in lines:
            padded = f"{' ' * padding}{line}{' ' * (width - len(line) - padding)}"
            result.append(
                self.colorize(chars['v'], "primary") + 
                padded + 
                self.colorize(chars['v'], "primary")
            )
        
        # 底部
        result.append(self.colorize(
            chars['bl'] + chars['h'] * width + chars['br'], 
            "primary"
        ))
        
        return '\n'.join(result)


class ProgressBar:
    """进度条"""
    
    def __init__(self, total: int, width: int = 50, 
                 fill_char: str = "█", empty_char: str = "░"):
        self.total = total
        self.width = width
        self.fill_char = fill_char
        self.empty_char = empty_char
        self.current = 0
        self.start_time = time.time()
    
    def update(self, current: int) -> str:
        """更新进度条"""
        self.current = min(current, self.total)
        percentage = self.current / self.total if self.total > 0 else 0
        filled = int(self.width * percentage)
        
        # 构建进度条
        bar = self.fill_char * filled + self.empty_char * (self.width - filled)
        
        # 计算时间
        elapsed = time.time() - self.start_time
        if self.current > 0 and percentage < 1:
            eta = elapsed * (self.total - self.current) / self.current
            time_str = f" ETA: {eta:.1f}s"
        else:
            time_str = f" 用时: {elapsed:.1f}s"
        
        return f"[{bar}] {percentage:>6.1%}{time_str}"
    
    def increment(self, amount: int = 1) -> str:
        """增加进度"""
        return self.update(self.current + amount)


class TextAnimation:
    """文本动画效果"""
    
    @staticmethod
    def typewriter(text: str, delay: float = 0.05):
        """打字机效果"""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()  # 换行
    
    @staticmethod
    def fade_in(text: str, steps: int = 5):
        """淡入效果（使用灰度）"""
        if not TextRenderer()._check_color_support():
            print(text)
            return
        
        # 从暗到亮的颜色序列
        colors = [Color.BRIGHT_BLACK, Color.WHITE]
        
        for i in range(steps):
            sys.stdout.write('\r' + colors[min(i, 1)] + text)
            sys.stdout.flush()
            time.sleep(0.1)
        
        print(Color.RESET)  # 重置颜色并换行
    
    @staticmethod
    def flash(text: str, times: int = 3, delay: float = 0.2):
        """闪烁效果"""
        for i in range(times):
            sys.stdout.write('\r' + text)
            sys.stdout.flush()
            time.sleep(delay)
            sys.stdout.write('\r' + ' ' * len(text))
            sys.stdout.flush()
            time.sleep(delay)
        
        sys.stdout.write('\r' + text + '\n')
        sys.stdout.flush()
    
    @staticmethod
    def loading_dots(message: str = "加载中", duration: float = 3.0):
        """加载动画"""
        start_time = time.time()
        while time.time() - start_time < duration:
            for dots in ['', '.', '..', '...']:
                sys.stdout.write(f'\r{message}{dots}   ')
                sys.stdout.flush()
                time.sleep(0.3)
        
        sys.stdout.write('\r' + ' ' * (len(message) + 6) + '\r')
        sys.stdout.flush()


class ASCIIArt:
    """ASCII艺术"""
    
    def __init__(self):
        self.arts = {
            "sword": """
       /\\
      /  \\
     /    \\
    /      \\
   /________\\
       ||
       ||
       ||
      ====
            """,
            "mountain": """
       /\\
      /  \\
     /    \\
    /  /\\  \\
   /  /  \\  \\
  /__/    \\__\\
            """,
            "cultivation": """
     _()_
    / __ \\
   | (  ) |
   | |  | |
   |_|  |_|
    \\    /
     \\  /
      \\/
            """,
            "treasure": """
     ___
    /   \\
   |  $  |
   |_____|
   [_____]
            """,
            "portal": """
    .-..-..-.
   /  ||  ||  \\
  |   ||  ||   |
  |   ||  ||   |
   \\  ||  ||  /
    '-''-''-'
            """
        }
    
    def get(self, name: str) -> Optional[str]:
        """获取ASCII艺术"""
        return self.arts.get(name)
    
    def add(self, name: str, art: str):
        """添加新的ASCII艺术"""
        self.arts[name] = art
    
    def random(self) -> str:
        """获取随机ASCII艺术"""
        return random.choice(list(self.arts.values()))


class VisualEffects:
    """视觉效果管理器"""
    
    def __init__(self):
        self.renderer = TextRenderer()
        self.ascii_art = ASCIIArt()
        self.animations_enabled = True
    
    def enable_animations(self):
        """启用动画"""
        self.animations_enabled = True
    
    def disable_animations(self):
        """禁用动画"""
        self.animations_enabled = False
    
    def display_title(self, title: str, subtitle: Optional[str] = None):
        """显示标题"""
        # 主标题
        main_title = self.renderer.colorize(title, "primary")
        if self.renderer.color_enabled:
            main_title = f"{Color.BOLD}{main_title}"
        
        # 创建分隔线
        separator = "=" * len(title)
        
        result = f"\n{separator}\n{main_title}\n"
        
        if subtitle:
            result += self.renderer.colorize(subtitle, "secondary") + "\n"
        
        result += separator + "\n"
        
        return result
    
    def status_bar(self, hp: int, max_hp: int, mp: int, max_mp: int, 
                   exp: int, max_exp: int) -> str:
        """状态栏"""
        hp_bar = self._create_bar(hp, max_hp, 20, Color.RED, "HP")
        mp_bar = self._create_bar(mp, max_mp, 20, Color.BLUE, "MP")
        exp_bar = self._create_bar(exp, max_exp, 20, Color.YELLOW, "EXP")
        
        return f"{hp_bar}\n{mp_bar}\n{exp_bar}"
    
    def _create_bar(self, current: int, maximum: int, width: int, 
                    color: str, label: str) -> str:
        """创建状态条"""
        percentage = current / maximum if maximum > 0 else 0
        filled = int(width * percentage)
        
        bar = "█" * filled + "░" * (width - filled)
        
        if self.renderer.color_enabled:
            bar = f"{color}{bar}{Color.RESET}"
        
        return f"{label:>3}: [{bar}] {current}/{maximum}"
    
    def transition_scene(self, message: str = "场景切换中"):
        """场景转换效果"""
        if self.animations_enabled:
            TextAnimation.loading_dots(message, 1.5)
        else:
            print(message)
    
    def combat_effect(self, effect_type: str = "hit"):
        """战斗特效"""
        effects = {
            "hit": "💥 重击！",
            "critical": "⚡ 暴击！",
            "dodge": "💨 闪避！",
            "block": "🛡️ 格挡！",
            "skill": "✨ 技能发动！"
        }
        
        message = effects.get(effect_type, "💫 攻击！")
        
        if self.animations_enabled:
            TextAnimation.flash(
                self.renderer.colorize(message, "accent"), 
                times=2, 
                delay=0.1
            )
        else:
            print(message)
    
    def show_achievement(self, title: str, description: str):
        """显示成就"""
        achievement_text = f"""
╔══════════════════════════╗
║  🏆 成就解锁！          ║
║  {title:<20}  ║
║  {description:<20}  ║
╚══════════════════════════╝
        """
        
        if self.animations_enabled:
            TextAnimation.fade_in(
                self.renderer.colorize(achievement_text, "success")
            )
        else:
            print(self.renderer.colorize(achievement_text, "success"))


# 全局实例
visual_effects = VisualEffects()
