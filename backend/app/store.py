import secrets
import uuid
from datetime import datetime, timezone

from .config import settings
from .schemas import AnalysisJob, AnalysisResult, Status

jobs: dict[str, AnalysisJob] = {}
order: list[str] = []


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def create(url: str) -> AnalysisJob:
    job = AnalysisJob(
        id=uuid.uuid4().hex[:12],
        access_token=secrets.token_urlsafe(32),
        url=url,
        status=Status.QUEUED,
        created_at=utc_now(),
    )
    jobs[job.id] = job
    order.append(job.id)

    while len(order) > settings.max_stored_jobs:
        jobs.pop(order.pop(0), None)

    return job


def get(job_id: str, access_token: str) -> AnalysisJob | None:
    job = jobs.get(job_id)
    if not job or not secrets.compare_digest(job.access_token, access_token):
        return None
    return job


def active_count() -> int:
    return sum(job.status in {Status.QUEUED, Status.RUNNING} for job in jobs.values())


def recent(limit: int = 20) -> list[AnalysisJob]:
    return [jobs[job_id] for job_id in reversed(order[-limit:]) if job_id in jobs]


def mark_running(job_id: str) -> None:
    if job := jobs.get(job_id):
        job.status = Status.RUNNING


def mark_done(job_id: str, result: AnalysisResult) -> None:
    if job := jobs.get(job_id):
        job.status = Status.DONE
        job.result = result
        job.finished_at = utc_now()


def mark_blocked(job_id: str, reason: str) -> None:
    if job := jobs.get(job_id):
        job.status = Status.BLOCKED
        job.error = reason
        job.finished_at = utc_now()


def mark_failed(job_id: str, error: str) -> None:
    if job := jobs.get(job_id):
        job.status = Status.FAILED
        job.error = error
        job.finished_at = utc_now()
