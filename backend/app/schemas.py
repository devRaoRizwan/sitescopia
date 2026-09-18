from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    PASS = "pass"


class Category(str, Enum):
    SEO = "seo"
    ACCESSIBILITY = "accessibility"
    SECURITY = "security"
    PERFORMANCE = "performance"
    CONTENT = "content"
    DOMAIN = "domain"
    CONTACT = "contact"


class Status(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    BLOCKED = "blocked"


class Finding(BaseModel):
    category: Category
    severity: Severity
    title: str
    detail: str = ""
    evidence: str | None = None
    recommendation: str | None = None


@dataclass
class FetchResult:
    url: str
    status: int
    headers: dict[str, str]
    html: str
    elapsed_ms: int
    bytes: int
    redirects: list[str] = field(default_factory=list)


@dataclass
class Image:
    src: str
    alt: str | None
    has_dimensions: bool


@dataclass
class Link:
    url: str
    text: str
    internal: bool
    rel: str
    target: str


@dataclass
class ParsedPage:
    url: str
    status: int
    headers: dict[str, str]
    elapsed_ms: int
    bytes: int
    redirects: list[str]
    title: str | None
    site_name: str | None
    favicon: str | None
    meta_description: str | None
    canonical: str | None
    lang: str | None
    viewport: str | None
    robots: str | None
    og: dict[str, str]
    headings: list[tuple[int, str]]
    images: list[Image]
    links: list[Link]
    scripts: list[str]
    stylesheets: list[str]
    inline_script_count: int
    text_length: int
    text_sample: str = ""


@dataclass
class CheckOutcome:
    category: Category
    label: str
    findings: list[Finding]
    weight: float = 1.0


@dataclass
class SocialProfile:
    platform: str
    url: str
    handle: str | None


@dataclass
class ContactHit:
    value: str
    source: str
    confidence: str


@dataclass
class Contacts:
    emails: list[ContactHit]
    phones: list[ContactHit]
    social: list[SocialProfile]


@dataclass
class DomainInfo:
    domain: str
    registrar: str | None = None
    registered_on: str | None = None
    expires_on: str | None = None
    updated_on: str | None = None
    age_days: int | None = None
    expires_in_days: int | None = None
    status: list[str] = field(default_factory=list)
    nameservers: list[str] = field(default_factory=list)
    dns_provider: str | None = None
    dnssec: bool | None = None
    ip_addresses: list[str] = field(default_factory=list)
    hosting_provider: str | None = None
    lookup_error: str | None = None


class SocialProfileOut(BaseModel):
    platform: str
    url: str
    handle: str | None


class ContactHitOut(BaseModel):
    value: str
    source: str
    confidence: str


class ContactsOut(BaseModel):
    emails: list[ContactHitOut]
    phones: list[ContactHitOut]
    social: list[SocialProfileOut]


class DomainInfoOut(BaseModel):
    domain: str
    registrar: str | None
    registered_on: str | None
    expires_on: str | None
    updated_on: str | None
    age_days: int | None
    expires_in_days: int | None
    status: list[str]
    nameservers: list[str]
    dns_provider: str | None
    dnssec: bool | None
    ip_addresses: list[str]
    hosting_provider: str | None
    lookup_error: str | None


class Insights(BaseModel):
    domain: DomainInfoOut | None = None
    contacts: ContactsOut | None = None


class Scores(BaseModel):
    overall: int
    by_category: dict[str, int]


class PageInfo(BaseModel):
    final_url: str
    status: int
    elapsed_ms: int
    bytes: int
    redirects: list[str]
    title: str | None
    site_name: str | None = None
    favicon: str | None = None


class AnalysisResult(BaseModel):
    page: PageInfo
    scores: Scores
    findings: list[Finding]
    insights: Insights = Insights()
    diagnostics: list[str] = []


class AnalysisJob(BaseModel):
    id: str
    url: str
    status: Status
    created_at: datetime
    finished_at: datetime | None = None
    error: str | None = None
    result: AnalysisResult | None = None


class AnalyzeRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)


class CheckInfo(BaseModel):
    name: str
    category: str


class CheckInventory(BaseModel):
    total: int
    by_category: dict[str, list[str]]
