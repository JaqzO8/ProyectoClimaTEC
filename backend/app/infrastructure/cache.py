import asyncio
from time import monotonic
from typing import Any

from cachetools import LRUCache


class TTLMemoryCache:
    def __init__(self, default_ttl: int = 300, maxsize: int = 1000):
        self._cache: LRUCache[str, tuple[float, Any]] = LRUCache(maxsize=maxsize)
        self._default_ttl = default_ttl
        self._lock = asyncio.Lock()

    def build_key(self, prefix: str, **kwargs: Any) -> str:
        items = []
        for k in sorted(kwargs.keys()):
            val = kwargs[k]
            if isinstance(val, float):
                val = round(val, 2)
            items.append(f"{k}:{val}")
        return f"{prefix}::" + "|".join(items)

    async def get(self, key: str) -> Any | None:
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            expires, value = entry
            if monotonic() >= expires:
                del self._cache[key]
                return None
            return value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        async with self._lock:
            self._cache[key] = (
                monotonic() + (ttl if ttl is not None else self._default_ttl),
                value,
            )

    async def clear(self) -> None:
        async with self._lock:
            self._cache.clear()
