"""
NPC系统优化实现
使用数据驱动的方式管理NPC行为和交互
"""

import logging
import random
from typing import Any, Dict, List, Optional, Tuple

from xwe.core.data_manager import DM
from xwe.core.formula_engine import evaluate_expression, formula_engine

logger = logging.getLogger(__name__)


class NPCSystemV3:
    """
    数据驱动的NPC系统V3
    从JSON配置加载所有NPC数据和行为模式
    """

    def __init__(self) -> None:
        self.npc_data = {}
        self.npcs = {}  # {npc_id: NPC instance}
        self.dialogue_states = {}  # {player_id: {npc_id: dialogue_state}}
        self.relationships = {}  # {player_id: {npc_id: relationship_value}}
        self._load_npc_data()

    def _load_npc_data(self) -> None:
        """加载NPC系统数据"""
        try:
            self.npc_data = DM.load("npc_template")
            logger.info("NPC system data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load NPC data: {e}")
            raise

    def create_npc(self, npc_id: str, template_id: Optional[str] = None) -> "NPC":
        """
        创建NPC实例

        Args:
            npc_id: NPC唯一标识
            template_id: 模板ID，如果为None则使用npc_id作为模板

        Returns:
            NPC实例
        """
        template_id = template_id or npc_id

        # 查找模板
        template = None
        for npc_template in self.npc_data.get("npcs", []):
            if npc_template["id"] == template_id:
                template = npc_template
                break

        if not template:
            raise ValueError(f"NPC template not found: {template_id}")

        # 创建NPC实例
        npc = NPC(self, npc_id, template)
        self.npcs[npc_id] = npc

        return npc

    def get_npc(self, npc_id: str) -> Optional["NPC"]:
        """获取NPC实例"""
        return self.npcs.get(npc_id)

    def create_npcs_for_location(self, location_id: str) -> List["NPC"]:
        """为特定地点创建NPC"""
        created_npcs = []

        for npc_template in self.npc_data.get("npcs", []):
            spawn_locations = npc_template.get("spawn_locations", [])
            if location_id in spawn_locations:
                # 检查生成概率
                spawn_chance = npc_template.get("spawn_chance", 1.0)
                if random.random() < spawn_chance:
                    npc_id = f"{npc_template['id']}_{location_id}"
                    if npc_id not in self.npcs:
                        npc = self.create_npc(npc_id, npc_template["id"])
                        created_npcs.append(npc)

        return created_npcs

    def get_dialogue_state(self, player_id: str, npc_id: str) -> Dict[str, Any]:
        """获取对话状态"""
        if player_id not in self.dialogue_states:
            self.dialogue_states[player_id] = {}

        if npc_id not in self.dialogue_states[player_id]:
            self.dialogue_states[player_id][npc_id] = {
                "current_node": "greeting",
                "flags": {},
                "history": [],
            }

        return self.dialogue_states[player_id][npc_id]

    def update_dialogue_state(
        self, player_id: str, npc_id: str, new_node: str, flags: Optional[Dict] = None
    ):
        """更新对话状态"""
        state = self.get_dialogue_state(player_id, npc_id)
        state["current_node"] = new_node

        if flags:
            state["flags"].update(flags)

        state["history"].append(new_node)

        # 限制历史记录长度
        if len(state["history"]) > 50:
            state["history"] = state["history"][-25:]

    def get_relationship(self, player_id: str, npc_id: str) -> int:
        """获取关系值"""
        if player_id not in self.relationships:
            self.relationships[player_id] = {}

        return self.relationships[player_id].get(npc_id, 0)

    def modify_relationship(self, player_id: str, npc_id: str, amount: int) -> Any:
        """修改关系值"""
        if player_id not in self.relationships:
            self.relationships[player_id] = {}

        current = self.relationships[player_id].get(npc_id, 0)
        new_value = max(-100, min(100, current + amount))
        self.relationships[player_id][npc_id] = new_value

        logger.info(
            f"Relationship between {player_id} and {npc_id} changed: {current} -> {new_value}"
        )

        return new_value


class NPC:
    """NPC类"""

    def __init__(self, system: NPCSystemV3, npc_id: str, template: Dict[str, Any]) -> None:
        self.system = system
        self.id = npc_id
        self.template = template

        # 基础属性
        self.name = template["name"]
        self.title = template.get("title", "")
        self.description = template.get("description", "")
        self.type = template.get("type", "generic")

        # 属性
        self.level = template.get("level", 1)
        self.realm = template.get("realm", "mortal")
        self.attributes = template.get("attributes", {}).copy()

        # 行为
        self.behavior = template.get("behavior", "friendly")
        self.personality = template.get("personality", {})

        # 交易
        self.is_merchant = template.get("merchant", False)
        self.shop_inventory = template.get("shop_inventory", [])
        self.price_modifier = template.get("price_modifier", 1.0)

        # 对话
        self.dialogue_id = template.get("dialogue", npc_id)
        self.dialogue_tree = self._load_dialogue_tree()

        # 任务
        self.quests = template.get("quests", [])

        # 战斗
        self.is_hostile = template.get("hostile", False)
        self.combat_ai = template.get("combat_ai", "defensive")

        # 状态
        self.current_location = None
        self.is_alive = True
        self.schedule = template.get("schedule", {})

    def _load_dialogue_tree(self) -> Dict[str, Any]:
        """加载对话树"""
        # TODO: 从单独的对话文件加载
        # 现在使用模板中的简单对话
        return self.template.get(
            "dialogue_tree",
            {
                "greeting": {
                    "text": f"你好，我是{self.name}。",
                    "options": [{"text": "你好", "next": "greeting"}],
                }
            },
        )

    def interact(self, player) -> Dict[str, Any]:
        """与玩家交互"""
        # 获取关系值
        relationship = self.system.get_relationship(player.id, self.id)

        # 检查是否敌对
        if self.is_hostile or relationship < -50:
            return {
                "type": "combat",
                "message": f"{self.name}对你充满敌意！",
                "trigger_combat": True,
            }

        # 商人交互
        if self.is_merchant and relationship >= -20:
            return {
                "type": "trade",
                "message": f"{self.name}：欢迎光临，看看有什么需要的吗？",
                "shop_inventory": self.get_shop_inventory(player),
            }

        # 对话交互
        return self.start_dialogue(player)

    def start_dialogue(self, player) -> Dict[str, Any]:
        """开始对话"""
        # 获取对话状态
        state = self.system.get_dialogue_state(player.id, self.id)
        current_node = state["current_node"]

        # 获取当前对话节点
        if current_node not in self.dialogue_tree:
            current_node = "greeting"

        node = self.dialogue_tree[current_node]

        # 处理对话文本（替换变量）
        text = self._process_dialogue_text(node["text"], player, state)

        # 过滤可用选项
        options = []
        for option in node.get("options", []):
            if self._check_dialogue_condition(option.get("condition"), player, state):
                options.append(
                    {
                        "text": option["text"],
                        "id": option.get("id", option["text"]),
                        "next": option.get("next", "greeting"),
                    }
                )

        # 如果没有选项，添加默认选项
        if not options:
            options.append({"text": "再见", "id": "goodbye", "next": None})

        return {"type": "dialogue", "npc_name": self.name, "text": text, "options": options}

    def process_dialogue_choice(self, player, choice_id: str) -> Dict[str, Any]:
        """处理对话选择"""
        state = self.system.get_dialogue_state(player.id, self.id)
        current_node = state["current_node"]

        if current_node not in self.dialogue_tree:
            return {"success": False, "message": "对话状态错误"}

        node = self.dialogue_tree[current_node]

        # 找到选择的选项
        selected_option = None
        for option in node.get("options", []):
            if option.get("id", option["text"]) == choice_id:
                selected_option = option
                break

        if not selected_option:
            return {"success": False, "message": "无效的选择"}

        # 执行效果
        result = {"success": True, "effects": []}

        if "effects" in selected_option:
            for effect in selected_option["effects"]:
                effect_result = self._apply_dialogue_effect(effect, player)
                result["effects"].append(effect_result)

        # 更新对话状态
        next_node = selected_option.get("next")
        if next_node:
            self.system.update_dialogue_state(player.id, self.id, next_node)

            # 如果有新的对话，返回它
            if next_node in self.dialogue_tree:
                result["continue_dialogue"] = self.start_dialogue(player)
        else:
            # 对话结束
            result["dialogue_end"] = True
            self.system.update_dialogue_state(player.id, self.id, "greeting")

        return result

    def _process_dialogue_text(self, text: str, player, state: Dict[str, Any]) -> str:
        """处理对话文本"""
        # 替换玩家名称
        text = text.replace("{player_name}", player.name)
        text = text.replace("{npc_name}", self.name)

        # 替换关系描述
        relationship = self.system.get_relationship(player.id, self.id)
        if relationship >= 80:
            rel_desc = "挚友"
        elif relationship >= 50:
            rel_desc = "好友"
        elif relationship >= 20:
            rel_desc = "友善"
        elif relationship >= -20:
            rel_desc = "中立"
        elif relationship >= -50:
            rel_desc = "冷淡"
        else:
            rel_desc = "敌对"

        text = text.replace("{relationship}", rel_desc)

        # 替换状态标记
        for flag, value in state["flags"].items():
            text = text.replace(f"{{{flag}}}", str(value))

        return text

    def _check_dialogue_condition(
        self, condition: Optional[Dict], player, state: Dict[str, Any]
    ) -> bool:
        """检查对话条件"""
        if not condition:
            return True

        cond_type = condition.get("type")

        if cond_type == "relationship":
            required = condition.get("value", 0)
            current = self.system.get_relationship(player.id, self.id)
            return current >= required

        elif cond_type == "flag":
            flag_name = condition.get("flag")
            expected = condition.get("value", True)
            return state["flags"].get(flag_name, False) == expected

        elif cond_type == "item":
            item_id = condition.get("item")
            return player.has_item(item_id)

        elif cond_type == "attribute":
            attr = condition.get("attribute")
            required = condition.get("value", 0)
            return getattr(player.attributes, attr, 0) >= required

        elif cond_type == "custom":
            # 使用公式引擎
            formula = condition.get("formula")
            if formula:
                context = {
                    "player_level": player.level,
                    "relationship": self.system.get_relationship(player.id, self.id),
                    **player.attributes.__dict__,
                }
                try:
                    return bool(evaluate_expression(formula, context))
                except:
                    return False

        return True

    def _apply_dialogue_effect(self, effect: Dict[str, Any], player) -> Dict[str, Any]:
        """应用对话效果"""
        effect_type = effect.get("type")
        result = {"type": effect_type}

        if effect_type == "relationship":
            amount = effect.get("amount", 0)
            new_value = self.system.modify_relationship(player.id, self.id, amount)
            result["message"] = f"与{self.name}的关系{'提升' if amount > 0 else '下降'}了"
            result["new_relationship"] = new_value

        elif effect_type == "give_item":
            item_id = effect.get("item")
            if item_id:
                player.add_item(item_id)
                result["message"] = f"{self.name}给了你: {item_id}"
                result["item"] = item_id

        elif effect_type == "give_quest":
            quest_id = effect.get("quest")
            if quest_id and quest_id in self.quests:
                player.add_quest(quest_id)
                result["message"] = f"接受任务: {quest_id}"
                result["quest"] = quest_id

        elif effect_type == "flag":
            flag_name = effect.get("flag")
            flag_value = effect.get("value", True)
            state = self.system.get_dialogue_state(player.id, self.id)
            state["flags"][flag_name] = flag_value
            result["flag_set"] = {flag_name: flag_value}

        elif effect_type == "teleport":
            destination = effect.get("destination")
            result["teleport_to"] = destination
            result["message"] = f"{self.name}将你传送到了{destination}"

        return result

    def get_shop_inventory(self, player) -> List[Dict[str, Any]]:
        """获取商店库存"""
        if not self.is_merchant:
            return []

        inventory = []
        relationship = self.system.get_relationship(player.id, self.id)

        for item_data in self.shop_inventory:
            item_id = item_data["id"]
            base_price = item_data.get("price", 100)
            stock = item_data.get("stock", -1)  # -1表示无限

            # 根据关系调整价格
            price_multiplier = self.price_modifier
            if relationship >= 50:
                price_multiplier *= 0.8  # 好友折扣
            elif relationship <= -20:
                price_multiplier *= 1.5  # 敌对加价

            final_price = int(base_price * price_multiplier)

            # 检查解锁条件
            if "unlock_condition" in item_data:
                condition = item_data["unlock_condition"]
                if not self._check_unlock_condition(condition, player):
                    continue

            inventory.append(
                {
                    "id": item_id,
                    "name": item_data.get("name", item_id),
                    "price": final_price,
                    "stock": stock,
                    "description": item_data.get("description", ""),
                }
            )

        return inventory

    def _check_unlock_condition(self, condition: Dict[str, Any], player) -> bool:
        """检查解锁条件"""
        # 简化版本，可以扩展
        if "min_level" in condition:
            if player.level < condition["min_level"]:
                return False

        if "min_relationship" in condition:
            if self.system.get_relationship(player.id, self.id) < condition["min_relationship"]:
                return False

        return True

    def process_trade(self, player, item_id: str, action: str = "buy") -> Dict[str, Any]:
        """处理交易"""
        if not self.is_merchant:
            return {"success": False, "message": f"{self.name}不是商人"}

        # 查找物品
        item_data = None
        for item in self.shop_inventory:
            if item["id"] == item_id:
                item_data = item
                break

        if not item_data:
            return {"success": False, "message": "商店没有这个物品"}

        if action == "buy":
            # 计算价格
            base_price = item_data.get("price", 100)
            relationship = self.system.get_relationship(player.id, self.id)

            price_multiplier = self.price_modifier
            if relationship >= 50:
                price_multiplier *= 0.8
            elif relationship <= -20:
                price_multiplier *= 1.5

            final_price = int(base_price * price_multiplier)

            # 检查金钱
            if player.gold < final_price:
                return {"success": False, "message": "金钱不足"}

            # 检查库存
            stock = item_data.get("stock", -1)
            if stock == 0:
                return {"success": False, "message": "物品已售罄"}

            # 执行交易
            player.gold -= final_price
            player.add_item(item_id)

            # 更新库存
            if stock > 0:
                item_data["stock"] = stock - 1

            # 提升关系
            self.system.modify_relationship(player.id, self.id, 1)

            return {
                "success": True,
                "message": f"购买了 {item_data.get('name', item_id)}",
                "cost": final_price,
            }

        elif action == "sell":
            # 出售物品给NPC
            if not player.has_item(item_id):
                return {"success": False, "message": "你没有这个物品"}

            # 计算出售价格（通常是购买价格的一半）
            base_price = item_data.get("price", 100)
            sell_price = int(base_price * 0.5 * self.price_modifier)

            # 执行交易
            player.remove_item(item_id)
            player.gold += sell_price

            return {
                "success": True,
                "message": f"出售了 {item_data.get('name', item_id)}",
                "earned": sell_price,
            }

        return {"success": False, "message": "无效的交易类型"}

    def get_schedule_location(self, game_time: float) -> Optional[str]:
        """根据时间表获取NPC应该在的位置"""
        if not self.schedule:
            return self.current_location

        # 将游戏时间转换为一天中的时间（0-24）
        hour = int(game_time % 24)

        for time_slot, location in self.schedule.items():
            # 解析时间范围，如 "8-12"
            if "-" in time_slot:
                start, end = map(int, time_slot.split("-"))
                if start <= hour < end:
                    return location

        return self.current_location

    def update(self, game_time: float) -> None:
        """更新NPC状态"""
        # 根据时间表更新位置
        scheduled_location = self.get_schedule_location(game_time)
        if scheduled_location and scheduled_location != self.current_location:
            self.current_location = scheduled_location
            logger.debug(f"NPC {self.name} moved to {scheduled_location}")

        # TODO: 其他更新逻辑


# 全局实例
npc_system = NPCSystemV3()


# 导出便捷函数
def create_npc(npc_id: str, template_id: Optional[str] = None) -> NPC:
    """创建NPC的便捷函数"""
    return npc_system.create_npc(npc_id, template_id)


def get_npc(npc_id: str) -> Optional[NPC]:
    """获取NPC的便捷函数"""
    return npc_system.get_npc(npc_id)


def spawn_npcs_for_location(location_id: str) -> List[NPC]:
    """为地点生成NPC的便捷函数"""
    return npc_system.create_npcs_for_location(location_id)
