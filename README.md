# SiteScopia

SiteScopia is an evidence-led website analyzer. Enter a public URL and get a clear report covering SEO, accessibility, security, performance, content, domain, and contact signals.

Instead of returning only a score, SiteScopia shows the finding, explains why it matters, displays the evidence, and suggests a practical fix.

## Product Overview

SiteScopia is designed for developers, designers, SEO specialists, and site owners who want a fast first review of a public webpage.

It answers questions such as:

- Is the page structured clearly for search engines?
- Are important accessibility basics present?
- Are security headers and HTTPS configured?
- Is the response slow or unusually large?
- Are domain, DNS, and contact signals available?
- What should be fixed first?

The tool analyzes one URL at a time. It does not crawl an entire website or execute JavaScript.

## How It Works

```text
User enters URL
      |
      v
Frontend sends analysis request
      |
      v
Backend validates URL and blocks private/internal targets
      |
      v
Backend fetches the public page
      |
      v
HTML is parsed into reusable page facts
      |
      +--> Domain and DNS enrichment
      +--> Contact and social extraction
      |
      v
Independent analyzers run their checks
      |
      v
Scores and findings are stored in the job
      |
      v
Frontend polls the job and renders the report
```

## Frontend

The frontend is a React and Vite application located in [`frontend/`](frontend/).

It is responsible for:

- URL input and validation feedback
- Starting an analysis
- Polling the backend job status
- Rendering progress and blocked states
- Displaying scores, categories, findings, evidence, and recommendations
- Showing domain and contact insights
- Providing routed pages such as About, Checks, Privacy, and Terms
- Managing SEO metadata and prerendered pages
- Sending optional Vercel Web Analytics events

Important frontend areas:

| Location | Responsibility |
| --- | --- |
| [`frontend/src/main.jsx`](frontend/src/main.jsx) | React entry point and providers |
| [`frontend/src/api.js`](frontend/src/api.js) | Backend API requests and job polling |
| [`frontend/src/App.jsx`](frontend/src/App.jsx) | Application shell and report flow |
| [`frontend/src/components/`](frontend/src/components/) | Reusable interface components |
| [`frontend/src/pages/`](frontend/src/pages/) | Routed content pages |
| [`frontend/src/styles.css`](frontend/src/styles.css) | Shared visual system and responsive layout |
| [`frontend/scripts/prerender.mjs`](frontend/scripts/prerender.mjs) | Generates HTML for public routes |

## Backend

The backend is a FastAPI application located in [`backend/`](backend/).

It is responsible for:

- Receiving analysis requests
- Validating public URLs
- Blocking SSRF targets and unsafe redirects
- Fetching HTML with timeout, size, and redirect limits
- Parsing the page once into structured facts
- Enriching results with RDAP, DNS, contact, and social data
- Running independent analyzers
- Calculating category and overall scores
- Storing short-lived analysis jobs in memory
- Returning results to the frontend through a JSON API

Important backend areas:

| Location | Responsibility |
| --- | --- |
| [`backend/app/main.py`](backend/app/main.py) | FastAPI routes and request controls |
| [`backend/app/safety.py`](backend/app/safety.py) | URL validation and SSRF protection |
| [`backend/app/fetcher.py`](backend/app/fetcher.py) | Safe page fetching and redirect checks |
| [`backend/app/parser.py`](backend/app/parser.py) | HTML parsing into page facts |
| [`backend/app/analyzers/`](backend/app/analyzers/) | SEO, security, accessibility, and other checks |
| [`backend/app/enrichment/`](backend/app/enrichment/) | Domain, DNS, contact, and social enrichment |
| [`backend/app/pipeline.py`](backend/app/pipeline.py) | Runs the analysis stages |
| [`backend/app/scoring.py`](backend/app/scoring.py) | Builds scores and report results |
| [`backend/app/store.py`](backend/app/store.py) | In-memory job storage |
| [`backend/app/rate_limit.py`](backend/app/rate_limit.py) | Analysis request limiting |
| [`backend/requirements.txt`](backend/requirements.txt) | Python dependencies |

## Request and Job Flow

Analysis requests run as background jobs so a slow target page does not keep the initial HTTP request open.

1. The frontend sends `POST /api/analyses` with a URL.
2. The backend validates the URL and checks the request rate limit.
3. The backend creates a private job id and access token.
4. The analysis runs in the background.
5. The frontend polls `GET /api/analyses/{id}` using `X-Analysis-Token`.
6. The backend returns queued, running, done, failed, or blocked status.
7. The frontend renders the completed report.

The API also exposes:

```text
GET  /api/health
POST /api/analyses
GET  /api/analyses/{id}
GET  /api/checks
```

Analysis results are protected by the private token returned when the job is created. There is no public endpoint for listing other users' jobs.

## Security and Reliability

The backend includes protections for public deployment:

- Private, loopback, link-local, reserved, and internal addresses are rejected.
- Every redirect destination is validated before it is fetched.
- Fetches have timeout, response-size, and redirect-count limits.
- Analysis creation is rate limited per client.
- The number of active analyses is bounded.
- Job results require a private access token.
- Bot challenges and error pages are marked as blocked instead of being scored.
- Detailed internal exceptions are logged server-side but generic errors are returned to users.
- CORS is configured for the production frontend origin.

## Deployment

The recommended production setup uses both services from the same GitHub repository:

```text
GitHub repository
├── frontend/  -> Vercel
└── backend/   -> Render
```

### Vercel frontend

Set the Vercel root directory to `frontend`:

```text
Framework: Vite
Build command: npm run build
Output directory: dist
```

Production environment variables:

```env
 VITE_API_URL=https://your-backend-service.example
 VITE_SITE_URL=https://your-frontend-domain.example
VITE_SHOW_ADVERTISEMENT=false
```

### Render backend

Set the Render root directory to `backend`:

```text
Build command: pip install -r requirements.txt
Start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Important Render environment variables:

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

Confirm the backend is healthy at:

```text
https://your-backend-service.example/api/health
```

More detailed setup, configuration, deployment, troubleshooting, and development guidance is available in [`TECHNICAL.md`](TECHNICAL.md).

## Local Development

Start the backend:

```bash
cd backend
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python -r requirements.txt
cp .env.example .env
.venv/bin/uvicorn app.main:app --reload
```

Start the frontend in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). Vite proxies local `/api` requests to the backend.

## Limitations

- Only one public URL is analyzed at a time.
- JavaScript is not executed.
- Browser-only metrics such as layout shift and rendered contrast are out of scope.
- The backend does not crawl linked pages.
- Jobs are stored in memory and disappear when the backend restarts.
- Render free services may sleep when idle.

## License

This repository does not currently declare a license. Add a license before distributing the project or accepting external contributions.
