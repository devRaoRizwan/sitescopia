import { useMemo, useState } from 'react'

const matches = (entry, term) => {
  if (!term) return true
  const haystack = [entry.label, ...Object.values(entry.props)].join(' ').toLowerCase()
  return haystack.includes(term)
}

export default function ElementInspector({ groups }) {
  const [active, setActive] = useState(groups?.[0]?.key ?? null)
  const [term, setTerm] = useState('')

  if (!groups || groups.length === 0) return null

  const group = groups.find((entry) => entry.key === active) ?? groups[0]
  const search = term.trim().toLowerCase()
  const visible = useMemo(() => group.items.filter((entry) => matches(entry, search)), [group, search])

  return (
    <section className="browser inspector">
      <div className="browser-toolbar">
        <h3>What is on this page</h3>
        <span className="result-count">
          {visible.length} of {group.total} shown
        </span>
      </div>

      <div className="browser-body">
        <aside className="browser-rail" aria-label="Choose what to inspect">
          <div className="rail-head">Look at</div>

          <label className="rail-search">
            <span className="sr-only">Search this list</span>
            <input
              type="search"
              value={term}
              onChange={(event) => setTerm(event.target.value)}
              placeholder="Search…"
            />
          </label>

          <ul className="rail-list">
            {groups.map((entry) => (
              <li key={entry.key}>
                <button
                  type="button"
                  className={entry.key === group.key ? 'rail-item active' : 'rail-item'}
                  onClick={() => setActive(entry.key)}
                >
                  <span>{entry.label}</span>
                  <span className="rail-count">{entry.total}</span>
                </button>
              </li>
            ))}
          </ul>
        </aside>

        <div className="browser-panel">
          <div className="panel-head">
            <h3>{group.label}</h3>
            <span>{group.hint}</span>
          </div>

          {visible.length === 0 ? (
            <p className="hint panel-empty">Nothing here matches “{term}”.</p>
          ) : (
            <ul className="entry-list">
              {visible.map((entry, index) => (
                <li
                  key={`${entry.label}-${index}`}
                  style={entry.depth > 1 ? { marginLeft: (entry.depth - 1) * 16 } : undefined}
                >
                  <div className="entry-head">
                    <span className="entry-label">{entry.label}</span>
                    {entry.line != null && (
                      <span className="entry-line" title="Line in the page source">
                        line {entry.line}
                      </span>
                    )}
                  </div>
                  <dl className="entry-props">
                    {Object.entries(entry.props).map(([key, value]) => (
                      <div key={key}>
                        <dt>{key}</dt>
                        <dd>{value}</dd>
                      </div>
                    ))}
                  </dl>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </section>
  )
}
