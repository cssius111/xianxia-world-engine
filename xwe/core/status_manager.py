# status_display_manager.py
"""
智能状态显示管理系统
只在需要时显示状态条，避免界面混乱
"""
import time
from typing import Any, Dict, Optional

class StatusDisplayManager:
    def __init__(self) -> None:
        self.display_contexts = {
            'battle': True,      # 战斗中始终显示
            'cultivation': True, # 修炼中显示
            'transaction': True, # 交易时显示
            'level_up': True,    # 升级时显示
            'injury': True,      # 受伤时显示
        }
        self.last_display_time = 0
        self.display_duration = 5  # 显示持续时间（秒）
        self.current_context = 'exploration'  # 当前场景
        self.force_display = False  # 强制显示标志
        
    def should_display_status(self, context=None, user_command=None) -> Any:
        """判断是否应该显示状态条"""
        
        # 玩家主动查看
        if user_command and self._is_status_command(user_command):
            self.force_display = True
            self.last_display_time = time.time()
            return True
            
        # 特定场景自动显示
        if context:
            self.current_context = context
            
        if self.current_context in self.display_contexts:
            return self.display_contexts[self.current_context]
            
        # 临时强制显示（如刚查看过状态）
        if self.force_display:
            if time.time() - self.last_display_time < self.display_duration:
                return True
            else:
                self.force_display = False
                
        return False
        
    def _is_status_command(self, command) -> Any:
        """检查是否是查看状态的命令"""
        status_commands = [
            '查看状态', '状态', 'status', 'stat', 
            '属性', '查看属性', '我的状态', '角色信息'
        ]
        return command.lower().strip() in status_commands
        
    def format_status_bar(self, player) -> Any:
        """格式化状态条显示"""
        if not self.should_display_status():
            return self._get_minimal_prompt()
            
        # 根据场景选择不同的状态条样式
        if self.current_context == 'battle':
            return self._format_battle_status(player)
        elif self.current_context == 'cultivation':
            return self._format_cultivation_status(player)
        else:
            return self._format_general_status(player)
            
    def _get_minimal_prompt(self) -> Any:
        """最小化提示"""
        return "💡 提示：输入'查看状态'查看详细属性 | 输入'帮助'查看所有命令"
        
    def _format_battle_status(self, player) -> Any:
        """战斗状态条"""
        hp_percent = player.attributes.current_health / player.attributes.max_health
        mp_percent = player.attributes.current_mana / player.attributes.max_mana
        
        hp_bar = self._create_bar(hp_percent, 20, '❤️')
        mp_bar = self._create_bar(mp_percent, 20, '💙')
        
        status = f"""
╔═══════════════════════════════════════╗
║ {player.name} - {player.get_realm_info()}         
║ 气血: {hp_bar} {player.attributes.current_health:.0f}/{player.attributes.max_health:.0f}
║ 灵力: {mp_bar} {player.attributes.current_mana:.0f}/{player.attributes.max_mana:.0f}
║ 攻击: {player.attributes.get('attack_power', 0):.0f} | 防御: {player.attributes.get('defense', 0):.0f}
╚═══════════════════════════════════════╝
"""
        return status
        
    def _format_cultivation_status(self, player) -> Any:
        """修炼状态条"""
        # 简化处理，因为游戏中没有明确的经验值系统
        cultivation_progress = 0.3  # 示例进度
        exp_bar = self._create_bar(cultivation_progress, 30, '✨')
        
        status = f"""
╔═══════════════════════════════════════╗
║ 修炼进度                              
║ 境界: {player.get_realm_info()}
║ 进度: {exp_bar}
║ 灵力流转中... 🧘
╚═══════════════════════════════════════╝
"""
        return status
        
    def _format_general_status(self, player) -> Any:
        """通用状态条"""
        status = f"""
╔═══════════════════════════════════════╗
║ {player.name} - {player.get_realm_info()}         
║ 气血: {player.attributes.current_health:.0f}/{player.attributes.max_health:.0f} | 灵力: {player.attributes.current_mana:.0f}/{player.attributes.max_mana:.0f}
║ 攻击: {player.attributes.get('attack_power', 0):.0f} | 防御: {player.attributes.get('defense', 0):.0f}
║ 位置: {player.extra_data.get('location', '未知')}
╚═══════════════════════════════════════╝
"""
        return status
        
    def _create_bar(self, percent, length, symbol) -> Any:
        """创建进度条"""
        filled = int(percent * length)
        bar = symbol * filled + '░' * (length - filled)
        return f"[{bar}]"
        
    def enter_context(self, context) -> None:
        """进入特定场景"""
        self.current_context = context
        
    def exit_context(self) -> None:
        """退出特定场景，回到探索模式"""
        self.current_context = 'exploration'
        self.force_display = False
