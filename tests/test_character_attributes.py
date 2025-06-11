import pytest
from xwe.core.attributes import CharacterAttributes


def test_extra_attribute_access():
    attrs = CharacterAttributes()
    # attack_power computed in __post_init__ should be accessible
    assert isinstance(attrs.attack_power, (int, float))
    # dynamically override attribute
    attrs.attack_power = 123
    assert attrs.attack_power == 123
    # dynamically set new extra attribute
    attrs.attack_power = 123
    assert attrs.attack_power == 123
    assert attrs.extra_attributes["attack_power"] == 123


def test_missing_attribute_error():
    attrs = CharacterAttributes()
    with pytest.raises(AttributeError):
        _ = attrs.nonexistent_attr

def test_max_cultivation_default():
    """Ensure newly created attributes include max_cultivation."""
    attrs = CharacterAttributes()
    assert attrs.max_cultivation == 100
