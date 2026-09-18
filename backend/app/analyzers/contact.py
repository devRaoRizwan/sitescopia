from ..schemas import Category, Contacts, Finding, Severity
from .helpers import CRITICAL, MINOR, Check, finding_factory, plural, sample

finding = finding_factory(Category.CONTACT)


def check_contact_method(contacts: Contacts) -> list[Finding]:
    total = len(contacts.emails) + len(contacts.phones)
    if total:
        return [
            finding(
                Severity.PASS,
                f"{plural(total, 'contact method')} found",
                evidence=f"{plural(len(contacts.emails), 'email')}, {plural(len(contacts.phones), 'phone number')}",
            )
        ]
    return [
        finding(
            Severity.INFO,
            "No email or phone number on this page",
            "Visitors and search engines both use contact details as a trust signal.",
            recommendation="Publish a contact route, even if only a form link.",
        )
    ]


def check_plaintext_email(contacts: Contacts) -> list[Finding]:
    exposed = [hit for hit in contacts.emails if hit.source == "page text"]
    if not exposed:
        return []
    return [
        finding(
            Severity.INFO,
            f"{plural(len(exposed), 'email address')} in plain page text",
            "Addresses written into the page body are easy for scrapers to harvest.",
            sample([hit.value for hit in exposed]),
            "Use a contact form, or obfuscate the address client-side.",
        )
    ]


def check_social_presence(contacts: Contacts) -> list[Finding]:
    if not contacts.social:
        return [
            finding(
                Severity.INFO,
                "No social profile links found",
                "Social links help search engines connect this site to your brand's other profiles.",
                recommendation="Link your profiles, and add sameAs entries in structured data.",
            )
        ]
    return [
        finding(
            Severity.PASS,
            f"{plural(len(contacts.social), 'social profile')} linked",
            evidence=", ".join(profile.platform for profile in contacts.social),
        )
    ]


CHECKS = [
    Check("Contact methods", check_contact_method),
    Check("Exposed email", check_plaintext_email, MINOR),
    Check("Social profiles", check_social_presence, MINOR),
]

