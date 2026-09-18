import UrlForm from './UrlForm'

export default function Hero({ onSubmit, busy, compact, checkCount }) {
  return (
    <section className={compact ? 'hero hero-compact' : 'hero'} id="analyze">
      <div className="shell hero-inner">
        {!compact && (
          <>
            <span className="eyebrow">Evidence-led website analysis</span>
            <h1>
              See what your page is really <em>telling</em> search engines and screen readers.
            </h1>
            <p className="lead">
              Paste a URL and we will pull the page apart: SEO, accessibility, security, speed,
              and the domain behind it. You get what is broken, why it matters, and how to fix it.
            </p>
          </>
        )}

        <UrlForm onSubmit={onSubmit} busy={busy} showExamples={!compact} />

        {!compact && (
          <p className="hero-meta">
            <strong>{checkCount ?? 38}</strong> checks across <strong>7</strong> categories
            <span aria-hidden="true">·</span> most scans finish in about a second
            <span aria-hidden="true">·</span> nothing is stored
          </p>
        )}
      </div>
    </section>
  )
}
