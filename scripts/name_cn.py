#!/usr/bin/env python3
"""中文姓名生成器"""

import json
import random
from pathlib import Path
from typing import List, Optional


DATA_PATH = Path(__file__).resolve().parent.parent / "data/names_common.json"


def _load_name_data() -> Optional[dict]:
    """加载姓名数据"""
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def random_name() -> str:
    """生成一个随机中文姓名"""
    data = _load_name_data()
    if not data:
        return "无名侠客"

    surnames: List[str] = data.get("surnames", [])
    given_names: List[str] = data.get("given_names", [])
    if not surnames or not given_names:
        return "无名侠客"

    surname = random.choice(surnames)
    given = random.choice(given_names)
    return f"{surname}{given}"


if __name__ == "__main__":
    print(random_name())
