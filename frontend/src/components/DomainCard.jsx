const ROWS = [
  { key: 'registrar', label: 'Registrar' },
  { key: 'registered_on', label: 'Registered' },
  { key: 'expires_on', label: 'Expires' },
  { key: 'updated_on', label: 'Last changed' },
  { key: 'hosting_provider', label: 'Hosting' },
  { key: 'dns_provider', label: 'DNS' },
]

const formatAge = (days) => {
  if (days == null) return null
  const years = Math.floor(days / 365)
  return years >= 1 ? `${years} year${years === 1 ? '' : 's'} old` : `${days} days old`
}

export default function DomainCard({ domain }) {
  if (!domain) return null

  return (
    <section className="insight-card">
      <h3>Domain</h3>

      {domain.lookup_error ? (
        <p className="insight-empty">{domain.lookup_error}</p>
      ) : (
        <>
          <div className="domain-name">
            <strong>{domain.domain}</strong>
            {formatAge(domain.age_days) && <span className="chip">{formatAge(domain.age_days)}</span>}
            {domain.dnssec === false && <span className="chip chip-muted">No DNSSEC</span>}
            {domain.dnssec === true && <span className="chip chip-good">DNSSEC</span>}
          </div>

          <dl className="kv">
            {ROWS.map(({ key, label }) =>
              domain[key] ? (
                <div key={key}>
                  <dt>{label}</dt>
                  <dd>{domain[key]}</dd>
                </div>
              ) : null,
            )}
            {domain.expires_in_days != null && (
              <div>
                <dt>Renews in</dt>
                <dd>{domain.expires_in_days} days</dd>
              </div>
            )}
            {domain.ip_addresses.length > 0 && (
              <div>
                <dt>IP</dt>
                <dd>{domain.ip_addresses.slice(0, 2).join(', ')}</dd>
              </div>
            )}
          </dl>

          {domain.nameservers.length > 0 && (
            <div className="ns-list">
              <span className="kv-label">Nameservers</span>
              <ul>
                {domain.nameservers.slice(0, 4).map((ns) => (
                  <li key={ns}>{ns}</li>
                ))}
              </ul>
            </div>
          )}

          {domain.status.length > 0 && (
            <div className="status-chips">
              {domain.status.slice(0, 4).map((status) => (
                <span key={status} className="chip chip-muted">
                  {status}
                </span>
              ))}
            </div>
          )}
        </>
      )}
    </section>
  )
}
