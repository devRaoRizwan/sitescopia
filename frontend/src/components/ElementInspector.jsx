import { useMemo, useState } from 'react'

const VIEWS = [
  { key: 'alerts', label: 'Needs attention' },
  { key: 'all', label: 'Everything' },
]

const matches = (entry, term) => {
  if (!term) return true
  return [entry.label, ...Object.values(entry.props)].join(' ').toLowerCase().includes(term)
}

export default function ElementInspector({ groups }) {
  const [view, setView] = useState('all')
  const [active, setActive] = useState(groups?.[0]?.key ?? null)
  const [term, setTerm] = useState('')

  const search = term.trim().toLowerCase()

  const shown = useMemo(
    () =>
      groups
        .map((group) => ({
          ...group,
          visible: group.items.filter(
            (entry) => (view === 'all' || entry.alert) && matches(entry, search),
          ),
        }))
        .filter((group) => view === 'all' || group.alerts > 0),
    [groups, view, search],
  )

  if (!groups || groups.length === 0) return null

  const group = shown.find((entry) => entry.key === active) ?? shown[0]
  const totalShown = shown.reduce((sum, entry) => sum + entry.visible.length, 0)
  const totalAll = groups.reduce((sum, entry) => sum + entry.total, 0)

  return (
    <section className="browser inspector">
      <div className="browser-toolbar">
        <h3>What is on this page</h3>

        <div className="segmented">
          {VIEWS.map(({ key, label }) => (
            <button
              key={key}
              type="button"
              className={view === key ? 'active' : ''}
              onClick={() => setView(key)}
            >
              {label}
            </button>
          ))}
        </div>

        <span className="result-count">
          {totalShown} of {totalAll}
        </span>
      </div>

      {!group ? (
        <p className="hint panel-empty inspector-clear">
          Nothing on this page needs attention. Switch to “Everything” to browse it all.
        </p>
      ) : (
        <div className="browser-body">
          <aside className="browser-rail" aria-label="Choose what to look at">
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
              {shown.map((entry) => (
                <li key={entry.key}>
                  <button
                    type="button"
                    className={entry.key === group.key ? 'rail-item active' : 'rail-item'}
                    onClick={() => setActive(entry.key)}
                  >
                    <span>{entry.label}</span>
                    {entry.alerts > 0 && view === 'all' && (
                      <span className="rail-alert" title={`${entry.alerts} need attention`}>
                        {entry.alerts}
                      </span>
                    )}
                    <span className="rail-count">
                      {view === 'all' ? entry.total : entry.visible.length}
                    </span>
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

            {group.visible.length === 0 ? (
              <p className="hint panel-empty">Nothing here matches “{term}”.</p>
            ) : (
              <ul className="entry-list">
                {group.visible.map((entry, index) => (
                  <li
                    key={`${entry.label}-${index}`}
                    className={entry.alert ? 'entry alert' : 'entry'}
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

            {group.total > group.items.length && view === 'all' && (
              <p className="summary-more">
                Showing the first {group.items.length} of {group.total}. The PDF has every one.
              </p>
            )}
          </div>
        </div>
      )}
    </section>
  )
}
