import SocialMark from './SocialMark'
import { InboxIcon, LinkIcon, MailIcon, PhoneIcon, UsersIcon } from './icons'

const CONFIDENCE_LABEL = {
  high: 'confirmed link',
  medium: 'likely',
  low: 'unverified',
}

const ContactRow = ({ Icon, href, value, confidence }) => (
  <li>
    <Icon className="contact-icon" />
    <a href={href}>{value}</a>
    <span className={`conf conf-${confidence}`}>{CONFIDENCE_LABEL[confidence]}</span>
  </li>
)

export default function ContactsCard({ contacts }) {
  if (!contacts) return null

  const { social, emails, phones } = contacts
  const nothing = !social.length && !emails.length && !phones.length

  return (
    <section className="insight-card">
      <h3>
        <UsersIcon className="card-icon" />
        Contact &amp; social
      </h3>

      {nothing ? (
        <div className="empty-state">
          <InboxIcon width={26} height={26} strokeWidth={1.4} />
          <strong>Nothing published on this page</strong>
          <p>
            No social profiles, email addresses or phone numbers were found. Visitors and search
            engines both read contact details as a trust signal.
          </p>
        </div>
      ) : (
        <div className="contact-groups">
          {social.length > 0 && (
            <div className="contact-group">
              <span className="fact-group-title">
                <LinkIcon width={13} height={13} />
                {social.length} social {social.length === 1 ? 'profile' : 'profiles'}
              </span>
              <ul className="social-list">
                {social.map((profile) => (
                  <li key={profile.platform}>
                    <a href={profile.url} target="_blank" rel="noopener noreferrer">
                      <SocialMark platform={profile.platform} />
                      <span className="social-body">
                        <span className="social-name">{profile.platform}</span>
                        {profile.handle && <span className="social-handle">@{profile.handle}</span>}
                        <span className="social-url">{profile.url}</span>
                      </span>
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {emails.length > 0 && (
            <div className="contact-group">
              <span className="fact-group-title">Email</span>
              <ul className="contact-list">
                {emails.map((hit) => (
                  <ContactRow
                    key={hit.value}
                    Icon={MailIcon}
                    href={`mailto:${hit.value}`}
                    value={hit.value}
                    confidence={hit.confidence}
                  />
                ))}
              </ul>
            </div>
          )}

          {phones.length > 0 && (
            <div className="contact-group">
              <span className="fact-group-title">Phone</span>
              <ul className="contact-list">
                {phones.map((hit) => (
                  <ContactRow
                    key={hit.value}
                    Icon={PhoneIcon}
                    href={`tel:${hit.value.replace(/[^\d+]/g, '')}`}
                    value={hit.value}
                    confidence={hit.confidence}
                  />
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </section>
  )
}
