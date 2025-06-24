#!/usr/bin/env python3
"""
角色生成器
支持随机生成、模板生成和自定义生成
"""

import json
import random
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

from scripts.name_cn import random_name

# 8个核心属性
ATTRIBUTES = [
    "comprehension",  # 悟性
    "constitution",   # 根骨
    "fortune",        # 气运
    "charisma",       # 魅力
    "willpower",      # 毅力
    "perception",     # 感知
    "destiny",        # 天命
    "opportunity"     # 机缘
]

# 灵根类型
SPIRITUAL_ROOTS = ["金", "木", "水", "火", "土", "雷", "冰", "风", "光", "暗"]

# 角色模板
TEMPLATES = {
    "sword": {
        "name": "剑修",
        "description": "专精剑道，攻击凌厉",
        "attributes": {
            "comprehension": (6, 9),
            "constitution": (4, 7),
            "fortune": (3, 7),
            "charisma": (3, 6),
            "willpower": (7, 10),
            "perception": (6, 9),
            "destiny": (3, 7),
            "opportunity": (3, 7)
        },
        "spiritual_root": ["金", "火", "雷"]
    },
    "body": {
        "name": "体修",
        "description": "炼体为主，防御无双",
        "attributes": {
            "comprehension": (3, 6),
            "constitution": (8, 10),
            "fortune": (3, 7),
            "charisma": (3, 6),
            "willpower": (7, 10),
            "perception": (4, 7),
            "destiny": (3, 7),
            "opportunity": (3, 7)
        },
        "spiritual_root": ["土", "金", "木"]
    },
    "talisman": {
        "name": "符修",
        "description": "精通符箓，变化多端",
        "attributes": {
            "comprehension": (7, 10),
            "constitution": (3, 6),
            "fortune": (5, 8),
            "charisma": (4, 7),
            "willpower": (5, 8),
            "perception": (7, 10),
            "destiny": (4, 8),
            "opportunity": (5, 8)
        },
        "spiritual_root": ["水", "木", "光"]
    }
}


def gen_random() -> Dict[str, Any]:
    """
    完全随机生成角色
    每个属性1-10随机
    """
    character = {
        "name": random_name(),
        "age": random.randint(16, 25),
        "spiritual_root": random.choice(SPIRITUAL_ROOTS),
        "attributes": {}
    }
    
    for attr in ATTRIBUTES:
        character["attributes"][attr] = random.randint(1, 10)
    
    character["created_at"] = datetime.now().isoformat()
    character["generation_type"] = "random"
    
    return character


def gen_template(template_type: str) -> Dict[str, Any]:
    """
    根据模板生成角色
    在模板范围内随机
    """
    if template_type not in TEMPLATES:
        template_type = "sword"  # 默认剑修
    
    template = TEMPLATES[template_type]
    character = {
        "name": random_name(),
        "age": random.randint(16, 25),
        "spiritual_root": random.choice(template["spiritual_root"]),
        "attributes": {},
        "template": template_type,
        "template_name": template["name"]
    }
    
    # 根据模板范围生成属性
    for attr in ATTRIBUTES:
        min_val, max_val = template["attributes"][attr]
        character["attributes"][attr] = random.randint(min_val, max_val)
    
    character["created_at"] = datetime.now().isoformat()
    character["generation_type"] = "template"
    
    return character


def gen_from_prompt(prompt: str) -> Dict[str, Any]:
    """
    根据文本描述生成角色
    这里暂时用简单的关键词匹配，后续可接入DeepSeek
    """
    # 简单的关键词映射
    character = {
        "name": "自定义侠客",
        "age": 20,
        "spiritual_root": "金",
        "attributes": {},
        "prompt": prompt
    }
    
    # 基础值都是5
    for attr in ATTRIBUTES:
        character["attributes"][attr] = 5
    
    # 根据关键词调整
    prompt_lower = prompt.lower()
    
    if "聪明" in prompt or "智慧" in prompt or "悟性" in prompt:
        character["attributes"]["comprehension"] = random.randint(7, 10)
    
    if "强壮" in prompt or "体魄" in prompt or "力量" in prompt:
        character["attributes"]["constitution"] = random.randint(7, 10)
    
    if "幸运" in prompt or "运气" in prompt:
        character["attributes"]["fortune"] = random.randint(7, 10)
    
    if "美貌" in prompt or "俊美" in prompt or "魅力" in prompt:
        character["attributes"]["charisma"] = random.randint(7, 10)
    
    if "坚韧" in prompt or "毅力" in prompt or "意志" in prompt:
        character["attributes"]["willpower"] = random.randint(7, 10)
    
    if "敏锐" in prompt or "感知" in prompt or "直觉" in prompt:
        character["attributes"]["perception"] = random.randint(7, 10)
    
    if "天选" in prompt or "命运" in prompt or "天命" in prompt:
        character["attributes"]["destiny"] = random.randint(7, 10)
    
    if "机缘" in prompt or "奇遇" in prompt:
        character["attributes"]["opportunity"] = random.randint(7, 10)
    
    # 选择合适的灵根
    if "火" in prompt or "炎" in prompt:
        character["spiritual_root"] = "火"
    elif "水" in prompt or "冰" in prompt:
        character["spiritual_root"] = "水"
    elif "雷" in prompt or "电" in prompt:
        character["spiritual_root"] = "雷"
    elif "木" in prompt or "生" in prompt:
        character["spiritual_root"] = "木"
    elif "土" in prompt or "山" in prompt:
        character["spiritual_root"] = "土"
    
    character["created_at"] = datetime.now().isoformat()
    character["generation_type"] = "custom"
    
    return character


def save_character(character: Dict[str, Any]) -> None:
    """
    保存角色到日志文件
    """
    log_dir = Path("logs/char_gen")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 按日期命名文件
    date_str = datetime.now().strftime("%Y%m%d")
    log_file = log_dir / f"{date_str}.jsonl"
    
    # 追加写入
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(character, ensure_ascii=False) + "\n")


def check_jackpot(character: Dict[str, Any]) -> Dict[str, Any]:
    """
    检查是否触发保底
    返回保底信息
    """
    high_attrs = sum(1 for v in character["attributes"].values() if v >= 8)
    
    if high_attrs >= 2:
        return {
            "triggered": True,
            "type": "big",
            "title": "✨ 触发大保底！",
            "description": f"你的角色有{high_attrs}项属性达到8以上，天纵奇才！"
        }
    elif high_attrs >= 1:
        return {
            "triggered": True,
            "type": "small",
            "title": "✨ 触发小保底！",
            "description": "你的角色拥有超凡天赋！"
        }
    else:
        return {
            "triggered": False
        }


if __name__ == "__main__":
    # 测试生成
    print("=== 随机生成测试 ===")
    char1 = gen_random()
    print(json.dumps(char1, indent=2, ensure_ascii=False))
    print(f"Jackpot: {check_jackpot(char1)}")
    
    print("\n=== 模板生成测试 ===")
    char2 = gen_template("sword")
    print(json.dumps(char2, indent=2, ensure_ascii=False))
    print(f"Jackpot: {check_jackpot(char2)}")
    
    print("\n=== 自定义生成测试 ===")
    char3 = gen_from_prompt("一个聪明绝顶、运气极好的年轻剑客")
    print(json.dumps(char3, indent=2, ensure_ascii=False))
    print(f"Jackpot: {check_jackpot(char3)}")
