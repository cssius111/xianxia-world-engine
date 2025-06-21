from __future__ import annotations

from typing import Any

from xwe.services import ServiceBase, ServiceContainer
from xwe.services.interfaces.world_service import IWorldService
from xwe.world.location_manager import LocationManager


class WorldService(ServiceBase["WorldService"], IWorldService):
    def __init__(self, container: ServiceContainer) -> None:
        super().__init__(container)
        self.location_manager = LocationManager()

    def get_current_location(self) -> Any:
        return self.location_manager.current_location

    def _do_initialize(self) -> None:
        self.logger.debug("WorldService initialized")

    def _do_shutdown(self) -> None:
        self.logger.debug("WorldService shutdown")
