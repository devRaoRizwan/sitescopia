import puppeteer from 'puppeteer-core'
const browser = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox'] })
const page = await browser.newPage()
await page.setViewport({ width: 1560, height: 900 })
await page.goto('http://127.0.0.1:4173/', { waitUntil: 'networkidle0' })
await page.type('.url-field input', 'example.com')
await page.evaluate(() => document.querySelector('.url-submit, .url-form button[type=submit]').click())
await page.waitForFunction(() => !!document.querySelector('.report'), { timeout: 90000 })
await new Promise((r) => setTimeout(r, 1200))

const read = () => page.evaluate(() => {
  const f = document.querySelector('footer').getBoundingClientRect()
  const escapees = [...document.querySelectorAll('body *')].filter((e) => {
    const s = getComputedStyle(e)
    return (s.position === 'absolute' || s.position === 'fixed') &&
      e.getBoundingClientRect().bottom + window.scrollY > document.body.scrollHeight + 1
  }).length
  return {
    docH: document.documentElement.scrollHeight,
    bodyH: document.body.scrollHeight,
    footerBottom: Math.round(f.bottom + window.scrollY),
    gapBelowFooter: Math.round(document.documentElement.scrollHeight - (f.bottom + window.scrollY)),
    escapedAbsolutes: escapees,
  }
})

console.log('all findings   ', JSON.stringify(await read()))

for (const label of ['Performance', 'SEO']) {
  await page.evaluate((l) => [...document.querySelectorAll('.rail-item')].find((b) => b.textContent.includes(l))?.click(), label)
  await new Promise((r) => setTimeout(r, 300))
  console.log(`${label.padEnd(15)}`, JSON.stringify(await read()))
}

await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight))
await new Promise((r) => setTimeout(r, 300))
await page.screenshot({ path: '/tmp/claude-1000/-home-rao-Desktop-RaoRizwan-webAnaylizer/d2a1c193-9010-4d57-84f1-4bce4caa0729/scratchpad/shots/18-fixed.png' })
await browser.close()
