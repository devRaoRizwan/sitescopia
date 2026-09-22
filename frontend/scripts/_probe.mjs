import puppeteer from 'puppeteer-core'
const SHOTS = '/tmp/claude-1000/-home-rao-Desktop-RaoRizwan-webAnaylizer/d2a1c193-9010-4d57-84f1-4bce4caa0729/scratchpad/shots'
const browser = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox'] })
const page = await browser.newPage()
await page.setViewport({ width: 1560, height: 1000 })

for (const site of ['python.org', 'wikipedia.org', 'github.com']) {
  await page.goto('http://127.0.0.1:4173/', { waitUntil: 'networkidle0' })
  await page.type('.url-field input', site)
  await page.evaluate(() => document.querySelector('.url-submit, .url-form button[type=submit]').click())
  const ok = await page.waitForFunction(() => !!document.querySelector('.report'), { timeout: 60000 }).then(() => true).catch(() => false)
  if (!ok) { console.log(site, '-> scan failed (sandbox egress)'); continue }
  await new Promise((r) => setTimeout(r, 1200))
  const info = await page.evaluate(() => ({
    social: document.querySelectorAll('.social-mark').length,
    contacts: document.querySelectorAll('.contact-list li').length,
    height: Math.round(document.querySelector('.insights').getBoundingClientRect().height),
  }))
  console.log(site, JSON.stringify(info))
  if (info.social > 0) {
    const b = await (await page.$('.insights')).boundingBox()
    await page.screenshot({ path: `${SHOTS}/21-cards.png`, clip: { x: b.x - 10, y: b.y - 10, width: b.width + 20, height: Math.min(b.height + 20, 560) } })
    break
  }
}
await browser.close()
