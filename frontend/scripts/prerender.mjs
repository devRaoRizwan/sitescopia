import { createServer } from 'node:http'
import { readFile, mkdir, writeFile, access } from 'node:fs/promises'
import { join, extname, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const ROUTES = ['/', '/how-it-works', '/checks', '/about', '/contact', '/privacy', '/terms']

const DIST = join(dirname(fileURLToPath(import.meta.url)), '..', 'dist')
const PORT = 41730
const API_TARGET = process.env.PRERENDER_API || 'http://127.0.0.1:8000'

const CHROME_CANDIDATES = [
  process.env.CHROME_PATH,
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
]

const TYPES = {
  '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.xml': 'application/xml',
  '.txt': 'text/plain', '.json': 'application/json', '.ico': 'image/x-icon',
}

async function findChrome() {
  for (const candidate of CHROME_CANDIDATES) {
    if (!candidate) continue
    try {
      await access(candidate)
      return candidate
    } catch {}
  }
  return null
}

function serveDist() {
  return createServer(async (req, res) => {
    const path = req.url.split('?')[0]

    if (path.startsWith('/api/')) {
      try {
        const upstream = await fetch(API_TARGET + req.url)
        res.writeHead(upstream.status, { 'Content-Type': 'application/json' })
        return res.end(Buffer.from(await upstream.arrayBuffer()))
      } catch {
        res.writeHead(502).end('{}')
        return
      }
    }

    const file = extname(path) ? join(DIST, path) : join(DIST, 'index.html')
    try {
      const body = await readFile(file)
      res.writeHead(200, { 'Content-Type': TYPES[extname(file)] ?? 'application/octet-stream' })
      res.end(body)
    } catch {
      res.writeHead(404).end('not found')
    }
  })
}

const chrome = await findChrome()
if (!chrome) {
  console.warn('[prerender] no Chrome found — skipping. Set CHROME_PATH to enable.')
  process.exit(0)
}

let puppeteer
try {
  puppeteer = (await import('puppeteer-core')).default
} catch {
  console.warn('[prerender] puppeteer-core not installed — skipping.')
  process.exit(0)
}

const server = serveDist()
await new Promise((resolve) => server.listen(PORT, '127.0.0.1', resolve))

const browser = await puppeteer.launch({
  executablePath: chrome,
  headless: 'new',
  args: ['--no-sandbox', '--disable-dev-shm-usage'],
})

for (const route of ROUTES) {
  const page = await browser.newPage()
  await page.goto(`http://127.0.0.1:${PORT}${route}`, { waitUntil: 'networkidle0', timeout: 30000 })
  await page.waitForSelector('h1', { timeout: 10000 }).catch(() => {})

  const html = await page.evaluate(() => `<!doctype html>\n${document.documentElement.outerHTML}`)
  const out = route === '/' ? join(DIST, 'index.html') : join(DIST, route, 'index.html')
  await mkdir(dirname(out), { recursive: true })
  await writeFile(out, html)

  const title = await page.title()
  console.log(`[prerender] ${route.padEnd(15)} ${(html.length / 1024).toFixed(0).padStart(3)} KB  ${title}`)
  await page.close()
}

await browser.close()
server.close()
