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
          <div className="hero-features" aria-label="Scan features">
            <div className="hero-feature">
              <span className="hero-feature-label">Coverage</span>
              <strong>{checkCount ?? 38}</strong>
              <span>checks across 7 categories</span>
            </div>
            <div className="hero-feature">
              <span className="hero-feature-label">Speed</span>
              <strong>Quick first pass</strong>
              <span>built for timely feedback</span>
            </div>
            <div className="hero-feature">
              <span className="hero-feature-label">Privacy</span>
              <strong>Nothing stored</strong>
              <span>your scan stays temporary</span>
            </div>
          </div>
        )}
      </div>
    </section>
  )
}
