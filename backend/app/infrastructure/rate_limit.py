"""Bounded in-memory rate limiting; apply per trusted client address, never raw XFF."""

from time import monotonic

from cachetools import TTLCache


class RateLimiter:
    def __init__(self) -> None:
        self._clients: TTLCache[str, tuple[float, int]] = TTLCache(maxsize=10000, ttl=3600)

    def allow(self, address: str, limit: int, window: int) -> bool:
        now = monotonic()
        start, count = self._clients.get(address, (now, 0))
        if now - start >= window:
            start, count = now, 0
        if count >= limit:
            return False
        self._clients[address] = start, count + 1
        return True
