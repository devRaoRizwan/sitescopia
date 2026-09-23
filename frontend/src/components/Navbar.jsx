import { useEffect, useRef, useState } from 'react'
import { Link, NavLink, useLocation } from 'react-router-dom'
import { useScan } from '../scan'

const LINKS = [
  { to: '/how-it-works', label: 'How it works' },
  { to: '/checks', label: 'Checks' },
  { to: '/about', label: 'About' },
  { to: '/contact', label: 'Contact' },
]

const scrollTo = (target) => {
  const smooth = !window.matchMedia('(prefers-reduced-motion: reduce)').matches
  const behavior = smooth ? 'smooth' : 'auto'
  if (target === 'top') window.scrollTo({ top: 0, behavior })
  else document.getElementById(target)?.scrollIntoView({ behavior, block: 'start' })
}

export default function Navbar() {
  const [open, setOpen] = useState(false)
  const { pathname } = useLocation()
  const { busy } = useScan()
  const navRef = useRef(null)

  useEffect(() => setOpen(false), [pathname])

  useEffect(() => {
    if (!open) return

    const onKeyDown = (event) => {
      if (event.key === 'Escape') setOpen(false)
    }
    const onPointerDown = (event) => {
      if (!navRef.current?.contains(event.target)) setOpen(false)
    }

    document.addEventListener('keydown', onKeyDown)
    document.addEventListener('pointerdown', onPointerDown)
    return () => {
      document.removeEventListener('keydown', onKeyDown)
      document.removeEventListener('pointerdown', onPointerDown)
    }
  }, [open])

  // Routing to the page you are already on fires no navigation, so the menu has
  // to close here and the scroll has to be done by hand.
  const navigateWithin = (target) => (event) => {
    setOpen(false)
    if (pathname !== '/') return
    event.preventDefault()
    scrollTo(target)
  }

  return (
    <header className="navbar" ref={navRef}>
      <div className="shell navbar-inner">
        <Link className="brand" to="/" onClick={navigateWithin('top')}>
          <img className="brand-mark-image" src="/site-scopia.svg" alt="" />
          <span className="brand-name">SiteScopia</span>
        </Link>

        <nav className={open ? 'nav-links open' : 'nav-links'} aria-label="Main">
          {LINKS.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => setOpen(false)}
              className={({ isActive }) => (isActive ? 'active' : '')}
            >
              {label}
            </NavLink>
          ))}
        </nav>

        <Link className="nav-cta" to="/" onClick={navigateWithin('analyze')}>
          {busy ? 'Scan running…' : 'Run a scan'}
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
