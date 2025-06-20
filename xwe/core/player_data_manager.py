"""
玩家数据管理系统
提供随机成长与持久化存档功能
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class PlayerDataManager:
    """负责玩家存档与修炼数据的管理器"""

    def __init__(self, save_dir: str = "saves") -> None:
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)

        self.player_file = self.save_dir / "player.json"
        self.history_file = self.save_dir / "history.json"
        self.settings_file = self.save_dir / "settings.json"

        # 加载数据
        self.player_data = self._load_player_data()
        self.history = self._load_history()
        self.settings = self._load_settings()

    def _load_player_data(self) -> Dict[str, Any]:
        """加载玩家数据"""
        if self.player_file.exists():
            with open(self.player_file, "r", encoding="utf-8") as f:
                return json.load(f)

        # 初始化新玩家
        return {
            "name": "无名修士",
            "level": 1,
            "realm": "炼气期一层",
            "exp": 0,
            "next_level_exp": 100,
            "attributes": {
                "strength": 10 + random.randint(-2, 2),
                "agility": 10 + random.randint(-2, 2),
                "intelligence": 10 + random.randint(-2, 2),
                "vitality": 10 + random.randint(-2, 2),
                "luck": 10 + random.randint(-2, 2),
            },
            "resources": {
                "spiritual_power": 100,
                "max_spiritual_power": 100,
                "health": 100,
                "max_health": 100,
                "stamina": 100,
                "max_stamina": 100,
            },
            "cultivation": {
                "total_days": 0,
                "breakthrough_count": 0,
                "cultivation_speed": 1.0 + random.random() * 0.5,
                "enlightenment_chance": 0.01,
            },
            "inventory": {},
            "skills": [],
            "achievements": [],
            "created_at": datetime.now().isoformat(),
            "last_save": datetime.now().isoformat(),
        }

    def _load_history(self) -> List[Dict[str, Any]]:
        """加载历史记录"""
        if self.history_file.exists():
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _load_settings(self) -> Dict[str, Any]:
        """加载设置"""
        if self.settings_file.exists():
            with open(self.settings_file, "r", encoding="utf-8") as f:
                return json.load(f)

        return {
            "difficulty": "normal",
            "auto_save": True,
            "random_events": True,
            "cultivation_multiplier": 1.0,
        }

    def save_all(self) -> None:
        """保存所有数据"""
        # 更新最后保存时间
        self.player_data["last_save"] = datetime.now().isoformat()

        # 保存玩家数据
        with open(self.player_file, "w", encoding="utf-8") as f:
            json.dump(self.player_data, f, ensure_ascii=False, indent=2)

        # 保存历史（只保留最新1000条）
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history[-1000:], f, ensure_ascii=False, indent=2)

        # 保存设置
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    def cultivate_dynamic(self, duration_days: int = 1) -> Dict[str, Any]:
        """
        动态修炼 - 每次都有随机性
        """
        results = {
            "duration": duration_days,
            "total_exp": 0,
            "attribute_gains": {},
            "events": [],
            "breakthroughs": [],
            "resource_changes": {},
        }

        player = self.player_data
        base_speed = player["cultivation"]["cultivation_speed"]

        for day in range(duration_days):
            # 每日基础收益（随机）
            daily_exp = random.randint(10, 30) * base_speed * player["level"]

            # 随机事件
            if random.random() < 0.1:  # 10%概率
                event = self._generate_random_event()
                results["events"].append(event)
                daily_exp *= event["exp_modifier"]

                # 事件可能影响属性
                if "attribute_changes" in event:
                    for attr, change in event["attribute_changes"].items():
                        player["attributes"][attr] += change
                        results["attribute_gains"][attr] = (
                            results["attribute_gains"].get(attr, 0) + change
                        )

            # 顿悟机会
            if random.random() < player["cultivation"]["enlightenment_chance"]:
                enlightenment = self._generate_enlightenment()
                results["events"].append(enlightenment)
                daily_exp *= enlightenment["exp_modifier"]

                # 顿悟提升悟性
                player["cultivation"]["enlightenment_chance"] *= 1.1

            # 累计经验
            results["total_exp"] += daily_exp
            player["exp"] += daily_exp

            # 消耗资源
            stamina_cost = random.randint(5, 15)
            spiritual_cost = random.randint(3, 10)

            player["resources"]["stamina"] = max(0, player["resources"]["stamina"] - stamina_cost)
            player["resources"]["spiritual_power"] = max(
                0, player["resources"]["spiritual_power"] - spiritual_cost
            )

            results["resource_changes"]["stamina"] = (
                results["resource_changes"].get("stamina", 0) - stamina_cost
            )
            results["resource_changes"]["spiritual_power"] = (
                results["resource_changes"].get("spiritual_power", 0) - spiritual_cost
            )

            # 检查升级
            while player["exp"] >= player["next_level_exp"]:
                level_up = self._level_up()
                results["events"].append(level_up)

            # 检查突破
            if self._can_breakthrough():
                breakthrough = self._attempt_breakthrough()
                if breakthrough["success"]:
                    results["breakthroughs"].append(breakthrough)

        # 更新修炼天数
        player["cultivation"]["total_days"] += duration_days

        # 记录历史
        self._add_history("cultivate", results)

        # 自动保存
        if self.settings["auto_save"]:
            self.save_all()

        return results

    def _generate_random_event(self) -> Dict[str, Any]:
        """生成随机事件"""
        events = [
            {
                "name": "灵气潮汐",
                "description": "天地灵气突然浓郁，修炼效果大增！",
                "exp_modifier": 2.0,
                "type": "positive",
            },
            {
                "name": "心魔侵扰",
                "description": "修炼中遭遇心魔，虽然最终克服，但消耗巨大。",
                "exp_modifier": 0.5,
                "attribute_changes": {"vitality": -1},
                "type": "negative",
            },
            {
                "name": "意外发现",
                "description": "在修炼中发现了一处隐藏的灵脉！",
                "exp_modifier": 1.5,
                "attribute_changes": {"luck": 1},
                "type": "positive",
            },
            {
                "name": "走火入魔",
                "description": "修炼过急，差点走火入魔，幸好及时调整。",
                "exp_modifier": 0.3,
                "attribute_changes": {"vitality": -2, "intelligence": 1},
                "type": "negative",
            },
        ]

        event = random.choice(events)
        event["timestamp"] = datetime.now().isoformat()
        return event

    def _generate_enlightenment(self) -> Dict[str, Any]:
        """生成顿悟事件"""
        enlightenments = [
            {
                "name": "天道感悟",
                "description": "突然对天道有了一丝明悟，修为大进！",
                "exp_modifier": 5.0,
            },
            {
                "name": "剑意初成",
                "description": "在修炼中领悟了一丝剑意！",
                "exp_modifier": 3.0,
                "skill_gained": "初级剑意",
            },
            {
                "name": "道心通明",
                "description": "道心变得更加通透，修炼速度永久提升！",
                "exp_modifier": 2.0,
                "permanent_bonus": {"cultivation_speed": 0.1},
            },
        ]

        enlightenment = random.choice(enlightenments)
        enlightenment["type"] = "enlightenment"
        enlightenment["timestamp"] = datetime.now().isoformat()

        # 应用永久加成
        if "permanent_bonus" in enlightenment:
            for key, value in enlightenment["permanent_bonus"].items():
                self.player_data["cultivation"][key] += value

        return enlightenment

    def _level_up(self) -> Dict[str, Any]:
        """升级"""
        old_level = self.player_data["level"]
        self.player_data["level"] += 1

        # 升级后的经验需求
        self.player_data["next_level_exp"] = int(100 * (1.5 ** self.player_data["level"]))

        # 随机属性提升
        attr_gains: Dict[str, Any] = {}
        for attr in self.player_data["attributes"]:
            gain = random.randint(1, 3)
            self.player_data["attributes"][attr] += gain
            attr_gains[attr] = gain

        # 资源上限提升
        self.player_data["resources"]["max_health"] += random.randint(10, 20)
        self.player_data["resources"]["max_spiritual_power"] += random.randint(5, 15)
        self.player_data["resources"]["max_stamina"] += random.randint(5, 10)

        return {
            "type": "level_up",
            "name": "等级提升",
            "description": f"恭喜！等级从{old_level}提升到{self.player_data['level']}",
            "attribute_gains": attr_gains,
        }

    def _can_breakthrough(self) -> bool:
        """检查是否可以突破"""
        realm_requirements = {
            "炼气期一层": {"level": 10, "exp": 1000},
            "炼气期二层": {"level": 20, "exp": 5000},
            "炼气期三层": {"level": 30, "exp": 15000},
            "筑基期": {"level": 50, "exp": 50000},
        }

        current_realm = self.player_data["realm"]
        if current_realm in realm_requirements:
            req = realm_requirements[current_realm]
            return (
                self.player_data["level"] >= req["level"] and self.player_data["exp"] >= req["exp"]
            )

        return False

    def _attempt_breakthrough(self) -> Dict[str, Any]:
        """尝试突破"""
        # 突破成功率基于属性
        success_rate = 0.3
        success_rate += self.player_data["attributes"]["intelligence"] * 0.01
        success_rate += self.player_data["attributes"]["luck"] * 0.005
        success_rate = min(0.95, success_rate)  # 最高95%成功率

        success = random.random() < success_rate

        if success:
            # 境界提升
            realm_progression = {
                "炼气期一层": "炼气期二层",
                "炼气期二层": "炼气期三层",
                "炼气期三层": "筑基期",
                "筑基期": "筑基中期",
            }

            old_realm = self.player_data["realm"]
            new_realm = realm_progression.get(old_realm, old_realm)
            self.player_data["realm"] = new_realm
            self.player_data["cultivation"]["breakthrough_count"] += 1

            # 大幅提升属性
            for attr in self.player_data["attributes"]:
                self.player_data["attributes"][attr] += random.randint(5, 10)

            # 提升资源上限
            self.player_data["resources"]["max_health"] += 50
            self.player_data["resources"]["max_spiritual_power"] += 30

            return {
                "success": True,
                "type": "breakthrough",
                "name": "境界突破",
                "description": f"突破成功！从{old_realm}晋升到{new_realm}！",
                "old_realm": old_realm,
                "new_realm": new_realm,
            }
        else:
            # 突破失败
            damage = random.randint(20, 40)
            self.player_data["resources"]["health"] -= damage
            self.player_data["exp"] = int(self.player_data["exp"] * 0.9)  # 损失10%经验

            return {
                "success": False,
                "type": "breakthrough_failed",
                "name": "突破失败",
                "description": f"突破失败！受到{damage}点反噬伤害，损失部分经验。",
            }

    def _add_history(self, action: str, data: Dict[str, Any]) -> None:
        """添加历史记录"""
        entry = {
            "id": len(self.history) + 1,
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "data": data,
            "player_snapshot": {
                "level": self.player_data["level"],
                "realm": self.player_data["realm"],
                "exp": self.player_data["exp"],
                "attributes": self.player_data["attributes"].copy(),
            },
        }

        self.history.append(entry)

    def get_status_report(self) -> str:
        """获取状态报告"""
        player = self.player_data

        report = f"""
=== 角色状态 ===
姓名：{player['name']}
境界：{player['realm']} (Lv.{player['level']})
经验：{player['exp']}/{player['next_level_exp']}

=== 属性 ===
力量：{player['attributes']['strength']}
敏捷：{player['attributes']['agility']}
智力：{player['attributes']['intelligence']}
体质：{player['attributes']['vitality']}
幸运：{player['attributes']['luck']}

=== 资源 ===
生命：{player['resources']['health']}/{player['resources']['max_health']}
灵力：{player['resources']['spiritual_power']}/{player['resources']['max_spiritual_power']}
体力：{player['resources']['stamina']}/{player['resources']['max_stamina']}

=== 修炼信息 ===
总修炼天数：{player['cultivation']['total_days']}
突破次数：{player['cultivation']['breakthrough_count']}
修炼速度：{player['cultivation']['cultivation_speed']:.2f}x
顿悟几率：{player['cultivation']['enlightenment_chance']*100:.1f}%
"""
        return report

    def get_history_summary(self, limit: int = 10) -> str:
        """获取历史摘要"""
        if not self.history:
            return "暂无修炼记录"

        summary = "=== 最近修炼记录 ===\n"

        for entry in self.history[-limit:]:
            timestamp = entry["timestamp"].split("T")[0]
            action = entry["action"]

            if action == "cultivate":
                data = entry["data"]
                exp_gained = data.get("total_exp", 0)
                duration = data.get("duration", 0)
                events = len(data.get("events", []))

                summary += f"\n[{timestamp}] 修炼{duration}天，获得{exp_gained:.0f}经验"
                if events > 0:
                    summary += f"，发生{events}个事件"

        return summary
