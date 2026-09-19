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
        <div className="skeleton skeleton-heading" />
        <div className="skeleton-grid">
          <div className="skeleton skeleton-card" />
          <div className="skeleton skeleton-card" />
          <div className="skeleton skeleton-card" />
        </div>
        <div className="skeleton skeleton-panel" />
      </div>
    </div>
  )
}
