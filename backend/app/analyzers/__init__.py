from ..schemas import (
    CheckOutcome,
    Category,
    Contacts,
    DomainInfo,
    Finding,
    ParsedPage,
)
from . import accessibility, contact, content, domain, performance, security, seo
from .helpers import Check

MODULES = {
    Category.SEO: seo,
    Category.ACCESSIBILITY: accessibility,
    Category.SECURITY: security,
    Category.PERFORMANCE: performance,
    Category.CONTENT: content,
    Category.DOMAIN: domain,
    Category.CONTACT: contact,
}

ALL_CHECKS: list[Check] = [check for module in MODULES.values() for check in module.CHECKS]


def subject_for(category: Category, page, domain_info, contacts):
    if category is Category.DOMAIN:
        return None if domain_info is None or domain_info.lookup_error else domain_info
    if category is Category.CONTACT:
        return contacts
    return page


def run_all(
    page: ParsedPage,
    domain_info: DomainInfo | None = None,
    contacts: Contacts | None = None,
) -> tuple[list[CheckOutcome], list[str]]:
    outcomes: list[CheckOutcome] = []
    diagnostics: list[str] = []

    for category, module in MODULES.items():
        subject = subject_for(category, page, domain_info, contacts)
        if subject is None:
            continue

        for check in module.CHECKS:
            try:
                findings = check.run(subject)
            except Exception as exc:
                diagnostics.append(f"The {check.label} check could not run: {exc}")
                continue
            outcomes.append(
                CheckOutcome(
                    category=category,
                    label=check.label,
                    findings=findings,
                    weight=check.weight,
                )
            )

    return outcomes, diagnostics


def flatten(outcomes: list[CheckOutcome]) -> list[Finding]:
    return [finding for outcome in outcomes for finding in outcome.findings]


def inventory() -> dict[str, list[str]]:
    return {category.value: [check.label for check in module.CHECKS] for category, module in MODULES.items()}


def check_count() -> int:
    return len(ALL_CHECKS)
