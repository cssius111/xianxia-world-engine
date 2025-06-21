from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List

from xwe.services import ServiceBase, ServiceContainer


class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class LogEntry:
    level: LogLevel
    message: str


@dataclass
class LogFilter:
    level: LogLevel | None = None


class ILogService(ServiceBase):
    def log(self, level: LogLevel, message: str) -> None:
        raise NotImplementedError

    def query(self, log_filter: LogFilter | None = None) -> List[LogEntry]:
        raise NotImplementedError


class LogService(ServiceBase["LogService"], ILogService):
    def __init__(self, container: ServiceContainer) -> None:
        super().__init__(container)
        self._entries: List[LogEntry] = []

    def log(self, level: LogLevel, message: str) -> None:
        entry = LogEntry(level=level, message=message)
        self._entries.append(entry)
        self.logger.log({
            LogLevel.DEBUG: 10,
            LogLevel.INFO: 20,
            LogLevel.WARNING: 30,
            LogLevel.ERROR: 40,
        }[level], message)

    def query(self, log_filter: LogFilter | None = None) -> List[LogEntry]:
        if log_filter and log_filter.level:
            return [e for e in self._entries if e.level == log_filter.level]
        return list(self._entries)

    def _do_initialize(self) -> None:
        self.logger.debug("LogService initialized")

    def _do_shutdown(self) -> None:
        self.logger.debug("LogService shutdown")
