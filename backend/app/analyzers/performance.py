from ..config import settings
from ..schemas import Category, Finding, ParsedPage, Severity
from .helpers import CRITICAL, MINOR, Check, finding_factory, plural, sample, verb

finding = finding_factory(Category.PERFORMANCE)


def check_response_time(page: ParsedPage) -> list[Finding]:
    elapsed = page.elapsed_ms
    if elapsed <= settings.slow_response_ms:
        return [finding(Severity.PASS, f"HTML delivered in {elapsed} ms")]

    if elapsed > settings.very_slow_response_ms:
        severity = Severity.ERROR
        note = "Well past the point where people abandon a page."
    else:
        severity = Severity.WARNING
        note = "Slower than the ~1.5s users tolerate comfortably."

    return [
        finding(
            severity,
            f"Slow response: {elapsed} ms to deliver the HTML",
            f"{note} Measured from this server, so network distance is included.",
            recommendation="Check server rendering time, database queries and CDN coverage.",
        )
    ]


def check_page_size(page: ParsedPage) -> list[Finding]:
    kilobytes = page.bytes / 1024
    if page.bytes > settings.max_html_bytes:
        return [
            finding(
                Severity.WARNING,
                f"Large HTML document ({kilobytes:.0f} KB)",
                "Big HTML delays first paint even on a fast connection.",
                recommendation="Move inline data and styles out, and paginate long lists.",
            )
        ]
    return [finding(Severity.PASS, f"HTML size is {kilobytes:.0f} KB")]


def check_compression(page: ParsedPage) -> list[Finding]:
    encoding = page.headers.get("content-encoding")
    if not encoding:
        return [
            finding(
                Severity.WARNING,
                "Response is not compressed",
                "HTML typically shrinks by 70-80% with gzip or brotli.",
                recommendation="Enable brotli or gzip at the server or CDN.",
            )
        ]
    return [finding(Severity.PASS, f"Response compressed with {encoding}")]


def check_caching(page: ParsedPage) -> list[Finding]:
    if "cache-control" in page.headers or "etag" in page.headers:
        return []
    return [
        finding(
            Severity.INFO,
            "No caching headers",
            "Repeat visitors re-download the document every time.",
            recommendation="Send Cache-Control, or at least an ETag for revalidation.",
        )
    ]


def check_script_count(page: ParsedPage) -> list[Finding]:
    if len(page.scripts) <= settings.max_external_scripts:
        return []
    return [
        finding(
            Severity.WARNING,
            f"{plural(len(page.scripts), 'external script')}",
            "Each one is a request that can block or delay interactivity.",
            sample(page.scripts),
            "Bundle what you control and defer what you do not.",
        )
    ]


def check_image_dimensions(page: ParsedPage) -> list[Finding]:
    undimensioned = [image for image in page.images if not image.has_dimensions]
    if not undimensioned:
        return []
    return [
        finding(
            Severity.INFO,
            f"{len(undimensioned)} of {plural(len(page.images), 'image')} "
            f"{verb(len(undimensioned), 'lacks', 'lack')} width/height",
            "Without dimensions the browser cannot reserve space, so content shifts as images load.",
            sample([image.src for image in undimensioned]),
            "Set width and height attributes (CSS can still scale them).",
        )
    ]


CHECKS = [
    Check("Response time", check_response_time, CRITICAL),
    Check("Document size", check_page_size),
    Check("Compression", check_compression),
    Check("Caching headers", check_caching, MINOR),
    Check("Script count", check_script_count),
    Check("Image dimensions", check_image_dimensions, MINOR),
]
