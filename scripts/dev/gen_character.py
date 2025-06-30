#!/usr/bin/env python3
import json
import os
import random
from pathlib import Path
from typing import Dict

# 基础数据：姓名、灵根和八维属性
SURNAMES = ["林", "张", "王", "李", "陈", "云", "苏", "白", "萧", "叶"]
GIVEN_NAMES = ["天", "云", "风", "辰", "宇", "逸", "浩", "轩", "凌", "霄",
              "雪", "月", "霜", "梦", "瑶", "婉", "清", "灵", "曦", "萱"]
SPIRITUAL_ROOTS = ["金", "木", "水", "火", "土", "雷", "冰", "风", "光", "暗"]
ATTR_KEYS = [
    "comprehension",
    "constitution",
    "fortune",
    "charisma",
    "willpower",
    "perception",
    "destiny",
    "opportunity",
]


def _random_name() -> str:
    return random.choice(SURNAMES) + random.choice(GIVEN_NAMES)


def _random_attributes() -> Dict[str, int]:
    return {k: random.randint(1, 10) for k in ATTR_KEYS}


def gen_random() -> Dict[str, object]:
    """随机生成角色数据"""
    return {
        "name": _random_name(),
        "age": random.randint(16, 25),
        "spiritual_root": random.choice(SPIRITUAL_ROOTS),
        "attributes": _random_attributes(),
    }


def gen_template(template_type: str) -> Dict[str, object]:
    """根据模板类型生成角色"""
    char = gen_random()
    if template_type == "sword":
        char["spiritual_root"] = random.choice(["金", "火", "雷"])
        char["attributes"]["comprehension"] = min(10, char["attributes"]["comprehension"] + 2)
        char["attributes"]["perception"] = min(10, char["attributes"]["perception"] + 1)
    elif template_type == "body":
        char["spiritual_root"] = random.choice(["土", "金", "木"])
        char["attributes"]["constitution"] = min(10, char["attributes"]["constitution"] + 2)
        char["attributes"]["willpower"] = min(10, char["attributes"]["willpower"] + 1)
    return char


def gen_from_prompt(prompt: str) -> Dict[str, object]:
    """使用用户提供的提示词生成角色(简化实现)"""
    char = gen_random()
    # 从提示词中提取前两个汉字作为名字
    if prompt:
        name = "".join(c for c in prompt if ord(c) > 127)[:2]
        if name:
            char["name"] = name
    return char


def save_character(character: Dict[str, object], path: str | os.PathLike = "generated_characters.jsonl") -> None:
    """将角色数据追加保存为 JSONL"""
    p = Path(path)
    line = json.dumps(character, ensure_ascii=False)
    with p.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


if __name__ == "__main__":
    char = gen_random()
    print(json.dumps(char, ensure_ascii=False, indent=2))
