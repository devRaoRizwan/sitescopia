import { createServer } from 'node:http'
import { readFile } from 'node:fs/promises'
import { join, extname } from 'node:path'

const DIST = new URL('../dist/', import.meta.url).pathname
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.png': 'image/png', '.xml': 'application/xml', '.txt': 'text/plain', '.ico': 'image/x-icon' }

createServer(async (req, res) => {
  const path = req.url.split('?')[0]
  if (path.startsWith('/api/')) {
    const upstream = await fetch('http://127.0.0.1:8000' + req.url, {
      method: req.method,
      headers: { 'content-type': 'application/json', ...(req.headers['x-analysis-token'] ? { 'x-analysis-token': req.headers['x-analysis-token'] } : {}) },
      body: ['POST', 'PUT'].includes(req.method) ? await new Promise((r) => { let b = ''; req.on('data', (c) => (b += c)); req.on('end', () => r(b)) }) : undefined,
    })
    res.writeHead(upstream.status, { 'content-type': 'application/json' })
    return res.end(Buffer.from(await upstream.arrayBuffer()))
  }
  for (const f of [extname(path) ? join(DIST, path) : null, join(DIST, path, 'index.html'), join(DIST, 'index.html')]) {
    if (!f) continue
    try {
      const body = await readFile(f)
      res.writeHead(200, { 'content-type': TYPES[extname(f)] ?? 'application/octet-stream' })
      return res.end(body)
    } catch {}
  }
  res.writeHead(404).end('nf')
}).listen(4173, '127.0.0.1', () => console.log('dist on 4173'))
