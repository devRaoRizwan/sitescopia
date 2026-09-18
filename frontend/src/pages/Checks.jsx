import { useQuery } from '@tanstack/react-query'
import { useSeo } from '../seo'
import PageHeader from '../components/PageHeader'
import { CATEGORY_LABELS } from '../components/status'

const DESCRIPTIONS = {
  seo: 'How search engines read and index the page.',
  accessibility: 'Whether people using screen readers and keyboards can use it.',
  security: 'Transport security and the response headers that protect visitors.',
  performance: 'Signals we can measure without a browser.',
  content: 'The shape and reachability of the page itself.',
  domain: 'Registration, expiry and DNS for the domain behind it.',
  contact: 'How the site can be reached, and what it exposes doing so.',
}

export default function Checks() {
  useSeo({
    title: 'Every Website Check We Run',
    description:
      "The full list of SEO, accessibility, security, performance, content and domain checks we run on every scan, generated live from the running service.",
    path: '/checks',
  })

  const { data, isPending, isError } = useQuery({ queryKey: ['checks'], queryFn: () => fetch('/api/checks').then((r) => r.json()), staleTime: Infinity })

  return (
    <>
      <PageHeader
        eyebrow="Checks"
        title={data ? `${data.total} checks, seven categories` : 'What we check'}
        lead="Every check runs on every scan. This list is generated from the running server, so it is never out of date."
      />

      <section className="section">
        <div className="shell">
          {isPending && <p className="hint">Loading the check inventory…</p>}
          {isError && <p className="hint">Could not load the check list. Is the API running?</p>}

          {data && (
            <>
              <h2 className="section-title">Grouped by category</h2>
              <div className="check-grid wide">
              {Object.entries(data.by_category).map(([category, items]) => (
                <article key={category} className="check-card">
                  <h3>
                    <span className={`dot dot-${category}`} aria-hidden="true" />
                    {CATEGORY_LABELS[category] ?? category}
                    <span className="count">{items.length}</span>
                  </h3>
                  <p className="check-desc">{DESCRIPTIONS[category]}</p>
                  <ul>
                    {items.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </article>
                ))}
              </div>
            </>
          )}

          <div className="callout callout-muted">
            <h2>A note on scores</h2>
            <p>
              These checks test whether something is present and well-formed — not whether it is
              any good. A page with <code>alt="image"</code> on every picture passes the alt-text
              check. Read the findings, and treat the score as a summary rather than a verdict.
            </p>
          </div>
        </div>
      </section>
    </>
  )
}
