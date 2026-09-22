from collections import Counter
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .schemas import ElementGroup, ElementItem

MAX_PER_GROUP = 120
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


def item(
    label: str,
    props: dict[str, str],
    line: int | None = None,
    depth: int = 0,
    alert: bool = False,
) -> ElementItem:
    return ElementItem(
        line=line,
        depth=depth,
        alert=alert,
        label=label or "(empty)",
        props={k: v for k, v in props.items() if v},
    )


def build_outline(soup) -> ElementGroup | None:
    tags = soup.select("h1,h2,h3,h4,h5,h6")
    if not tags:
        return None

    main_titles = sum(1 for tag in tags if tag.name == "h1")
    seen_main = 0
    items = []
    for tag in tags:
        level = int(tag.name[1])
        alert = False
        if level == 1:
            seen_main += 1
            alert = seen_main > 1
        text = tag.get_text(" ", strip=True)
        if not text:
            alert = True
        items.append(
            item(
                shorten(text) or "(empty heading)",
                {
                    "Role": HEADING_ROLE[level],
                    "Problem": "A second main title. Google expects one per page." if level == 1 and seen_main > 1 else ("This heading has no text" if not text else ""),
                },
                tag.sourceline,
                level,
                alert,
            )
        )
    hint = "Google reads these as your page's table of contents and uses them to work out what it is about."
    if main_titles == 0:
        hint = "No main title, so Google has nothing to anchor the page's topic to."
    elif main_titles > 1:
        hint = f"{main_titles} main titles. Google expects one, so the page's topic reads as split."

    return ElementGroup(
        key="outline",
        label="Page outline",
        headline=f"{len(items)} headings",
        hint=hint,
        total=len(items),
        items=items[:MAX_PER_GROUP],
    )


def build_pictures(soup, base: str) -> ElementGroup | None:
    tags = soup.select("img")
    if not tags:
        return None

    items = []
    for tag in tags:
        src = tag.get("src", "")
        alt = tag.get("alt")
        if alt is None:
            description = "Missing, so people using a screen reader are told nothing"
        elif not alt.strip():
            description = "Marked decorative, so screen readers skip it"
        else:
            description = f'"{shorten(alt, 70)}"'
        items.append(
            item(
                (urlparse(urljoin(base, src)).path.rsplit("/", 1)[-1] or "picture") if src else "(no source)",
                {
                    "Description": description,
                    "Reserved space": "Yes" if tag.get("width") and tag.get("height") else "No, so the page can jump as it loads",
                },
                tag.sourceline,
                0,
                alt is None,
            )
        )

    missing = sum(1 for tag in tags if tag.get("alt") is None)
    hint = (
        f"{missing} of {len(tags)} pictures have no description. Google cannot see pictures, so it reads the description to understand them, and they can rank in image search."
        if missing
        else "Every picture has a description, so Google can understand them and rank them in image search."
    )
    return ElementGroup(
        key="pictures",
        label="Pictures",
        headline=f"{missing} of {len(tags)} need a description" if missing else f"{len(tags)} all described",
        hint=hint,
        total=len(items),
        items=items[:MAX_PER_GROUP],
    )


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
        example.setdefault(host, shorten(tag.get_text(" ", strip=True)) or "(the link has no words)")

    if not counts:
        return None

    items = [
        item(host, {"Links from this page": str(count), "First link reads": example[host]})
        for host, count in counts.most_common(MAX_PER_GROUP)
    ]
    return ElementGroup(
        key="destinations",
        label="Sites you link to",
        headline=f"{len(counts)} other {'site' if len(counts) == 1 else 'sites'}",
        hint=f"Every outbound link passes a little of your page's authority to {len(counts)} other {'site' if len(counts) == 1 else 'sites'}. Add rel=\"nofollow\" to any you do not want to vouch for.",
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
        item(host, {"Files it loads": str(count), "Looks like": describe_service(sample[host])})
        for host, count in counts.most_common(MAX_PER_GROUP)
    ]
    return ElementGroup(
        key="third-party",
        label="Other companies' code",
        headline=f"{len(counts)} outside {'company' if len(counts) == 1 else 'companies'}",
        hint=f"{len(counts)} outside {'company runs' if len(counts) == 1 else 'companies run'} code here. Each one slows the page down, and page speed is a Google ranking factor.",
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
            problem = "No words at all, so a screen reader reads out the address instead"
        elif text.lower().strip(" .!>→") in {"click here", "here", "read more", "more", "link", "this", "learn more"}:
            problem = "Says nothing about where it goes"
        if problem:
            items.append(
                item(
                    text or "(no words)",
                    {"Problem": problem, "Goes to": shorten(urljoin(base, href), 70)},
                    tag.sourceline,
                    0,
                    True,
                )
            )

    if not items:
        return None
    return ElementGroup(
        key="weak-links",
        label="Links that need words",
        headline=f"{len(items)} to reword",
        hint="Google uses link wording to understand the page being linked to. \"Click here\" tells it nothing, and tells screen reader users nothing either.",
        total=len(items),
        items=items[:MAX_PER_GROUP],
    )


def build_internal_links(soup, base: str) -> ElementGroup | None:
    base_domain = registrable(host_of(base))
    counts: Counter[str] = Counter()
    anchors: dict[str, str] = {}

    for tag in soup.select("a[href]"):
        href = tag.get("href", "").strip()
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        absolute = urljoin(base, href)
        host = host_of(absolute)
        if not host or registrable(host) != base_domain:
            continue
        path = urlparse(absolute).path or "/"
        counts[path] += 1
        text = shorten(tag.get_text(" ", strip=True), 60)
        if text and path not in anchors:
            anchors[path] = text

    if not counts:
        return None

    items = [
        item(
            path,
            {"Linked from here": str(count), "Wording used": anchors.get(path, "(no words, so Google learns nothing)")},
            alert=path not in anchors,
        )
        for path, count in counts.most_common(MAX_PER_GROUP)
    ]
    return ElementGroup(
        key="internal",
        label="Your own pages you link to",
        headline=f"{len(counts)} of your pages",
        hint="Internal links tell Google which of your pages matter and what they are about. The wording you use is the strongest hint it gets.",
        total=len(counts),
        items=items,
    )


def inspect(html: str, base: str) -> list[ElementGroup]:
    soup = BeautifulSoup(html, "html.parser")
    groups = [
        build_outline(soup),
        build_pictures(soup, base),
        build_internal_links(soup, base),
        build_destinations(soup, base),
        build_third_party(soup, base),
        build_problem_links(soup, base),
    ]
    result = []
    for group in groups:
        if not group:
            continue
        group.alerts = sum(1 for entry in group.items if entry.alert)
        result.append(group)
    return result
