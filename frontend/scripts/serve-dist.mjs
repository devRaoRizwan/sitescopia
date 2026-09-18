import { createServer } from 'node:http'
import { gzipSync } from 'node:zlib'
import { readFile } from 'node:fs/promises'
import { join, extname, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const DIST = join(dirname(fileURLToPath(import.meta.url)), '..', 'dist')
const PORT = Number(process.env.PORT) || 4173

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.xml': 'application/xml',
  '.txt': 'text/plain', '.json': 'application/json', '.ico': 'image/x-icon',
}

const SECURITY_HEADERS = {
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Content-Security-Policy':
    "default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'",
}

createServer(async (req, res) => {
  const path = decodeURIComponent(req.url.split('?')[0])

  for (const candidate of [
    extname(path) ? join(DIST, path) : null,
    join(DIST, path, 'index.html'),
    join(DIST, 'index.html'),
  ]) {
    if (!candidate) continue
    try {
      const raw = await readFile(candidate)
      const type = TYPES[extname(candidate)] ?? 'application/octet-stream'
      const compressible = /text|json|javascript|xml|svg/.test(type)
      const wantsGzip = (req.headers['accept-encoding'] ?? '').includes('gzip')
      const body = compressible && wantsGzip ? gzipSync(raw) : raw

      res.writeHead(200, {
        'Content-Type': type,
        'Cache-Control': extname(candidate) === '.html' ? 'no-cache' : 'public, max-age=31536000',
        ...(body === raw ? {} : { 'Content-Encoding': 'gzip', Vary: 'Accept-Encoding' }),
        ...SECURITY_HEADERS,
      })
      return res.end(body)
    } catch {}
  }

  res.writeHead(404, { 'Content-Type': 'text/plain' }).end('not found')
}).listen(PORT, '127.0.0.1', () => console.log(`serving dist on http://127.0.0.1:${PORT}`))
