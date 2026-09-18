import re
from dataclasses import dataclass

from .schemas import FetchResult

CHALLENGE_STATUSES = {401, 403, 429, 503}

HEADER_SIGNALS = {
    "cf-mitigated": "Cloudflare",
    "x-datadome": "DataDome",
    "x-sucuri-block": "Sucuri",
    "x-iinfo": "Imperva Incapsula",
}

BODY_SIGNALS = (
    (re.compile(r"/cdn-cgi/challenge-platform/", re.I), "Cloudflare"),
    (re.compile(r"\bcf[_-]chl[_-]opt\b", re.I), "Cloudflare"),
    (re.compile(r"Checking your browser before accessing", re.I), "Cloudflare"),
    (re.compile(r"Attention Required!\s*\|\s*Cloudflare", re.I), "Cloudflare"),
    (re.compile(r"Enable JavaScript and cookies to continue", re.I), "Cloudflare"),
    (re.compile(r"_Incapsula_Resource", re.I), "Imperva Incapsula"),
    (re.compile(r"Incapsula incident ID", re.I), "Imperva Incapsula"),
    (re.compile(r"Sucuri WebSite Firewall", re.I), "Sucuri"),
    (re.compile(r"\bPerimeterX\b|\b_px(hd|Captcha)\b", re.I), "PerimeterX"),
    (re.compile(r"captcha-delivery\.com|\bdatadome\b", re.I), "DataDome"),
    (re.compile(r"Request blocked\..{0,80}AWS WAF", re.I | re.S), "AWS WAF"),
    (re.compile(r"Access Denied.{0,200}Reference #\d", re.I | re.S), "Akamai"),
    (re.compile(r"\bg-recaptcha\b.{0,200}verify you are (a )?human", re.I | re.S), "reCAPTCHA"),
)

TITLE_SIGNALS = (
    "just a moment",
    "attention required",
    "access denied",
    "security check",
    "please wait",
    "are you a robot",
    "verify you are human",
    "one more step",
    "bot verification",
    "ddos protection",
)


@dataclass
class Blocked:
    vendor: str | None
    status: int
    signal: str

    @property
    def reason(self) -> str:
        who = self.vendor or "A bot-protection service"
        return (
            f"{who} served a challenge page instead of the site "
            f"(HTTP {self.status}). Detected via {self.signal}."
        )


def title_of(html: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    return match.group(1).strip().lower() if match else ""


def detect(fetched: FetchResult) -> Blocked | None:
    for header, vendor in HEADER_SIGNALS.items():
        if header in fetched.headers:
            return Blocked(vendor, fetched.status, f"the {header} response header")

    head = fetched.html[:60_000]

    for pattern, vendor in BODY_SIGNALS:
        if pattern.search(head):
            return Blocked(vendor, fetched.status, "a challenge script in the page body")

    title = title_of(head)
    if any(signal in title for signal in TITLE_SIGNALS):
        vendor = "Cloudflare" if "cf-ray" in fetched.headers else None
        return Blocked(vendor, fetched.status, f"the page title {title!r}")

    if fetched.status in CHALLENGE_STATUSES and len(fetched.html) < 8_000:
        return Blocked(None, fetched.status, f"an HTTP {fetched.status} with a near-empty body")

    return None
