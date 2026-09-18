import { Link } from 'react-router-dom'
import { useSeo } from '../seo'

export default function NotFound() {
  useSeo({
    title: 'Page Not Found',
    description:
      "That page does not exist on SiteScopia. Head back to the analyzer and scan a URL instead.",
    path: '/404', noindex: true,
  })

  return (
    <section className="section">
      <div className="shell narrow center">
        <span className="eyebrow">404</span>
        <h1>That page does not exist</h1>
        <p className="lead">
          The link may be out of date, or the address mistyped.
        </p>
        <p>
          <Link className="primary-button" to="/">
            Back to the analyzer
          </Link>
        </p>
      </div>
    </section>
  )
}
