import logging
import random
import time
from urllib.parse import urljoin, urlparse

import httpx

from .config import settings
from .proxy_manager import ProxyUnavailable, proxy_manager
from .interstitial import detect as detect_challenge
from .safety import UnsafeURL, assert_public_host
from .tls_fetch import fetch_with_browser_tls
from .schemas import FetchResult

log = logging.getLogger(__name__)


class FetchError(Exception):
    pass


def _random_headers() -> dict[str, str]:
    """Generate a realistic browser-like header set with a random User-Agent."""
    ua = random.choice(settings.user_agents)

    # Slight variation in Accept-Language keeps fingerprints different.
    accept_languages = [
        "en-US,en;q=0.9",
        "en-GB,en;q=0.9",
        "en-US,en;q=0.8,fr;q=0.6",
        "en-US,en;q=0.9,es;q=0.8",
    ]

    return {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": random.choice(accept_languages),
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }


def build_client(proxy_url: str | None = None) -> httpx.AsyncClient:
    # No fixed headers here – we set them per request so each call is unique
    return httpx.AsyncClient(
        follow_redirects=False,
        timeout=settings.fetch_timeout,
        max_redirects=settings.fetch_max_redirects,
        proxy=proxy_url,
        trust_env=False,
    )


async def read_body(response: httpx.Response) -> bytes:
    chunks = []
    total = 0
    async for chunk in response.aiter_bytes():
        total += len(chunk)
        if total > settings.fetch_max_bytes:
            raise FetchError(f"Page exceeds the {settings.fetch_max_bytes // 1024} KB limit.")
        chunks.append(chunk)
    return b"".join(chunks)


async def _fetch_once(url: str, proxy_url: str | None) -> FetchResult:
    started = time.perf_counter()
    current_url = url
    redirects: list[str] = []
    async with build_client(proxy_url) as client:
        for _ in range(settings.fetch_max_redirects + 1):
            # This runs for the initial URL and every redirect before any request.
            assert_public_host(current_url)

            # Fresh random headers on every request (including redirects)
            headers = _random_headers()

            async with client.stream("GET", current_url, headers=headers) as response:
                if response.is_redirect:
                    location = response.headers.get("location")
                    if not location:
                        raise FetchError("Redirect response had no Location header.")
                    next_url = urljoin(str(response.url), location)
                    assert_public_host(next_url)
                    redirects.append(str(response.url))
                    current_url = next_url
                    continue

                body = await read_body(response)
                return FetchResult(
                    url=str(response.url),
                    status=response.status_code,
                    headers={k.lower(): v for k, v in response.headers.items()},
                    html=body.decode(response.encoding or "utf-8", errors="replace"),
                    elapsed_ms=int((time.perf_counter() - started) * 1000),
                    bytes=len(body),
                    redirects=redirects,
                )
        raise FetchError(f"More than {settings.fetch_max_redirects} redirects.")


async def _fetch_direct(url: str) -> FetchResult:
    """Last resort when the proxy provider will not reach a host at all."""
    try:
        return await _fetch_once(url, None)
    except UnsafeURL as exc:
        raise FetchError(str(exc)) from exc
    except httpx.TimeoutException as exc:
        raise FetchError(f"Timed out after {settings.fetch_timeout:.0f}s.") from exc
    except httpx.TooManyRedirects as exc:
        raise FetchError(f"More than {settings.fetch_max_redirects} redirects.") from exc
    except httpx.HTTPError as exc:
        raise FetchError(f"Request failed: {exc}") from exc


async def fetch(url: str) -> FetchResult:
    """Fetch through Webshare when configured, with bounded proxy failover."""
    attempts = settings.proxy_max_attempts if proxy_manager.configured else 1
    attempts = max(1, attempts)

    host = (urlparse(url).hostname or "").lower()

    for attempt in range(attempts):
        proxy_url: str | None = None
        try:
            proxy_url = await proxy_manager.get_proxy(host)
            fetched = await _fetch_once(url, proxy_url)

            # A challenge page is a valid HTTP response, so httpx never raises.
            # Exit-IP reputation is the main variable, so retry on a fresh one.
            if detect_challenge(fetched):
                # Same IP, browser TLS: catches edges that fingerprint the handshake.
                retried = await fetch_with_browser_tls(url, proxy_url)
                if retried is not None and not detect_challenge(retried):
                    log.info("Browser TLS fingerprint cleared the challenge.")
                    await proxy_manager.mark_succeeded(proxy_url, host)
                    return retried

                if proxy_url and attempt + 1 < attempts:
                    await proxy_manager.mark_burned(proxy_url, host)
                    log.info("Challenge page returned; retrying through a different exit IP.")
                    continue

            await proxy_manager.mark_succeeded(proxy_url, host)
            return fetched
        except UnsafeURL as exc:
            raise FetchError(str(exc)) from exc
        except FetchError:
            raise
        except ProxyUnavailable as exc:
            raise FetchError("No outbound proxy is currently available.") from exc
        except httpx.ProxyError as exc:
            # The provider refused the CONNECT tunnel, so the site was never
            # contacted.  Its destination blocklist covers the whole pool, so
            # rotating exit IPs cannot help -- go direct for this host instead.
            await proxy_manager.mark_tunnel_refused(host)
            if not settings.proxy_direct_fallback:
                raise FetchError(
                    "The outbound proxy will not connect to this host."
                ) from exc
            log.info("Outbound proxy refused this destination; fetching directly.")
            return await _fetch_direct(url)
        except httpx.TimeoutException as exc:
            if proxy_url:
                await proxy_manager.mark_failed(proxy_url)
                log.warning("Outbound proxy timed out; trying another proxy when available.")
                if attempt + 1 < attempts:
                    continue
            raise FetchError(f"Timed out after {settings.fetch_timeout:.0f}s.") from exc
        except httpx.TooManyRedirects as exc:
            raise FetchError(f"More than {settings.fetch_max_redirects} redirects.") from exc
        except httpx.HTTPError as exc:
            # Connection-level errors are handled above.  HTTP responses (including
            # 4xx/5xx) are returned normally by httpx and preserve analyzer behavior.
            if proxy_url:
                await proxy_manager.mark_failed(proxy_url)
                log.warning("Outbound proxy connection failed; trying another proxy when available.")
                if attempt + 1 < attempts:
                    continue
                raise FetchError("Request failed while using an outbound proxy.") from exc
            raise FetchError(f"Request failed: {exc}") from exc

    raise FetchError("No outbound proxy is currently available.")
