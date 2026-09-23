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
        # host -> {proxy_url: blocked_until}. A proxy burned by one site's WAF is
        # usually still fine everywhere else, so this is kept per host.
        self._burned: dict[str, dict[str, float]] = {}
        self.last_error: str | None = None
        # host -> proxy_url that last worked, tried first next time.
        self._sticky: dict[str, str] = {}
        # host -> time until which the provider is known to refuse CONNECT.
        # This is the provider's own destination blocklist, so it applies to
        # every proxy in the pool, not to one exit IP.
        self._tunnel_refused: dict[str, float] = {}

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
            self.last_error = "the configured source returned no proxies"
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

    def _is_burned(self, host: str, proxy_url: str, now: float) -> bool:
        return self._burned.get(host, {}).get(proxy_url, 0.0) > now

    async def get_proxy(self, host: str = "") -> str | None:
        if not self.configured:
            return None

        async with self._lock:
            if self._tunnel_refused.get(host, 0.0) > time.monotonic():
                return None

            if not self._loaded:
                await self._load()
            now = time.monotonic()

            sticky = self._sticky.get(host)
            if sticky and not self._is_burned(host, sticky, now):
                for proxy in self._proxies:
                    if proxy.url == sticky and proxy.cooldown_until <= now:
                        return proxy.url

            for offset in range(len(self._proxies)):
                index = (self._next_index + offset) % len(self._proxies)
                proxy = self._proxies[index]
                if proxy.cooldown_until <= now and not self._is_burned(host, proxy.url, now):
                    self._next_index = (index + 1) % len(self._proxies)
                    return proxy.url

            # every proxy is burned for this host; fall back to any healthy one
            for offset in range(len(self._proxies)):
                index = (self._next_index + offset) % len(self._proxies)
                proxy = self._proxies[index]
                if proxy.cooldown_until <= now:
                    self._next_index = (index + 1) % len(self._proxies)
                    return proxy.url

        raise ProxyUnavailable("No healthy outbound proxies are available.")

    async def mark_burned(self, proxy_url: str | None, host: str) -> None:
        """This exit IP was challenged by this host. Avoid it here, keep it elsewhere."""
        if not proxy_url or not host:
            return
        async with self._lock:
            self._burned.setdefault(host, {})[proxy_url] = (
                time.monotonic() + settings.proxy_burn_seconds
            )
            if self._sticky.get(host) == proxy_url:
                self._sticky.pop(host, None)

    async def mark_tunnel_refused(self, host: str) -> None:
        """The provider blocks this destination. Rotating exit IPs cannot help."""
        if not host:
            return
        async with self._lock:
            self._tunnel_refused[host] = time.monotonic() + settings.proxy_burn_seconds

    async def mark_failed(self, proxy_url: str) -> None:
        async with self._lock:
            for proxy in self._proxies:
                if proxy.url == proxy_url:
                    proxy.cooldown_until = time.monotonic() + settings.proxy_cooldown_seconds
                    log.warning("Outbound proxy temporarily unavailable.")
                    return

    async def mark_succeeded(self, proxy_url: str | None, host: str = "") -> None:
        if not proxy_url:
            return
        async with self._lock:
            if host:
                self._sticky[host] = proxy_url
            for proxy in self._proxies:
                if proxy.url == proxy_url:
                    proxy.cooldown_until = 0.0
                    return


    async def diagnostics(self) -> dict:
        """Non-secret view of proxy state, for operational checks."""
        if not self.configured:
            return {
                "configured": False,
                "source": None,
                "loaded": 0,
                "healthy": 0,
                "last_error": "no WEBSHARE_API_KEY or WEBSHARE_PROXY_LIST set",
            }

        async with self._lock:
            if not self._loaded:
                try:
                    await self._load()
                except Exception as exc:
                    self.last_error = f"{type(exc).__name__}: {exc}"

            now = time.monotonic()
            healthy = sum(1 for p in self._proxies if p.cooldown_until <= now)
            return {
                "configured": True,
                "source": "list" if settings.webshare_proxy_list else "api",
                "loaded": len(self._proxies),
                "healthy": healthy,
                "blocked_destinations": sorted(
                    host for host, until in self._tunnel_refused.items() if until > now
                ),
                "last_error": self.last_error,
            }


proxy_manager = ProxyManager()
