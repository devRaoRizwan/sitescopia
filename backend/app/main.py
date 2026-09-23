from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import analyzers, pipeline, store
from .proxy_manager import proxy_manager
from .config import settings
from .rate_limit import SlidingWindowRateLimiter
from .safety import UnsafeURL, validate
from .schemas import AnalysisJob, AnalyzeRequest, CheckInventory

app = FastAPI(
    title="SiteScopia",
    version="0.1.0",
    docs_url="/docs" if settings.api_docs_enabled else None,
    redoc_url="/redoc" if settings.api_docs_enabled else None,
    openapi_url="/openapi.json" if settings.api_docs_enabled else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

analysis_rate_limiter = SlidingWindowRateLimiter(
    settings.analysis_rate_limit,
    settings.rate_limit_window,
    settings.rate_limit_max_keys,
)


def client_key(request: Request) -> str:
    if settings.trust_proxy_headers:
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",", 1)[0].strip()
    return request.client.host if request.client else "unknown"


@app.api_route("/api/health", methods=["GET", "HEAD"])
async def health() -> dict:
    return {"status": "ok", "proxy": await proxy_manager.diagnostics()}


@app.post("/api/analyses", status_code=202, response_model=AnalysisJob)
async def create_analysis(
    request: AnalyzeRequest,
    background: BackgroundTasks,
    http_request: Request,
) -> AnalysisJob | JSONResponse:
    allowed, retry_after = analysis_rate_limiter.check(client_key(http_request))
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Analysis rate limit exceeded. Try again later.",
                "retry_after": retry_after,
            },
            headers={"Retry-After": str(retry_after)},
        )

    if store.active_count() >= settings.max_active_analyses:
        raise HTTPException(
            status_code=503,
            detail="The analysis queue is full. Try again later.",
        )

    try:
        url = validate(request.url)
    except UnsafeURL as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    job = store.create(url)
    background.add_task(pipeline.run, job.id, url)
    return job


@app.get("/api/analyses/{job_id}", response_model=AnalysisJob)
async def get_analysis(job_id: str, x_analysis_token: str | None = Header(default=None)) -> AnalysisJob:
    job = store.get(job_id, x_analysis_token or "")
    if not job:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return job


@app.get("/api/checks", response_model=CheckInventory)
async def list_checks() -> CheckInventory:
    return CheckInventory(total=analyzers.check_count(), by_category=analyzers.inventory())

