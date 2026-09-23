import { FallbackIcon, ICONS } from './socialIcons'

const COLORS = {
  GitHub: '#24292f',
  'X (Twitter)': '#0f1419',
  LinkedIn: '#0a66c2',
  YouTube: '#e62117',
  Instagram: '#d62976',
  Facebook: '#1877f2',
  TikTok: '#111111',
  Telegram: '#229ed9',
  Discord: '#5865f2',
  WhatsApp: '#1da851',
  Reddit: '#ff4500',
  Pinterest: '#bd081c',
  Medium: '#1a1a1a',
  GitLab: '#e24329',
  Twitch: '#7c46d6',
  Vimeo: '#1ab7ea',
  Threads: '#101010',
  Bluesky: '#0285ff',
  Mastodon: '#5b4be1',
  Behance: '#1769ff',
  Dribbble: '#ea4c89',
}



export default function SocialMark({ platform }) {
  const Icon = ICONS[platform] ?? FallbackIcon
  return <Icon className="social-icon" style={{ color: COLORS[platform] ?? 'var(--muted)' }} />
}
