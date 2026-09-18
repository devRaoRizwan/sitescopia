import logging

from . import analyzers, interstitial, scoring, store
from .config import settings
from .enrichment import contacts as contact_extractor
from .enrichment import domain as domain_lookup
from .fetcher import FetchError, fetch
from .parser import parse

log = logging.getLogger(__name__)


async def run(job_id: str, url: str) -> None:
    store.mark_running(job_id)
    try:
        fetched = await fetch(url)

        if blocked := interstitial.detect(fetched):
            store.mark_blocked(job_id, blocked.reason)
            return

        if fetched.status >= 400:
            store.mark_blocked(
                job_id,
                f"The server returned HTTP {fetched.status}, so there was no page to analyze.",
            )
            return

        page = parse(fetched)
        contacts = contact_extractor.extract(page, fetched.html)
        domain_info = await domain_lookup.lookup(page.url) if settings.domain_lookup_enabled else None

        outcomes, diagnostics = analyzers.run_all(page, domain_info, contacts)
        store.mark_done(
            job_id,
            scoring.build_result(page, outcomes, diagnostics, domain_info, contacts),
        )
    except FetchError as exc:
        log.info("Analysis %s could not fetch the page: %s", job_id, exc)
        store.mark_failed(job_id, "The page could not be fetched or analyzed.")
    except Exception as exc:
        log.exception("Analysis %s crashed", job_id)
        store.mark_failed(job_id, "The analysis failed unexpectedly. Please try again later.")
