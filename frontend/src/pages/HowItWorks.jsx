import { Link } from 'react-router-dom'
import { useSeo } from '../seo'
import PageHeader from '../components/PageHeader'

const STAGES = [
  {
    step: '01',
    title: 'Fetch',
    body: 'A single HTTP request with a 15-second timeout, a 5 MB size cap and a 5-redirect cap. Before anything is fetched the hostname is resolved and rejected if it points at a private, loopback, link-local or reserved address — and again after any redirect, so a redirect cannot smuggle us onto an internal network.',
  },
  {
    step: '02',
    title: 'Parse',
    body: 'The HTML is parsed once into a flat set of facts: headings in document order, links resolved to absolute URLs and tagged internal or external, images with their alt text and dimensions, metadata, Open Graph tags and response headers. Every later step reads this, so nothing is parsed twice.',
  },
  {
    step: '03',
    title: 'Enrich',
    body: 'In parallel we query the domain registry over RDAP and resolve DNS, then extract social profiles, email addresses and phone numbers from the page. A failed or slow registry lookup degrades gracefully and never fails the scan.',
  },
  {
    step: '04',
    title: 'Analyze',
    body: 'Every check runs over the parsed facts. Each one is an independent function with no network access, so a check cannot be slow and cannot fail in a way that affects another. Each returns findings with a severity, an explanation, the evidence it found, and the specific fix.',
  },
  {
    step: '05',
    title: 'Score and report',
    body: 'Findings are grouped by category and scored, then returned as JSON. The frontend polls until the job is done and renders the report.',
  },
]

export default function HowItWorks() {
  useSeo({
    title: 'How Our Website Analysis Works',
    description:
      "See exactly how we fetch, parse and check a page: five stages, one HTTP request, and an honest account of what a scan can and cannot tell you.",
    path: '/how-it-works',
  })

  return (
    <>
      <PageHeader
        eyebrow="How it works"
        title="Five stages, one request"
        lead="Analysis takes seconds, so scans run as background jobs. Here is what happens between submitting a URL and seeing a report."
      />

      <section className="section workflow-section">
        <div className="shell">
          <div className="workflow-intro">
            <div>
              <span className="eyebrow">The path from URL to report</span>
              <h2>One clean pass through the page.</h2>
            </div>
            <p>
              The scan is deliberately linear. It gathers the facts once, keeps network work at
              the edges, and lets every check reason over the same snapshot.
            </p>
          </div>

          <ol className="workflow-stages">
            {STAGES.map(({ step, title, body }) => (
              <li key={step} className="workflow-stage">
                <span className="workflow-stage-number">{step}</span>
                <div className="workflow-stage-copy">
                  <h2>{title}</h2>
                  <p>{body}</p>
                </div>
              </li>
            ))}
          </ol>

          <div className="workflow-notes">
            <article>
              <span className="workflow-note-label">Why background jobs?</span>
              <h3>The page can take its time.</h3>
              <p>
                Submitting a URL returns a job id immediately. The report is polled until the scan
                is ready, so a slow page does not hold an HTTP request open or disappear mid-check.
              </p>
            </article>
            <article>
              <span className="workflow-note-label">A deliberate limit</span>
              <h3>We do not execute JavaScript.</h3>
              <p>
                A client-rendered shell is reported as a limitation. Contrast ratios, layout shift,
                and real browser timings need a browser, so they are out of scope for now.
              </p>
            </article>
          </div>

          <p className="section-more workflow-link">
            <Link to="/checks">See every check we run →</Link>
          </p>
        </div>
      </section>
    </>
  )
}
