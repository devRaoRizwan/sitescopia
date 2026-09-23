import asyncio
from dataclasses import dataclass, field

import httpx

from ..config import settings
from ..safety import UnsafeURL, assert_public_host
from ..schemas import ParsedPage

RETRY_WITH_GET = {403, 405, 501}


@dataclass
class LinkCheck:
    url: str
    text: str
    internal: bool
    status: int | None = None
    error: str | None = None

    @property
    def broken(self) -> bool:
        return self.error is not None or (self.status is not None and self.status >= 400)

    @property
    def reason(self) -> str:
        if self.error:
            return self.error
        return f"HTTP {self.status}"


@dataclass
class LinkReport:
    checked: list[LinkCheck] = field(default_factory=list)
    total_links: int = 0
    skipped: int = 0

    @property
    def broken(self) -> list[LinkCheck]:
        return [check for check in self.checked if check.broken]


def candidates(page: ParsedPage, limit: int) -> list[LinkCheck]:
    seen: set[str] = set()
    internal, external = [], []

    for link in page.links:
        url = link.url.split("#")[0]
        if url in seen or url.rstrip("/") == page.url.rstrip("/"):
            continue
        seen.add(url)
        target = internal if link.internal else external
        target.append(LinkCheck(url=url, text=link.text, internal=link.internal))

    ordered = internal + external
    return ordered[:limit]


async def probe(client: httpx.AsyncClient, check: LinkCheck) -> LinkCheck:
    try:
        assert_public_host(check.url)
    except UnsafeURL:
        check.error = "points at a non-public address"
        return check

    try:
        response = await client.head(check.url)
        if response.status_code in RETRY_WITH_GET:
            response = await client.get(check.url)
        check.status = response.status_code
    except httpx.TimeoutException:
        check.error = "timed out"
    except httpx.HTTPError:
        check.error = "could not be reached"
    return check


async def verify(page: ParsedPage) -> LinkReport:
    report = LinkReport(total_links=len(page.links))
    if not settings.link_check_enabled:
        return report

    targets = candidates(page, settings.link_check_limit)
    report.skipped = max(0, len(page.links) - len(targets))
    if not targets:
        return report

    gate = asyncio.Semaphore(settings.link_check_concurrency)

    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=settings.link_check_timeout,
        headers={"User-Agent": settings.user_agent},
    ) as client:

        async def run(check: LinkCheck) -> LinkCheck:
            async with gate:
                return await probe(client, check)

        tasks = [asyncio.create_task(run(check)) for check in targets]
        done, pending = await asyncio.wait(tasks, timeout=settings.link_check_budget)
        for task in pending:
            task.cancel()

        report.checked = [task.result() for task in done if not task.cancelled()]
        report.skipped += len(pending)

    return report
