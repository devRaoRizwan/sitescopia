from ..schemas import Category, DomainInfo, Finding, Severity
from .helpers import CRITICAL, MINOR, Check, finding_factory, plural

finding = finding_factory(Category.DOMAIN)

EXPIRY_CRITICAL_DAYS = 30
EXPIRY_WARNING_DAYS = 90
NEW_DOMAIN_DAYS = 90
TRANSFER_LOCK_STATUSES = {"client transfer prohibited", "server transfer prohibited"}


def check_expiry(info: DomainInfo) -> list[Finding]:
    days = info.expires_in_days
    if days is None:
        return []

    if days < 0:
        return [
            finding(
                Severity.ERROR,
                "Domain registration has expired",
                "An expired domain can be suspended or bought by someone else.",
                f"expired on {info.expires_on}",
                "Renew it immediately.",
            )
        ]
    if days < EXPIRY_CRITICAL_DAYS:
        return [
            finding(
                Severity.ERROR,
                f"Domain expires in {plural(days, 'day')}",
                "If it lapses the site goes offline and the name becomes available to others.",
                f"expires {info.expires_on}",
                "Renew now and enable auto-renew.",
            )
        ]
    if days < EXPIRY_WARNING_DAYS:
        return [
            finding(
                Severity.WARNING,
                f"Domain expires in {plural(days, 'day')}",
                "Worth renewing before it becomes urgent.",
                f"expires {info.expires_on}",
                "Renew early and enable auto-renew.",
            )
        ]
    return [
        finding(
            Severity.PASS,
            f"Domain registered until {info.expires_on}",
            evidence=f"{plural(days, 'day')} remaining",
        )
    ]


def check_age(info: DomainInfo) -> list[Finding]:
    if info.age_days is None:
        return []
    if info.age_days < NEW_DOMAIN_DAYS:
        return [
            finding(
                Severity.INFO,
                f"Domain is only {plural(info.age_days, 'day')} old",
                "Very new domains carry less trust with search engines and spam filters.",
                f"registered {info.registered_on}",
                "Nothing to fix — expect reputation to build over time.",
            )
        ]
    years = info.age_days // 365
    return [
        finding(
            Severity.PASS,
            f"Domain registered {plural(years, 'year')} ago",
            evidence=f"since {info.registered_on}",
        )
    ]


def check_dnssec(info: DomainInfo) -> list[Finding]:
    if info.dnssec is None:
        return []
    if not info.dnssec:
        return [
            finding(
                Severity.INFO,
                "DNSSEC is not enabled",
                "Without DNSSEC, DNS answers for this domain cannot be cryptographically verified.",
                recommendation="Enable DNSSEC at your registrar and DNS host.",
            )
        ]
    return [finding(Severity.PASS, "DNSSEC is enabled")]


def check_transfer_lock(info: DomainInfo) -> list[Finding]:
    if not info.status:
        return []
    locked = {s.lower() for s in info.status} & TRANSFER_LOCK_STATUSES
    if not locked:
        return [
            finding(
                Severity.WARNING,
                "No transfer lock on the domain",
                "A transfer lock is the main defence against domain hijacking.",
                ", ".join(info.status),
                "Enable the registrar transfer lock.",
            )
        ]
    return [finding(Severity.PASS, "Transfer lock is active")]


CHECKS = [
    Check("Registration expiry", check_expiry, CRITICAL),
    Check("Domain age", check_age, MINOR),
    Check("DNSSEC", check_dnssec, MINOR),
    Check("Transfer lock", check_transfer_lock),
]

