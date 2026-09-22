import { useState } from 'react'

export default function ElementInspector({ groups }) {
  const [open, setOpen] = useState(null)

  if (!groups || groups.length === 0) return null

  return (
    <section className="page-summary">
      <div className="summary-head">
        <h3>What is on this page</h3>
        <span>Open any row to see the detail. All of it is in the PDF.</span>
      </div>

      <ul className="summary-rows">
        {groups.map((group) => {
          const isOpen = open === group.key
          return (
            <li key={group.key} className={isOpen ? 'summary-row open' : 'summary-row'}>
              <button
                type="button"
                className="summary-trigger"
                aria-expanded={isOpen}
                onClick={() => setOpen(isOpen ? null : group.key)}
              >
                <span className="summary-count">{group.total}</span>
                <span className="summary-text">
                  <span className="summary-label">{group.label}</span>
                  <span className="summary-hint">{group.hint}</span>
                </span>
                <span className="summary-toggle" aria-hidden="true">
                  {isOpen ? 'Hide' : 'Show'}
                </span>
              </button>

              {isOpen && (
                <div className="summary-detail">
                  <ul className="entry-list">
                    {group.items.map((entry, index) => (
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

                  {group.total > group.items.length && (
                    <p className="summary-more">
                      Showing the first {group.items.length} of {group.total}. The PDF has every one.
                    </p>
                  )}
                </div>
              )}
            </li>
          )
        })}
      </ul>
    </section>
  )
}
