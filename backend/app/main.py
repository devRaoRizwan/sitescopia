from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import analyzers, pipeline, store
from .config import settings
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


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyses", status_code=202, response_model=AnalysisJob)
async def create_analysis(request: AnalyzeRequest, background: BackgroundTasks) -> AnalysisJob:
    try:
        url = validate(request.url)
    except UnsafeURL as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    job = store.create(url)
    background.add_task(pipeline.run, job.id, url)
    return job


@app.get("/api/analyses/{job_id}", response_model=AnalysisJob)
async def get_analysis(job_id: str) -> AnalysisJob:
    job = store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="No analysis with that id.")
    return job


@app.get("/api/analyses", response_model=list[AnalysisJob])
async def list_analyses(limit: int = 20) -> list[AnalysisJob]:
    return store.recent(min(limit, 50))


@app.get("/api/checks", response_model=CheckInventory)
async def list_checks() -> CheckInventory:
    return CheckInventory(total=analyzers.check_count(), by_category=analyzers.inventory())

