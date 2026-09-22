from dataclasses import asdict

from .schemas import (
    AnalysisResult,
    HeadingOut,
    Structure,
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


MAX_OUTLINE_HEADINGS = 12


def build_structure(page: ParsedPage) -> Structure:
    internal = sum(1 for link in page.links if link.internal)
    return Structure(
        headings=[
            HeadingOut(level=level, text=text[:90])
            for level, text in page.headings[:MAX_OUTLINE_HEADINGS]
            if text
        ],
        heading_total=len(page.headings),
        links_internal=internal,
        links_external=len(page.links) - internal,
        images=len(page.images),
        images_without_alt=sum(1 for image in page.images if image.alt is None),
        scripts=len(page.scripts),
        inline_scripts=page.inline_script_count,
        stylesheets=len(page.stylesheets),
        text_length=page.text_length,
        word_count=len(page.text_sample.split()) if page.text_sample else 0,
        lang=page.lang,
    )


def build_result(
    page: ParsedPage,
    outcomes: list[CheckOutcome],
    diagnostics: list[str] | None = None,
    elements: list | None = None,
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
            meta_description=page.meta_description,
            canonical=page.canonical,
            robots=page.robots,
            site_name=page.site_name,
            favicon=page.favicon,
        ),
        scores=score(outcomes),
        findings=ordered,
        insights=Insights(
            domain=asdict(domain_info) if domain_info else None,
            contacts=asdict(contacts) if contacts else None,
            structure=build_structure(page),
            elements=elements or [],
        ),
        diagnostics=diagnostics or [],
    )
