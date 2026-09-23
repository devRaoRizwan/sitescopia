import asyncio
import logging

from . import analyzers, inspector, interstitial, scoring, store
from .config import settings
from .enrichment import contacts as contact_extractor
from .enrichment import domain as domain_lookup
from .enrichment import links as link_checker
from .fetcher import FetchError, fetch
from .parser import parse
from .schemas import FetchResult

log = logging.getLogger(__name__)


async def no_domain():
    return None


def response_block_reason(fetched: FetchResult) -> str | None:
    if fetched.status == 403:
        return "The site refused automated access with HTTP 403."

    if fetched.status in {429, 503}:
        retry_after = fetched.headers.get("retry-after")
        suffix = f" Retry after {retry_after}." if retry_after else " Please try again later."
        return f"The site temporarily refused the request with HTTP {fetched.status}.{suffix}"

    return None


async def run(job_id: str, url: str) -> None:
    store.mark_running(job_id)
    try:
        fetched = await fetch(url)

        if blocked := interstitial.detect(fetched):
            store.mark_blocked(job_id, blocked.reason)
            return

        if reason := response_block_reason(fetched):
            store.mark_blocked(job_id, reason)
            return

        if fetched.status >= 400:
            store.mark_blocked(
                job_id,
                f"The server returned HTTP {fetched.status}, so there was no page to analyze.",
            )
            return

        page = parse(fetched)
        contacts = contact_extractor.extract(page, fetched.html)
        domain_info, link_report = await asyncio.gather(
            domain_lookup.lookup(page.url) if settings.domain_lookup_enabled else no_domain(),
            link_checker.verify(page),
        )

        elements = inspector.inspect(fetched.html, page.url)
        outcomes, diagnostics = analyzers.run_all(page, domain_info, contacts, link_report)
        store.mark_done(
            job_id,
            scoring.build_result(page, outcomes, diagnostics, elements, domain_info, contacts),
        )
    except FetchError as exc:
        log.info("Analysis %s could not fetch the page: %s", job_id, exc)
        store.mark_failed(job_id, "The page could not be fetched or analyzed.")
    except Exception as exc:
        log.exception("Analysis %s crashed", job_id)
        store.mark_failed(job_id, "The analysis failed unexpectedly. Please try again later.")
