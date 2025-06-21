# world/location_manager.py
"""
位置管理器

管理玩家和NPC的位置，处理移动逻辑。
"""

import logging
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from .world_map import AreaType, WorldMap

logger = logging.getLogger(__name__)


@dataclass
class TravelInfo:
    """旅行信息"""

    from_area: str
    to_area: str
    path: List[str]
    distance: int
    travel_time: int  # 回合数
    stamina_cost: int
    encounters: List[str] = field(default_factory=list)


class LocationManager:
    """
    位置管理器

    管理所有实体的位置和移动。
    """

    def __init__(self, world_map: WorldMap) -> None:
        """
        初始化位置管理器

        Args:
            world_map: 世界地图实例
        """
        self.world_map = world_map
        self.entity_locations: Dict[str, str] = {}  # 实体ID -> 区域ID
        self.area_entities: Dict[str, Set[str]] = {}  # 区域ID -> 实体ID集合

        logger.info("位置管理器初始化")

    def set_location(self, entity_id: str, area_id: str) -> None:
        """
        设置实体位置

        Args:
            entity_id: 实体ID（玩家或NPC）
            area_id: 区域ID
        """
        # 检查区域是否存在
        area = self.world_map.get_area(area_id)
        if not area:
            logger.error(f"尝试设置到不存在的区域: {area_id}")
            return

        # 移除旧位置
        old_location = self.entity_locations.get(entity_id)
        if old_location and old_location in self.area_entities:
            self.area_entities[old_location].discard(entity_id)

        # 设置新位置
        self.entity_locations[entity_id] = area_id

        # 更新区域实体列表
        if area_id not in self.area_entities:
            self.area_entities[area_id] = set()
        self.area_entities[area_id].add(entity_id)

        logger.debug(f"实体 {entity_id} 移动到 {area.name}")

    def get_location(self, entity_id: str) -> Optional[str]:
        """获取实体当前位置"""
        return self.entity_locations.get(entity_id)

    def get_entities_in_area(self, area_id: str) -> List[str]:
        """获取区域内的所有实体"""
        return list(self.area_entities.get(area_id, set()))

    def plan_travel(self, entity_id: str, target_area_id: str) -> Optional[TravelInfo]:
        """
        规划旅行路线

        Args:
            entity_id: 实体ID
            target_area_id: 目标区域ID

        Returns:
            旅行信息，如果无法到达则返回None
        """
        current_area_id = self.get_location(entity_id)
        if not current_area_id:
            return None

        # 查找路径
        path = self.world_map.find_path(current_area_id, target_area_id)
        if not path:
            return None

        # 计算旅行信息
        distance = len(path) - 1

        # 基础旅行时间（每个区域1回合）
        travel_time = distance

        # 计算体力消耗
        stamina_cost = 0
        for i in range(len(path) - 1):
            area = self.world_map.get_area(path[i + 1])
            if area:
                # 根据地形类型计算体力消耗
                terrain_cost = {
                    AreaType.CITY: 5,
                    AreaType.MARKET: 5,
                    AreaType.WILDERNESS: 10,
                    AreaType.FOREST: 15,
                    AreaType.MOUNTAIN: 20,
                    AreaType.CAVE: 15,
                    AreaType.RUINS: 10,
                }
                stamina_cost += terrain_cost.get(area.type, 10)

        # 生成可能的遭遇
        encounters = self._generate_travel_encounters(path)

        return TravelInfo(
            from_area=current_area_id,
            to_area=target_area_id,
            path=path,
            distance=distance,
            travel_time=travel_time,
            stamina_cost=stamina_cost,
            encounters=encounters,
        )

    def move_entity(
        self, entity_id: str, target_area_id: str, player_level: int = 0
    ) -> Tuple[bool, str]:
        """
        移动实体到目标区域

        Args:
            entity_id: 实体ID
            target_area_id: 目标区域ID
            player_level: 玩家等级（用于检查区域要求）

        Returns:
            (是否成功, 消息)
        """
        current_area_id = self.get_location(entity_id)
        if not current_area_id:
            return False, "实体位置未知"

        # 检查是否可以移动
        can_move, reason = self.world_map.can_move_to(current_area_id, target_area_id, player_level)

        if not can_move:
            return False, reason

        # 执行移动
        self.set_location(entity_id, target_area_id)

        # 发现新区域
        target_area = self.world_map.get_area(target_area_id)
        if target_area and not target_area.is_discovered:
            self.world_map.discover_area(target_area_id)
            return True, f"你发现了新区域：{target_area.name}！"

        return True, f"你来到了{target_area.name}"

    def teleport_entity(self, entity_id: str, target_area_id: str) -> bool:
        """
        传送实体（无视距离和限制）

        Args:
            entity_id: 实体ID
            target_area_id: 目标区域ID

        Returns:
            是否成功
        """
        area = self.world_map.get_area(target_area_id)
        if not area:
            return False

        self.set_location(entity_id, target_area_id)
        return True

    def get_nearby_areas(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        获取实体附近的区域信息

        Returns:
            区域信息列表
        """
        current_area_id = self.get_location(entity_id)
        if not current_area_id:
            return []

        current_area = self.world_map.get_area(current_area_id)
        if not current_area:
            return []

        nearby = []
        for area_id in current_area.connected_areas:
            area = self.world_map.get_area(area_id)
            if area:
                info = {
                    "id": str(area.id),
                    "name": area.name,
                    "type": area.type.value,
                    "danger_level": area.danger_level,
                    "discovered": area.is_discovered,
                    "accessible": area.is_accessible,
                    "distance": 1,
                }

                if area.is_discovered:
                    info["description"] = area.description
                else:
                    info["description"] = "未探索的区域"

                nearby.append(info)

        return nearby

    def explore_area(self, entity_id: str) -> Dict[str, Any]:
        """
        探索当前区域

        Returns:
            探索结果
        """
        current_area_id = self.get_location(entity_id)
        if not current_area_id:
            return {"success": False, "message": "位置未知"}

        area = self.world_map.get_area(current_area_id)
        if not area:
            return {"success": False, "message": "区域不存在"}

        result = {
            "success": True,
            "area": area.name,
            "discovered_features": [],
            "found_npcs": [],
            "found_items": [],
            "triggered_events": [],
        }

        # 发现地点特性
        if area.features:
            # 有概率发现新的特性
            for feature in area.features:
                if random.random() < 0.3:  # 30%概率发现
                    result["discovered_features"].append(feature)

        # 遭遇NPC
        area_entities = self.get_entities_in_area(current_area_id)
        for entity in area_entities:
            if entity != entity_id and random.random() < 0.5:  # 50%概率遇到
                result["found_npcs"].append(entity)

        # 发现物品（简化处理）
        if area.resources:
            for resource, abundance in area.resources.items():
                if random.random() < 0.2:  # 20%概率发现资源
                    result["found_items"].append(
                        {"type": resource, "quantity": random.randint(1, 3)}
                    )

        # 触发事件
        if random.random() < 0.1:  # 10%概率触发事件
            result["triggered_events"].append("遭遇低阶妖兽")

        return result

    def _generate_travel_encounters(self, path: List[str]) -> List[str]:
        """生成旅行中的遭遇"""
        encounters = []

        for area_id in path[1:]:  # 跳过起点
            area = self.world_map.get_area(area_id)
            if not area:
                continue

            # 根据危险等级生成遭遇
            encounter_chance = area.danger_level * 0.05  # 5%每危险等级

            if random.random() < encounter_chance:
                encounter_type = random.choice(
                    ["妖兽袭击", "强盗拦路", "恶劣天气", "迷路", "发现宝物"]
                )
                encounters.append(f"在{area.name}遭遇{encounter_type}")

        return encounters

    def get_area_description(self, entity_id: str) -> str:
        """
        获取实体当前区域的描述

        Returns:
            区域描述文本
        """
        current_area_id = self.get_location(entity_id)
        if not current_area_id:
            return "你不知道自己在哪里。"

        area = self.world_map.get_area(current_area_id)
        if not area:
            return "这里一片虚无。"

        # 基础描述
        description = f"【{area.name}】\n{area.description}\n"

        # 添加特性描述
        if area.features:
            description += f"\n这里有：{', '.join(area.features)}"

        # 添加其他实体
        other_entities = [e for e in self.get_entities_in_area(current_area_id) if e != entity_id]
        if other_entities:
            description += f"\n\n你看到这里还有{len(other_entities)}个人。"

        # 添加可去的地方
        connected_areas = self.world_map.get_connected_areas(current_area_id)
        if connected_areas:
            description += "\n\n可以前往："
            for connected in connected_areas:
                if connected.is_discovered:
                    description += f"\n- {connected.name} ({connected.type.value})"
                else:
                    description += "\n- 未知区域"

        return description
