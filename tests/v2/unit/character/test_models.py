from xwe_v2.domain.character.models import Character, Attribute

def test_character_is_alive_with_hp():
    c = Character(name="TestHero", level=1, attributes=[Attribute("HP", 10)])
    assert c.is_alive()

def test_character_is_dead_when_hp_zero():
    c = Character(name="TestHero", level=1, attributes=[Attribute("HP", 0)])
    assert not c.is_alive()

def test_get_attribute_returns_correct_value():
    c = Character(name="TestHero", level=1, attributes=[Attribute("MP", 25)])
    assert c.get_attribute("MP") == 25
