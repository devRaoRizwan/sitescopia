from ..enrichment.links import LinkReport
from ..schemas import Category, Finding, Severity
from .helpers import CRITICAL, Check, finding_factory, plural, sample

finding = finding_factory(Category.CONTENT)


def check_broken_links(report: LinkReport) -> list[Finding]:
    if not report.checked:
        return []

    broken = report.broken
    if not broken:
        return [
            finding(
                Severity.PASS,
                f"All {plural(len(report.checked), 'checked link')} resolve",
                evidence=f"{report.skipped} more were not checked" if report.skipped else None,
            )
        ]

    internal = [check for check in broken if check.internal]
    severity = Severity.ERROR if internal else Severity.WARNING

    return [
        finding(
            severity,
            f"{plural(len(broken), 'link')} on this page {'leads' if len(broken) == 1 else 'lead'} nowhere",
            "Visitors hit a dead end, and Google wastes crawl budget following them. "
            + (
                f"{len(internal)} of them point at your own pages."
                if internal
                else "They all point at other sites."
            ),
            sample([f"{check.url} ({check.reason})" for check in broken]),
            "Repair or remove them. Internal ones matter most.",
        )
    ]


CHECKS = [Check("Broken links", check_broken_links, CRITICAL)]
