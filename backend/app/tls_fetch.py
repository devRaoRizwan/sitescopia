"""Fallback fetch using a real browser TLS fingerprint.

Some edges (Wikimedia's HAProxy tier, for example) reject a request whose TLS
handshake does not look like a browser, even when the exit IP is fine.  httpx
speaks OpenSSL; this speaks Chrome.  Used only after a normal fetch is
challenged, so the cost is paid on failures alone.
"""

import time

from .config import settings
from .safety import assert_public_host
from .schemas import FetchResult

try:
    from curl_cffi.requests import AsyncSession

    AVAILABLE = True
except ImportError:
    AsyncSession = None
    AVAILABLE = False


async def fetch_with_browser_tls(url: str, proxy_url: str | None) -> FetchResult | None:
    if not AVAILABLE or not settings.tls_impersonation_enabled:
        return None

    started = time.perf_counter()
    try:
        async with AsyncSession() as session:
            response = await session.get(
                url,
                impersonate=settings.tls_impersonate_profile,
                proxy=proxy_url,
                timeout=settings.fetch_timeout,
                allow_redirects=True,
                max_redirects=settings.fetch_max_redirects,
            )

            final_url = str(response.url)
            assert_public_host(final_url)

            body = response.content
            if len(body) > settings.fetch_max_bytes:
                return None

            return FetchResult(
                url=final_url,
                status=response.status_code,
                headers={k.lower(): v for k, v in response.headers.items()},
                html=body.decode(response.encoding or "utf-8", errors="replace"),
                elapsed_ms=int((time.perf_counter() - started) * 1000),
                bytes=len(body),
                redirects=[final_url] if final_url != url else [],
            )
    except Exception:
        return None
