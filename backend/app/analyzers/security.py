from urllib.parse import urlparse

from ..schemas import Category, Finding, ParsedPage, Severity
from .helpers import CRITICAL, MINOR, Check, finding_factory, plural, sample

finding = finding_factory(Category.SECURITY)

EXPECTED_HEADERS = [
    (
        "strict-transport-security",
        Severity.WARNING,
        "HSTS not set",
        "Browsers may still attempt an insecure first connection.",
        "Send Strict-Transport-Security: max-age=31536000; includeSubDomains",
    ),
    (
        "content-security-policy",
        Severity.WARNING,
        "No Content-Security-Policy",
        "CSP is the main defence against injected scripts.",
        "Start with a report-only policy, then tighten it.",
    ),
    (
        "x-content-type-options",
        Severity.INFO,
        "No X-Content-Type-Options",
        "Browsers may MIME-sniff responses into an unintended type.",
        "Send X-Content-Type-Options: nosniff",
    ),
    (
        "x-frame-options",
        Severity.INFO,
        "No X-Frame-Options or frame-ancestors",
        "The page can be framed by other sites (clickjacking).",
        "Send X-Frame-Options: DENY, or use CSP frame-ancestors.",
    ),
    (
        "referrer-policy",
        Severity.INFO,
        "No Referrer-Policy",
        "Full URLs may leak to third parties in the Referer header.",
        "Send Referrer-Policy: strict-origin-when-cross-origin",
    ),
]

VERSION_HEADERS = ("server", "x-powered-by", "x-aspnet-version")


def check_https(page: ParsedPage) -> list[Finding]:
    if urlparse(page.url).scheme != "https":
        return [
            finding(
                Severity.ERROR,
                "Page is served over HTTP",
                "Traffic is readable and modifiable in transit.",
                page.url,
                "Serve over HTTPS and redirect HTTP permanently.",
            )
        ]
    return [finding(Severity.PASS, "Served over HTTPS")]


def check_security_headers(page: ParsedPage) -> list[Finding]:
    csp = page.headers.get("content-security-policy", "")
    findings = []

    for name, severity, title, detail, fix in EXPECTED_HEADERS:
        superseded = name == "x-frame-options" and "frame-ancestors" in csp
        if name not in page.headers and not superseded:
            findings.append(finding(severity, title, detail, recommendation=fix))

    present = [name for name, *_ in EXPECTED_HEADERS if name in page.headers]
    if present:
        findings.append(
            finding(
                Severity.PASS,
                f"{plural(len(present), 'security header')} present",
                evidence=", ".join(present),
            )
        )
    return findings


def check_server_disclosure(page: ParsedPage) -> list[Finding]:
    leaks = {
        name: page.headers[name]
        for name in VERSION_HEADERS
        if any(character.isdigit() for character in page.headers.get(name, ""))
    }
    if leaks:
        return [
            finding(
                Severity.INFO,
                "Server software version disclosed",
                "Version numbers let attackers match the host to known CVEs.",
                "\n".join(f"{name}: {value}" for name, value in leaks.items()),
                "Strip version detail from these response headers.",
            )
        ]
    return []


def check_blank_target(page: ParsedPage) -> list[Finding]:
    risky = [
        link
        for link in page.links
        if link.target == "_blank" and "noopener" not in link.rel and "noreferrer" not in link.rel
    ]
    if risky:
        return [
            finding(
                Severity.INFO,
                f'{plural(len(risky), "link")} with target="_blank" and no rel="noopener"',
                "The opened page gets a window.opener handle back to yours. "
                "Modern browsers imply noopener, but older ones do not.",
                sample([link.url for link in risky]),
                'Add rel="noopener noreferrer".',
            )
        ]
    return []


def check_mixed_content(page: ParsedPage) -> list[Finding]:
    if urlparse(page.url).scheme != "https":
        return []

    insecure = [url for url in page.scripts + page.stylesheets if url.startswith("http://")]
    if insecure:
        return [
            finding(
                Severity.ERROR,
                f"{plural(len(insecure), 'resource')} loaded over HTTP on an HTTPS page",
                "Browsers block mixed active content, so these assets will not load.",
                sample(insecure),
                "Load every script and stylesheet over HTTPS.",
            )
        ]
    return []


CHECKS = [
    Check("HTTPS", check_https, CRITICAL),
    Check("Security headers", check_security_headers),
    Check("Version disclosure", check_server_disclosure, MINOR),
    Check("External link safety", check_blank_target, MINOR),
    Check("Mixed content", check_mixed_content, CRITICAL),
]
