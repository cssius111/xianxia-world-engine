"""
探索系统
处理角色探索时的随机事件和物品掉落
"""

import random
import json
from typing import Dict, List, Optional, Tuple, Callable
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ExplorationSystem:
    """
    探索系统
    
    管理探索事件、物品掉落等
    """
    
    def __init__(self):
        """初始化探索系统"""
        self.exploration_data = self._load_exploration_data()
        
    def _load_exploration_data(self) -> Dict:
        """加载探索数据"""
        try:
            data_path = Path(__file__).parent.parent / "data" / "restructured" / "exploration_data.json"
            if data_path.exists():
                with open(data_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"加载探索数据失败: {e}")
            
        # 返回默认数据
        return {
            "locations": {
                "青云城": {
                    "description": "繁华的修仙城市",
                    "exploration_events": [
                        {
                            "id": "city_herb",
                            "weight": 30,
                            "narration": "你在青云城的药材市场发现了一株品质不错的灵草。",
                            "items": [{"name": "百年人参", "qty": 1, "rarity": "rare"}]
                        },
                        {
                            "id": "city_stone",
                            "weight": 40,
                            "narration": "你在城中古玩店淘到了一块蕴含灵气的小石头。",
                            "items": [{"name": "下品灵石", "qty": 1, "rarity": "common"}]
                        },
                        {
                            "id": "city_pill",
                            "weight": 20,
                            "narration": "一位路过的炼丹师看你有缘，赠送了你一颗丹药。",
                            "items": [{"name": "回气丹", "qty": 1, "rarity": "common"}]
                        },
                        {
                            "id": "city_nothing",
                            "weight": 10,
                            "narration": "你在城中转了一圈，没有特别的发现。",
                            "items": []
                        }
                    ]
                },
                "青云山": {
                    "description": "青云城外的灵山",
                    "exploration_events": [
                        {
                            "id": "mountain_herb",
                            "weight": 40,
                            "narration": "你在山中采到了一株野生灵草。",
                            "items": [{"name": "千年灵芝", "qty": 1, "rarity": "epic"}]
                        },
                        {
                            "id": "mountain_beast",
                            "weight": 30,
                            "narration": "你击退了一只妖兽，获得了它的内丹。",
                            "items": [{"name": "妖兽内丹", "qty": 1, "rarity": "rare"}]
                        },
                        {
                            "id": "mountain_ore",
                            "weight": 30,
                            "narration": "你在山洞中发现了一块稀有矿石。",
                            "items": [{"name": "玄铁矿", "qty": 1, "rarity": "rare"}]
                        }
                    ]
                }
            },
            "default_events": [
                {
                    "id": "default_item",
                    "weight": 70,
                    "narration": "你在探索中有所收获。",
                    "items": [{"name": "灵石", "qty": 1, "rarity": "common"}]
                },
                {
                    "id": "default_nothing",
                    "weight": 30,
                    "narration": "你四处探索，暂时没有发现。",
                    "items": []
                }
            ]
        }
    
    def explore(
        self,
        location: str = "青云城",
        command_context: Optional[Dict] = None,
        inventory_add_cb: Optional[Callable[[List[Dict]], None]] = None,
    ) -> Dict:
        """
        执行探索

        Args:
            location: 当前位置
            command_context: 发起探索命令时的上下文信息
            inventory_add_cb: 处理获得物品的回调

        Returns:
            探索结果，包含叙述文本和获得的物品
        """
        logger.debug(
            "[EXPLORE] Start exploring '%s' with context: %s", location, command_context
        )

        # 获取当前位置的探索事件
        location_data = self.exploration_data.get("locations", {}).get(location)
        
        if location_data:
            events = location_data.get("exploration_events", [])
        else:
            # 使用默认事件
            events = self.exploration_data.get("default_events", [])
            
        # 根据权重选择事件
        event = self._weighted_choice(events)
        logger.debug(
            "[EXPLORE] Selected event %s, rewards: %s",
            event.get("id", "unknown") if event else "none",
            bool(event.get("items")) if event else False,
        )
        
        if event:
            # 返回统一格式的结果
            result = {
                "success": True,
                "narration": event["narration"],
                "items": event.get("items", []),
                "location": location,
                "event_id": event.get("id", "unknown"),
            }

            # 记录日志
            if result["items"]:
                item_names = [f"{item['name']}x{item['qty']}" for item in result["items"]]
                logger.info("[EXPLORE] Reward items: %s", ", ".join(item_names))
                if inventory_add_cb:
                    inventory_add_cb(result["items"])
                    logger.info("[EXPLORE] Inventory add callback invoked")
                else:
                    logger.info("[EXPLORE] Inventory add callback not provided")
            else:
                logger.info("[EXPLORE] No reward items")
                if inventory_add_cb:
                    logger.info("[EXPLORE] Inventory add callback invoked with empty items")

            return result
        else:
            return {
                "success": False,
                "narration": "探索时发生了错误。",
                "items": [],
                "location": location,
                "event_id": "error"
            }
    
    def _weighted_choice(self, events: List[Dict]) -> Optional[Dict]:
        """
        根据权重随机选择事件
        
        Args:
            events: 事件列表
            
        Returns:
            选中的事件
        """
        if not events:
            return None
            
        # 计算总权重
        total_weight = sum(event.get("weight", 1) for event in events)
        
        # 随机选择
        rand = random.uniform(0, total_weight)
        current_weight = 0
        
        for event in events:
            current_weight += event.get("weight", 1)
            if rand <= current_weight:
                return event
                
        # 保底返回最后一个
        return events[-1]
        
    def add_custom_event(self, location: str, event: Dict) -> bool:
        """
        添加自定义探索事件
        
        Args:
            location: 位置
            event: 事件数据
            
        Returns:
            是否成功添加
        """
        try:
            if location not in self.exploration_data["locations"]:
                self.exploration_data["locations"][location] = {
                    "description": location,
                    "exploration_events": []
                }
                
            self.exploration_data["locations"][location]["exploration_events"].append(event)
            return True
        except Exception as e:
            logger.error(f"添加自定义事件失败: {e}")
            return False
