import random
import time
from urllib.parse import urljoin

import httpx

from .config import settings
from .safety import UnsafeURL, assert_public_host
from .schemas import FetchResult


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


def build_client() -> httpx.AsyncClient:
    # No fixed headers here – we set them per request so each call is unique
    return httpx.AsyncClient(
        follow_redirects=False,
        timeout=settings.fetch_timeout,
        max_redirects=settings.fetch_max_redirects,
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


async def fetch(url: str) -> FetchResult:
    started = time.perf_counter()
    current_url = url
    redirects: list[str] = []
    try:
        async with build_client() as client:
            for _ in range(settings.fetch_max_redirects + 1):
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
    except UnsafeURL as exc:
        raise FetchError(str(exc)) from exc
    except httpx.TimeoutException as exc:
        raise FetchError(f"Timed out after {settings.fetch_timeout:.0f}s.") from exc
    except httpx.TooManyRedirects as exc:
        raise FetchError(f"More than {settings.fetch_max_redirects} redirects.") from exc
    except httpx.HTTPError as exc:
        raise FetchError(f"Request failed: {exc}") from exc