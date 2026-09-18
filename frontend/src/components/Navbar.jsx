import { useEffect, useState } from 'react'
import { Link, NavLink, useLocation } from 'react-router-dom'

const LINKS = [
  { to: '/how-it-works', label: 'How it works' },
  { to: '/checks', label: 'Checks' },
  { to: '/about', label: 'About' },
  { to: '/contact', label: 'Contact' },
]

export default function Navbar() {
  const [open, setOpen] = useState(false)
  const { pathname } = useLocation()

  useEffect(() => setOpen(false), [pathname])

  return (
    <header className="navbar">
      <div className="shell navbar-inner">
        <Link className="brand" to="/">
          <img className="brand-mark-image" src="/site-scopia.svg" alt="" />
          <span className="brand-name">SiteScopia</span>
        </Link>

        <nav className={open ? 'nav-links open' : 'nav-links'} aria-label="Main">
          {LINKS.map(({ to, label }) => (
            <NavLink key={to} to={to} className={({ isActive }) => (isActive ? 'active' : '')}>
              {label}
            </NavLink>
          ))}
        </nav>

        <Link className="nav-cta" to="/">
          Run a scan
        </Link>

        <button
          type="button"
          className="nav-toggle"
          aria-expanded={open}
          aria-label="Toggle navigation"
          onClick={() => setOpen((value) => !value)}
        >
          <span aria-hidden="true">{open ? '✕' : '☰'}</span>
        </button>
      </div>
    </header>
  )
}
