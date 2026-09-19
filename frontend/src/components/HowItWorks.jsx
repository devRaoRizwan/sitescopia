import { CATEGORY_LABELS } from './status'

const STEPS = [
  {
    step: '01',
    title: 'We fetch the page',
    body: 'One request, with a timeout, a size cap and a redirect cap. Private and internal addresses are refused.',
  },
  {
    step: '02',
    title: 'We parse it once',
    body: 'The HTML becomes a flat set of facts: headings in document order, links resolved to absolute URLs, images, metadata, and headers.',
  },
  {
    step: '03',
    title: 'Every check runs over it',
    body: 'Each check is independent and reports what it found, why it matters, and the specific fix.',
  },
]

const CHECKS = {
  seo: ['Title length and presence', 'Meta description', 'Single <h1>', 'Canonical URL', 'Open Graph tags', 'noindex directives'],
  accessibility: ['Image alt attributes', 'Page language', 'Heading hierarchy', 'Descriptive link text', 'Responsive viewport'],
  security: ['HTTPS', 'HSTS, CSP, frame options', 'Referrer policy', 'Version disclosure', 'Mixed content'],
  performance: ['Response time', 'Document size', 'Compression', 'Caching headers', 'Script count', 'Image dimensions'],
  content: ['HTTP status', 'Client-rendered detection', 'Redirect chains', 'Thin content', 'Link profile'],
}

export default function HowItWorks() {
  return (
    <>
      <section className="section" id="how-it-works">
        <div className="shell">
          <h2 className="section-title">How it works</h2>
          <div className="steps">
            {STEPS.map(({ step, title, body }) => (
              <article key={step} className="step">
                <span className="step-number">{step}</span>
                <h3>{title}</h3>
                <p>{body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section section-alt" id="checks">
        <div className="shell">
          <h2 className="section-title">What we check</h2>
          <div className="check-grid">
            {Object.entries(CHECKS).map(([category, items]) => (
              <article key={category} className="check-card">
                <h3>
                  <span className={`dot dot-${category}`} aria-hidden="true" />
                  {CATEGORY_LABELS[category]}
                </h3>
                <ul>
                  {items.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </div>
      </section>
    </>
  )
}
