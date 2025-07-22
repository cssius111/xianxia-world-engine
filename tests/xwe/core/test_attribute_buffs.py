import pytest
from src.xwe.core.attributes import CharacterAttributes, AttributeSystem


def test_apply_buff_updates_effective_values():
    attrs = CharacterAttributes()
    system = AttributeSystem()

    # 基础值检查
    assert attrs.strength == 10
    assert pytest.approx(attrs.attack_power) == 25

    # 数值型增益
    system.apply_buff(attrs, "strength", 5)
    assert attrs.strength == 15
    assert pytest.approx(attrs.attack_power) == 35

    # 百分比增益
    system.apply_buff(attrs, "attack_power", 10, is_percentage=True)
    assert pytest.approx(attrs.attack_power) == 38.5
