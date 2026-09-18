# SiteScopia

SiteScopia is an evidence-led website analyzer. Give it one public URL and it checks the page for SEO, accessibility, security, performance, content, domain, and contact signals.

The report does more than return a score. Each finding explains:

- what was found
- why it matters
- the evidence behind the result
- a practical next step

SiteScopia is intentionally honest about its limits. It analyzes the HTML and HTTP response it can fetch, does not execute JavaScript, does not crawl a site, and refuses private or internal network addresses.

## What It Does

The analyzer runs a single URL through this pipeline:

```text
validate URL -> fetch page -> parse facts -> enrich domain/contact data
             -> run checks -> calculate scores -> return report
```

The frontend submits a URL, receives a job id, and polls until the background analysis is complete. The finished report groups findings by category and severity.

## Requirements

- Python 3.13 or newer
- Node.js 18 or newer
- npm
- `uv` (recommended) or a standard Python virtual environment
- A Chromium-based browser only if you want frontend prerendering during a production build

## Run Locally

The backend and frontend run as two separate processes.

### 1. Start the backend

From the repository root:

```bash
cd backend
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python -r requirements.txt
cp .env.example .env
.venv/bin/uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`.

Check that it is running:

```bash
curl http://127.0.0.1:8000/api/health
```

Expected response:

```json
{"status":"ok"}
```

### 2. Start the frontend

Open a second terminal from the repository root:

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

Vite proxies `/api/*` to `http://127.0.0.1:8000`, so no frontend API URL is required for local development.

## Try the API Directly

Create an analysis:

```bash
curl -X POST http://127.0.0.1:8000/api/analyses \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com"}'
```

The API responds with `202 Accepted` and a job object. Use its `id` to poll the result:

```bash
curl http://127.0.0.1:8000/api/analyses/<job-id>
```

Useful endpoints:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Check whether the backend is alive |
| `POST` | `/api/analyses` | Start an analysis; returns `202` and a job id |
| `GET` | `/api/analyses/{id}` | Read a job and its completed result |
| `GET` | `/api/analyses` | List recent in-memory jobs |
| `GET` | `/api/checks` | Return the check inventory and total count |

FastAPI's interactive documentation is disabled by default. For local API development, set `API_DOCS_ENABLED=true` in `backend/.env`, restart the backend, and open `/docs` or `/redoc`.

## Configuration

Copy `backend/.env.example` to `backend/.env`. Environment variables override the defaults in `app/config.py`.

| Variable | Default | Description |
| --- | ---: | --- |
| `FETCH_TIMEOUT` | `15` | Maximum seconds allowed for the page fetch |
| `FETCH_MAX_BYTES` | `5242880` | Maximum response body size accepted by the fetcher |
| `FETCH_MAX_REDIRECTS` | `5` | Maximum redirect hops followed |
| `USER_AGENT` | `SiteScopia/0.1` | User-Agent sent with page requests |
| `RDAP_TIMEOUT` | `10` | Maximum seconds for registry lookup |
| `DOMAIN_LOOKUP_ENABLED` | `true` | Enable or disable RDAP and DNS enrichment |
| `CORS_ORIGINS` | localhost origins | JSON list of allowed frontend origins |
| `MAX_STORED_JOBS` | `200` | Number of recent jobs kept in memory |
| `API_DOCS_ENABLED` | `false` | Enable Swagger UI, ReDoc, and OpenAPI output |
| `SLOW_RESPONSE_MS` | `1500` | Threshold for a slow-response warning |
| `VERY_SLOW_RESPONSE_MS` | `3000` | Threshold for a very-slow-response error |
| `MAX_HTML_BYTES` | `153600` | HTML size threshold used by checks |
| `MAX_EXTERNAL_SCRIPTS` | `15` | External script count threshold |

`CORS_ORIGINS` uses JSON syntax, for example:

```env
CORS_ORIGINS=["http://localhost:5173","https://app.example.com"]
```

## Production Frontend Build

Build the frontend and generate prerendered HTML for every public route:

```bash
cd frontend
npm run build
```

The command runs Vite and then `scripts/prerender.mjs`. The result is written to `frontend/dist`.

Preview the built site with the repository's production-like server:

```bash
npm run preview
```

The preview server handles route directories, compression, cache headers, and security headers. `npm run preview:vite` is also available for a basic Vite preview, but it does not reproduce the route handling of the production-like server.

### Prerendering requirements

Prerendering uses `puppeteer-core`. If Chrome is not found, the build continues with a warning and the prerender step is skipped. Set `CHROME_PATH` when Chrome is installed in a non-standard location.

If the backend is not running at `http://127.0.0.1:8000`, set `PRERENDER_API` before building. The checks page uses the API while it is prerendered.

Example:

```bash
CHROME_PATH=/usr/bin/google-chrome \
PRERENDER_API=http://127.0.0.1:8000 \
npm run build
```

## Frontend Routes

| Route | Purpose |
| --- | --- |
| `/` | URL analyzer and report interface |
| `/how-it-works` | Five-stage analysis walkthrough |
| `/checks` | Live inventory of checks by category |
| `/about` | Product principles and analysis boundaries |
| `/contact` | Contact flow using the visitor's mail client |
| `/privacy` | Privacy information |
| `/terms` | Terms of use |
| anything else | Not-found page |

## Analysis Stages

### Validate and fetch

Before fetching, the backend validates the URL and resolves its hostname. Private, loopback, link-local, and reserved addresses are rejected. The same protection is applied after redirects to prevent a public URL from redirecting into an internal network.

The fetcher enforces a timeout, response-size limit, redirect limit, and explicit User-Agent.

### Parse

The HTML is parsed once into a flat `ParsedPage` object. It contains headings, links, images, metadata, Open Graph tags, response headers, page language, response timing, and other facts used by analyzers.

### Enrich

Optional enrichment runs for domain and contact information:

- RDAP registry information and DNS records
- registrar, registration and expiry dates
- nameservers, DNSSEC state, resolved IPs, and inferred provider
- social profiles, email addresses, and phone numbers

Enrichment failures degrade gracefully and do not fail the complete scan.

### Analyze and score

Analyzers are pure functions over parsed facts. They do not perform network I/O. Each finding has a category, severity, title, explanation, evidence, and recommendation when applicable.

The score is a summary of check results, not a complete quality judgment. A page can pass a presence check while still needing human review.

## What SiteScopia Does Not Do

- It does not execute JavaScript or render a browser DOM.
- It analyzes one URL and does not crawl linked pages.
- It does not measure real browser layout shift, contrast rendering, or interaction performance.
- It does not bypass bot challenges or authentication walls.
- It does not fetch private, loopback, link-local, reserved, or internal addresses.
- Jobs are stored in memory and disappear when the backend restarts.
- There is no robots.txt-aware crawler because crawling is not implemented.

If a site is client-rendered, the response may be only an HTML shell. SiteScopia reports that limitation instead of pretending that missing content was found on the original page.

Bot challenges and error responses finish as `blocked` jobs without scores or findings. This prevents the analyzer from confidently scoring a Cloudflare, WAF, or error page instead of the requested site.

## Project Structure

```text
webAnaylizer/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI routes
│   │   ├── config.py            # Environment-backed settings
│   │   ├── safety.py            # URL validation and SSRF protection
│   │   ├── fetcher.py           # Network fetcher
│   │   ├── parser.py            # HTML to ParsedPage
│   │   ├── pipeline.py          # Analysis orchestration
│   │   ├── store.py             # In-memory job store
│   │   ├── interstitial.py      # Bot/error page detection
│   │   ├── enrichment/          # Domain and contact enrichment
│   │   └── analyzers/           # SEO, security, accessibility, and other checks
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Application shell and report flow
│   │   ├── api.js               # Backend client and polling
│   │   ├── components/          # Reusable UI pieces
│   │   └── pages/               # Routed pages
│   ├── scripts/prerender.mjs
│   ├── styles.css
│   └── package.json
└── README.md
```

## Add a New Check

Add a pure function to the relevant analyzer module and include it in that module's `CHECKS` list:

```python
from ..schemas import Finding, Severity


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

The frontend renders the shared finding shape, so a new check does not need a UI change. To add a new category, create an analyzer module, expose its checks through `app/analyzers/__init__.py`, and add its label/color to the frontend status mapping.

## Contact Flow

The contact page does not post messages to the backend. It composes a message in the visitor's own mail client using the configured recipient in `frontend/src/gmail.js`.

- Desktop opens Gmail in a new tab.
- Android attempts the Gmail app and falls back to Gmail web.
- iOS attempts the Gmail app and falls back to Gmail web.
- Visitors without Gmail can use the `mailto:` fallback.

Message bodies are capped at 2,000 characters because the message is passed through a URL.

## Printing Reports

The report's **Download PDF** action uses the browser's native print dialog. There is no PDF backend or PDF dependency. The print stylesheet hides navigation, filters, ads, and interactive controls while keeping the report text selectable.

Use the active findings filter before printing:

- **Issues only** prints warnings, errors, and notes.
- **All checks** prints passing checks as well.

## Troubleshooting

### The frontend shows a network error

Confirm the backend is running on port `8000` and that `GET /api/health` returns `{"status":"ok"}`. When using a different backend origin in development, update the Vite proxy and `CORS_ORIGINS`.

### The checks page is empty during prerendering

Start the backend before `npm run build`, or set `PRERENDER_API` to a reachable backend URL. The development frontend can still load checks after both servers are running.

### The backend rejects a URL

This is expected for localhost, private IP ranges, loopback addresses, link-local addresses, reserved addresses, and unsafe redirect destinations. SiteScopia is designed to scan public pages only.

### Jobs disappear

The default store is in memory. Jobs are lost whenever the backend restarts. A persistent database or queue is required for production retention and multi-process deployments.

### The prerender step cannot find Chrome

Install a Chromium-based browser or set `CHROME_PATH` to its executable. The Vite build still completes without prerendering, but the generated output will not include the route-specific HTML.

## License and Contributions

This repository does not currently declare a license. Add a license before distributing or accepting external contributions.

For changes, keep analyzer functions free of network I/O, preserve the shared finding schema, and run the relevant build or API checks before opening a pull request.
