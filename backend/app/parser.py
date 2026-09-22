from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .schemas import FetchResult, Image, Link, ParsedPage

SKIPPED_SCHEMES = ("mailto:", "tel:", "javascript:", "#")

ICON_SELECTORS = (
    'link[rel="icon"][href]',
    'link[rel="shortcut icon"][href]',
    'link[rel="apple-touch-icon"][href]',
    'link[rel="apple-touch-icon-precomposed"][href]',
)


def registrable_domain(host: str) -> str:
    parts = (host or "").lower().split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host.lower()


def meta_content(soup: BeautifulSoup, **attrs: str) -> str | None:
    tag = soup.find("meta", attrs=attrs)
    return tag["content"].strip() if tag and tag.get("content") else None


def extract_favicon(soup: BeautifulSoup, base: str) -> str | None:
    for selector in ICON_SELECTORS:
        tag = soup.select_one(selector)
        if not tag:
            continue
        candidate = urljoin(base, tag["href"].strip())
        if urlparse(candidate).scheme in ("http", "https"):
            return candidate
    return None


def read_site_name(soup: BeautifulSoup, og: dict[str, str], base: str) -> str | None:
    if og.get("site_name"):
        return og["site_name"]
    tag = soup.select_one('meta[name="application-name"][content]')
    if tag:
        return tag["content"].strip()
    return (urlparse(base).hostname or "").removeprefix("www.") or None


def extract_headings(soup: BeautifulSoup) -> list[tuple[int, str]]:
    return [
        (int(tag.name[1]), tag.get_text(" ", strip=True))
        for tag in soup.select("h1,h2,h3,h4,h5,h6")
    ]


def extract_images(soup: BeautifulSoup, base: str) -> list[Image]:
    return [
        Image(
            src=urljoin(base, tag.get("src", "")),
            alt=tag.get("alt"),
            has_dimensions=bool(tag.get("width") and tag.get("height")),
        )
        for tag in soup.select("img")
    ]


def extract_links(soup: BeautifulSoup, base: str, base_domain: str) -> list[Link]:
    links = []
    for tag in soup.select("a[href]"):
        href = tag["href"].strip()
        if href.startswith(SKIPPED_SCHEMES):
            continue

        url = urljoin(base, href)
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            continue

        rel = tag.get("rel")
        links.append(
            Link(
                url=url,
                text=tag.get_text(" ", strip=True)[:120],
                internal=registrable_domain(parsed.hostname or "") == base_domain,
                rel=" ".join(rel) if isinstance(rel, list) else (rel or ""),
                target=tag.get("target", ""),
            )
        )
    return links


def parse(fetched: FetchResult) -> ParsedPage:
    soup = BeautifulSoup(fetched.html, "html.parser")
    base = fetched.url
    base_domain = registrable_domain(urlparse(base).hostname or "")

    title = soup.select_one("title")
    canonical = soup.select_one('link[rel="canonical"][href]')
    html_tag = soup.select_one("html")
    body = soup.select_one("body")
    body_text = body.get_text(" ", strip=True) if body else ""
    og = {
        tag["property"][3:]: tag.get("content", "").strip()
        for tag in soup.select('meta[property^="og:"][content]')
        if tag.get("property")
    }

    return ParsedPage(
        url=base,
        status=fetched.status,
        headers=fetched.headers,
        elapsed_ms=fetched.elapsed_ms,
        bytes=fetched.bytes,
        redirects=fetched.redirects,
        title=title.get_text(" ", strip=True) if title else None,
        site_name=read_site_name(soup, og, base),
        favicon=extract_favicon(soup, base),
        meta_description=meta_content(soup, name="description"),
        canonical=urljoin(base, canonical["href"]) if canonical else None,
        lang=html_tag.get("lang") if html_tag else None,
        viewport=meta_content(soup, name="viewport"),
        robots=meta_content(soup, name="robots"),
        og=og,
        headings=extract_headings(soup),
        images=extract_images(soup, base),
        links=extract_links(soup, base, base_domain),
        scripts=[urljoin(base, tag["src"]) for tag in soup.select("script[src]")],
        stylesheets=[
            urljoin(base, tag["href"]) for tag in soup.select('link[rel="stylesheet"][href]')
        ],
        inline_script_count=len(soup.select("script:not([src])")),
        text_length=len(body_text),
        text_sample=body_text[:4000],
    )
