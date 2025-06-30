import time

from xwe.core.data_loader import DataLoader
from xwe.core.optimizations.smart_cache import SmartCache


def test_data_loader_ttl(tmp_path):
    f = tmp_path / "data.json"
    f.write_text('{"a":1}', encoding="utf-8")
    loader = DataLoader(data_path=tmp_path, cache_ttl=1)
    assert loader.load_json("data.json") == {"a": 1}
    f.write_text('{"a":2}', encoding="utf-8")
    assert loader.load_json("data.json") == {"a": 1}
    time.sleep(1.1)
    assert loader.load_json("data.json") == {"a": 2}


def test_smart_cache_ttl():
    cache = SmartCache(ttl=1)
    count = {"n": 0}

    @cache.cache
    def add(a, b):
        count["n"] += 1
        return a + b

    assert add(1, 2) == 3
    assert add(1, 2) == 3
    assert count["n"] == 1
    time.sleep(1.1)
    assert add(1, 2) == 3
    assert count["n"] == 2

