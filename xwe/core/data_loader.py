"""
数据加载器
负责加载游戏配置和数据文件
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """
    数据加载器
    
    从文件系统加载游戏数据
    """
    
    def __init__(self, data_path: Optional[Path] = None):
        """
        初始化数据加载器
        
        Args:
            data_path: 数据文件路径
        """
        if data_path is None:
            # 默认使用项目下的data目录
            self.data_path = Path(__file__).parent.parent / "data"
        else:
            self.data_path = Path(data_path)
            
        # 缓存已加载的数据
        self._cache: Dict[str, Any] = {}
        
        # 确保数据目录存在
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"数据加载器初始化，数据路径: {self.data_path}")
        
    def load_json(self, filename: str, default: Any = None) -> Any:
        """
        加载JSON文件
        
        Args:
            filename: 文件名
            default: 默认值
            
        Returns:
            加载的数据或默认值
        """
        # 检查缓存
        if filename in self._cache:
            return self._cache[filename]
            
        filepath = self.data_path / filename
        
        try:
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._cache[filename] = data
                    logger.debug(f"成功加载数据文件: {filename}")
                    return data
            else:
                logger.warning(f"数据文件不存在: {filename}")
                return default if default is not None else {}
        except Exception as e:
            logger.error(f"加载数据文件失败 {filename}: {e}")
            return default if default is not None else {}
            
    def save_json(self, filename: str, data: Any) -> bool:
        """
        保存JSON文件
        
        Args:
            filename: 文件名
            data: 要保存的数据
            
        Returns:
            是否成功保存
        """
        filepath = self.data_path / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            # 更新缓存
            self._cache[filename] = data
            logger.debug(f"成功保存数据文件: {filename}")
            return True
        except Exception as e:
            logger.error(f"保存数据文件失败 {filename}: {e}")
            return False
            
    def get_player_template(self) -> Dict[str, Any]:
        """获取玩家角色模板"""
        template = self.load_json("templates/player_template.json", {
            "initial_state": {
                "name": "无名侠客",
                "base_attributes": {
                    "strength": 10,
                    "constitution": 10,
                    "agility": 10,
                    "intelligence": 10,
                    "willpower": 10,
                    "comprehension": 10,
                    "luck": 10
                },
                "cultivation": {
                    "realm": "凡人",
                    "level": 0
                }
            },
            "initial_skills": ["basic_attack"],
            "initial_items": {
                "healing_pill": 5,
                "spirit_stones": 100
            }
        })
        return template
        
    def get_npc_templates(self) -> Dict[str, Any]:
        """获取NPC模板"""
        return self.load_json("templates/npc_templates.json", {
            "npcs": [
                {
                    "id": "npc_wang_boss",
                    "name": "王老板",
                    "type": "npc",
                    "base_attributes": {
                        "strength": 8,
                        "constitution": 12,
                        "agility": 6,
                        "intelligence": 15,
                        "willpower": 10,
                        "comprehension": 8,
                        "luck": 12
                    },
                    "ai_profile": "merchant",
                    "location": "青云城"
                }
            ]
        })
        
    def get_skill_definitions(self) -> Dict[str, Any]:
        """获取技能定义"""
        return self.load_json("skills/skill_definitions.json", {
            "skills": {
                "basic_attack": {
                    "id": "basic_attack",
                    "name": "基础攻击",
                    "description": "最基本的攻击方式",
                    "damage_multiplier": 1.0,
                    "mana_cost": 0,
                    "cooldown": 0,
                    "target_type": "single_enemy"
                },
                "power_strike": {
                    "id": "power_strike",
                    "name": "力量打击",
                    "description": "消耗体力进行的强力攻击",
                    "damage_multiplier": 1.5,
                    "stamina_cost": 10,
                    "cooldown": 2,
                    "target_type": "single_enemy"
                }
            }
        })
        
    def get_item_definitions(self) -> Dict[str, Any]:
        """获取物品定义"""
        return self.load_json("items/item_definitions.json", {
            "items": {
                "healing_pill": {
                    "id": "healing_pill",
                    "name": "回血丹",
                    "description": "恢复少量生命值",
                    "type": "consumable",
                    "effect": {"heal": 50},
                    "value": 10
                },
                "spirit_stones": {
                    "id": "spirit_stones",
                    "name": "灵石",
                    "description": "修仙界通用货币",
                    "type": "currency",
                    "stack_size": 9999
                }
            }
        })
        
    def get_world_config(self) -> Dict[str, Any]:
        """获取世界配置"""
        return self.load_json("world/world_config.json", {
            "regions": [],
            "areas": [],
            "events": []
        })
        
    def get_dialogue_trees(self) -> Dict[str, Any]:
        """获取对话树"""
        return self.load_json("dialogues/dialogue_trees.json", {})
        
    def get_event_definitions(self) -> Dict[str, Any]:
        """获取事件定义"""
        return self.load_json("events/event_definitions.json", {
            "events": []
        })

    def get_destinies(self) -> Dict[str, Any]:
        """获取命格数据"""
        return self.load_json("character/destiny.json", {})

    def get_fortunes(self) -> Dict[str, Any]:
        """获取气运数据"""
        return self.load_json("character/fortune.json", {})
        
    def clear_cache(self) -> None:
        """清除缓存"""
        self._cache.clear()
        logger.debug("数据缓存已清除")
        
    def reload_data(self, filename: str) -> Any:
        """重新加载数据文件"""
        # 从缓存中移除
        if filename in self._cache:
            del self._cache[filename]
            
        # 重新加载
        return self.load_json(filename)
