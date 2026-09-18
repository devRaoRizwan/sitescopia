import { useMemo, useState } from 'react'
import FindingCard from './FindingCard'
import AdSlot from './AdSlot'
import { CATEGORY_LABELS } from './status'

const SEVERITY_FILTERS = [
  { key: 'issues', label: 'Issues only' },
  { key: 'all', label: 'All checks' },
]

const AD_AFTER_NTH_FINDING = 6

const matches = (finding, term) => {
  if (!term) return true
  const haystack = [
    finding.title,
    finding.detail,
    finding.evidence,
    finding.recommendation,
    CATEGORY_LABELS[finding.category],
  ]
  return haystack.some((value) => value && value.toLowerCase().includes(term))
}

export default function FindingsBrowser({ findings, category, onCategory }) {
  const [severity, setSeverity] = useState('issues')
  const [term, setTerm] = useState('')

  const search = term.trim().toLowerCase()

  const bySeverity = useMemo(
    () => findings.filter((f) => severity === 'all' || f.severity !== 'pass'),
    [findings, severity],
  )

  const searched = useMemo(() => bySeverity.filter((f) => matches(f, search)), [bySeverity, search])

  const counts = useMemo(() => {
    const totals = {}
    for (const finding of searched) {
      totals[finding.category] = (totals[finding.category] || 0) + 1
    }
    return totals
  }, [searched])

  const visible = searched.filter((f) => category === 'all' || f.category === category)
  const activeLabel = category === 'all' ? 'All findings' : CATEGORY_LABELS[category]

  return (
    <section className="browser">
      <div className="browser-toolbar">
        <div className="segmented">
          {SEVERITY_FILTERS.map(({ key, label }) => (
            <button
              key={key}
              type="button"
              className={severity === key ? 'active' : ''}
              onClick={() => setSeverity(key)}
            >
              {label}
            </button>
          ))}
        </div>
        <span className="result-count">
          {visible.length} of {findings.length} checks
        </span>
      </div>

      <div className="browser-body">
        <aside className="browser-rail" aria-label="Filter findings by category">
          <div className="rail-head">Category</div>

          <label className="rail-search">
            <span className="sr-only">Search findings</span>
            <input
              type="search"
              value={term}
              onChange={(event) => setTerm(event.target.value)}
              placeholder="Search findings…"
            />
          </label>

          <ul className="rail-list">
            <li>
              <button
                type="button"
                className={category === 'all' ? 'rail-item active' : 'rail-item'}
                onClick={() => onCategory('all')}
              >
                <span>All</span>
                <span className="rail-count">{searched.length}</span>
              </button>
            </li>
            {Object.entries(CATEGORY_LABELS)
              .filter(([key]) => counts[key])
              .sort(([a], [b]) => counts[b] - counts[a])
              .map(([key, label]) => (
                <li key={key}>
                  <button
                    type="button"
                    className={category === key ? 'rail-item active' : 'rail-item'}
                    onClick={() => onCategory(category === key ? 'all' : key)}
                  >
                    <span className={`dot dot-${key}`} aria-hidden="true" />
                    <span>{label}</span>
                    <span className="rail-count">{counts[key]}</span>
                  </button>
                </li>
              ))}
          </ul>
        </aside>

        <div className="browser-panel">
          <div className="panel-head">
            <h3>{activeLabel}</h3>
            <span>{visible.length} items</span>
          </div>

          {visible.length === 0 ? (
            <p className="hint panel-empty">
              Nothing matches {search ? `“${term}”` : 'these filters'}.
            </p>
          ) : (
            <ul className="panel-list">
              {visible.map((finding, index) => (
                <li key={`${finding.category}-${finding.title}-${index}`}>
                  <FindingCard finding={finding} />
                  {index === AD_AFTER_NTH_FINDING - 1 && visible.length > AD_AFTER_NTH_FINDING + 2 && (
                    <AdSlot format="inline" />
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </section>
  )
}
