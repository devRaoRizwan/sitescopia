export default function Progress({ url }) {
  return (
    <div className="progress">
      <div className="spinner" aria-hidden="true" />
      <div>
        <strong>Analyzing{url ? ` ${url}` : ''}…</strong>
        <span className="muted">Fetching the page and running every check.</span>
      </div>
    </div>
  )
}
