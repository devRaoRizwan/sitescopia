export const CONTACT_EMAIL = 'dev.raorizwan@gmail.com'

const GMAIL_WEB = 'https://mail.google.com/mail/?view=cm&fs=1'
const IOS_APP_TIMEOUT_MS = 1200

const isAndroid = (ua) => /Android/i.test(ua)

const isIOS = (ua) =>
  /iPad|iPhone|iPod/.test(ua) ||
  (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)

export function buildBody({ name, subject, message }) {
  return [
    message.trim(),
    '',
    '—',
    `From: ${name.trim() || 'a SiteScopia visitor'}`,
    `Topic: ${subject}`,
    `Sent via SiteScopia · ${window.location.origin}`,
  ].join('\n')
}

const webUrl = (to, subject, body) =>
  `${GMAIL_WEB}&to=${encodeURIComponent(to)}` +
  `&su=${encodeURIComponent(subject)}` +
  `&body=${encodeURIComponent(body)}`

export function openGmail({ to = CONTACT_EMAIL, subject, body }) {
  const web = webUrl(to, subject, body)
  const ua = navigator.userAgent

  if (isAndroid(ua)) {
    window.location.href =
      `intent://co?to=${encodeURIComponent(to)}` +
      `&subject=${encodeURIComponent(subject)}` +
      `&body=${encodeURIComponent(body)}` +
      `#Intent;scheme=googlegmail;package=com.google.android.gm` +
      `;S.browser_fallback_url=${encodeURIComponent(web)};end`
    return 'android-app'
  }

  if (isIOS(ua)) {
    const timer = setTimeout(() => {
      window.location.href = web
    }, IOS_APP_TIMEOUT_MS)

    document.addEventListener(
      'visibilitychange',
      () => document.hidden && clearTimeout(timer),
      { once: true },
    )

    window.location.href =
      `googlegmail:///co?to=${encodeURIComponent(to)}` +
      `&subject=${encodeURIComponent(subject)}` +
      `&body=${encodeURIComponent(body)}`
    return 'ios-app'
  }

  window.open(web, '_blank', 'noopener,noreferrer')
  return 'web'
}

export const composeUrls = { webUrl }
