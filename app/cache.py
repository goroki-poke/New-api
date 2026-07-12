import time
from collections import OrderedDict
from typing import Optional, Any

from app.config import settings


class TTLCache:
    def __init__(self, ttl: int = 300, max_size: int = 1000):
        self._ttl = ttl
        self._max_size = max_size
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        if key not in self._store:
            return None
        expires_at, value = self._store[key]
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        self._store.move_to_end(key)
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        expires_at = time.monotonic() + (ttl or self._ttl)
        self._store[key] = (expires_at, value)
        self._store.move_to_end(key)
        if len(self._store) > self._max_size:
            self._store.popitem(last=False)

    def invalidate(self, key: str):
        self._store.pop(key, None)

    def clear(self):
        self._store.clear()


product_cache = TTLCache(ttl=settings.cache_ttl_seconds)
