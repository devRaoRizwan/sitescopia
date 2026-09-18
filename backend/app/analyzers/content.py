from ..schemas import Category, Finding, ParsedPage, Severity
from .helpers import CRITICAL, MINOR, Check, finding_factory, plural, sample

finding = finding_factory(Category.CONTENT)

THIN_TEXT_CHARS = 500

PLACEHOLDER_MARKERS = (
    "lorem ipsum", "dolor sit amet", "coming soon", "under construction",
    "your text here", "insert text here", "sample text", "todo:",
)
CLIENT_RENDERED_CHARS = 200


def check_status(page: ParsedPage) -> list[Finding]:
    if page.status >= 400:
        return [
            finding(
                Severity.ERROR,
                f"Page returned HTTP {page.status}",
                "The server reported an error for this URL.",
                recommendation="Fix the route or redirect it to a working page.",
            )
        ]
    if page.status >= 300:
        return [finding(Severity.INFO, f"Page returned HTTP {page.status}")]
    return []


def check_client_rendered(page: ParsedPage) -> list[Finding]:
    if page.text_length >= CLIENT_RENDERED_CHARS or not page.scripts:
        return []
    return [
        finding(
            Severity.INFO,
            "Page appears to be client-rendered",
            f"The server returned only {page.text_length} characters of text alongside "
            f"{plural(len(page.scripts), 'script')}. The real content is probably built "
            "by JavaScript, which this scan does not execute.",
            sample(page.scripts, limit=3),
            "Treat the other findings as provisional. Server-side rendering or "
            "prerendering would make the page visible to crawlers too.",
        )
    ]


def check_redirects(page: ParsedPage) -> list[Finding]:
    if len(page.redirects) < 2:
        return []
    return [
        finding(
            Severity.WARNING,
            f"{plural(len(page.redirects), 'redirect')} before the final page",
            "Each hop adds a full round trip before anything renders.",
            " ->\n".join(page.redirects + [page.url]),
            "Point the first URL straight at the destination.",
        )
    ]


def check_text_volume(page: ParsedPage) -> list[Finding]:
    if not CLIENT_RENDERED_CHARS <= page.text_length < THIN_TEXT_CHARS:
        return []
    return [
        finding(
            Severity.INFO,
            f"Thin content ({page.text_length} characters of text)",
            "Pages with little text rarely rank for anything competitive.",
            recommendation="Expand the page, or accept this if it is a utility page.",
        )
    ]


def check_link_profile(page: ParsedPage) -> list[Finding]:
    if not page.links:
        return [
            finding(
                Severity.WARNING,
                "No links found on the page",
                "Crawlers discover the rest of a site by following links.",
                recommendation="Check that navigation is rendered server-side.",
            )
        ]

    internal = sum(1 for link in page.links if link.internal)
    return [
        finding(
            Severity.PASS,
            f"{plural(len(page.links), 'link')} found",
            evidence=f"{internal} internal, {len(page.links) - internal} external",
        )
    ]


def check_placeholder_text(page: ParsedPage) -> list[Finding]:
    haystack = " ".join(
        [page.title or "", page.meta_description or "", page.text_sample]
        + [text for _, text in page.headings]
    ).lower()

    found = [marker for marker in PLACEHOLDER_MARKERS if marker in haystack]
    if found:
        return [
            finding(
                Severity.ERROR,
                "Placeholder text is still on the page",
                "Unfinished copy is visible to visitors and to search engines.",
                ", ".join(found),
                "Replace it with the real content before this page is indexed.",
            )
        ]
    return [finding(Severity.PASS, "No placeholder text in headings or metadata")]


CHECKS = [
    Check("HTTP status", check_status, CRITICAL),
    Check("Placeholder text", check_placeholder_text, CRITICAL),
    Check("Client rendering", check_client_rendered),
    Check("Redirect chain", check_redirects),
    Check("Text volume", check_text_volume),
    Check("Link profile", check_link_profile, MINOR),
]
