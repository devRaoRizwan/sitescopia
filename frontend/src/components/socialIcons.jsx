const shell = {
  width: 16,
  height: 16,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.7,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
  'aria-hidden': true,
  focusable: false,
}

const glyph = (children) => (props) => (
  <svg {...shell} {...props}>
    {children}
  </svg>
)

const letter = (text, size = 11) => (props) => (
  <svg {...shell} {...props}>
    <rect x="3" y="3" width="18" height="18" rx="5" />
    <text
      x="12"
      y="12"
      textAnchor="middle"
      dominantBaseline="central"
      fontSize={size}
      fontWeight="700"
      fill="currentColor"
      stroke="none"
      fontFamily="inherit"
    >
      {text}
    </text>
  </svg>
)

const RoundedFrame = <rect x="3" y="3" width="18" height="18" rx="5" />

export const ICONS = {
  GitHub: glyph(
    <>
      <path d="M9 20.5c-3.8 1.1-3.8-2.2-5.3-2.6m10.6 4.1v-3.1a2.7 2.7 0 0 0-.8-2.1c2.6-.3 5.3-1.3 5.3-5.7a4.4 4.4 0 0 0-1.2-3.1 4.1 4.1 0 0 0-.1-3.1s-1-.3-3.2 1.2a11 11 0 0 0-5.7 0C6.4 4.6 5.4 4.9 5.4 4.9a4.1 4.1 0 0 0-.1 3.1A4.4 4.4 0 0 0 4 11.1c0 4.4 2.7 5.4 5.3 5.7a2.7 2.7 0 0 0-.8 2.1v3.1" />
    </>,
  ),
  'X (Twitter)': glyph(<path d="M4 4l16 16M20 4L4 20" />),
  LinkedIn: glyph(
    <>
      {RoundedFrame}
      <path d="M8 10.5V17M8 7.6v.1M12 17v-3.6a2 2 0 0 1 4 0V17" />
    </>,
  ),
  YouTube: glyph(
    <>
      <rect x="2.5" y="6" width="19" height="12" rx="4" />
      <path d="M10.5 9.8l4.5 2.2-4.5 2.2z" />
    </>,
  ),
  Instagram: glyph(
    <>
      {RoundedFrame}
      <circle cx="12" cy="12" r="3.6" />
      <path d="M17 7v.1" />
    </>,
  ),
  Facebook: glyph(
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M13.8 8.5h-1.3a1.6 1.6 0 0 0-1.6 1.7V21M9.4 13.2h4.4" />
    </>,
  ),
  TikTok: glyph(
    <>
      <path d="M14 4v10.2a3.4 3.4 0 1 1-3.4-3.4" />
      <path d="M14 4a5 5 0 0 0 5 5" />
    </>,
  ),
  Telegram: glyph(<path d="M21 4L3 11l5.5 2L21 4zm0 0l-9 16-2.5-6.5" />),
  WhatsApp: glyph(
    <>
      <path d="M3.5 20.5l1.4-4.2a8 8 0 1 1 3.1 3z" />
      <path d="M9 9.5c.3 2.5 2.4 4.7 5 5 .6 0 1.2-.5 1.2-1.1l-1.8-.8-.8.9a6 6 0 0 1-2.2-2.2l.9-.8-.8-1.8c-.6 0-1.5.2-1.5.8z" />
    </>,
  ),
  Discord: glyph(
    <>
      <path d="M8.5 6.5A15 15 0 0 1 12 6a15 15 0 0 1 3.5.5C18 7 20 9 20 13c0 2.5-1 4-1 4l-2.5-2.5" />
      <path d="M15.5 6.5A15 15 0 0 0 12 6a15 15 0 0 0-3.5.5C6 7 4 9 4 13c0 2.5 1 4 1 4l2.5-2.5" />
      <path d="M9.5 12v.1M14.5 12v.1" />
    </>,
  ),
  Reddit: glyph(
    <>
      <circle cx="12" cy="13.5" r="7.5" />
      <path d="M15.5 6.5L16.5 3l3 .7" />
      <path d="M9.5 13v.1M14.5 13v.1M9.5 16.5a4 4 0 0 0 5 0" />
    </>,
  ),
  Pinterest: glyph(
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M10 20l2-7.5M9.8 11.2a2.6 2.6 0 1 1 3.9 2.6c-1.2.6-2.6 0-3-1" />
    </>,
  ),
  Twitch: glyph(
    <>
      <path d="M4 4h16v10l-4 4h-3l-3 3H9v-3H4z" />
      <path d="M11 8v4M15 8v4" />
    </>,
  ),
  GitLab: glyph(<path d="M12 21L4 10l1.6-5L8 10h8l2.4-5L20 10z" />),
  Vimeo: glyph(
    <>
      {RoundedFrame}
      <path d="M8.5 9.5l3.5 6 3.5-6" />
    </>,
  ),
  Threads: glyph(
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M15 9.5a4 4 0 0 0-6 .8c-1 1.8-.3 4.6 2 5.2 1.8.5 3.3-.6 3.4-2.4.1-1.6-1.4-2.3-2.7-1.9" />
    </>,
  ),
  Bluesky: glyph(
    <>
      <path d="M12 13c-2-4-6-6.5-7.5-5.5S3.5 12 5 13.5c1 1 3 .8 4 .3" />
      <path d="M12 13c2-4 6-6.5 7.5-5.5S20.5 12 19 13.5c-1 1-3 .8-4 .3" />
      <path d="M12 13v5" />
    </>,
  ),
  Mastodon: glyph(
    <>
      <path d="M7 17c3 1.2 7 1.2 10 0" />
      <path d="M5 15c-.7-2.5-.6-6 .3-8C6.5 5 9 4.5 12 4.5s5.5.5 6.7 2.5c.9 2 1 5.5.3 8" />
      <path d="M9 13V9.8a1.8 1.8 0 0 1 3-1.3 1.8 1.8 0 0 1 3 1.3V13" />
    </>,
  ),
  Behance: letter('Bē', 9),
  Medium: glyph(
    <>
      <circle cx="7" cy="12" r="4.5" />
      <ellipse cx="15.5" cy="12" rx="2" ry="4.5" />
      <path d="M20.5 8v8" />
    </>,
  ),
  Dribbble: glyph(
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M5 8.5c4.5 1 9.5.2 13-2.2M3.6 14c4.5-1.6 9.6-.3 12.4 3.6M9 3.8c3 3.6 5 8.4 5.4 13.9" />
    </>,
  ),
}

export const FallbackIcon = glyph(
  <>
    <circle cx="12" cy="12" r="9" />
    <path d="M3 12h18M12 3a15 15 0 0 1 0 18a15 15 0 0 1 0-18" />
  </>,
)
