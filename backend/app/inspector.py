from collections import Counter
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .schemas import ElementGroup, ElementItem

MAX_PER_GROUP = 40
MAX_TEXT = 110

HEADING_ROLE = {
    1: "Main title",
    2: "Section",
    3: "Sub-section",
    4: "Minor heading",
    5: "Minor heading",
    6: "Minor heading",
}

KNOWN_SERVICES = {
    "google-analytics.com": "Website analytics",
    "googletagmanager.com": "Tag and analytics manager",
    "googleapis.com": "Hosted code library",
    "gstatic.com": "Google hosted assets",
    "bootstrapcdn": "Styling framework",
    "typekit": "Web fonts",
    "segment.com": "Analytics routing",
    "sentry": "Error reporting",
    "disqus": "Comments",
    "mailchimp": "Email marketing",
    "analytics": "Website analytics",
    "plausible.io": "Website analytics",
    "hotjar": "Session recording",
    "doubleclick.net": "Advertising",
    "adservice": "Advertising",
    "ethicalads.io": "Advertising",
    "facebook.net": "Facebook tracking",
    "fonts.googleapis.com": "Web fonts",
    "fonts.gstatic.com": "Web fonts",
    "cloudflare": "Content delivery",
    "jsdelivr.net": "Content delivery",
    "unpkg.com": "Content delivery",
    "cdnjs": "Content delivery",
    "stripe.com": "Payments",
    "youtube.com": "Video embed",
    "recaptcha": "Bot protection",
    "intercom": "Live chat",
    "hubspot": "Marketing and CRM",
}


def shorten(value: str | None, limit: int = MAX_TEXT) -> str:
    if not value:
        return ""
    value = " ".join(value.split())
    return value if len(value) <= limit else value[: limit - 1] + "…"


def host_of(url: str) -> str:
    return (urlparse(url).hostname or "").removeprefix("www.")


def registrable(host: str) -> str:
    parts = (host or "").lower().split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host.lower()


def describe_service(url: str) -> str:
    lowered = url.lower()
    for marker, label in KNOWN_SERVICES.items():
        if marker in lowered:
            return label
    return "Unknown purpose"


def item(label: str, props: dict[str, str], line: int | None = None, depth: int = 0) -> ElementItem:
    return ElementItem(
        line=line,
        depth=depth,
        label=label or "(empty)",
        props={k: v for k, v in props.items() if v},
    )


def build_outline(soup) -> ElementGroup | None:
    tags = soup.select("h1,h2,h3,h4,h5,h6")
    if not tags:
        return None

    items = [
        item(
            shorten(tag.get_text(" ", strip=True)) or "(empty heading)",
            {"Role": HEADING_ROLE[int(tag.name[1])]},
            tag.sourceline,
            int(tag.name[1]),
        )
        for tag in tags
    ]
    main_titles = sum(1 for tag in tags if tag.name == "h1")
    hint = "This is the table of contents search engines and screen readers build from your page."
    if main_titles == 0:
        hint = "This page has no main title, so readers and search engines have nothing to anchor to."
    elif main_titles > 1:
        hint = f"This page has {main_titles} main titles. One is expected, so the topic reads as split."

    return ElementGroup(key="outline", label="Page outline", hint=hint, total=len(items), items=items[:MAX_PER_GROUP])


def build_pictures(soup, base: str) -> ElementGroup | None:
    tags = soup.select("img")
    if not tags:
        return None

    items = []
    for tag in tags:
        src = tag.get("src", "")
        alt = tag.get("alt")
        if alt is None:
            description = "Missing — people using a screen reader are told nothing"
        elif not alt.strip():
            description = "Marked decorative — screen readers skip it"
        else:
            description = f'"{shorten(alt, 70)}"'
        items.append(
            item(
                (urlparse(urljoin(base, src)).path.rsplit("/", 1)[-1] or "picture") if src else "(no source)",
                {
                    "Description": description,
                    "Reserved space": "Yes" if tag.get("width") and tag.get("height") else "No — the page can jump as it loads",
                },
                tag.sourceline,
            )
        )

    missing = sum(1 for tag in tags if tag.get("alt") is None)
    hint = (
        f"{missing} of {len(tags)} pictures have no description for screen readers."
        if missing
        else "Every picture has a description for screen readers."
    )
    return ElementGroup(key="pictures", label="Pictures", hint=hint, total=len(items), items=items[:MAX_PER_GROUP])


def build_destinations(soup, base: str) -> ElementGroup | None:
    base_domain = registrable(host_of(base))
    counts: Counter[str] = Counter()
    example: dict[str, str] = {}

    for tag in soup.select("a[href]"):
        href = tag.get("href", "").strip()
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        absolute = urljoin(base, href)
        host = host_of(absolute)
        if not host or registrable(host) == base_domain:
            continue
        counts[host] += 1
        example.setdefault(host, shorten(tag.get_text(" ", strip=True)) or absolute)

    if not counts:
        return None

    items = [
        item(host, {"Links to it": str(count), "First one says": example[host]})
        for host, count in counts.most_common(MAX_PER_GROUP)
    ]
    return ElementGroup(
        key="destinations",
        label="Sites you link to",
        hint=f"This page sends visitors to {len(counts)} other {'site' if len(counts) == 1 else 'sites'}.",
        total=len(counts),
        items=items,
    )


def build_third_party(soup, base: str) -> ElementGroup | None:
    base_domain = registrable(host_of(base))
    counts: Counter[str] = Counter()
    sample: dict[str, str] = {}

    for tag in soup.select("script[src], link[rel='stylesheet'][href]"):
        url = urljoin(base, tag.get("src") or tag.get("href") or "")
        host = host_of(url)
        if not host or registrable(host) == base_domain:
            continue
        counts[host] += 1
        sample.setdefault(host, url)

    if not counts:
        return None

    items = [
        item(host, {"Files loaded": str(count), "Looks like": describe_service(sample[host])})
        for host, count in counts.most_common(MAX_PER_GROUP)
    ]
    return ElementGroup(
        key="third-party",
        label="Other companies' code",
        hint=f"{len(counts)} outside {'company runs' if len(counts) == 1 else 'companies run'} code on this page. Each one can slow it down and see your visitors.",
        total=len(counts),
        items=items,
    )


def build_problem_links(soup, base: str) -> ElementGroup | None:
    items = []
    for tag in soup.select("a[href]"):
        text = tag.get_text(" ", strip=True)
        href = tag.get("href", "").strip()
        if href.startswith(("mailto:", "tel:", "javascript:")):
            continue
        problem = None
        if not text:
            problem = "No words at all — a screen reader reads out the address instead"
        elif text.lower().strip(" .!>→") in {"click here", "here", "read more", "more", "link", "this", "learn more"}:
            problem = "Says nothing about where it goes"
        if problem:
            items.append(item(text or "(no words)", {"Problem": problem, "Goes to": shorten(urljoin(base, href), 70)}, tag.sourceline))

    if not items:
        return None
    return ElementGroup(
        key="weak-links",
        label="Links that need words",
        hint="People who navigate by jumping between links hear only the link text, with none of the surrounding sentence.",
        total=len(items),
        items=items[:MAX_PER_GROUP],
    )


def inspect(html: str, base: str) -> list[ElementGroup]:
    soup = BeautifulSoup(html, "html.parser")
    groups = [
        build_outline(soup),
        build_pictures(soup, base),
        build_destinations(soup, base),
        build_third_party(soup, base),
        build_problem_links(soup, base),
    ]
    return [group for group in groups if group]
