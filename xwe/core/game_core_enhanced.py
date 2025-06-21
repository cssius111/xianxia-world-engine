"""
增强版游戏核心
包含额外的功能和优化
"""

from xwe.core.game_core import GameCore
from typing import Optional


def create_enhanced_game(game_mode: str = "player") -> GameCore:
    """
    创建增强版游戏实例
    
    Args:
        game_mode: 游戏模式 ("player" 或 "dev")
    
    Returns:
        配置好的游戏实例
    """
    # 创建基础游戏实例
    game = GameCore(game_mode=game_mode)
    
    # 添加增强功能
    _setup_enhanced_features(game)
    
    return game


def _setup_enhanced_features(game: GameCore) -> None:
    """设置增强功能"""
    # 开发模式特殊配置
    if game.game_mode == "dev":
        # 启用所有GM命令
        game.game_state.flags["gm_enabled"] = True
        
        # 跳过新手教程
        game.game_state.flags["tutorial_completed"] = True
        
        # 添加调试信息输出
        import logging
        logging.getLogger("xwe").setLevel(logging.DEBUG)
    
    # 优化性能设置
    if hasattr(game, "config"):
        game.config.cache_size = 2000  # 增加缓存大小
        game.config.auto_save_interval = 600  # 10分钟自动保存
    
    # 注册额外的命令处理器
    _register_custom_commands(game)


def _register_custom_commands(game: GameCore) -> None:
    """注册自定义命令"""
    # 添加快捷命令
    if hasattr(game, "command_parser"):
        shortcuts = {
            "s": "状态",
            "i": "背包",
            "m": "地图",
            "h": "帮助",
            "q": "退出"
        }
        
        for short, full in shortcuts.items():
            # 这里简化处理，实际应该修改命令解析器
            pass


class EnhancedGameCore(GameCore):
    """
    增强版游戏核心类
    
    添加了额外的功能和优化
    """
    
    def __init__(self, data_path: Optional[str] = None, game_mode: str = "player"):
        super().__init__(data_path, game_mode)
        
        # 添加增强功能
        self._enhanced_features = {
            "auto_combat": False,
            "quick_travel": False,
            "enhanced_ui": True
        }
    
    def enable_feature(self, feature: str) -> bool:
        """启用增强功能"""
        if feature in self._enhanced_features:
            self._enhanced_features[feature] = True
            return True
        return False
    
    def disable_feature(self, feature: str) -> bool:
        """禁用增强功能"""
        if feature in self._enhanced_features:
            self._enhanced_features[feature] = False
            return True
        return False
    
    def get_feature_status(self, feature: str) -> Optional[bool]:
        """获取功能状态"""
        return self._enhanced_features.get(feature)


# 导出
__all__ = ["create_enhanced_game", "EnhancedGameCore"]
