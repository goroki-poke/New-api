from abc import ABC, abstractmethod
from typing import Optional

import httpx

from app.models import Product


class BaseScraper(ABC):
    BASE_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers=self.BASE_HEADERS,
                follow_redirects=True,
                timeout=30.0,
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    @abstractmethod
    def product_id_from_url(self, url: str) -> str:
        ...

    @abstractmethod
    async def scrape(self, url: str) -> Product:
        ...

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> list[Product]:
        ...
