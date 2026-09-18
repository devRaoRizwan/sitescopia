import re
from urllib.parse import unquote, urlparse

from ..schemas import Contacts, ContactHit, ParsedPage, SocialProfile

EMAIL_RE = re.compile(
    r"[A-Za-z0-9._%+\-]{1,64}"
    r"@"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9\-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,24}"
)

NON_EMAIL_TLDS = {
    "png", "jpg", "jpeg", "gif", "svg", "webp", "avif", "ico", "bmp",
    "css", "js", "mjs", "json", "html", "htm", "php", "xml",
    "woff", "woff2", "ttf", "otf", "eot", "mp4", "webm", "pdf", "zip",
}

PLACEHOLDER_DOMAINS = {
    "example.com", "example.org", "example.net", "domain.com", "yourdomain.com",
    "email.com", "youremail.com", "test.com", "sentry.io", "wixpress.com",
}

PLACEHOLDER_LOCALS = {
    "email", "youremail", "your", "username", "user", "name", "someone",
    "john.doe", "jane.doe", "firstname.lastname", "no-reply-example",
}

PHONE_PATTERNS = (
    re.compile(r"\+\d{1,3}[\s.\-]?\(?\d{1,4}\)?(?:[\s.\-]?\d{2,4}){2,4}"),
    re.compile(r"\(\d{3}\)\s?\d{3}[\s.\-]\d{4}"),
    re.compile(r"(?<![\d.])\d{3}[\s\-]\d{3}[\s\-]\d{4}(?![\d.])"),
)

DATE_LIKE = re.compile(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}")

PLATFORMS = {
    "facebook.com": "Facebook",
    "fb.com": "Facebook",
    "twitter.com": "X (Twitter)",
    "x.com": "X (Twitter)",
    "instagram.com": "Instagram",
    "linkedin.com": "LinkedIn",
    "youtube.com": "YouTube",
    "youtu.be": "YouTube",
    "github.com": "GitHub",
    "gitlab.com": "GitLab",
    "tiktok.com": "TikTok",
    "pinterest.com": "Pinterest",
    "reddit.com": "Reddit",
    "t.me": "Telegram",
    "telegram.me": "Telegram",
    "discord.gg": "Discord",
    "discord.com": "Discord",
    "wa.me": "WhatsApp",
    "threads.net": "Threads",
    "bsky.app": "Bluesky",
    "mastodon.social": "Mastodon",
    "medium.com": "Medium",
    "dribbble.com": "Dribbble",
    "behance.net": "Behance",
    "vimeo.com": "Vimeo",
    "twitch.tv": "Twitch",
}

SHARE_MARKERS = (
    "/sharer", "/share", "/intent/", "/dialog/", "share.php",
    "/submit", "/widgets/", "/plugins/", "/oauth", "/login", "/signup",
)

NON_HANDLE_SEGMENTS = {
    "company", "in", "channel", "c", "user", "users", "watch", "groups",
    "pages", "profile.php", "school", "showcase", "@", "home", "about",
}


def registrable_host(host: str) -> str:
    parts = (host or "").lower().removeprefix("www.").split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host.lower()


def is_real_email(candidate: str) -> bool:
    local, _, domain = candidate.rpartition("@")
    tld = domain.rsplit(".", 1)[-1].lower()
    if tld in NON_EMAIL_TLDS:
        return False
    if domain.lower() in PLACEHOLDER_DOMAINS:
        return False
    if local.lower() in PLACEHOLDER_LOCALS:
        return False
    if len(candidate) > 254 or ".." in candidate:
        return False
    return True


def is_real_phone(candidate: str) -> bool:
    if DATE_LIKE.search(candidate):
        return False
    digits = re.sub(r"\D", "", candidate)
    if not 8 <= len(digits) <= 15:
        return False
    if len(set(digits)) <= 2:
        return False
    return True


def extract_emails(page: ParsedPage, text: str) -> list[ContactHit]:
    found: dict[str, ContactHit] = {}

    for link in page.links:
        if link.url.lower().startswith("mailto:"):
            address = unquote(link.url[7:].split("?")[0]).strip()
            if EMAIL_RE.fullmatch(address) and is_real_email(address):
                found.setdefault(address.lower(), ContactHit(address, "mailto", "high"))

    for match in EMAIL_RE.finditer(text):
        address = match.group(0).rstrip(".")
        if is_real_email(address):
            found.setdefault(address.lower(), ContactHit(address, "page text", "medium"))

    return list(found.values())[:25]


CONFIDENCE_RANK = {"high": 0, "medium": 1, "low": 2}


NATIONAL_NUMBER_DIGITS = 9


def phone_key(number: str) -> str:
    return re.sub(r"\D", "", number)[-NATIONAL_NUMBER_DIGITS:]


def extract_phones(page: ParsedPage, text: str) -> list[ContactHit]:
    candidates: list[ContactHit] = []

    for link in page.links:
        if link.url.lower().startswith("tel:"):
            number = unquote(link.url[4:]).strip()
            if is_real_phone(number):
                candidates.append(ContactHit(number, "tel: link", "high"))

    for pattern in PHONE_PATTERNS:
        for match in pattern.finditer(text):
            number = match.group(0).strip()
            if is_real_phone(number):
                confidence = "medium" if number.startswith("+") else "low"
                candidates.append(ContactHit(number, "page text", confidence))

    best: dict[str, ContactHit] = {}
    for hit in sorted(
        candidates,
        key=lambda h: (CONFIDENCE_RANK[h.confidence], -len(re.sub(r"\D", "", h.value))),
    ):
        best.setdefault(phone_key(hit.value), hit)

    return list(best.values())[:25]


def handle_from(path: str) -> str | None:
    segments = [s for s in path.split("/") if s]
    meaningful = [s for s in segments if s.lower() not in NON_HANDLE_SEGMENTS]
    if not meaningful:
        return None
    handle = meaningful[0].lstrip("@")
    return handle if 1 < len(handle) <= 40 else None


def extract_social(page: ParsedPage) -> list[SocialProfile]:
    found: dict[str, SocialProfile] = {}

    for link in page.links:
        parsed = urlparse(link.url)
        platform = PLATFORMS.get(registrable_host(parsed.hostname or ""))
        if not platform:
            continue

        lowered = link.url.lower()
        if any(marker in lowered for marker in SHARE_MARKERS):
            continue
        if not parsed.path.strip("/"):
            continue

        found.setdefault(
            platform,
            SocialProfile(platform=platform, url=link.url, handle=handle_from(parsed.path)),
        )

    return sorted(found.values(), key=lambda profile: profile.platform)


def extract(page: ParsedPage, html_text: str) -> Contacts:
    return Contacts(
        emails=extract_emails(page, html_text),
        phones=extract_phones(page, html_text),
        social=extract_social(page),
    )
