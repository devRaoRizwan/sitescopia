import { Link } from 'react-router-dom'

export default function Blocked({ url, reason }) {
  return (
    <section className="blocked">
      <span className="blocked-badge">Could not analyze</span>
      <h2>We did not get the real page</h2>
      <p className="blocked-url">{url}</p>
      <p className="blocked-reason">{reason}</p>

      <div className="blocked-body">
        <h3>Why there is no report</h3>
        <p>
          What came back was a challenge or error page, not the site's own content. Scoring it
          would describe that placeholder — its title, its headings, its headers — and present it
          as though it were your page. That would be wrong, so we stop here instead.
        </p>

        <h3>What you can do</h3>
        <ul>
          <li>Open the URL in a browser to confirm what a visitor actually sees.</li>
          <li>
            If you control the site, allow this scanner's user agent through your WAF or bot
            protection, then run the scan again.
          </li>
          <li>Try a page that is not behind the challenge, such as a blog post or docs page.</li>
        </ul>
      </div>

      <p className="blocked-footer">
        Think this is wrong? <Link to="/contact">Tell us the URL</Link> — false positives are bugs.
      </p>
    </section>
  )
}
