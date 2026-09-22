const BRANDS = {
  GitHub: { color: '#181717', glyph: 'GH' },
  'X (Twitter)': { color: '#0f1419', glyph: 'X' },
  LinkedIn: { color: '#0a66c2', glyph: 'in' },
  YouTube: { color: '#e62117', glyph: '▶' },
  Instagram: { color: '#d62976', glyph: 'IG' },
  Facebook: { color: '#1877f2', glyph: 'f' },
  TikTok: { color: '#010101', glyph: 'TT' },
  Telegram: { color: '#229ed9', glyph: '✈' },
  Discord: { color: '#5865f2', glyph: 'DC' },
  WhatsApp: { color: '#1da851', glyph: '✆' },
  Reddit: { color: '#ff4500', glyph: 'r' },
  Pinterest: { color: '#bd081c', glyph: 'P' },
  Medium: { color: '#1a1a1a', glyph: 'M' },
  GitLab: { color: '#e24329', glyph: 'GL' },
  Twitch: { color: '#7c46d6', glyph: 'TV' },
  Vimeo: { color: '#1ab7ea', glyph: 'V' },
  Threads: { color: '#101010', glyph: '@' },
  Bluesky: { color: '#0285ff', glyph: 'BS' },
  Mastodon: { color: '#5b4be1', glyph: 'm' },
  Behance: { color: '#1769ff', glyph: 'Be' },
  Dribbble: { color: '#ea4c89', glyph: 'Dr' },
}

export default function SocialMark({ platform }) {
  const brand = BRANDS[platform] ?? { color: '#4b5563', glyph: platform.charAt(0) }
  return (
    <span className="social-mark" style={{ background: brand.color }} aria-hidden="true">
      {brand.glyph}
    </span>
  )
}
