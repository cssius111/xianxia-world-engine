from __future__ import annotations

from typing import Any

from xwe.services import ServiceBase
from xwe.services.interfaces.cultivation_service import (
    BreakthroughInfo,
    CultivationResult,
    CultivationTechnique,
    ICultivationService,
)


class CultivationService(ServiceBase["CultivationService"], ICultivationService):
    """简单的修炼服务实现"""

    def cultivate(self, player: Any, technique: CultivationTechnique) -> CultivationResult:
        self.logger.debug("Cultivating with %s", technique.name)
        return CultivationResult(success=True, message="Cultivation not implemented")

    def check_breakthrough(self, player: Any) -> BreakthroughInfo:
        self.logger.debug("Checking breakthrough")
        from xwe.services.interfaces.cultivation_service import CultivationRealm
        return BreakthroughInfo(realm=CultivationRealm.MORTAL, possible=False)

    def _do_initialize(self) -> None:
        self.logger.debug("CultivationService initialized")

    def _do_shutdown(self) -> None:
        self.logger.debug("CultivationService shutdown")

