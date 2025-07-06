"""新手任务管理器
负责引导玩家完成基础操作并发放奖励
"""

from __future__ import annotations

from typing import Dict, List, Optional
import logging

from .inventory_system import InventorySystem

logger = logging.getLogger(__name__)


class OnboardingQuestManager:
    """管理新手引导任务进度"""

    TASKS = ["status", "inventory", "cultivate", "explore", "attack"]

    def __init__(self, inventory_system: Optional[InventorySystem] = None) -> None:
        self.inventory_system = inventory_system
        self.progress: Dict[str, List[str]] = {}

    def get_progress(self, player_id: str) -> Dict[str, any]:
        """获取玩家的新手任务进度"""
        completed = self.progress.get(player_id, [])
        return {
            "tasks": [
                {"id": t, "completed": t in completed, "index": i + 1}
                for i, t in enumerate(self.TASKS)
            ],
            "completed_count": len(completed),
            "total": len(self.TASKS),
        }

    def complete_step(self, player_id: str, step: str) -> bool:
        """记录任务步骤完成并发放奖励"""
        if step not in self.TASKS:
            logger.warning("无效的新手任务步骤: %s", step)
            return False

        completed = self.progress.setdefault(player_id, [])
        if step in completed:
            return False

        completed.append(step)
        self._grant_reward(player_id, step)
        logger.info("玩家 %s 完成新手任务: %s", player_id, step)
        return True

    # ------------------------------------------------------------------
    def _grant_reward(self, player_id: str, step: str) -> None:
        """发放奖励，默认给予少量金币"""
        if not self.inventory_system:
            return
        try:
            inv = self.inventory_system.get_inventory(player_id)
            inv.add_gold(10)
            self.inventory_system.save(player_id)
            logger.debug("已为 %s 发放新手奖励: gold +10", player_id)
        except Exception as exc:
            logger.error("发放新手奖励失败: %s", exc)
