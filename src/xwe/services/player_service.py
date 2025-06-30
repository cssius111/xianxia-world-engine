from __future__ import annotations

from src.xwe.services import ServiceBase, ServiceContainer
from src.xwe.services.interfaces.player_service import IPlayerService, PlayerData


class PlayerService(ServiceBase["PlayerService"], IPlayerService):
    def __init__(self, container: ServiceContainer) -> None:
        super().__init__(container)
        self._player: PlayerData | None = None

    def get_player(self) -> PlayerData:
        if self._player is None:
            self._player = PlayerData(name="Hero")
        return self._player

    def set_player(self, data: PlayerData) -> None:
        self._player = data

    def _do_initialize(self) -> None:
        self.logger.debug("PlayerService initialized")

    def _do_shutdown(self) -> None:
        self.logger.debug("PlayerService shutdown")
