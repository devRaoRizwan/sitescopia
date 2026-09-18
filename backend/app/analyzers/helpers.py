from collections.abc import Callable
from typing import NamedTuple

from ..schemas import Category, Finding, Severity


CRITICAL = 3.0
NORMAL = 1.0
MINOR = 0.4


class Check(NamedTuple):
    label: str
    run: Callable[..., list[Finding]]
    weight: float = NORMAL

FindingBuilder = Callable[..., Finding]


def finding_factory(category: Category) -> FindingBuilder:
    def build(
        severity: Severity,
        title: str,
        detail: str = "",
        evidence: str | None = None,
        recommendation: str | None = None,
    ) -> Finding:
        return Finding(
            category=category,
            severity=severity,
            title=title,
            detail=detail,
            evidence=evidence,
            recommendation=recommendation,
        )

    return build


def plural(count: int, singular: str, plural_form: str | None = None) -> str:
    word = singular if count == 1 else (plural_form or singular + "s")
    return f"{count} {word}"


def verb(count: int, singular: str, plural_form: str) -> str:
    return singular if count == 1 else plural_form


def sample(values: list[str], limit: int = 5) -> str:
    shown = "\n".join(values[:limit])
    return shown + "\n..." if len(values) > limit else shown
