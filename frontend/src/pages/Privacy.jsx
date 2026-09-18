import PageHeader from '../components/PageHeader'
import { useSeo } from '../seo'

export default function Privacy() {
  useSeo({
    title: 'Privacy Policy',
    description:
      "What SiteScopia stores when you scan a page, how long we keep it, and the things we deliberately do not collect.",
    path: '/privacy',
  })

  return (
    <>
      <PageHeader eyebrow="Legal" title="Privacy" lead="What this service stores, and for how long." />

      <section className="section">
        <div className="shell narrow legal">
          <h2>Scans</h2>
          <p>
            When you submit a URL we store the URL, the time of the scan and the resulting report.
            Scan records are held in memory and are dropped when the service restarts or when the
            retention limit is reached. They are not associated with you.
          </p>

          <h2>Pages we fetch</h2>
          <p>
            We request the page as an ordinary HTTP client, identifying ourselves in the
            User-Agent header. We fetch only the single URL you give us — no crawling, no forms
            submitted, nothing written. Content we extract, such as email addresses or phone
            numbers published on the page, is shown back to you in the report and stored only as
            part of that report.
          </p>

          <h2>Contact messages</h2>
          <p>
            Messages sent through the contact form are stored with your name, email address, the
            message and the originating IP address, so we can reply and so we can rate-limit
            abuse. They are kept until the matter is resolved.
          </p>

          <h2>Advertising</h2>
          <p>
            Ad slots on this site are reserved at fixed dimensions. Any third-party ad network
            placed into them operates under its own privacy policy and may set its own cookies;
            that is outside our control and disclosed here so you know it exists.
          </p>

          <h2>What we do not do</h2>
          <p>
            We do not require an account, do not profile visitors across sessions, and do not sell
            or share scan data.
          </p>
        </div>
      </section>
    </>
  )
}
