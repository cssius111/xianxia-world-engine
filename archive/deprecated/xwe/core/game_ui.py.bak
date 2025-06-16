"""
游戏UI模块 - 处理修炼进度等显示
"""

import time
import sys

class GameUI:
    """游戏UI管理器"""
    
    def __init__(self):
        self.last_status = None
    
    def display_cultivation_result(self, duration: str, gained_exp: int, player_status=None) -> None:
        """显示修炼结果"""
        print(f"\n{'='*50}")
        print(f"🧘 修炼完成！")
        print(f"⏱️  修炼时长: {duration}")
        print(f"✨ 获得经验: {gained_exp} 点")
        
        if player_status:
            level_info = f"📊 当前境界: {player_status.get('realm', '未知')} {player_status.get('level', 0)}层"
            exp_info = f"📈 经验进度: {player_status.get('exp', 0)}/{player_status.get('exp_required', 100)}"
            print(level_info)
            print(exp_info)
            
            # 检查是否突破
            if player_status.get('breakthrough', False):
                print(f"\n🎉 恭喜突破到 {player_status['new_realm']}！")
        
        print(f"{'='*50}\n")
        
        # 显示进度条动画
        self.show_progress_bar(duration_seconds=2, label="消化修为中")
    
    def show_progress_bar(self, duration_seconds=3, label="处理中") -> None:
        """显示进度条动画"""
        total_width = 40
        for i in range(duration_seconds * 10):
            progress = (i + 1) / (duration_seconds * 10)
            filled = int(total_width * progress)
            bar = "█" * filled + "░" * (total_width - filled)
            percentage = int(progress * 100)
            print(f"\r{label}: [{bar}] {percentage}%", end="", flush=True)
            time.sleep(0.1)
        print("\r" + " " * 60 + "\r", end="", flush=True)  # 清除进度条
    
    def display_status_change(self, old_status, new_status) -> None:
        """显示状态变化"""
        changes = []
        
        # 检查等级变化
        if old_status.get('level') != new_status.get('level'):
            changes.append(f"等级提升: {old_status['level']} → {new_status['level']}")
        
        # 检查属性变化
        for attr in ['hp', 'mp', 'stamina']:
            if old_status.get(attr) != new_status.get(attr):
                changes.append(f"{attr.upper()}: {old_status.get(attr, 0)} → {new_status.get(attr, 0)}")
        
        if changes:
            print("\n📋 状态变化:")
            for change in changes:
                print(f"  • {change}")
    
    def display_cultivation_preview(self, duration: str) -> None:
        """显示修炼预览"""
        print(f"\n🧘 开始修炼 {duration}...")
        self.show_progress_bar(duration_seconds=1, label="准备中")

# 全局UI实例
game_ui = GameUI()
