export const STATUS_COLORS = {
  good: '#0ca30c',
  warning: '#fab219',
  serious: '#ec835a',
  critical: '#d03b3b',
}

export const SEVERITY_COLORS = {
  error: STATUS_COLORS.critical,
  warning: STATUS_COLORS.warning,
  info: STATUS_COLORS.serious,
  pass: STATUS_COLORS.good,
}

const BANDS = [
  { min: 90, role: 'good', label: 'Good' },
  { min: 70, role: 'warning', label: 'Needs work' },
  { min: 50, role: 'serious', label: 'Poor' },
  { min: 0, role: 'critical', label: 'Critical' },
]

export const scoreBand = (score) => BANDS.find((band) => score >= band.min)

export const SEVERITY = {
  error: { label: 'Error', icon: '✕' },
  warning: { label: 'Warning', icon: '!' },
  info: { label: 'Info', icon: 'i' },
  pass: { label: 'Pass', icon: '✓' },
}

export const CATEGORY_LABELS = {
  seo: 'SEO',
  accessibility: 'Accessibility',
  security: 'Security',
  performance: 'Performance',
  content: 'Content',
  domain: 'Domain',
  contact: 'Contact',
}
