import asyncio

from xwe.features.exploration_system import ExplorationSystem


async def _run():
    system = ExplorationSystem()
    result = await system.explore_async("青云城")
    return result.get("success") is not None


def test_explore_async():
    assert asyncio.run(_run())

