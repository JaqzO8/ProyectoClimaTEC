import pytest

from app.infrastructure.cache import TTLMemoryCache


@pytest.mark.asyncio
async def test_cache_build_key_and_operations():
    cache = TTLMemoryCache(default_ttl=10, maxsize=100)
    key1 = cache.build_key("test", lat=-9.2934, lon=-76.0012, unit="celsius")
    key2 = cache.build_key("test", lat=-9.29, lon=-76.00, unit="celsius")
    assert key1 == key2

    await cache.set(key1, {"data": 123})
    res = await cache.get(key1)
    assert res == {"data": 123}

    await cache.clear()
    res_after_clear = await cache.get(key1)
    assert res_after_clear is None
