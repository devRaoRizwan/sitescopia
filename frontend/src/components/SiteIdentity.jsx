import { useState } from 'react'

const faviconFor = (page) => {
  if (page.favicon) return page.favicon
  try {
    return new URL('/favicon.ico', page.final_url).href
  } catch {
    return null
  }
}

const hostOf = (url) => {
  try {
    return new URL(url).hostname.replace(/^www\./, '')
  } catch {
    return url
  }
}

export default function SiteIdentity({ page }) {
  const [iconFailed, setIconFailed] = useState(false)

  const icon = faviconFor(page)
  const host = hostOf(page.final_url)
  const name = page.site_name || host
  const initial = name.charAt(0).toUpperCase()

  return (
    <div className="site-identity">
      {icon && !iconFailed ? (
        <img
          className="site-favicon"
          src={icon}
          alt=""
          width={28}
          height={28}
          loading="lazy"
          referrerPolicy="no-referrer"
          onError={() => setIconFailed(true)}
        />
      ) : (
        <span className="site-favicon site-favicon-fallback" aria-hidden="true">
          {initial}
        </span>
      )}

      <div className="site-names">
        <span className="site-name">{name}</span>
        <span className="site-host">{host}</span>
      </div>
    </div>
  )
}
