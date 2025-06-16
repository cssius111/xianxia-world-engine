import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional


CONFIG_PATH = Path(__file__).resolve().parents[1] / "data" / "restructured" / "character_creation_config.json"


class RandomPlayerPanel:
    """角色创建面板逻辑，支持随机与自定义模式"""

    def __init__(self, game_mode: str = "player", config_path: Optional[Path] = None) -> None:
        self.game_mode = game_mode
        self.config_path = config_path or CONFIG_PATH
        self.config = self._load_config()
        self.mode_cfg = self.config.get("mode_config", {}).get(game_mode, {})
        self.max_stat_value = int(self.mode_cfg.get("max_stat_value", 20))

    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ---------------------------------------------------------------
    # 配置读取
    # ---------------------------------------------------------------
    def get_origins(self) -> List[Dict[str, Any]]:
        origins = self.config.get("origins", [])
        if not self.mode_cfg.get("show_hidden_origins", False):
            origins = [o for o in origins if not o.get("hidden")]
        if not self.mode_cfg.get("show_all_options", False):
            origins = origins[:3]
        return origins

    def get_spiritual_roots(self) -> List[Dict[str, Any]]:
        return self.config.get("spiritual_roots", [])

    def get_talents(self) -> List[Dict[str, Any]]:
        talents = self.config.get("initial_talents", [])
        if not self.mode_cfg.get("unlock_all_talents", False):
            talents = [t for t in talents if t.get("id") != "none"]
        return talents

    # ---------------------------------------------------------------
    # 随机生成
    # ---------------------------------------------------------------
    def random_name(self) -> str:
        surnames = ["李", "王", "赵", "张", "欧阳", "司马"]
        given = ["云", "凡", "灵", "雪", "风", "剑", "龙"]
        return random.choice(surnames) + random.choice(given)

    def random_attributes(self) -> Dict[str, int]:
        attrs = {"constitution": 5, "comprehension": 5, "spirit": 5, "luck": 5}
        points = 10
        keys = list(attrs.keys())
        while points > 0:
            k = random.choice(keys)
            if attrs[k] < self.max_stat_value:
                attrs[k] += 1
                points -= 1
        return attrs

    def random_character(self) -> Dict[str, Any]:
        return {
            "name": self.random_name(),
            "gender": random.choice(["male", "female"]),
            "background": random.choice(self.get_origins()).get("id"),
            "attributes": self.random_attributes(),
        }

    # ---------------------------------------------------------------
    # 自定义处理
    # ---------------------------------------------------------------
    def sanitize_attributes(self, attributes: Dict[str, Any]) -> Dict[str, int]:
        clean = {}
        for k in ["constitution", "comprehension", "spirit", "luck"]:
            value = int(attributes.get(k, 5))
            if value < 1:
                value = 1
            if value > self.max_stat_value:
                value = self.max_stat_value
            clean[k] = value
        return clean


