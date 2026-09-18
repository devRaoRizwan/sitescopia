import time
from urllib.parse import urljoin

import httpx

from .config import settings
from .safety import UnsafeURL, assert_public_host
from .schemas import FetchResult


class FetchError(Exception):
    pass


def build_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        follow_redirects=False,
        timeout=settings.fetch_timeout,
        max_redirects=settings.fetch_max_redirects,
        headers={"User-Agent": settings.user_agent, "Accept": "text/html,*/*"},
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
                async with client.stream("GET", current_url) as response:
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
