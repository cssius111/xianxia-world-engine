from xwe.core.command_router import CommandRouter
from xwe.core.inventory import Inventory


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
