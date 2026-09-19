import PageHeader from '../components/PageHeader'
import { useSeo } from '../seo'

export default function Terms() {
  useSeo({
    title: 'Terms of Use',
    description:
      "The terms for using SiteScopia: scan pages you are allowed to scan, and treat every report as advice rather than a certification.",
    path: '/terms',
  })

  return (
    <>
      <PageHeader eyebrow="Legal" title="Terms of use" lead="The short version: scan pages you are allowed to scan, and treat the output as advice." />

      <section className="section">
        <div className="shell narrow legal">
          <h2>Acceptable use</h2>
          <p>
            Scan pages you own or have permission to test. Do not use this service to probe
            systems you have no authorisation for, and do not automate it at a volume that
            burdens the sites being scanned or this service.
          </p>

          <h2>What a report is</h2>
          <p>
            Reports are generated automatically from a single HTTP request. They are informational
            and may be incomplete or wrong, particularly for pages that render content with
            JavaScript, or sites behind a bot challenge that serve us something other than the
            real page. Nothing here is a security audit, a legal accessibility assessment or a
            compliance certification.
          </p>

          <h2>No warranty</h2>
          <p>
            The service is provided as is, without warranty of any kind. We are not liable for
            decisions made on the basis of a report, or for any loss arising from use of this
            service.
          </p>

          <h2>Availability</h2>
          <p>
            Scans are rate-limited and may be unavailable at times. We may change or withdraw
            features without notice.
          </p>

          <h2>Your content</h2>
          <p>
            You keep any rights in the pages you scan. Submitting a URL does not give us rights
            over the site's content beyond fetching it once to produce your report.
          </p>
        </div>
      </section>
    </>
  )
}
