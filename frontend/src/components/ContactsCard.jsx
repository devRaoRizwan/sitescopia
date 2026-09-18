const CONFIDENCE_LABEL = {
  high: 'confirmed link',
  medium: 'likely',
  low: 'unverified',
}

export default function ContactsCard({ contacts }) {
  if (!contacts) return null

  const { social, emails, phones } = contacts
  const nothing = !social.length && !emails.length && !phones.length

  return (
    <section className="insight-card">
      <h3>Contact &amp; social</h3>

      {nothing && <p className="insight-empty">No social links, emails or phone numbers on this page.</p>}

      {social.length > 0 && (
        <div className="insight-block">
          <span className="kv-label">Social profiles</span>
          <ul className="social-list">
            {social.map((profile) => (
              <li key={profile.platform}>
                <a href={profile.url} target="_blank" rel="noopener noreferrer">
                  {profile.platform}
                </a>
                {profile.handle && <span className="handle">@{profile.handle}</span>}
              </li>
            ))}
          </ul>
        </div>
      )}

      {emails.length > 0 && (
        <div className="insight-block">
          <span className="kv-label">Email</span>
          <ul className="contact-list">
            {emails.map((hit) => (
              <li key={hit.value}>
                <a href={`mailto:${hit.value}`}>{hit.value}</a>
                <span className={`conf conf-${hit.confidence}`}>{CONFIDENCE_LABEL[hit.confidence]}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {phones.length > 0 && (
        <div className="insight-block">
          <span className="kv-label">Phone</span>
          <ul className="contact-list">
            {phones.map((hit) => (
              <li key={hit.value}>
                <a href={`tel:${hit.value.replace(/[^\d+]/g, '')}`}>{hit.value}</a>
                <span className={`conf conf-${hit.confidence}`}>{CONFIDENCE_LABEL[hit.confidence]}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}
