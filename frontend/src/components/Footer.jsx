import { Link } from 'react-router-dom'

const COLUMNS = [
  {
    title: 'Product',
    links: [
      { to: '/', label: 'Analyze a page' },
      { to: '/checks', label: 'What we check' },
      { to: '/how-it-works', label: 'How it works' },
    ],
  },
  {
    title: 'Company',
    links: [
      { to: '/about', label: 'About' },
      { to: '/contact', label: 'Contact' },
    ],
  },
  {
    title: 'Legal',
    links: [
      { to: '/privacy', label: 'Privacy' },
      { to: '/terms', label: 'Terms' },
    ],
  },
]

export default function Footer() {
  return (
    <footer className="footer">
      <div className="shell">
        <div className="footer-grid">
          <div className="footer-about">
            <Link className="brand" to="/">
              <img className="brand-mark-image" src="/site-scopia.svg" alt="" />
              <span className="brand-name">SiteScopia</span>
            </Link>
            <p>
              Point us at any page and we will tell you what is wrong with it. We show you the
              evidence, not just a score.
            </p>
          </div>

          {COLUMNS.map(({ title, links }) => (
            <nav key={title} className="footer-col" aria-label={title}>
              <h3>{title}</h3>
              <ul>
                {links.map(({ to, label }) => (
                  <li key={to}>
                    <Link to={to}>{label}</Link>
                  </li>
                ))}
              </ul>
            </nav>
          ))}
        </div>

        <div className="footer-bottom">
          <span>© {new Date().getFullYear()} SiteScopia</span>
          <span>Scans public pages only, and refuses private or internal addresses.</span>
        </div>
      </div>
    </footer>
  )
}
