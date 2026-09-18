from dataclasses import asdict

from .schemas import (
    AnalysisResult,
    Category,
    CheckOutcome,
    Contacts,
    DomainInfo,
    Finding,
    Insights,
    PageInfo,
    ParsedPage,
    Scores,
    Severity,
)

CREDIT = {
    Severity.PASS: 1.0,
    Severity.INFO: 0.9,
    Severity.WARNING: 0.6,
    Severity.ERROR: 0.0,
}

SEVERITY_ORDER = {
    Severity.ERROR: 0,
    Severity.WARNING: 1,
    Severity.INFO: 2,
    Severity.PASS: 3,
}


def worst_severity(findings: list[Finding]) -> Severity:
    if not findings:
        return Severity.PASS
    return min((f.severity for f in findings), key=lambda s: SEVERITY_ORDER[s])


def score(outcomes: list[CheckOutcome]) -> Scores:
    by_category: dict[str, int] = {}

    for category in Category:
        relevant = [o for o in outcomes if o.category == category]
        if not relevant:
            continue
        earned = sum(CREDIT[worst_severity(o.findings)] * o.weight for o in relevant)
        possible = sum(o.weight for o in relevant)
        by_category[category.value] = round(100 * earned / possible)

    overall = round(sum(by_category.values()) / len(by_category)) if by_category else 0
    return Scores(overall=overall, by_category=by_category)


def build_result(
    page: ParsedPage,
    outcomes: list[CheckOutcome],
    diagnostics: list[str] | None = None,
    domain_info: DomainInfo | None = None,
    contacts: Contacts | None = None,
) -> AnalysisResult:
    findings = [f for outcome in outcomes for f in outcome.findings]
    ordered = sorted(findings, key=lambda f: (SEVERITY_ORDER[f.severity], f.category.value))

    return AnalysisResult(
        page=PageInfo(
            final_url=page.url,
            status=page.status,
            elapsed_ms=page.elapsed_ms,
            bytes=page.bytes,
            redirects=page.redirects,
            title=page.title,
            site_name=page.site_name,
            favicon=page.favicon,
        ),
        scores=score(outcomes),
        findings=ordered,
        insights=Insights(
            domain=asdict(domain_info) if domain_info else None,
            contacts=asdict(contacts) if contacts else None,
        ),
        diagnostics=diagnostics or [],
    )
