import { useEffect, useState } from 'react'

const MESSAGES = [
  'Wait a moment',
  'Almost there',
  'Checking the details',
  'Putting your report together',
]

export default function Progress() {
  const [messageIndex, setMessageIndex] = useState(0)

  useEffect(() => {
    const timer = window.setInterval(() => {
      setMessageIndex((index) => (index + 1) % MESSAGES.length)
    }, 2400)

    return () => window.clearInterval(timer)
  }, [])

  return (
    <div className="progress" role="status" aria-live="polite">
      <div className="spinner" aria-hidden="true" />
      <strong>{MESSAGES[messageIndex]}…</strong>
      <span className="muted">Your report is on its way.</span>
      <div className="progress-skeleton" aria-hidden="true">
        <div className="skeleton-report-head">
          <div>
            <div className="skeleton skeleton-title" />
            <div className="skeleton skeleton-meta" />
          </div>
          <div className="skeleton-actions">
            <div className="skeleton skeleton-action" />
            <div className="skeleton skeleton-action" />
          </div>
        </div>
        <div className="skeleton-grid">
          <div className="skeleton skeleton-card" />
          <div className="skeleton skeleton-card" />
          <div className="skeleton skeleton-card" />
          <div className="skeleton skeleton-card" />
        </div>
        <div className="skeleton-insights">
          <div className="skeleton skeleton-insight" />
          <div className="skeleton skeleton-insight" />
        </div>
        <div className="skeleton-browser">
          <div className="skeleton skeleton-browser-toolbar" />
          <div className="skeleton-browser-body">
            <div className="skeleton skeleton-rail" />
            <div className="skeleton skeleton-findings" />
          </div>
        </div>
      </div>
    </div>
  )
}
