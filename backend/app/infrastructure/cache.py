import asyncio
from typing import Any

from cachetools import TTLCache


class TTLMemoryCache:
    def __init__(self, default_ttl: int = 300, maxsize: int = 1000):
        self._cache: TTLCache[str, Any] = TTLCache(maxsize=maxsize, ttl=default_ttl)
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
            return self._cache.get(key)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        async with self._lock:
            self._cache[key] = value

    async def clear(self) -> None:
        async with self._lock:
            self._cache.clear()
