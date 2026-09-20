import asyncio
import logging
import time
from dataclasses import dataclass
from urllib.parse import quote

import httpx

from .config import settings

log = logging.getLogger(__name__)


class ProxyUnavailable(Exception):
    pass


@dataclass
class ProxyState:
    url: str
    cooldown_until: float = 0.0


class ProxyManager:
    """Loads Webshare proxies and rotates healthy entries in memory."""

    def __init__(self) -> None:
        self._proxies: list[ProxyState] = []
        self._next_index = 0
        self._loaded = False
        self._lock = asyncio.Lock()

    @property
    def configured(self) -> bool:
        return bool(settings.webshare_api_key or settings.webshare_proxy_list)

    async def _load(self) -> None:
        if settings.webshare_proxy_list:
            urls = [item.strip() for item in settings.webshare_proxy_list.split(",") if item.strip()]
        elif settings.webshare_api_key:
            try:
                # Webshare's documented proxy-list endpoint returns credentials for
                # each proxy.  Keep those URLs in memory only; never log them.
                async with httpx.AsyncClient(
                    timeout=settings.fetch_timeout, trust_env=False
                ) as client:
                    response = await client.get(
                        settings.webshare_api_url,
                        headers={"Authorization": f"Token {settings.webshare_api_key}"},
                        params={"mode": "direct", "page": 1, "page_size": 100},
                    )
                    response.raise_for_status()
                    payload = response.json()
            except (httpx.HTTPError, ValueError) as exc:
                log.warning("Could not load outbound proxies from Webshare: %s", type(exc).__name__)
                raise ProxyUnavailable("Could not load outbound proxies.") from exc
            urls = [self._proxy_url(item) for item in payload.get("results", [])]
        else:
            urls = []

        # Ignore duplicate entries so round-robin always moves to a genuinely
        # different proxy while healthy alternatives exist.
        unique_urls = list(dict.fromkeys(url for url in urls if url))
        self._proxies = [ProxyState(url) for url in unique_urls]
        self._loaded = True
        if self._proxies:
            log.info("Loaded %d outbound proxies.", len(self._proxies))
        else:
            log.warning("No outbound proxies were returned by the configured source.")

    @staticmethod
    def _proxy_url(item: dict) -> str | None:
        address = item.get("proxy_address")
        port = item.get("port")
        username = item.get("username")
        password = item.get("password")
        if not all((address, port, username, password)):
            return None
        return (
            f"http://{quote(str(username), safe='')}:{quote(str(password), safe='')}"
            f"@{address}:{port}"
        )

    async def get_proxy(self) -> str | None:
        if not self.configured:
            return None

        async with self._lock:
            if not self._loaded:
                await self._load()
            now = time.monotonic()
            for offset in range(len(self._proxies)):
                index = (self._next_index + offset) % len(self._proxies)
                proxy = self._proxies[index]
                if proxy.cooldown_until <= now:
                    self._next_index = (index + 1) % len(self._proxies)
                    return proxy.url
        raise ProxyUnavailable("No healthy outbound proxies are available.")

    async def mark_failed(self, proxy_url: str) -> None:
        async with self._lock:
            for proxy in self._proxies:
                if proxy.url == proxy_url:
                    proxy.cooldown_until = time.monotonic() + settings.proxy_cooldown_seconds
                    log.warning("Outbound proxy temporarily unavailable.")
                    return

    async def mark_succeeded(self, proxy_url: str | None) -> None:
        if not proxy_url:
            return
        async with self._lock:
            for proxy in self._proxies:
                if proxy.url == proxy_url:
                    proxy.cooldown_until = 0.0
                    return


proxy_manager = ProxyManager()
