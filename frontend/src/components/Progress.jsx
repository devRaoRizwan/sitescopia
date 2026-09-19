const MESSAGES = {
  queued: 'Waiting in the analysis queue.',
  running: 'Fetching the page and running every check.',
}

export default function Progress({ url, status }) {
  const title = status === 'queued' ? 'Waiting to start' : status === 'running' ? 'Analyzing' : 'Waiting'
  const detail = MESSAGES[status] ?? 'Connecting to the analyzer.'

  return (
    <div className="progress" role="status" aria-live="polite">
      <div className="spinner" aria-hidden="true" />
      <div>
        <strong>{title}{url ? ` ${url}` : ''}…</strong>
        <span className="muted">{detail}</span>
      </div>
    </div>
  )
}
