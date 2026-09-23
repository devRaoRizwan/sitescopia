import {
  BuildingIcon,
  CalendarIcon,
  ClockIcon,
  GlobeIcon,
  HashIcon,
  RouteIcon,
  ServerIcon,
  ShieldIcon,
} from './icons'

const REGISTRATION = [
  { key: 'registrar', label: 'Registrar', Icon: BuildingIcon },
  { key: 'registered_on', label: 'Registered', Icon: CalendarIcon },
  { key: 'expires_on', label: 'Expires', Icon: CalendarIcon },
  { key: 'updated_on', label: 'Updated', Icon: ClockIcon },
]

const INFRASTRUCTURE = [
  { key: 'hosting_provider', label: 'Hosting', Icon: ServerIcon },
  { key: 'dns_provider', label: 'DNS', Icon: RouteIcon },
]

const formatAge = (days) => {
  if (days == null) return null
  const years = Math.floor(days / 365)
  return years >= 1 ? `${years} year${years === 1 ? '' : 's'} old` : `${days} days old`
}

const Row = ({ Icon, label, value }) =>
  value ? (
    <div className="fact">
      <Icon className="fact-icon" />
      <span className="fact-label">{label}</span>
      <span className="fact-value">{value}</span>
    </div>
  ) : null

export default function DomainCard({ domain }) {
  if (!domain) return null

  const age = formatAge(domain.age_days)
  const hasData = domain.ip_addresses.length > 0 || domain.nameservers.length > 0 || domain.registrar

  return (
    <section className="insight-card">
      <h3>
        <GlobeIcon className="card-icon icon-domain" />
        Domain
      </h3>

      {domain.lookup_error && !hasData ? (
        <p className="insight-empty">{domain.lookup_error}</p>
      ) : (
        <>
          <div className="domain-name">
            <strong>{domain.domain}</strong>
            {age && <span className="chip">{age}</span>}
            {domain.expires_in_days != null && (
              <span className="chip chip-muted">renews in {domain.expires_in_days}d</span>
            )}
            <span className={domain.dnssec ? 'chip chip-good' : 'chip chip-muted'}>
              <ShieldIcon width={12} height={12} />
              {domain.dnssec ? 'DNSSEC' : 'No DNSSEC'}
            </span>
          </div>

          {domain.lookup_error && <p className="insight-note">{domain.lookup_error}</p>}

          <div className="fact-columns">
            <div className="fact-group">
              <span className="fact-group-title">Registration</span>
              {REGISTRATION.map(({ key, label, Icon }) => (
                <Row key={key} Icon={Icon} label={label} value={domain[key]} />
              ))}
            </div>

            <div className="fact-group">
              <span className="fact-group-title">Infrastructure</span>
              {INFRASTRUCTURE.map(({ key, label, Icon }) => (
                <Row key={key} Icon={Icon} label={label} value={domain[key]} />
              ))}
              <Row
                Icon={HashIcon}
                label="IP"
                value={domain.ip_addresses.slice(0, 2).join(', ')}
              />
            </div>
          </div>

          {domain.nameservers.length > 0 && (
            <div className="ns-panel">
              <span className="fact-group-title">Nameservers</span>
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
                  {status.replace(' prohibited', ' lock')}
                </span>
              ))}
            </div>
          )}
        </>
      )}
    </section>
  )
}
