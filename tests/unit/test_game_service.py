import importlib.util
from pathlib import Path
import sys
import types


def _load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, Path(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)  # type: ignore
    return module


stub_services = types.ModuleType('xwe.services')


class StubServiceBase:
    def __init__(self, container):
        self.container = container
        self._initialized = False
        import logging
        self.logger = logging.getLogger(self.__class__.__name__)

    def __class_getitem__(cls, item):
        return cls

    def initialize(self):
        self._initialized = True

    def shutdown(self):
        self._initialized = False


class StubServiceContainer:
    pass


stub_services.ServiceBase = StubServiceBase
stub_services.ServiceContainer = StubServiceContainer
sys.modules['xwe.services'] = stub_services

game_service_module = _load_module('src/xwe/services/game_service.py', 'xwe.services.game_service')
GameService = game_service_module.GameService
CommandResult = game_service_module.CommandResult


class DummyContainer:
    pass


def test_process_command_success():
    container = DummyContainer()
    service = GameService(container)

    result = service.process_command("look around")
    assert isinstance(result, CommandResult)
    assert result.success


def test_initialize_and_shutdown():
    container = DummyContainer()
    service = GameService(container)

    service.initialize()
    assert service._initialized

    service.shutdown()
    assert not service._initialized
