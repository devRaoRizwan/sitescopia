from ..schemas import Category, Finding, ParsedPage, Severity
import re

from .helpers import CRITICAL, MINOR, Check, finding_factory, plural

finding = finding_factory(Category.SEO)

TITLE_MIN, TITLE_MAX = 10, 60

BOILERPLATE_TITLES = {
    "home", "homepage", "home page", "welcome", "welcome to our website",
    "welcome to my website", "untitled", "untitled document", "new page",
    "index", "document", "page", "website", "my site", "my website",
}
DESCRIPTION_MIN, DESCRIPTION_MAX = 50, 160


def check_title(page: ParsedPage) -> list[Finding]:
    if not page.title:
        return [
            finding(
                Severity.ERROR,
                "Missing <title>",
                "The page has no title element.",
                recommendation="Add a unique 10-60 character <title> describing the page.",
            )
        ]

    length = len(page.title)
    if length > TITLE_MAX:
        return [
            finding(
                Severity.WARNING,
                f"Title too long ({length} characters)",
                "Search results truncate titles past roughly 60 characters.",
                page.title,
                f"Trim to under {TITLE_MAX} characters.",
            )
        ]
    if length < TITLE_MIN:
        return [
            finding(
                Severity.WARNING,
                f"Title very short ({length} characters)",
                evidence=page.title,
                recommendation="Describe the page more fully; aim for 10-60 characters.",
            )
        ]
    return [finding(Severity.PASS, "Title length is good", evidence=page.title)]


def check_meta_description(page: ParsedPage) -> list[Finding]:
    description = page.meta_description
    if not description:
        return [
            finding(
                Severity.WARNING,
                "Missing meta description",
                "Search engines will invent a snippet from page text instead.",
                recommendation=f'Add <meta name="description"> of {DESCRIPTION_MIN}-{DESCRIPTION_MAX} characters.',
            )
        ]

    length = len(description)
    if not DESCRIPTION_MIN <= length <= DESCRIPTION_MAX:
        return [
            finding(
                Severity.INFO,
                f"Meta description is {length} characters",
                f"Outside the {DESCRIPTION_MIN}-{DESCRIPTION_MAX} range that displays well.",
                description[:200],
                "Rewrite to fit the range.",
            )
        ]
    return [finding(Severity.PASS, "Meta description is well sized")]


def check_h1(page: ParsedPage) -> list[Finding]:
    h1s = [text for level, text in page.headings if level == 1]
    if not h1s:
        return [
            finding(
                Severity.ERROR,
                "No <h1> heading",
                "The page has no top-level heading.",
                recommendation="Add exactly one <h1> stating what the page is about.",
            )
        ]
    if len(h1s) > 1:
        return [
            finding(
                Severity.WARNING,
                f"{plural(len(h1s), '<h1> heading')}",
                "Multiple top-level headings dilute the page's main topic.",
                " | ".join(h1s[:5]),
                "Keep one <h1> and demote the rest to <h2>.",
            )
        ]
    return [finding(Severity.PASS, "Exactly one <h1>", evidence=h1s[0])]


def check_canonical(page: ParsedPage) -> list[Finding]:
    if not page.canonical:
        return [
            finding(
                Severity.INFO,
                "No canonical URL",
                "Without a canonical tag, duplicate URLs can compete with each other.",
                recommendation='Add <link rel="canonical" href="...">.',
            )
        ]
    if page.canonical.rstrip("/") != page.url.rstrip("/"):
        return [
            finding(
                Severity.INFO,
                "Canonical points elsewhere",
                "This page declares a different URL as the canonical version.",
                f"canonical: {page.canonical}\nactual: {page.url}",
                "Confirm this is deliberate; if not, it hides the page from search.",
            )
        ]
    return [finding(Severity.PASS, "Canonical URL is self-referencing")]


def check_robots_meta(page: ParsedPage) -> list[Finding]:
    if "noindex" in (page.robots or "").lower():
        return [
            finding(
                Severity.ERROR,
                "Page is set to noindex",
                "Search engines are instructed not to index this page at all.",
                page.robots,
                "Remove noindex unless this page is intentionally hidden.",
            )
        ]
    return []


def check_open_graph(page: ParsedPage) -> list[Finding]:
    missing = [tag for tag in ("title", "description", "image") if tag not in page.og]
    if missing:
        return [
            finding(
                Severity.INFO,
                "Incomplete Open Graph tags",
                "Links shared on social platforms will render without a rich preview.",
                "missing: " + ", ".join(f"og:{tag}" for tag in missing),
                "Add og:title, og:description and og:image.",
            )
        ]
    return [finding(Severity.PASS, "Open Graph tags present")]


def check_title_quality(page: ParsedPage) -> list[Finding]:
    if not page.title:
        return []

    normalized = page.title.strip().lower().rstrip(".!")
    if normalized in BOILERPLATE_TITLES:
        return [
            finding(
                Severity.WARNING,
                "Title is boilerplate",
                "This tells a searcher nothing about the page, so it competes with every other page using the same words.",
                page.title,
                "Say what the page is actually about, and include the term people would search for.",
            )
        ]

    host = (page.site_name or "").strip().lower()
    if host and normalized == host:
        return [
            finding(
                Severity.INFO,
                "Title is only the site name",
                "Every page sharing one title makes them indistinguishable in search results.",
                page.title,
                "Lead with the page topic, then the site name.",
            )
        ]
    return [finding(Severity.PASS, "Title describes the page")]


def check_description_quality(page: ParsedPage) -> list[Finding]:
    description = page.meta_description
    if not description:
        return []

    if page.title and description.strip().lower() == page.title.strip().lower():
        return [
            finding(
                Severity.WARNING,
                "Meta description repeats the title",
                "The snippet adds nothing beyond what the headline already says.",
                description,
                "Use the description to add detail the title does not have room for.",
            )
        ]

    words = [w for w in re.findall(r"[a-z']{4,}", description.lower())]
    if words:
        top = max(set(words), key=words.count)
        if words.count(top) >= 4:
            return [
                finding(
                    Severity.WARNING,
                    f"Meta description repeats '{top}' {words.count(top)} times",
                    "Repetition reads as keyword stuffing and can suppress the snippet entirely.",
                    description,
                    "Write it for a person deciding whether to click.",
                )
            ]
    return [finding(Severity.PASS, "Meta description reads naturally")]


CHECKS = [
    Check("Title", check_title, CRITICAL),
    Check("Title quality", check_title_quality, CRITICAL),
    Check("Description quality", check_description_quality),
    Check("Meta description", check_meta_description),
    Check("Single h1", check_h1, CRITICAL),
    Check("Canonical URL", check_canonical, MINOR),
    Check("Robots directives", check_robots_meta, CRITICAL),
    Check("Open Graph tags", check_open_graph, MINOR),
]
