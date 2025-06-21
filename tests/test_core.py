import importlib.util
from pathlib import Path
import sys
import types

def _load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, Path(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore
    return module

CommandRouter = _load_module('xwe/core/command_router.py', 'command_router').CommandRouter
Inventory = _load_module('xwe/core/inventory.py', 'inventory').Inventory


def test_command_router_move():
    router = CommandRouter()
    cmd, params = router.route_command('移动 北')
    assert cmd == 'move'
    assert params.get('target') == '北'


def test_inventory_add_remove():
    inv = Inventory(capacity=2)
    assert inv.add('sword')
    assert inv.add('potion', 2)
    assert inv.is_full()
    assert inv.get_quantity('potion') == 2
    assert inv.remove('potion')
    assert inv.get_quantity('potion') == 1
