# SiteScopia Technical Guide

This document describes the architecture, local development workflow, API contract, security controls, configuration, and deployment model for SiteScopia.

For the short product overview, see [`README.md`](README.md).

## Contents

- [Architecture](#architecture)
- [Local development](#local-development)
- [Analysis lifecycle](#analysis-lifecycle)
- [API](#api)
- [Configuration](#configuration)
- [Security controls](#security-controls)
- [Frontend](#frontend)
- [Backend](#backend)
- [Deployment](#deployment)
- [Adding checks](#adding-checks)
- [Operational notes](#operational-notes)

## Architecture

SiteScopia is a two-service application in one repository:

```text
frontend/  React + Vite application  ->  Vercel
backend/   FastAPI service            ->  Render
```

At runtime, the browser talks to the backend over JSON. The frontend does not fetch scanned websites directly.

```text
Browser
  |
  | POST /api/analyses
  v
FastAPI API
  |
  +--> URL validation and SSRF checks
  +--> controlled page fetch
  +--> HTML parsing
  +--> RDAP/DNS and contact enrichment
  +--> analyzers and scoring
  v
In-memory job store
  |
  | GET /api/analyses/{id} + X-Analysis-Token
  v
Browser report
```

## Local Development

### Requirements

- Python 3.13 or newer
- Node.js 18 or newer
- npm
- [`uv`](https://docs.astral.sh/uv/) for Python environment management
- Chromium-based browser for optional prerendering

### Start the backend

From the repository root:

```bash
cd backend
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python -r requirements.txt
cp .env.example .env
.venv/bin/uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`.

```bash
curl http://127.0.0.1:8000/api/health
```

Expected response:

```json
{"status":"ok"}
```

### Start the frontend

Use a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

Vite proxies local `/api/*` requests to `http://127.0.0.1:8000`. The frontend uses `VITE_API_URL` only when calling a separately deployed backend.

### Build the frontend

```bash
cd frontend
npm run build
```

This runs Vite and then the prerender script. The generated site is placed in `frontend/dist`.

To preview the generated output:

```bash
npm run preview
```

## Analysis Lifecycle

1. The frontend sends `POST /api/analyses` with a URL.
2. The backend applies the request rate limit.
3. The URL is normalized and resolved. Non-public addresses are rejected.
4. A job is created with a random id and private access token.
5. The fetcher requests the page with timeout, size, and redirect limits.
6. Each redirect destination is validated before it is requested.
7. The response is checked for bot challenges and HTTP errors.
8. BeautifulSoup parses the HTML into a `ParsedPage` fact object.
9. Domain/DNS and contact enrichment runs where enabled.
10. Pure analyzer functions produce findings by category.
11. The scoring layer builds category and overall scores.
12. The frontend polls the job until it is `done`, `failed`, or `blocked`.

A blocked job has no score or findings. This prevents a bot challenge or error page from being reported as if it were the requested website.

## API

Interactive FastAPI documentation is disabled by default. Set `API_DOCS_ENABLED=true` for local API work, then open `/docs` or `/redoc`.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Liveness check |
| `POST` | `/api/analyses` | Start an analysis; returns `202` |
| `GET` | `/api/analyses/{id}` | Read a job with its private token |
| `GET` | `/api/checks` | Return the check inventory |

### Create an analysis

```bash
curl -X POST http://127.0.0.1:8000/api/analyses \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com"}'
```

The response contains an `id` and an `access_token`. Keep the token with the frontend session and send it when polling:

```bash
curl http://127.0.0.1:8000/api/analyses/<job-id> \
  -H 'X-Analysis-Token: <access-token>'
```

There is no endpoint that lists other users' jobs.

## Configuration

Copy `backend/.env.example` to `backend/.env`. Pydantic Settings reads environment variables and uses `.env` for local development.

| Variable | Default | Purpose |
| --- | ---: | --- |
| `FETCH_TIMEOUT` | `15` | Page request timeout in seconds |
| `FETCH_MAX_BYTES` | `5242880` | Maximum fetched response body |
| `FETCH_MAX_REDIRECTS` | `5` | Maximum redirect hops |
| `USER_AGENT` | `SiteScopia/0.1` | User-Agent for page requests |
| `RDAP_TIMEOUT` | `10` | Registry lookup timeout |
| `DOMAIN_LOOKUP_ENABLED` | `true` | Enable RDAP/DNS enrichment |
| `CORS_ORIGINS` | frontend origin | Allowed browser origins as a JSON list |
| `MAX_STORED_JOBS` | `200` | Maximum retained in-memory jobs |
| `ANALYSIS_RATE_LIMIT` | `10` | Analyses accepted per client per window |
| `RATE_LIMIT_WINDOW` | `60` | Rate-limit window in seconds |
| `RATE_LIMIT_MAX_KEYS` | `10000` | Maximum in-memory client buckets |
| `MAX_ACTIVE_ANALYSES` | `4` | Maximum queued or running analyses |
| `TRUST_PROXY_HEADERS` | `false` | Trust `X-Forwarded-For` only behind a sanitizing proxy |
| `API_DOCS_ENABLED` | `false` | Enable FastAPI docs and OpenAPI |
| `SLOW_RESPONSE_MS` | `1500` | Slow response warning threshold |
| `VERY_SLOW_RESPONSE_MS` | `3000` | Very slow response error threshold |
| `MAX_HTML_BYTES` | `153600` | HTML size warning threshold |
| `MAX_EXTERNAL_SCRIPTS` | `15` | External script warning threshold |

Production backend example:

```env
CORS_ORIGINS=["https://your-frontend-domain.example"]
DOMAIN_LOOKUP_ENABLED=true
API_DOCS_ENABLED=false
ANALYSIS_RATE_LIMIT=10
RATE_LIMIT_WINDOW=60
RATE_LIMIT_MAX_KEYS=10000
MAX_ACTIVE_ANALYSES=4
TRUST_PROXY_HEADERS=false
```

## Security Controls

### SSRF protection

`backend/app/safety.py` resolves the submitted hostname and rejects non-global addresses, including loopback, private, link-local, reserved, and multicast ranges.

`backend/app/fetcher.py` does not allow the HTTP client to follow redirects automatically. It validates every `Location` target before making the next request.

### Resource limits

The fetcher limits timeout, response bytes, and redirect hops. The API limits both accepted analysis requests and the number of queued/running analyses.

### Job privacy

Each job receives a random access token. Reading a job without the matching `X-Analysis-Token` returns `404`. Job data is not exposed through a public list endpoint.

### Proxy headers

`X-Forwarded-For` is ignored by default. Set `TRUST_PROXY_HEADERS=true` only when a trusted reverse proxy removes client-supplied forwarding headers and writes the real client address.

### Error handling

Detailed failures are written to server logs. Public job responses use generic failure messages rather than exposing exception text, connection details, or internal implementation information.

### CORS

CORS is allowlist-based. Production should contain only the real frontend origin, for example:

```env
CORS_ORIGINS=["https://your-frontend-domain.example"]
```

## Frontend

The frontend is a React application using Vite, React Router, TanStack Query, and Vercel Web Analytics.

| Location | Responsibility |
| --- | --- |
| `frontend/src/main.jsx` | React providers, router, and analytics |
| `frontend/src/api.js` | API base URL and JSON requests |
| `frontend/src/App.jsx` | Application shell and report polling |
| `frontend/src/components/` | Shared interface components |
| `frontend/src/pages/` | Routed public pages |
| `frontend/src/styles.css` | Shared visual system and responsive styles |
| `frontend/scripts/prerender.mjs` | Static HTML generation |
| `frontend/public/` | Robots, sitemap, verification, and brand assets |

Frontend production variables:

```env
VITE_API_URL=https://your-backend-service.example
VITE_SITE_URL=https://your-frontend-domain.example
VITE_SHOW_ADVERTISEMENT=false
```

`VITE_*` values are embedded at build time. Redeploy after changing them.

## Backend

| Location | Responsibility |
| --- | --- |
| `backend/app/main.py` | FastAPI routes, CORS, rate and active-job controls |
| `backend/app/config.py` | Environment-backed settings |
| `backend/app/safety.py` | URL validation and public-host checks |
| `backend/app/fetcher.py` | Controlled HTTP fetching |
| `backend/app/parser.py` | HTML to `ParsedPage` conversion |
| `backend/app/pipeline.py` | Fetch, parse, enrich, analyze, and score orchestration |
| `backend/app/analyzers/` | Pure category-specific checks |
| `backend/app/enrichment/` | Domain and contact enrichment |
| `backend/app/scoring.py` | Finding-to-score conversion |
| `backend/app/store.py` | In-memory job lifecycle |
| `backend/app/rate_limit.py` | Sliding-window request limiter |

## Deployment

### Render backend

Create a Render Web Service from the repository and set:

```text
Root directory: backend
Build command:  pip install -r requirements.txt
Start command:  uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Add the production environment variables shown in [Configuration](#configuration). Verify:

```text
https://your-backend-service.example/api/health
```

### Vercel frontend

Create a Vercel project from the same repository and set:

```text
Root directory: frontend
Framework: Vite
Build command: npm run build
Output directory: dist
```

Add:

```env
VITE_API_URL=https://your-backend-service.example
VITE_SITE_URL=https://your-frontend-domain.example
VITE_SHOW_ADVERTISEMENT=false
```

The custom domain should point to the Vercel project. Put the actual frontend origin in the backend `CORS_ORIGINS` value.

## Adding Checks

Analyzer checks are pure functions that receive parsed facts and return findings. Add a function to the appropriate module and include it in that module's `CHECKS` collection.

```python
def check_favicon(page: ParsedPage) -> list[Finding]:
    if page.favicon:
        return []
    return [
        finding(
            Severity.INFO,
            "No favicon",
            recommendation="Add a favicon link in the document head.",
        )
    ]
```

The frontend consumes the shared finding shape, so normal checks do not require a frontend change. A new category also needs a frontend label and color mapping.

## Operational Notes

- Jobs are stored in memory and disappear when the backend restarts.
- The in-memory limiter is per process. Use Redis or an edge provider for multiple backend instances.
- Render free services may sleep when idle.
- The analyzer does not execute JavaScript.
- The analyzer checks one URL and does not crawl.
- Browser-only metrics such as layout shift and rendered contrast are out of scope.
- The contact flow opens the visitor's mail client; messages are not stored by the backend.
- Report PDF export uses the browser's native print dialog.

## Troubleshooting

### Vercel returns API 404s

Set `VITE_API_URL` to the deployed backend URL in Vercel and redeploy. Vite embeds this value during the build.

### Browser reports a CORS error

Check that Render contains the exact frontend origin:

```env
CORS_ORIGINS=["https://your-frontend-domain.example"]
```

Restart or redeploy the Render service after changing it.

### Render cannot install dependencies

Use the current `backend/requirements.txt` and redeploy with a cleared build cache. The dependency pins include Python 3.14-compatible wheels.

### A scan is slow on the first request

The Render service may be waking from sleep. Open `/api/health` once, wait for `{"status":"ok"}`, and submit the scan again.

### A target URL is rejected

This is expected for private, loopback, link-local, reserved, internal, or unsafe redirect destinations. SiteScopia scans public pages only.

## Contribution Guidelines

- Keep analyzer functions free of network I/O.
- Preserve the shared `Finding` schema.
- Keep user-facing errors generic and log diagnostic details server-side.
- Add or update focused validation when changing security controls.
- Run the frontend build and backend compilation before opening a pull request.

The repository does not currently declare a license. Add one before distributing the project or accepting external contributions.
