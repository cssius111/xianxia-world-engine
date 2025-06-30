"""
游戏配置文件 - 统一管理所有配置项
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class GameConfig:
    """游戏配置"""

    # 基础设置
    game_name: str = "仙侠世界引擎"
    version: str = "2.0.0"
    debug_mode: bool = True

    # 游戏平衡
    max_health: int = 100
    base_damage: float = 10.0
    cultivation_exp_multiplier: float = 1.0

    # API设置
    deepseek_api_key: str = ""
    api_timeout: int = 15
    api_max_retries: int = 3

    # 性能设置
    cache_size: int = 1000
    max_npcs_in_memory: int = 50
    auto_save_interval: int = 300  # 秒
    data_cache_ttl: int = 300
    smart_cache_ttl: int = 300
    smart_cache_size: int = 128

    # 路径设置
    data_path: str | Path | None = "xwe/data"
    save_path: str = "saves"
    log_path: str = "logs"

    def __post_init__(self):
        """初始化后处理"""
        # 从环境变量读取API密钥
        if not self.deepseek_api_key:
            self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "")

        # 将数据路径转换为 Path
        if self.data_path is not None:
            self.data_path = Path(self.data_path)
            if not self.data_path.exists():
                os.makedirs(self.data_path, exist_ok=True)

        # 确保路径存在
        for path_attr in ["save_path", "log_path"]:
            path = getattr(self, path_attr)
            if path and not os.path.exists(path):
                os.makedirs(path, exist_ok=True)


# 全局配置实例
config = GameConfig()
