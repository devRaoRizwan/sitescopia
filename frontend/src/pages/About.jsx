import { Link } from 'react-router-dom'
import { useSeo } from '../seo'
import PageHeader from '../components/PageHeader'

export default function About() {
  useSeo({
    title: 'About SiteScopia',
    description:
      "Why we built a website analyzer that shows its evidence, admits what it cannot see, and refuses to score a page it never actually reached.",
    path: '/about',
  })

  return (
    <>
      <PageHeader
        eyebrow="About"
        title="A page analyzer that shows its working"
        lead="Most site auditors hand you a number. This one hands you the evidence, the reason it matters, and the exact fix. It also tells you when it could not see enough to judge."
      />

      <section className="section about-editorial">
        <div className="shell">
          <div className="about-editorial-intro">
            <span className="eyebrow">Why SiteScopia exists</span>
            <h2>A useful answer is more than a score.</h2>
            <p>
              Give us one public URL and we turn it into a readable set of facts, findings, and
              next steps. The report is designed to be checked, not simply trusted.
            </p>
          </div>

          <div className="about-editorial-layout">
            <aside className="about-index-nav" aria-label="About this page">
              <span>Inside the report</span>
              <ol>
                <li>Evidence first</li>
                <li>Honest boundaries</li>
                <li>A score in context</li>
              </ol>
            </aside>

            <div className="about-chapters">
              <section className="about-chapter">
                <span className="about-kicker">01 / Evidence first</span>
                <h3>Every result should be explainable.</h3>
                <p>
                  SiteScopia fetches the page once, parses what it received, checks the response and
                  surrounding domain signals, then shows the detail that triggered each finding.
                  You can move from a warning to its evidence to a practical fix without guessing.
                </p>
              </section>
              <section className="about-chapter">
                <span className="about-kicker">02 / Honest boundaries</span>
                <h3>A limitation belongs in the report.</h3>
                <p>
                  The analyzer does not execute JavaScript or crawl beyond the URL you provide. It
                  refuses private, loopback, and internal addresses, and checks every redirect. A
                  client-rendered shell is reported as a limitation, not misread as a broken page.
                </p>
              </section>
              <section className="about-chapter">
                <span className="about-kicker">03 / A score in context</span>
                <h3>Read the findings before the number.</h3>
                <p>
                  A check tests whether something is present and well-formed, not whether it is
                  perfect. A page with <code>alt="image"</code> on every picture can pass the
                  alt-text check. The score is a useful summary, never a verdict.
                </p>
              </section>
            </div>
          </div>
        </div>
      </section>

      <section className="section section-alt about-principles-strip">
        <div className="shell">
          <div className="about-strip-heading">
            <span className="eyebrow">The practical promise</span>
            <h2>Fast enough to use. Clear enough to act on.</h2>
          </div>
          <div className="about-strip-items">
            <p><strong>Built with</strong> FastAPI, Python, React, and RDAP.</p>
            <p><strong>Made for</strong> quick checks of public pages.</p>
            <p><strong>Improved by</strong> reports of false positives.</p>
          </div>
        </div>
      </section>

      <section className="section about-feedback">
        <div className="shell narrow">
          <div className="about-close">
            <h2>Found something wrong?</h2>
            <p>
              False positives are bugs. <Link to="/contact">Tell us what you scanned</Link> and
              what you expected to see.
            </p>
          </div>
        </div>
      </section>
    </>
  )
}
